# CS24 PDF File Classification System

Backend service for validating, classifying, optimizing, and storing academic exam PDFs. The system accepts user-supplied exam metadata, extracts text from the uploaded PDF, verifies that the document matches the metadata, and stores the optimized file in structured cloud storage.

The project is built with FastAPI and uses a layered validation strategy:
- First, try deterministic validation with local text extraction and heuristic matching.
- If that is not enough, fall back to AI-assisted metadata extraction with Gemini.
- Before storage, optimize the PDF with linearization for better delivery and handling.

Default storage is **Cloudflare R2**. An alternative **Google Drive** storage backend is also implemented.

## What It Solves

This project was designed to reduce manual exam-file classification and upload work.

Instead of relying on a person to:
- open each PDF,
- verify whether it is really an exam,
- check that the metadata is correct,
- rename or organize the file manually,
- and upload it to the correct location,

the backend automates that workflow with a validation pipeline and metadata-based storage path generation.

## Core Features

- PDF validation at upload time
  - Rejects non-PDF files by MIME type and `%PDF` magic bytes check
- Text extraction pipeline
  - Local extraction with `PyMuPDF`
  - OCR fallback with `Google Cloud Vision` for scanned PDFs
- Metadata validation
  - Local exam-context detection and field matching
  - AI fallback with `Gemini` when local validation is insufficient
- PDF optimization
  - Linearizes PDFs with `pikepdf` before upload
- Cloud storage backends
  - Default: `Cloudflare R2`
  - Alternative: `Google Drive`
- Structured file organization
  - Builds storage paths from `institution`, `degree`, `course_name`, `semester`, `year`, and `term`

## Request Flow

The runtime flow is:

1. Client uploads `multipart/form-data` with metadata and a PDF.
2. FastAPI validates the file type and checks the PDF signature.
3. The PDF processor extracts text locally with `PyMuPDF`.
4. If local extraction returns too little text, the system falls back to `Google Cloud Vision OCR`.
5. Extracted text is normalized and cleaned.
6. The validator first attempts local heuristic validation.
7. If local validation fails, Gemini extracts metadata from the text and compares it against user input.
8. If validation succeeds, the PDF is linearized and uploaded to cloud storage.
9. The API returns the final metadata and whether the decision came from `local` or `ai` validation.

## Tech Stack

- API framework: `FastAPI`
- App server: `Uvicorn`
- PDF parsing: `PyMuPDF`
- PDF optimization: `pikepdf`
- OCR: `Google Cloud Vision`
- AI extraction: `Google Gemini`
- Object storage: `Cloudflare R2` via `boto3`
- Alternative storage: `Google Drive API`
- Testing: `pytest`, `unittest.mock`

## Project Structure

```text
cs24-backend/
├── app/
│   ├── core/
│   │   └── logger.py
│   ├── services/
│   │   ├── pdf_processor/
│   │   │   ├── local_extractor.py
│   │   │   ├── cloud_extractor.py
│   │   │   ├── linearization.py
│   │   │   ├── interface.py
│   │   │   └── manager.py
│   │   ├── validator/
│   │   │   ├── local_validator.py
│   │   │   ├── gemini_extractor.py
│   │   │   ├── ai_validator.py
│   │   │   ├── interface.py
│   │   │   └── manager.py
│   │   ├── storage/
│   │   │   ├── cloudflare_r2.py
│   │   │   ├── google_drive.py
│   │   │   └── interface.py
│   │   └── workflow_service.py
│   ├── dependencies.py
│   └── main.py
├── tests/
│   ├── test_local_extractor.py
│   └── test_cloud_extractor.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Prerequisites

- Python `3.8+`
- A virtual environment is recommended

Required for the default flow:
- `GOOGLE_APPLICATION_CREDENTIALS`
  - path to a Google Cloud Vision service account JSON file
- `GOOGLE_API_KEY`
  - used for Gemini metadata extraction fallback
- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY`
- `R2_SECRET_KEY`
- `R2_BUCKET_NAME`

Optional for the alternative Google Drive backend:
- `GOOGLE_DRIVE_FOLDER_ID`
- local OAuth credentials and `token.json`

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd cs24-backend
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a local `.env` file in the project root:

```env
# Google Cloud Vision OCR
GOOGLE_APPLICATION_CREDENTIALS=/path/to/vision-credentials.json

# Gemini
GOOGLE_API_KEY=your_gemini_api_key

# Cloudflare R2
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY=your_access_key
R2_SECRET_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name

# Optional: Google Drive backend
GOOGLE_DRIVE_FOLDER_ID=your_root_folder_id_here
```

## Running the Server

Start the application with:

```bash
uvicorn app.main:app --reload
```

Server URL:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## API

### Endpoint

`POST /upload-file`

### Form Fields

- `institution`
- `course_name`
- `semester`
- `year`
- `term`
- `degree`
- `pdf_file` (`application/pdf`)

### Example Request

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

### Success Response Example

```json
{
  "status": "success",
  "message": "File processed and uploaded successfully",
  "drive_link": "HIT/מדעי המחשב/אלגוריתמים 2/מבחנים/מועד ב סמסטר חורף 2025.pdf",
  "final_metadata": {
    "institution": "HIT",
    "course_name": "אלגוריתמים 2",
    "semester": "חורף",
    "year": "2025",
    "term": "ב",
    "degree": "מדעי המחשב"
  },
  "source": "local"
}
```

Note: when using the default Cloudflare R2 backend, `drive_link` is the uploaded object key, not a public URL.

### Validation Failure Response Example

```json
{
  "status": "failed",
  "message": "Validation failed. Manual review required.",
  "ai_suggestion": {
    "institution": "HIT",
    "course_name": "אלגוריתמים 2",
    "semester": "חורף",
    "year": "2025",
    "term": "ב",
    "degree": "מדעי המחשב"
  }
}
```

## Validation Strategy

### Local Validation

The local validator checks:
- whether the extracted text appears to be exam-related,
- whether expected metadata values appear in the document,
- and whether enough fields match to trust the result.

### AI Validation

If local validation fails:
- Gemini extracts metadata from the PDF text,
- the extracted values are compared against the user input,
- and the API accepts the file if enough fields align.

This gives the system a balance of speed and determinism for straightforward documents, while still handling noisier or scanned PDFs.

## Storage Behavior

### Cloudflare R2

The default storage backend uploads the optimized PDF to an R2 bucket using an S3-compatible client.

Generated path pattern:

```text
{institution}/{degree}/{course_name}/מבחנים/מועד {term} סמסטר {semester} {year}.pdf
```

### Google Drive

An alternative storage backend is implemented for Google Drive. It:
- creates folder levels dynamically,
- organizes files by metadata,
- and skips upload if the target filename already exists.

## Tests

Run the unit tests with:

```bash
pytest
```

Current tests focus on:
- local PDF text extraction behavior,
- OCR extractor behavior,
- and failure handling in those components.

## Limitations

- Text extraction currently reads only the first page of the PDF.
- OCR fallback also processes the first page only.
- Validation is designed around exam-style Hebrew academic documents and metadata conventions.
- End-to-end integration tests for the full upload pipeline are not included yet.

## Future Improvements

- Add full integration tests for the upload endpoint and storage backends
- Support multi-page extraction and OCR
- Add stronger metadata normalization and fuzzy matching
- Return a more precise storage field name than `drive_link` when using R2
- Make the active storage backend configurable via environment variables

## Contributing

Contributions are welcome through pull requests and issue reports.
