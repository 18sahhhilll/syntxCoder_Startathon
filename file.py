

# Import required libraries
import cv2
import numpy as np
import re
import shutil
import os
import threading
import uvicorn
import nest_asyncio
from paddleocr import PaddleOCR
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Dict

import subprocess
subprocess.run(["fuser", "-k", "8000/tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ocr = PaddleOCR(use_angle_cls=True, lang="en", det_db_box_thresh=0.5, rec_algorithm="SVTR_LCNet")


def preprocess_image(image_path: str):
    """Convert to grayscale, resize, enhance contrast, and apply noise removal."""
    img = cv2.imread(image_path)
    
   
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

 
    height, width = gray.shape
    if width > 1000:  
        gray = cv2.resize(gray, (1000, int(height * (1000 / width))))

 
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

   
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

   
    processed_img = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    return processed_img


def extract_text(image_path: str) -> str:
    """Extract text from an image using PaddleOCR"""
    processed_img = preprocess_image(image_path)

   
    temp_path = "temp_processed.jpg"
    cv2.imwrite(temp_path, processed_img)

    
    result = ocr.ocr(temp_path, cls=True)
    extracted_text = " ".join([word_info[1][0] for line in result for word_info in line])

    return extracted_text.strip()


def extract_info(text: str) -> Dict[str, str]:
    """Extract structured information (Name, DOB, Gender, Aadhaar) from OCR text"""
    info = {}

    #  Remove unwanted words from the extracted text
    text = text.replace("\n", " ").replace("  ", " ")  # Remove extra spaces & newlines
    text = text.replace("GOVERNMENT OF INDIA", "").replace("Government of India", "")
    text = text.replace("Republic of India", "").replace("INDIA", "").strip()

    # Improved Name Extraction (Handles 3-word names like "Rahul Kumar Singh")
    common_wrong_words = ["Government of India", "Unique Identification Authority", "Republic of India"]
    
    name_matches = re.findall(r"([A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)?)", text)
    info["Name"] = next((name for name in name_matches if name not in common_wrong_words), "Not Found")

    # Improved DOB Extraction (Supports "DD/MM/YYYY" and "DD-MM-YYYY")
    dob_match = re.search(r"(\d{2}/\d{2}/\d{4})", text) or re.search(r"(\d{2}-\d{2}-\d{4})", text)
    info["DOB"] = dob_match.group(1) if dob_match else "Not Found"

    # Gender Extraction
    gender_match = re.search(r"\b(Male|Female|Other)\b", text, re.IGNORECASE)
    info["Gender"] = gender_match.group(1).capitalize() if gender_match else "Not Found"

    #  Aadhaar Extraction (Handles different formats)
    aadhaar_match = re.search(r"\b\d{4} ?\d{4} ?\d{4}\b", text)  # Supports "1234 5678 9012" & "123456789012"
    info["Aadhaar_Number"] = aadhaar_match.group(0).replace(" ", "") if aadhaar_match else "Not Found"

    return info

#  Step 6: Build FastAPI Server
app = FastAPI()

@app.post("/extract")
async def extract_personal_info(file: UploadFile = File(...)):
    """API to process Aadhaar card image and extract applicant details"""
    file_location = f"temp_{file.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text using OCR
    extracted_text = extract_text(file_location)

    #  Debugging: Print extracted raw text for verification
    print("\n🔹 Extracted Text from OCR:\n", extracted_text, "\n")

    extracted_info = extract_info(extracted_text)

  
    os.remove(file_location)


    print(f" Applicant Details:\n"
          f"Name: {extracted_info['Name']}\n"
          f"DOB: {extracted_info['DOB']}\n"
          f"Gender: {extracted_info['Gender']}\n"
          f"Aadhaar Number: {extracted_info['Aadhaar_Number']}\n")

    return JSONResponse(content={
        "Raw Text": extracted_text,  # Include raw text in response for debugging
        "Applicant Details": {
            "Name": extracted_info["Name"],
            "DOB": extracted_info["DOB"],
            "Gender": extracted_info["Gender"],
            "Aadhaar Number": extracted_info["Aadhaar_Number"]
        }
    })

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

nest_asyncio.apply()
threading.Thread(target=run_api, daemon=True).start()

print("✅ FastAPI server started successfully at: http://127.0.0.1:8000/extract")