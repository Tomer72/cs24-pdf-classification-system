# CS24 PDF File Classification System

FastAPI backend that extracts exam metadata from uploaded PDFs, validates it (local heuristic -> Gemini fallback), optimizes the PDF, and stores the optimized file in **Cloudflare R2** by default (Google Drive storage is also implemented as an alternative backend).

## Features
- Smart PDF processing
  - Validates uploaded files as real PDFs (`%PDF` magic bytes check)
  - Local text extraction with `PyMuPDF`
  - Cloud OCR fallback using **Google Cloud Vision**
  - PDF linearization/optimization before upload
- Metadata validation
  - Local exam detection + field matching for `institution`, `course_name`, `semester`, `year`, `term`, `degree`
  - If local validation fails, metadata is extracted with **Gemini** (requires `GOOGLE_API_KEY`) and compared to the user-provided fields
- Storage
  - Default: **Cloudflare R2** (S3-compatible object upload)
  - Alternative: **Google Drive** storage (`GoogleDriveStorage`) with duplicate checks
- Default storage backend is configured in `app/dependencies.py` (currently Cloudflare R2).

## Prerequisites
- Python 3.8+
- Google Cloud Vision OCR
  - A Google service account JSON file for Vision OCR
  - Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of that JSON
- Gemini API
  - Set `GOOGLE_API_KEY`
- Cloudflare R2 storage
  - `R2_ACCOUNT_ID`
  - `R2_ACCESS_KEY`
  - `R2_SECRET_KEY`
  - `R2_BUCKET_NAME`
- (Optional) Google Drive storage backend
  - `GOOGLE_DRIVE_FOLDER_ID`
  - Requires a locally created OAuth auth token (not committed)

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd cs24-backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv <env>
    source <env>/bin/activate  # On Windows: <env>\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Setup:**
    Create a local environment file (not committed) in the repo root:
    ```env
    # Google Cloud Vision OCR (service account json)
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/vision-credentials.json

    # Gemini (used for metadata fallback extraction)
    GOOGLE_API_KEY=your_gemini_api_key

    # Cloudflare R2 (S3-compatible)
    R2_ACCOUNT_ID=your_account_id
    R2_ACCESS_KEY=your_access_key
    R2_SECRET_KEY=your_secret_key
    R2_BUCKET_NAME=your_bucket_name

    # Optional (if switching storage to Google Drive)
    GOOGLE_DRIVE_FOLDER_ID=your_root_folder_id_here
    ```

5.  **Auth files:**
    - **Vision OCR**: ensure `GOOGLE_APPLICATION_CREDENTIALS` points to your Vision service account JSON.
    - **Google Drive (optional)**: configure OAuth client credentials and an auth token locally (not committed)

## 🚀 Usage

1.  **Start the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The server will start at `http://127.0.0.1:8000`.

2.  **API Documentation:**
    Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

3.  **Upload a File:**
    Send a `POST` request to `/upload-file` as `multipart/form-data` with the following form fields:
    - `institution`: (string)
    - `course_name`: (string)
    - `semester`: (string)
    - `year`: (string)
    - `term`: (string)
    - `degree`: (string)
    - `pdf_file`: (file, must be `application/pdf`)

    Example:
    ```bash
    curl -X POST "http://127.0.0.1:8000/upload-file" \
      -F "institution=HIT" \
      -F "course_name=אלגוריתמים 2" \
      -F "semester=חורף" \
      -F "year=2025" \
      -F "term=ב" \
      -F "degree=מדעי המחשב" \
      -F "pdf_file=@./algo2.pdf;type=application/pdf"
    ```

    Response:
    - On success: `status`, `message`, `drive_link` (R2 object key when using the default storage backend), `final_metadata`, `source` (`local` or `ai`)
    - On validation failure: `status=failed` and `ai_suggestion` (Gemini extracted suggestion when available)

## Tests
Run unit tests with `pytest`.

## 📂 Project Structure

```
cs24-backend/
├── app/
│   ├── core/
│   │   └── logger.py
│   ├── services/
│   │   ├── pdf_processor/
│   │   │   ├── local_extractor.py
│   │   │   ├── cloud_extractor.py
│   │   │   ├── linearization.py
│   │   │   └── manager.py
│   │   ├── validator/
│   │   │   ├── local_validator.py
│   │   │   ├── gemini_extractor.py
│   │   │   ├── ai_validator.py
│   │   │   └── manager.py
│   │   ├── storage/
│   │   │   ├── cloudflare_r2.py
│   │   │   └── google_drive.py
│   │   └── workflow_service.py
│   ├── dependencies.py
│   └── main.py
├── requirements.txt
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
