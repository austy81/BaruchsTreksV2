"""
Test script to verify Azure Table Storage connection
Run this directly to test the connection outside of Django
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import Azure modules
try:
    from azure.data.tables import TableServiceClient
    logger.info("Successfully imported Azure modules")
except ImportError as e:
    logger.error(f"Failed to import Azure modules: {e}")
    logger.error("Please ensure azure-data-tables is installed: pip install azure-data-tables")
    sys.exit(1)

def test_connection():
    # Get connection string from environment variable
    connection_string = os.environ.get('BARUCHSTREKS_STORAGE_CONNECTION')
    
    if not connection_string:
        logger.error("No connection string found in environment variables")
        return False
    
    try:
        # Log partial connection string (hide the key)
        parts = connection_string.split(';')
        safe_conn = ';'.join([p for p in parts if not p.startswith('AccountKey=')])
        logger.info(f"Testing connection with: {safe_conn}...")
        
        # Create table service client
        logger.info("Creating TableServiceClient...")
        table_service_client = TableServiceClient.from_connection_string(connection_string)
        
        # Get table client
        logger.info("Getting table client for 'Trips'...")
        table_client = table_service_client.get_table_client(table_name="Trips")
        
        # Query for a small number of entities
        logger.info("Querying for trips...")
        query = "PartitionKey eq 'Trips'"
        entities = list(table_client.query_entities(query_filter=query, select=["PartitionKey", "RowKey", "Title"], top=5))
        
        # Log results
        logger.info(f"Successfully retrieved {len(entities)} entities")
        for entity in entities:
            logger.info(f"  - {entity.get('RowKey')}: {entity.get('Title')}")
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to Azure Table Storage: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting Azure Table Storage connection test")
    success = test_connection()
    
    if success:
        logger.info("✅ Connection test successful!")
        sys.exit(0)
    else:
        logger.error("❌ Connection test failed!")
        sys.exit(1)
