# Aadhaar OCR Extraction API

## Overview

This project is a FastAPI-based service for extracting Aadhaar card details (Name, DOB, Gender, Aadhaar Number, and Mobile Number) from an image using PaddleOCR.

## Features

- **OCR-based text extraction** using PaddleOCR
- **Preprocessing of images** for better OCR accuracy
- **FastAPI server** for easy API integration
- **Structured extraction** of Aadhaar card details

## Installation

### Step 1: Install Dependencies

Run the following command to install the necessary dependencies:

```sh
pip install paddleocr paddlepaddle opencv-python fastapi uvicorn python-multipart nest_asyncio requests
```

### Step 2: Run the API Server

Create a Python file (e.g., `app.py`) and paste the provided code. Then, run the script:

```sh
python app.py
```

## API Usage

### **Endpoint:**

```
POST /extract
```

### **Request:**

- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Body:** Upload an Aadhaar card image as `file`

### **Example cURL Request:**

```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/extract' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@aadhaar.jpg'
```

### **Response Example:**

```json
{
  "Raw Text": "Swapnil Omprakash Doddi 29/11/2005 MALE 767535140060",
  "Applicant Details": {
    "Name": "Swapnil Omprakash Doddi",
    "DOB": "29/11/2005",
    "Gender": "Male",
    "Aadhaar Number": "767535140060"
  }
}
```

## Notes

- The model processes only Aadhaar card images.
- Ensure the image is **clear and well-lit** for better OCR accuracy.
- You may need to adjust **regex patterns** in `extract_info()` for different Aadhaar formats.

## License

This project is licensed under the MIT License.

