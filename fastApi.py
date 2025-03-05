import requests

url = "http://127.0.0.1:8000/extract"

# Open the image file in binary mode
with open("swa.jpg", "rb") as img:
    files = {"file": img}
    response = requests.post(url, files=files)

print(response.json())  # Should return extracted Aadhaar details