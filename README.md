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

## 🏗️ Architecture & Code Flow (main.py - Modular Version)

### System Architecture Overview

```mermaid
graph TB
    A[📁 input/] --> B[🎯 main.py]
    B --> C[🔄 DocumentProcessor]
    C --> D[📄 PDFExtractor]
    C --> E[📊 TableExtractor]
    D --> F[🐍 PyMuPDF/fitz]
    E --> G[🔍 Regex Patterns]
    
    subgraph "📋 Data Models"
        H[PDFDocument]
        I[PDFPage] 
        J[DocumentData]
        K[TableRow]
    end
    
    subgraph "⚙️ Configuration"
        L[config.py]
    end
    
    subgraph "🛠️ Utilities"
        M[FileUtils]
    end
    
    D --> H
    D --> I
    C --> J
    E --> K
    B --> L
    C --> M
    C --> N[📊 JSON Output]
```

### Modular Component Interaction

```mermaid
graph LR
    subgraph "🎯 Entry Point"
        A[main.py]
    end
    
    subgraph "📋 Data Layer"
        B[models/pdf_models.py]
    end
    
    subgraph "🔧 Processing Layer"
        C[processors/document_processor.py]
    end
    
    subgraph "📄 Extraction Layer"
        D[extractors/pdf_extractor.py]
        E[extractors/table_extractor.py]
    end
    
    subgraph "🛠️ Utility Layer"
        F[utils/file_utils.py]
    end
    
    subgraph "⚙️ Configuration"
        G[config.py]
    end
    
    A --> C
    C --> D
    C --> E
    C --> B
    C --> F
    A --> G
    D --> B
    E --> B
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

### Modular Class Architecture

```mermaid
classDiagram
    %% Data Models (models/pdf_models.py)
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
        +Optional[str] participants
        +Optional[str] ballots_completed
        +Optional[str] completion_percentage
    }
    
    class TableData {
        +List[str] columns
        +List[TableRow] rows
    }
    
    %% Processing Classes
    class DocumentProcessor {
        +str input_folder
        +Path input_path
        +validate_input_folder() bool
        +get_pdf_files() List[Path]
        +process_single_pdf(Path) Dict
        +process_all_pdfs() Dict
        +process_and_output_json() None
    }
    
    class PDFExtractor {
        +read_pdf_metadata(str) PDFDocument
        +extract_text_from_pdf(str) List[PDFPage]
        +extract_complete_document_data(str) DocumentData
    }
    
    class TableExtractor {
        +CATEGORY_PATTERNS List[Dict]
        +extract_table_data(str) List[TableRow]
        +get_target_columns() List[str]
    }
    
    class FileUtils {
        +save_json_to_file(Dict, str) bool
        +load_json_from_file(str) Dict
        +ensure_directory_exists(str) bool
    }
    
    class Config {
        +DEFAULT_INPUT_FOLDER str
        +DEFAULT_OUTPUT_FOLDER str
        +TARGET_COLUMNS List[str]
        +get_project_root() Path
    }
    
    %% Relationships
    DocumentData --> PDFDocument
    DocumentData --> PDFPage
    TableData --> TableRow
    DocumentProcessor --> PDFExtractor
    DocumentProcessor --> TableExtractor
    DocumentProcessor --> FileUtils
    DocumentProcessor --> Config
    PDFExtractor --> PDFDocument
    PDFExtractor --> PDFPage
    PDFExtractor --> DocumentData
    TableExtractor --> TableRow
```

### Processing Pipeline Architecture

```mermaid
flowchart TD
    A[🎯 main.py] --> B[⚙️ Config.DEFAULT_INPUT_FOLDER]
    A --> C[🔄 DocumentProcessor.__init__]
    
    C --> D[📂 validate_input_folder]
    D --> E{📄 PDFs found?}
    E -->|No| F[❌ Exit with error]
    E -->|Yes| G[📋 get_pdf_files]
    
    G --> H[🔄 Loop: process_single_pdf]
    
    subgraph "Single PDF Processing"
        H --> I[📄 PDFExtractor.extract_complete_document_data]
        I --> J[📊 TableExtractor.extract_table_data]
        J --> K[🏗️ Build document structure]
    end
    
    K --> L[📝 Collect all documents]
    L --> M[📊 Generate final JSON]
    M --> N[🖨️ Output results]
    
    subgraph "📄 PDF Extraction Details"
        I --> O[📋 read_pdf_metadata]
        I --> P[📃 extract_text_from_pdf]
        O --> Q[🔍 PyMuPDF operations]
        P --> Q
    end
    
    subgraph "📊 Table Extraction Details"
        J --> R[🔍 Apply regex patterns]
        R --> S[🎯 Extract target columns]
        S --> T[✅ Validate data types]
    end
```

## 🔄 Modular Function Flow

### Main Execution Sequence

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Main as 🎯 main.py
    participant Config as ⚙️ Config
    participant Processor as 🔄 DocumentProcessor
    participant PDFExt as 📄 PDFExtractor
    participant TableExt as 📊 TableExtractor
    participant Models as 📋 Pydantic Models
    participant Output as 📊 JSON Output
    
    User->>Main: python main.py
    Main->>Config: Get DEFAULT_INPUT_FOLDER
    Config-->>Main: "input"
    Main->>Processor: DocumentProcessor("input")
    Processor->>Processor: validate_input_folder()
    Processor->>Processor: get_pdf_files()
    
    loop For each PDF file
        Processor->>PDFExt: extract_complete_document_data(pdf_path)
        PDFExt->>PDFExt: read_pdf_metadata()
        PDFExt->>Models: Create PDFDocument
        PDFExt->>PDFExt: extract_text_from_pdf()
        PDFExt->>Models: Create PDFPage objects
        PDFExt->>Models: Create DocumentData
        PDFExt-->>Processor: Return DocumentData
        
        Processor->>TableExt: extract_table_data(full_text)
        TableExt->>TableExt: Apply regex patterns
        TableExt->>Models: Create TableRow objects
        TableExt-->>Processor: Return List[TableRow]
        
        Processor->>Processor: Build document structure
    end
    
    Processor->>Output: Generate final JSON
    Output-->>User: Display results
```

### Module Interaction Flow

```mermaid
flowchart LR
    subgraph "🎯 Execution Layer"
        A[main.py<br/>- Entry point<br/>- 15 lines]
    end
    
    subgraph "🔄 Business Logic Layer"
        B[DocumentProcessor<br/>- Orchestrates workflow<br/>- Handles file operations<br/>- Manages processing loop]
    end
    
    subgraph "🔧 Service Layer"
        C[PDFExtractor<br/>- PDF reading<br/>- Metadata extraction<br/>- Text extraction]
        D[TableExtractor<br/>- Pattern matching<br/>- Data parsing<br/>- Structure validation]
    end
    
    subgraph "📋 Data Layer"
        E[Pydantic Models<br/>- Type safety<br/>- Data validation<br/>- Structure definitions]
    end
    
    subgraph "⚙️ Configuration Layer"
        F[Config<br/>- Settings management<br/>- Path configuration<br/>- Constants]
    end
    
    subgraph "🛠️ Utility Layer"
        G[FileUtils<br/>- File operations<br/>- JSON handling<br/>- Path management]
    end
    
    A --> B
    B --> C
    B --> D
    C --> E
    D --> E
    A --> F
    B --> G
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#fce4ec
    style G fill:#f1f8e9
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
# 🎯 Recommended: Modular architecture (main.py)
python main.py

# 📄 Alternative: Original monolithic version
python sampleFitz.py
```

### **🏗️ Modular Architecture Usage**

The `main.py` version demonstrates clean architecture principles:

```python
# 🎯 main.py - Clean entry point
from processors.document_processor import DocumentProcessor
from config import Config

def main():
    processor = DocumentProcessor(Config.DEFAULT_INPUT_FOLDER)
    processor.process_and_output_json()

if __name__ == "__main__":
    main()
```

**Key Architectural Features:**
- ✅ **Single Responsibility**: Each module has one job
- ✅ **Dependency Injection**: Configurable components  
- ✅ **Type Safety**: Pydantic model validation
- ✅ **Testability**: Isolated, mockable components
- ✅ **Extensibility**: Easy to add new features

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

## 🏛️ Modular Architecture Benefits

### **🎯 Separation of Concerns**

| Module | Responsibility | Lines | Purpose |
|--------|---------------|--------|---------|
| **`main.py`** | Entry point | ~15 | Application bootstrap |
| **`config.py`** | Configuration | ~35 | Settings management |
| **`models/pdf_models.py`** | Data structures | ~45 | Type safety & validation |
| **`extractors/pdf_extractor.py`** | PDF operations | ~85 | Document reading |
| **`extractors/table_extractor.py`** | Pattern matching | ~75 | Data parsing |
| **`processors/document_processor.py`** | Orchestration | ~95 | Business logic |
| **`utils/file_utils.py`** | File operations | ~55 | Utility functions |

### **🔧 Module Dependencies**

```mermaid
graph TD
    A[main.py] --> B[processors/]
    A --> C[config.py]
    B --> D[extractors/]
    B --> E[models/]
    B --> F[utils/]
    D --> E
    
    style A fill:#ffcdd2
    style B fill:#f8bbd9
    style C fill:#e1bee7
    style D fill:#d1c4e9
    style E fill:#c5cae9
    style F fill:#bbdefb
```

## 📊 Data Model Details

### **Pydantic Models Structure**

The modular application uses strongly-typed Pydantic models:

- **`PDFDocument`**: Stores PDF metadata (author, title, page count)
- **`PDFPage`**: Represents individual page content and statistics  
- **`DocumentData`**: Complete document structure with all pages
- **`TableRow`**: Individual table row with disability data
- **`TableData`**: Complete table structure with columns and rows

### **Type Safety Benefits**

```python
# ✅ Type-safe operations
document: PDFDocument = PDFExtractor.read_pdf_metadata(path)
pages: List[PDFPage] = PDFExtractor.extract_text_from_pdf(path)
table_data: List[TableRow] = TableExtractor.extract_table_data(text)

# ✅ Automatic validation
row = TableRow(
    disability_category="Blind",
    participants="5",
    ballots_completed="1"
)  # Validates data types automatically
```

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
