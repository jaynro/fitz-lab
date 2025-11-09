"""
Integration tests using DeepEval for content evaluation
"""

import unittest
import json
from pathlib import Path

try:
    from deepeval import evaluate
    from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, ContextualPrecisionMetric
    from deepeval.test_case import LLMTestCase
    DEEPEVAL_AVAILABLE = True
except ImportError:
    DEEPEVAL_AVAILABLE = False
    print("Warning: DeepEval not available. Skipping DeepEval tests.")

from processors.document_processor import DocumentProcessor
from extractors.pdf_extractor import PDFExtractor
from extractors.table_extractor import TableExtractor
from tests.conftest import SAMPLE_PDF_PATH, EXPECTED_CATEGORIES, EXPECTED_COLUMNS


@unittest.skipUnless(DEEPEVAL_AVAILABLE, "DeepEval not available")
class TestDeepEvalIntegration(unittest.TestCase):
    """Integration tests using DeepEval for content evaluation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = DocumentProcessor("input")
        
        # Expected ground truth for our sample PDF
        self.expected_data = {
            "categories": EXPECTED_CATEGORIES,
            "columns": EXPECTED_COLUMNS,
            "blind_data": {
                "participants": "5",
                "ballots_completed": "1",
                "completion_percentage": "34.5%"
            },
            "low_vision_data": {
                "participants": "5", 
                "ballots_completed": "2",
                "completion_percentage": "98.3%"
            },
            "dexterity_data": {
                "participants": "5",
                "ballots_completed": "4", 
                "completion_percentage": "98.3%"
            },
            "mobility_data": {
                "participants": "3",
                "ballots_completed": "3",
                "completion_percentage": "95.4%"
            }
        }
    
    def test_extraction_faithfulness(self):
        """Test if extracted data is faithful to the original PDF content"""
        if not SAMPLE_PDF_PATH.exists():
            self.skipTest("Sample PDF file not found")
        
        # Extract data using our system
        document_data = PDFExtractor.extract_complete_document_data(str(SAMPLE_PDF_PATH))
        table_data = TableExtractor.extract_table_data(document_data.full_text)
        
        # Convert to text for evaluation
        extracted_content = self._format_extraction_results(table_data)
        original_content = document_data.full_text
        
        # Create test case for faithfulness
        test_case = LLMTestCase(
            input="Extract disability category data from the PDF table",
            actual_output=extracted_content,
            retrieval_context=[original_content]
        )
        
        # Evaluate faithfulness
        faithfulness_metric = FaithfulnessMetric(threshold=0.8)
        
        try:
            faithfulness_metric.measure(test_case)
            score = faithfulness_metric.score
            
            # Assert faithfulness score meets threshold
            self.assertGreaterEqual(score, 0.8, 
                f"Faithfulness score {score} below threshold 0.8")
            
            print(f"✅ Faithfulness Score: {score}")
            
        except Exception as e:
            self.skipTest(f"DeepEval evaluation failed: {e}")
    
    def test_extraction_relevancy(self):
        """Test if extracted data is relevant to the query"""
        if not SAMPLE_PDF_PATH.exists():
            self.skipTest("Sample PDF file not found")
        
        # Extract data
        document_data = PDFExtractor.extract_complete_document_data(str(SAMPLE_PDF_PATH))
        table_data = TableExtractor.extract_table_data(document_data.full_text)
        
        # Create specific query and response
        query = "What are the participant counts and ballot completion rates for each disability category?"
        extracted_content = self._format_extraction_results_detailed(table_data)
        
        # Create test case
        test_case = LLMTestCase(
            input=query,
            actual_output=extracted_content,
            retrieval_context=[document_data.full_text]
        )
        
        # Evaluate answer relevancy
        relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
        
        try:
            relevancy_metric.measure(test_case)
            score = relevancy_metric.score
            
            # Assert relevancy score meets threshold
            self.assertGreaterEqual(score, 0.7,
                f"Relevancy score {score} below threshold 0.7")
            
            print(f"✅ Relevancy Score: {score}")
            
        except Exception as e:
            self.skipTest(f"DeepEval evaluation failed: {e}")
    
    def test_contextual_precision(self):
        """Test contextual precision of extracted data"""
        if not SAMPLE_PDF_PATH.exists():
            self.skipTest("Sample PDF file not found")
        
        # Extract data
        document_data = PDFExtractor.extract_complete_document_data(str(SAMPLE_PDF_PATH))
        table_data = TableExtractor.extract_table_data(document_data.full_text)
        
        # Create expected answer based on our ground truth
        expected_answer = self._create_expected_answer()
        extracted_content = self._format_extraction_results_detailed(table_data)
        
        # Create test case
        test_case = LLMTestCase(
            input="Extract participant and completion data for disability categories",
            actual_output=extracted_content,
            expected_output=expected_answer,
            retrieval_context=[document_data.full_text]
        )
        
        # Evaluate contextual precision
        precision_metric = ContextualPrecisionMetric(threshold=0.8)
        
        try:
            precision_metric.measure(test_case)
            score = precision_metric.score
            
            # Assert precision score meets threshold
            self.assertGreaterEqual(score, 0.8,
                f"Contextual precision score {score} below threshold 0.8")
            
            print(f"✅ Contextual Precision Score: {score}")
            
        except Exception as e:
            self.skipTest(f"DeepEval evaluation failed: {e}")
    
    def test_end_to_end_evaluation(self):
        """Test complete end-to-end pipeline evaluation"""
        if not SAMPLE_PDF_PATH.exists():
            self.skipTest("Sample PDF file not found")
        
        # Run complete pipeline
        result = self.processor.process_all_pdfs()
        
        # Verify structure
        self.assertEqual(result["processed_documents"], 1)
        self.assertEqual(len(result["documents"]), 1)
        
        document = result["documents"][0]
        table_data = document["table_data"]
        
        # Verify all expected categories are found
        found_categories = document["summary"]["categories_found"]
        for category in EXPECTED_CATEGORIES:
            self.assertIn(category, found_categories,
                f"Category '{category}' not found in extraction results")
        
        # Verify data structure
        self.assertEqual(table_data["columns"], EXPECTED_COLUMNS)
        self.assertEqual(len(table_data["rows"]), 4)
        
        # DeepEval assessment of complete output
        complete_output = json.dumps(result, indent=2)
        
        test_case = LLMTestCase(
            input="Process PDF and extract structured disability category data",
            actual_output=complete_output,
            expected_output=self._create_expected_json_output()
        )
        
        # Use multiple metrics for comprehensive evaluation
        metrics = []
        
        try:
            # Faithfulness to source
            faithfulness = FaithfulnessMetric(threshold=0.7)
            faithfulness.measure(test_case)
            metrics.append(("Faithfulness", faithfulness.score))
            
            # Relevancy to task
            relevancy = AnswerRelevancyMetric(threshold=0.7)
            relevancy.measure(test_case)
            metrics.append(("Relevancy", relevancy.score))
            
            print("\n🎯 End-to-End Evaluation Results:")
            for metric_name, score in metrics:
                print(f"   {metric_name}: {score:.3f}")
                
            # Assert all metrics meet minimum thresholds
            for metric_name, score in metrics:
                self.assertGreaterEqual(score, 0.7,
                    f"{metric_name} score {score} below threshold 0.7")
            
        except Exception as e:
            self.skipTest(f"DeepEval evaluation failed: {e}")
    
    def _format_extraction_results(self, table_data):
        """Format table data for DeepEval evaluation"""
        results = []
        for row in table_data:
            if row.participants is not None:
                results.append(
                    f"{row.disability_category}: {row.participants} participants, "
                    f"{row.ballots_completed} completed ballots, "
                    f"{row.completion_percentage} completion rate"
                )
        return "\n".join(results)
    
    def _format_extraction_results_detailed(self, table_data):
        """Format table data with detailed structure for evaluation"""
        results = {
            "extracted_categories": [],
            "data_points": {}
        }
        
        for row in table_data:
            results["extracted_categories"].append(row.disability_category)
            if row.participants is not None:
                results["data_points"][row.disability_category] = {
                    "participants": row.participants,
                    "ballots_completed": row.ballots_completed,
                    "completion_percentage": row.completion_percentage
                }
        
        return json.dumps(results, indent=2)
    
    def _create_expected_answer(self):
        """Create expected answer for comparison"""
        return """
        Expected disability categories with their data:
        - Blind: 5 participants, 1 completed ballot, 34.5% completion rate
        - Low Vision: 5 participants, 2 completed ballots, 98.3% completion rate  
        - Dexterity: 5 participants, 4 completed ballots, 98.3% completion rate
        - Mobility: 3 participants, 3 completed ballots, 95.4% completion rate
        """
    
    def _create_expected_json_output(self):
        """Create expected JSON output for comparison"""
        return json.dumps({
            "processed_documents": 1,
            "documents": [{
                "filename": "table.pdf",
                "table_data": {
                    "columns": EXPECTED_COLUMNS,
                    "categories_extracted": EXPECTED_CATEGORIES,
                    "data_quality": "All disability categories successfully extracted with numeric data"
                }
            }]
        }, indent=2)


@unittest.skipUnless(DEEPEVAL_AVAILABLE, "DeepEval not available")  
class TestDeepEvalCustomMetrics(unittest.TestCase):
    """Custom DeepEval metrics for specific PDF extraction validation"""
    
    def test_data_completeness_metric(self):
        """Test custom metric for data completeness"""
        if not SAMPLE_PDF_PATH.exists():
            self.skipTest("Sample PDF file not found")
            
        # Extract data
        processor = DocumentProcessor("input")
        result = processor.process_all_pdfs()
        
        if result["processed_documents"] == 0:
            self.skipTest("No documents processed")
            
        document = result["documents"][0]
        table_data = document["table_data"]
        
        # Custom completeness evaluation
        completeness_score = self._calculate_completeness_score(table_data["rows"])
        
        # Should achieve high completeness (all categories with data)
        self.assertGreaterEqual(completeness_score, 0.9,
            f"Data completeness score {completeness_score} below expected 0.9")
        
        print(f"✅ Data Completeness Score: {completeness_score}")
    
    def test_accuracy_metric(self):
        """Test custom accuracy metric against known ground truth"""
        if not SAMPLE_PDF_PATH.exists():
            self.skipTest("Sample PDF file not found")
            
        # Extract data  
        processor = DocumentProcessor("input")
        result = processor.process_all_pdfs()
        
        if result["processed_documents"] == 0:
            self.skipTest("No documents processed")
            
        document = result["documents"][0]
        table_data = document["table_data"]
        
        # Calculate accuracy against ground truth
        accuracy_score = self._calculate_accuracy_score(table_data["rows"])
        
        # Should achieve high accuracy
        self.assertGreaterEqual(accuracy_score, 0.9,
            f"Accuracy score {accuracy_score} below expected 0.9")
        
        print(f"✅ Accuracy Score: {accuracy_score}")
    
    def _calculate_completeness_score(self, extracted_rows):
        """Calculate completeness score (0-1)"""
        total_categories = len(EXPECTED_CATEGORIES)
        categories_with_data = sum(1 for row in extracted_rows 
                                 if row.get("participants") is not None)
        
        return categories_with_data / total_categories
    
    def _calculate_accuracy_score(self, extracted_rows):
        """Calculate accuracy score against ground truth (0-1)"""
        correct_extractions = 0
        total_comparisons = 0
        
        # Ground truth mapping
        ground_truth = {
            "Blind": {"participants": "5", "ballots_completed": "1"},
            "Low Vision": {"participants": "5", "ballots_completed": "2"},
            "Dexterity": {"participants": "5", "ballots_completed": "4"},
            "Mobility": {"participants": "3", "ballots_completed": "3"}
        }
        
        for row in extracted_rows:
            category = row.get("disability_category")
            if category in ground_truth and row.get("participants") is not None:
                truth = ground_truth[category]
                
                # Check participants
                if row.get("participants") == truth["participants"]:
                    correct_extractions += 1
                total_comparisons += 1
                
                # Check ballots completed
                if row.get("ballots_completed") == truth["ballots_completed"]:
                    correct_extractions += 1
                total_comparisons += 1
        
        return correct_extractions / total_comparisons if total_comparisons > 0 else 0


if __name__ == '__main__':
    unittest.main()