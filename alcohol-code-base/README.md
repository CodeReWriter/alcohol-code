# Building Smeta Bot

A Telegram bot for automated analysis and processing of construction invoices and documents. The bot uses AI-powered document recognition to extract structured data from invoices, receipts, and other construction-related documents.

## Features

### 🤖 AI-Powered Document Analysis
- **Google Gemini Integration**: Advanced image and document analysis using Google's Gemini AI
- **N8N Workflow Support**: Alternative document processing pipeline
- **Multi-format Support**: PDF, DOCX, and various image formats (JPG, PNG, GIF, BMP, WEBP)

### 📊 Data Export & Storage
- **Google Services Integration**: 
  - Automatic Google Sheets creation with structured data
  - Google Drive storage for processed files and JSON exports
  - Public sharing links for easy access
- **Local Fallback**: Excel and JSON file generation when Google services are unavailable
- **Dual Processing Mode**: Seamless switching between cloud and local processing

### 🔧 Document Processing Pipeline
1. **Document Upload**: Support for both compressed photos and high-quality file uploads
2. **AI Analysis**: Intelligent extraction of:
   - Document type and number
   - Supplier and customer information
   - Itemized product/service details
   - Quantities, units, prices, and totals
   - Document dates and metadata
3. **Data Validation**: Pydantic v2 models ensure data integrity
4. **Export Generation**: Automated creation of structured reports

### 🛡️ Robust Error Handling
- **Graceful Degradation**: Automatic fallback to local processing
- **Comprehensive Logging**: Detailed operation tracking
- **User-Friendly Feedback**: Clear error messages and processing status

## Technology Stack

- **Framework**: aiogram 3.x (Telegram Bot API)
- **AI/ML**: Google Gemini API
- **Data Validation**: Pydantic v2
- **File Processing**: openpyxl, python-docx
- **Cloud Services**: Google Drive API, Google Sheets API
- **Workflow Automation**: N8N integration
- **Configuration**: Environment-based settings with validation

## Installation

### Prerequisites
- Python 3.12+
- Telegram Bot Token
- Google Cloud Project with enabled APIs:
  - Google Drive API
  - Google Sheets API
- Google Gemini API Key (optional)
- N8N instance (optional)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd building-smeta-bot
2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    # or using poetry
    poetry install
    ```
3. **Configure environment**
    ```bash
    cp example.env .env
    # Edit .env with your configuration
    ```
4. **Set up Google credentials**
    ```
    Download service account JSON from Google Cloud Console
    Place it in the project directory
    Update GOOGLE_CREDENTIALS_PATH in .env
    ```
5. **Run the bot**
    ```bash
    python src/bot.py
    ```
   
### Processing Modes
The bot automatically detects available services and adjusts processing accordingly:
- **Full Cloud Mode:** Google services + AI analysis
- **Hybrid Mode:** AI analysis + local file generation
- **Local Mode:** Basic processing with local file output

## Usage
### Basic Workflow
1. **Start the bot:** Send /start command
2. **To be continued** 

### Supported Document Types
- **Construction invoices**
- **Material receipts**
- **Service bills**
- **Equipment rental agreements**
- **Supply chain documents**

### Output Formats
- **Google Sheets:** Live spreadsheet with formulas and formatting
- **Excel Files:** Local .xlsx files with structured data
- **JSON:** Machine-readable data export
- **Summary:** Telegram message with key information

## API Integration
### Google Services
- **Drive API:** File storage and sharing
- **Sheets API:** Spreadsheet creation and manipulation
- **Service Account:** Automated access without user intervention

### AI Services
- **Gemini Vision:** Image-based document analysis
- **N8N Workflows:** Custom document processing pipelines
## Development
## Code Style
- **Type Hints:** Full type annotation coverage
- **Pydantic v2:** Modern data validation and serialization
- **Async/Await:** Non-blocking operations throughout
- **Error Handling:** Comprehensive exception management