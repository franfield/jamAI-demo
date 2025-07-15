import logging
import pytesseract
from PIL import Image

logger = logging.getLogger()

def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR.
    
    Args:
        image_path (str): Path to the local image file
        
    Returns:
        str: Extracted text from the image
    """
    try:
        logger.info(f"Extracting text from image: {image_path}")
        
        # Check if image_path is a tuple and extract the actual path
        if isinstance(image_path, tuple):
            # Extract the first element if it's a tuple
            image_path = image_path[0]
            logger.info(f"Converted tuple to string path: {image_path}")
        
        # Open the image using PIL
        image = Image.open(image_path)
        
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image)
        
        logger.info(f"Successfully extracted {len(text)} characters from image")
        return text
        
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise 