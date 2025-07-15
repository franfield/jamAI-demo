import os
import logging
from PIL import Image

logger = logging.getLogger()

def validate_image(image_path):
    """
    Validate if a file is a valid image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        bool: True if valid image, False otherwise
    """
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        return False

def get_image_info(image_path):
    """
    Get information about an image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Image information including format, size, mode
    """
    try:
        with Image.open(image_path) as img:
            return {
                'format': img.format,
                'size': img.size,
                'mode': img.mode,
                'filename': os.path.basename(image_path)
            }
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        raise 