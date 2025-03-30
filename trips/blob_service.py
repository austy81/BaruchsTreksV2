import os
import logging
from azure.storage.blob import BlobServiceClient, ContentSettings
from datetime import datetime

logger = logging.getLogger(__name__)

class AzureBlobService:
    """Service for interacting with Azure Blob Storage"""
    
    def __init__(self, connection_string=None, container_name="photos"):
        self.connection_string = connection_string or os.environ.get("BARUCHSTREKS_STORAGE_CONNECTION")
        self.container_name = container_name
        logger.info(f"AzureBlobService initialized with container: {container_name}")
        
        # Log partial connection string for debugging (hide the key)
        if self.connection_string:
            parts = self.connection_string.split(';')
            safe_conn = ';'.join([p for p in parts if not p.startswith('AccountKey=')])
            logger.info(f"Connection string provided: {safe_conn}...")
        else:
            logger.warning("No connection string provided!")
    
    def get_blob_service_client(self):
        """Get a blob service client for Azure Blob Storage"""
        if not self.connection_string:
            logger.warning("No connection string available")
            return None
        
        try:
            return BlobServiceClient.from_connection_string(self.connection_string)
        except Exception as e:
            logger.error(f"Error creating blob service client: {str(e)}", exc_info=True)
            return None
    
    def get_container_client(self):
        """Get a container client for the photos container"""
        blob_service_client = self.get_blob_service_client()
        if not blob_service_client:
            return None
        
        try:
            return blob_service_client.get_container_client(self.container_name)
        except Exception as e:
            logger.error(f"Error getting container client: {str(e)}", exc_info=True)
            return None
    
    def upload_photo(self, trip_id, photo_file, filename=None):
        """Upload a photo to Azure Blob Storage
        
        Args:
            trip_id (str): The trip's row key
            photo_file (file): The photo file object
            filename (str, optional): Custom filename. If None, original filename is used.
            
        Returns:
            tuple: (success, url or error message)
        """
        if not self.connection_string:
            logger.warning("No connection string available, cannot upload photo")
            return False, "No connection string available"
        
        if not photo_file:
            logger.warning("No photo file provided")
            return False, "No photo file provided"
        
        try:
            # Create a unique blob name
            original_filename = filename or photo_file.name
            # Get file extension
            _, file_extension = os.path.splitext(original_filename)
            # Create timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            # Create blob name with folder structure
            blob_name = f"{trip_id}/{timestamp}{file_extension}"
            
            # Get container client
            container_client = self.get_container_client()
            if not container_client:
                return False, "Could not connect to blob container"
            
            # Create blob client
            blob_client = container_client.get_blob_client(blob_name)
            
            # Set content settings based on file type
            content_settings = ContentSettings(
                content_type=self._get_content_type(file_extension)
            )
            
            # Upload the file
            photo_file.seek(0)  # Ensure we're at the start of the file
            blob_client.upload_blob(photo_file, content_settings=content_settings, overwrite=True)
            
            # Get the URL of the uploaded blob
            blob_url = blob_client.url
            
            logger.info(f"Successfully uploaded photo to {blob_name}")
            return True, blob_url
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error uploading photo: {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return False, error_msg
    
    def list_photos(self, trip_id):
        """List all photos for a specific trip
        
        Args:
            trip_id (str): The trip's row key
            
        Returns:
            list: List of photo URLs
        """
        if not self.connection_string:
            logger.warning("No connection string available, cannot list photos")
            return []
        
        try:
            # Get container client
            container_client = self.get_container_client()
            if not container_client:
                return []
            
            # List blobs with the trip_id prefix
            blobs = container_client.list_blobs(name_starts_with=f"{trip_id}/")
            
            # Get URLs for all blobs
            photo_urls = []
            for blob in blobs:
                blob_client = container_client.get_blob_client(blob.name)
                photo_urls.append(blob_client.url)
            
            logger.info(f"Found {len(photo_urls)} photos for trip {trip_id}")
            return photo_urls
            
        except Exception as e:
            logger.error(f"Error listing photos: {str(e)}", exc_info=True)
            return []
    
    def delete_photo(self, blob_url):
        """Delete a photo from Azure Blob Storage
        
        Args:
            blob_url (str): The full URL of the blob to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connection_string:
            logger.warning("No connection string available, cannot delete photo")
            return False
        
        try:
            # Extract blob name from URL
            blob_service_client = self.get_blob_service_client()
            if not blob_service_client:
                return False
            
            # Get the account name from the connection string
            account_name = None
            for part in self.connection_string.split(';'):
                if part.startswith('AccountName='):
                    account_name = part.split('=')[1]
                    break
            
            if not account_name:
                logger.error("Could not extract account name from connection string")
                return False
            
            # Extract blob name from URL
            # URL format: https://{account}.blob.core.windows.net/{container}/{blob_name}
            url_parts = blob_url.split(f"{account_name}.blob.core.windows.net/{self.container_name}/")
            if len(url_parts) != 2:
                logger.error(f"Could not extract blob name from URL: {blob_url}")
                return False
            
            blob_name = url_parts[1]
            
            # Get container client
            container_client = self.get_container_client()
            if not container_client:
                return False
            
            # Delete the blob
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
            
            logger.info(f"Successfully deleted photo: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting photo: {str(e)}", exc_info=True)
            return False
    
    def _get_content_type(self, file_extension):
        """Get the content type based on file extension"""
        extension = file_extension.lower()
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.heic': 'image/heic',
        }
        return content_types.get(extension, 'application/octet-stream')
