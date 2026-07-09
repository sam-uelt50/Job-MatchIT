# app/core/ocr_processor.py - OCR Processor for Image Text Extraction
import tempfile
import os
import re
import pytesseract
from PIL import Image

class OCRProcessor:
    def __init__(self):
        # Set the correct Tesseract path
        self.tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        if os.path.exists(self.tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
            self.is_available = True
            print(f"✅ Tesseract initialized at: {self.tesseract_path}")
        else:
            self.is_available = False
            print(f"❌ Tesseract not found at: {self.tesseract_path}")
            print("   Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    def extract_text_from_image(self, image_file) -> str:
        """Extract text from image using Tesseract OCR"""
        if not self.is_available:
            raise Exception(
                "Tesseract OCR not installed. "
                "Please install from: https://github.com/UB-Mannheim/tesseract/wiki"
            )
        
        try:
            # Save uploaded image to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                image_file.seek(0)
                content = image_file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            # Open image and extract text
            image = Image.open(tmp_path)
            text = pytesseract.image_to_string(image)
            
            # Clean up
            os.unlink(tmp_path)
            
            if not text or len(text.strip()) < 20:
                raise Exception("Could not extract enough text from image. Please ensure the image is clear and well-lit.")
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
            
        except Exception as e:
            raise Exception(f"OCR Error: {str(e)}")

# Create singleton instance
ocr_processor = OCRProcessor()