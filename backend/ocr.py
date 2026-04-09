import fitz
import pytesseract
from PIL import Image
import re
import io
import numpy as np
import cv2

#  ------- PDF Handling ---------

#  ------- PDF Handling ---------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Docstring for extract_text_from_pdf
    
    :param file_bytes: bytes
    :return: str
    extract text from pdf using pymupdf 
    if that doesnot work then it has a fallback ocr model 
    """    
    doc=fitz.open(stream=file_bytes,filetype="pdf")
    full_text=""

    for page in doc:
        text = page.get_text("text")

        if text.strip():
            full_text += text + "\n"
        else:
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            full_text += extract_text_from_image(img) + "\n"

    # return after processing all pages
    return clean_text(full_text)
    

# -------- Image OCR Handling ---------

def extract_text_from_image(image: Image.Image) -> str:
    """ Docstring for extract_text_from_image
    
    :param image: Image.Image
    :return: str
    extract text from image using pytesseract with preprocessing for table awareness
    """
    img=np.array(image)
    processed_img=preprocess_image(img)

    # Use psm 4 (Assume a single column of text of variable sizes) or 6 (uniform block)
    # psm 6 with preserve_interword_spaces keeps table columns aligned horizontally better than default
    custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
    text=pytesseract.image_to_string(processed_img, config=custom_config)

    return clean_text(text)


#  ---------  Preprocesing(with table awareness) --------

def preprocess_image(img: np.ndarray) -> np.ndarray:
    """
    Docstring for preprocess_image
    
    :param img: np.ndarray
    :return: ndarray
    preprocessing images with table awareness, upscaling for small text
    """
    # convert to grayscale (handle both color and grayscale images)
    if len(img.shape) == 3:
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Upscale the image by 2x. This drastically improves OCR for the small text 
    # commonly found in insurance tables and footnotes.
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # Mild Gaussian blur to remove noise but keep text edges sharp
    # (Median blur with k=3 was destroying small text)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive Thresholding handles varying illumination across scanned pages well
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )

    # We skip morphological closing (MORPH_CLOSE) because it can merge nearby letters 
    # or column data together, garbling the OCR output.
    return thresh


#  --------- Text Cleaning ---------

def clean_text(text: str) -> str:
    """
    Docstring for clean_text
    
    :param text: str
    :return: str
    clean OCR output text while preserving the structure of the tables.
    """
    # Replace weird Characters but keep basic typography and newlines. 
    # Ascii printable characters plus newline/carriage return are mostly safe.
    text = re.sub(r"[^\x20-\x7E\n\r]+", " ", text)

    # Preserve table structure by NOT removing newlines. 
    # Previous implementation (re.sub("\n", " ", text)) destroyed table row isolation.
    # We instead normalize multiple newlines to a single newline if there are huge gaps.
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Normalize excessive horizontal whitespace (but allow multiple spaces for table columns)
    text = re.sub(r" {4,}", "   ", text)

    return text.strip()


# --------- Main Extraction Function ---------

def extract_text(file_bytes:bytes, file_name: str) -> str:
    """
    Docstring for extract_text
    
    :param file_bytes: bytes
    :param file_name: str
    :return: str
    extract text from file based on file type
    """
    if file_name.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    else:
        image=Image.open(io.BytesIO(file_bytes))
        return extract_text_from_image(image)
