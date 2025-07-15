import os
import logging
import boto3
import tempfile
from botocore.exceptions import ClientError

logger = logging.getLogger()

def download_from_s3(bucket, key, local_dir=None):
    """
    Download a file from S3 to a local directory.
    
    Args:
        bucket (str): S3 bucket name
        key (str): S3 object key
        local_dir (str, optional): Local directory to save the file. If None, 
                                  a temporary directory will be created.
        
    Returns:
        str: Path to the downloaded file
        str or None: Path to the temporary directory if created, None otherwise
    """
    temp_dir = None
    try:
        logger.info(f"Downloading s3://{bucket}/{key}")
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Generate local file path
        filename = os.path.basename(key)
        
        # Create temporary directory if local_dir is not provided
        if local_dir is None:
            temp_dir = tempfile.TemporaryDirectory()
            local_dir = temp_dir.name
            logger.info(f"Created temporary directory: {local_dir}")
        
        local_path = os.path.join(local_dir, filename)
        
        # Download the file
        s3_client.download_file(bucket, key, local_path)
        
        logger.info(f"Successfully downloaded to {local_path}")
        return local_path, temp_dir
        
    except ClientError as e:
        # Clean up temp directory if there was an error
        if temp_dir:
            temp_dir.cleanup()
        logger.error(f"Error downloading from S3: {str(e)}")
        raise

def delete_local_file(file_path):
    """
    Utility function to delete a local file.
    
    Args:
        file_path (str): Path to the file to be deleted
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Successfully deleted local file: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting local file {file_path}: {str(e)}")
        return False 

def generate_s3_presigned_url(bucket, key, expiration=3600):
    """
    Generate a presigned URL for accessing an S3 object using HTTP GET.
    
    Args:
        bucket (str): S3 bucket name
        key (str): S3 object key
        expiration (int, optional): Time in seconds for the presigned URL to remain valid.
                                   Default is 3600 (1 hour).
        
    Returns:
        str or None: Presigned URL as a string if successful, None otherwise
    """
    try:
        logger.info(f"Generating presigned URL for s3://{bucket}/{key}")
        
        # Create S3 client
        s3_client = boto3.client('s3')
        
        # Generate the presigned URL for GET method
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        
        logger.info(f"Successfully generated presigned URL (expires in {expiration} seconds)")
        return presigned_url
        
    except ClientError as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return None 