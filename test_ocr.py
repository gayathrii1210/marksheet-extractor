from PIL import Image
import pytesseract

# Set path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load image
img = Image.open(r"\Users\gayat\Downloads\marks_sheet_2 (1).png")

# Extract text
text = pytesseract.image_to_string(img)

print("Extracted Text:")
print(text)