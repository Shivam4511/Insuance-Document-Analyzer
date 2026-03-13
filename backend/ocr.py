import fitz
import pytesseract
from PIL import Image
import re
import io
import numpy as np
import cv2

#  ------- PDF Handling ---------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Docstring for extract_text_from_pdf
    
    :param file_bytes: Description
    :type file_bytes: bytes
    :return: Description
    :rtype: str
    """
    """ extract text from pdf using pymupdf 
    if that doesnot work then it has a fallback ocr model """    

    """if the native text doesnot exist then convert to image and read by ocr."""

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
    
    :param image: Description
    :type image: Image.Image
    :return: Description
    :rtype: str
    extract text from image using pytesseract with preprocessing for table awareness
    """

    img=np.array(image)

    processed_img=preprocess_image(img)

    #  we are assuming a block with some tables

    custom_config=r'--oem 3 --psm 6'

    text=pytesseract.image_to_string(processed_img, config=custom_config)

    return clean_text(text)


#  ---------  Preprocesing(with table awareness) --------

def preprocess_image(img: np.ndarray) -> np.ndarray:

    """
    Docstring for preprocess_image
    
    :param img: Description
    :type img: np.ndarray
    :return: Description
    :rtype: ndarray

    preprocessing images with table awareness

    """

    # convert to grayscale (handle both color and grayscale images)
    if len(img.shape) == 3:
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Denoising
    gray=cv2.medianBlur(gray, 3)

    # Adaptive Thresholding (better for grid layouts)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        15, 3
    )

    kernel = np.ones((2,2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    return thresh

#  --------- Text Cleaning ---------

def clean_text(text: str) -> str:
    """
    Docstring for clean_text
    
    :param text: Description
    :type text: str
    :return: Description
    :rtype: str

    clean OCR output text while we are preserving the structure of the tables.
    """

    # Replace weird Characters
    text=re.sub(r"[^\x00-\x7F]+"," ",text)

    # Fix Broken Lines
    text=re.sub("\n", " ", text)

    # Normalizing spacing

    text=re.sub(r"\s+"," ",text)


    text=text.strip()

    return text


# --------- Main Extraction Function ---------

def extract_text(file_bytes:bytes, file_name: str) -> str:
    """
    Docstring for extract_text
    
    :param file_bytes: Description
    :type file_bytes: bytes
    :param file_name: Description
    :type file_name: str
    :return: Description
    :rtype: str
    extract text from file based on file type
    """

    if file_name.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    
    else:
        image=Image.open(io.BytesIO(file_bytes))
        return extract_text_from_image(image)
     


    

