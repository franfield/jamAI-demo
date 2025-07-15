import json
import logging
import os

from app.postprocess import process_text
from app.s3_utils import download_from_s3, delete_local_file
from app.tesseract_engine import extract_text_from_image

logger = logging.getLogger()
logger.setLevel(logging.INFO)
upload_s3_bucket = os.environ.get('UPLOAD_BUCKET_NAME')
resource_s3_bucket = os.environ.get('RESOURCE_BUCKET_NAME')

def lambda_handler(event, context):
    """
    AWS Lambda handler function that processes images from S3 using OCR.
    
    Args:
        event (dict): Lambda event data, expected to contain:
            - bucket: S3 bucket name
            - key: S3 object key (image path)
        context (LambdaContext): Lambda context object
        
    Returns:
        dict: Response containing extracted text and processing results
    """
    local_image_path = None
    try:
        # Check if the body is a JSON string (as it usually is with API Gateway)
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event.get("body", event)  # fallback to event for test console
        # Extract bucket and key from the event
        key = body["key"]
        
        if not key:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required parameters: key'})
            }
        
        logger.info(f"Processing image from s3://{upload_s3_bucket}/{key}")
        
        # Download image from S3
        local_image_path = download_from_s3(upload_s3_bucket, key)
        
        # Extract text using OCR
        extracted_text = extract_text_from_image(local_image_path)

        # Process the extracted text
        processed_result = process_text(extracted_text)
        
        return {
            'statusCode': 200,
            'body': json.dumps(processed_result),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            }
        }
    finally:
        # Clean up the local file regardless of success or failure
        if local_image_path:
            delete_local_file(local_image_path) 