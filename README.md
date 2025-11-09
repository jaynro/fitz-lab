# Fitz Lab - PDF Document Analysis Tool

A Python application that extracts and analyzes table data from PDF documents using PyMuPDF (fitz), with structured data validation using Pydantic.

## 🚀 Features

- Extract metadata from PDF documents
- Parse table data from PDFs with specific column filtering
- Structured JSON output with data validation
- Support for disability category analysis
- Clean, type-safe data models using Pydantic

## 📋 Requirements

See `requirements.txt` for all dependencies:
- `pydantic>=2.0.0` - Data validation and settings management
- `PyMuPDF>=1.23.0` - PDF manipulation (provides fitz module)
- `deepeval>=0.21.0` - LLM evaluation and testing

## 🏗️ Architecture & Code Flow

### System Overview

```mermaid
graph TB
    A[PDF Files in input/] --> B[sampleFitz.py]
    B --> C[PyMuPDF/fitz]
    C --> D[Text Extraction]
    D --> E[Data Processing]
    E --> F[Pydantic Models]
    F --> G[JSON Output]
    
    subgraph "Data Models"
        H[PDFDocument]
        I[PDFPage] 
        J[DocumentData]
    end
    
    F --> H
    F --> I
    F --> J
```

### Data Flow Diagram

```mermaid
flowchart LR
    subgraph "Input"
        PDF[📄 table.pdf]
    end
    
    subgraph "Processing Pipeline"
        A[Load PDF] --> B[Extract Metadata]
        B --> C[Extract Text Content]
        C --> D[Parse Table Structure]
        D --> E[Apply Column Filter]
        E --> F[Validate Data Types]
    end
    
    subgraph "Output"
        JSON[📊 Structured JSON]
    end
    
    PDF --> A
    F --> JSON
    
    subgraph "Target Columns"
        COL1[Disability Category]
        COL2[Participants]
        COL3[Ballots Completed]
    end
    
    E --> COL1
    E --> COL2
    E --> COL3
```

### Class Structure

```mermaid
classDiagram
    class PDFDocument {
        +str filename
        +int page_count
        +Optional[str] title
        +Optional[str] author
        +Optional[str] subject
        +Optional[str] creator
    }
    
    class PDFPage {
        +int page_number
        +str text_content
        +str filtered_content
        +int image_count
        +int link_count
    }
    
    class DocumentData {
        +PDFDocument metadata
        +List[PDFPage] pages
        +str full_text
        +str filtered_text
    }
    
    class TableRow {
        +str disability_category
        +str participants
        +str ballots_completed
        +str completion_percentage
    }
    
    DocumentData --> PDFDocument
    DocumentData --> PDFPage
    PDFPage --> TableRow : "extracts to"
```

## 🔄 Function Flow

### Main Processing Function

```mermaid
sequenceDiagram
    participant Main as main()
    participant Processor as process_pdfs_in_folder_json()
    participant Extractor as extract_complete_document_data()
    participant Parser as extract_table_data()
    participant Output as JSON Output
    
    Main->>Processor: Call with "input" folder
    Processor->>Processor: Find PDF files
    loop For each PDF
        Processor->>Extractor: Extract document data
        Extractor->>Extractor: Get metadata
        Extractor->>Extractor: Get page content
        Extractor-->>Processor: Return DocumentData
        Processor->>Parser: Parse table from text
        Parser-->>Processor: Return structured data
    end
    Processor->>Output: Generate JSON result
```

### Table Data Extraction Process

```mermaid
flowchart TD
    A[Raw PDF Text] --> B[Split into Lines]
    B --> C[Combine to Single Line]
    C --> D[Apply Regex Patterns]
    
    subgraph "Category Patterns"
        E["Blind\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+%)"]
        F["Low Vision\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+%)"]
        G["Dexterity\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+%)"]
        H["Mobility\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+%)"]
    end
    
    D --> E
    D --> F
    D --> G
    D --> H
    
    E --> I[Extract: Participants, Completed, Percentage]
    F --> I
    G --> I
    H --> I
    
    I --> J[Structured Table Data]
```

## 📁 Project Structure

### **Modular Version (Recommended):**
```
fitz-lab/
├── README.md                        # This documentation
├── requirements.txt                 # Python dependencies
├── config.py                        # Configuration settings
├── main.py                         # 🎯 Entry point (modular)
├── models/
│   ├── __init__.py
│   └── pdf_models.py               # 📋 Pydantic data models
├── extractors/
│   ├── __init__.py
│   ├── pdf_extractor.py            # 📄 PDF reading utilities
│   └── table_extractor.py          # 📊 Table parsing logic
├── processors/
│   ├── __init__.py
│   └── document_processor.py       # 🔄 Main orchestration
├── utils/
│   ├── __init__.py
│   └── file_utils.py               # 🛠️ File operations
└── input/                          # PDF files directory
    └── table.pdf                   # Sample data
```

### **Original Version (For Comparison):**
```
├── sampleFitz.py                   # 📄 Original monolithic script (271 lines)
```

## 🚀 Usage

### **Two Versions Available:**

#### **🔹 Version 1: Modular Structure (Recommended)**
```bash
# Clean, maintainable, production-ready
python main.py
```

#### **🔹 Version 2: Original Monolithic**
```bash
# Original single-file version for comparison
python sampleFitz.py
```

### **Setup Instructions:**

1. **Set up environment:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2. **Run either version:**
```bash
# Recommended: Use the modular version
python main.py

# Or: Use the original version
python sampleFitz.py
```

3. **Expected Output:**
```json
{
  "processed_documents": 1,
  "documents": [
    {
      "filename": "table.pdf",
      "table_data": {
        "columns": ["Disability Category", "Participants", "Ballots Completed"],
        "rows": [
          {
            "disability_category": "Blind",
            "participants": "5",
            "ballots_completed": "1",
            "completion_percentage": "34.5%"
          }
          // ... more categories
        ]
      }
    }
  ]
}
```

## 📊 Data Model Details

The application uses Pydantic models for type safety and data validation:

- **PDFDocument**: Stores PDF metadata (author, title, page count)
- **PDFPage**: Represents individual page content and statistics
- **DocumentData**: Complete document structure with all pages
- **Table Extraction**: Processes structured data into clean JSON format

## 🎯 Key Features Explained

### Column Filtering
The system specifically extracts three columns from PDF tables:
1. **Disability Category** (Blind, Low Vision, Dexterity, Mobility)
2. **Participants** (Total number in each category)
3. **Ballots Completed** (Successfully completed ballots)

### Pattern Matching
Uses regex patterns to identify and extract structured data from unformatted PDF text, handling variations in spacing and formatting.

### Type Safety
All data structures use Pydantic models ensuring type safety and automatic validation of extracted data.

## 🔄 Version Comparison

| Feature | `main.py` (Modular) | `sampleFitz.py` (Original) |
|---------|-------------------|---------------------------|
| **Lines of Code** | ~15 (main) + modules | ~271 (single file) |
| **Structure** | Separated concerns | Mixed responsibilities |
| **Maintainability** | ✅ High | ⚠️ Medium |
| **Testability** | ✅ Easy to unit test | ❌ Hard to test parts |
| **Readability** | ✅ Clear modules | ⚠️ Large single file |
| **Extensibility** | ✅ Easy to add features | ❌ Requires modification |
| **Configuration** | ✅ Centralized in `config.py` | ❌ Hardcoded values |

### **When to Use Which Version:**

- **🎯 Use `main.py`** for:
  - Production environments
  - When adding new features
  - Team collaboration
  - Long-term maintenance

- **📚 Use `sampleFitz.py`** for:
  - Learning/educational purposes
  - Quick prototyping
  - Understanding the full flow in one file
  - Comparing architectural approaches

## 🧪 Testing Both Versions

```bash
# Test modular version
echo "Testing modular version..."
python main.py

echo -e "\n" + "="*50 + "\n"

# Test original version
echo "Testing original version..."
python sampleFitz.py
```

Both versions produce identical output, demonstrating that refactoring improved code organization without changing functionality.

---

**Author:** Mary  
**Created with:** Python 3.12.2, PyMuPDF, Pydantic  
**Architecture:** Available in both monolithic and modular versions
