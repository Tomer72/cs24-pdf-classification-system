# CS24 PDF File Classification System

A robust backend service designed to automate the processing, validation, and organization of academic PDF files (specifically exams) into Google Drive.

## 🚀 Features

- **Smart PDF Processing**:
  - Validates file integrity (Magic bytes check).
  - Extracts text using a hybrid approach:
    - **Fast Local Extraction**: Uses `PyMuPDF` for high-quality PDFs.
    - **Cloud Fallback**: Automatically switches to **Google Cloud Vision OCR** for scanned or low-quality documents.

- **Intelligent Validation**:
  - **Local Validation**: Uses regex patterns to verify exam metadata (Course, Semester, Year).
  - **AI Validation**: Leverages LLMs to correct and validate metadata when local methods fail.

- **Automated Organization**:
  - Seamlessly integrates with **Google Drive**.
  - Automatically creates a folder hierarchy: `Degree -> Course -> Exams`.
  - Renames files to a standard format: `Date - Semester - Term.pdf`.
  - Prevents duplicate uploads.

## 🛠️ Prerequisites

- **Python 3.8+**
- **Google Cloud Project** with:
  - Drive API enabled.
  - Vision API enabled.
- `credentials.json` (OAuth 2.0 Client ID) from Google Cloud Console.

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd cs24-backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Setup:**
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_DRIVE_FOLDER_ID=your_root_folder_id_here
    # Add other necessary env vars if applicable (e.g., OPENAI_API_KEY if used for AI validation)
    ```

5.  **Google Auth Setup:**
    Place your `credentials.json` file in the root directory. Then run the token generation script to authenticate:
    ```bash
    python generate_token.py
    ```
    Follow the browser prompts to authorize the application. This will generate a `token.json` file.

## 🚀 Usage

1.  **Start the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The server will start at `http://127.0.0.1:8000`.

2.  **API Documentation:**
    Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

3.  **Upload a File:**
    Send a `POST` request to `/upload-file` with the following form data:
    - `course_name`: (string)
    - `semester`: (string)
    - `year`: (string)
    - `term`: (string)
    - `degree`: (string)
    - `pdf_file`: (file)

## 📂 Project Structure

```
cs24-backend/
├── app/
│   ├── core/           # Core configurations (Logger, etc.)
│   ├── services/       # Business logic
│   │   ├── pdf_processor/  # Text extraction (Local + OCR)
│   │   ├── validator/      # Metadata validation (Regex + AI)
│   │   └── storage/        # Google Drive integration
│   └── main.py         # FastAPI entry point
├── generate_token.py   # Google Auth script
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
