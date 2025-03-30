from azure.data.tables import TableServiceClient, TableClient
import os
import json
import logging
from datetime import datetime, date

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureTableService:
    def __init__(self, connection_string=None, table_name="Trips"):
        # Try to get connection string from parameter, then environment, then settings
        if connection_string:
            self.connection_string = connection_string
        else:
            # Try to get from environment directly
            env_conn = os.environ.get("BARUCHSTREKS_STORAGE_CONNECTION")
            if env_conn:
                self.connection_string = env_conn
            else:
                # No connection string available
                self.connection_string = None
                logger.error("No Azure Storage connection string available. Please set BARUCHSTREKS_STORAGE_CONNECTION environment variable.")
                
        self.table_name = table_name
        logger.info(f"AzureTableService initialized with table: {table_name}")
        
        # Log partial connection string for debugging (hide the key)
        if self.connection_string:
            parts = self.connection_string.split(';')
            safe_conn = ';'.join([p for p in parts if not p.startswith('AccountKey=')])
            logger.info(f"Connection string provided: {safe_conn}...")
        else:
            logger.warning("No connection string provided! Trip data will not be available.")
        
    def get_table_client(self):
        """Get a table client for the Trips table"""
        logger.info("Getting table client...")
        try:
            table_service_client = TableServiceClient.from_connection_string(self.connection_string)
            table_client = table_service_client.get_table_client(table_name=self.table_name)
            logger.info("Table client created successfully")
            return table_client
        except Exception as e:
            logger.error(f"Error creating table client: {str(e)}")
            raise
    
    def get_all_trips(self):
        """Get all trips from the Azure Table"""
        logger.info("Fetching all trips from Azure Table...")
        
        if not self.connection_string:
            logger.warning("No connection string available, returning empty list")
            return []
            
        try:
            table_client = self.get_table_client()
            logger.info(f"Querying entities with filter: PartitionKey eq 'Trips'")
            entities = list(table_client.query_entities(query_filter="PartitionKey eq 'Trips'"))
            logger.info(f"Retrieved {len(entities)} entities from Azure Table")
            
            # Transform the entities to match the expected format in the templates
            trips = []
            for entity in entities:
                # Skip entries without a RowKey
                if not entity.get('RowKey'):
                    logger.warning(f"Skipping entity without RowKey: {entity}")
                    continue
                
                # Map Azure Table entity to the expected format
                trip = {
                    'row_key': entity.get('RowKey'),
                    'title': entity.get('Title', 'Untitled Trip'),
                    'description': entity.get('Description', ''),
                    'trip_completed_on': entity.get('TripCompletedOn', ''),
                    'length_hours': entity.get('LengthHours', 0),
                    'location': entity.get('Location', ''),
                    'elevation_gain': entity.get('ElevationGain', 0),
                    'difficulty': entity.get('Difficulty', ''),
                    'map_url': entity.get('MapUrl', ''),
                    'image_url': entity.get('ImageUrl', ''),
                    'timestamp': entity.get('Timestamp', ''),  # Include Timestamp for sorting
                    # Add any other fields needed by your templates
                }
                
                # Debug: Log each trip's key data
                logger.info(f"Trip: {trip['row_key']} - {trip['title']} - Completed: {trip['trip_completed_on']}")
                
                trips.append(trip)
            
            # Try sorting by timestamp first (most reliable)
            try:
                trips = sorted(trips, key=lambda x: x.get('timestamp', ''), reverse=True)
                logger.info(f"Sorted {len(trips)} trips by timestamp (newest first)")
            except Exception as sort_error:
                logger.error(f"Error sorting by timestamp: {str(sort_error)}")
                # Fallback to trip_completed_on
                try:
                    trips = sorted(trips, key=lambda x: x.get('trip_completed_on', ''), reverse=True)
                    logger.info(f"Sorted {len(trips)} trips by trip_completed_on (newest first)")
                except Exception as sort_error2:
                    logger.error(f"Error sorting by trip_completed_on: {str(sort_error2)}")
                    # No sorting as last resort
            
            return trips
            
        except Exception as e:
            logger.error(f"Error fetching trips from Azure: {str(e)}", exc_info=True)
            return []
    
    def get_trip_by_id(self, row_key):
        """Get a specific trip by its row key"""
        logger.info(f"Fetching trip with row_key: {row_key}")
        
        if not self.connection_string:
            logger.warning("No connection string available, returning None")
            return None
            
        try:
            table_client = self.get_table_client()
            entity = table_client.get_entity(partition_key="Trips", row_key=row_key)
            logger.info(f"Successfully retrieved trip: {entity.get('Title', 'Unknown')}")
            
            # Log all keys in the entity to help debug
            logger.info(f"Entity keys: {list(entity.keys())}")
            
            # Transform the entity to match the expected format in the templates
            trip = {
                'row_key': entity.get('RowKey'),
                'title': entity.get('Title', 'Untitled Trip'),
                'description': entity.get('Description', ''),
                'trip_completed_on': entity.get('TripCompletedOn', ''),
                'length_hours': entity.get('LengthHours', 0),
                'location': entity.get('Location', ''),
                'elevation_gain': entity.get('ElevationGain', 0),
                'difficulty': entity.get('Difficulty', ''),
                'map_url': entity.get('MapUrl', ''),
                'image_url': entity.get('ImageUrl', ''),
                'timestamp': entity.get('Timestamp', ''),
                'participants': entity.get('Participants', ''),
                'meters_ascend': entity.get('MetersAscend', 0),
                'meters_descend': entity.get('MetersDescend', 0),
                
                # Check for different case variations of the grade fields
                'uiaa_grade': entity.get('UiaaGrade') or 'none',
                'alpine_grade': entity.get('AlpineGrade') or 'none',
                'trip_class': entity.get('TripClass') or 'none',
                'ferata_grade': entity.get('FerataGrade') or 'none',
                
                'parking_json': entity.get('ParkingJson', ''),
                'high_point_json': entity.get('HighPointJson', ''),
            }
            
            # Debug: Log the transformed trip data
            logger.info(f"Grade fields in entity: UiaaGrade={entity.get('UiaaGrade')}, AlpineGrade={entity.get('AlpineGrade')}, FerataGrade={entity.get('FerataGrade')}")
            logger.info(f"Transformed trip data: {json.dumps(trip, default=str)}")
            
            return trip
        except Exception as e:
            logger.error(f"Error fetching trip {row_key} from Azure: {str(e)}", exc_info=True)
            return None

    def parse_trip_data(self, trip_entity):
        """Parse the trip data from Azure Table format to a more usable format"""
        trip_data = {}
        
        for key, value in trip_entity.items():
            # Skip metadata fields
            if key.startswith('_') or key.endswith('@type'):
                continue
                
            # Handle date fields
            if isinstance(value, str) and len(value) > 10 and 'T' in value and 'Z' in value:
                try:
                    trip_data[key.lower()] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    continue
                except ValueError:
                    pass
            
            # Parse JSON strings for coordinates
            if key in ['ParkingJson', 'HighPointJson'] and value:
                try:
                    json_value = json.loads(value)
                    trip_data[key.lower()] = value  # Store original string
                    # Also store parsed values if needed
                    if key == 'ParkingJson':
                        trip_data['parking_coords'] = (json_value.get('Latitude'), json_value.get('Longtitude'))
                    elif key == 'HighPointJson':
                        trip_data['high_point_coords'] = (json_value.get('Latitude'), json_value.get('Longtitude'))
                except json.JSONDecodeError:
                    trip_data[key.lower()] = value
            else:
                trip_data[key.lower()] = value
            
        return trip_data
        
    def update_trip(self, row_key, trip_data):
        """Update a trip in the Azure Table"""
        logger.info(f"Updating trip with row_key: {row_key}")
        
        if not self.connection_string:
            logger.warning("No connection string available, cannot update trip")
            return False, "No connection string available"
            
        try:
            table_client = self.get_table_client()
            
            # First, get the existing entity to preserve any fields not in the update
            existing_entity = table_client.get_entity(partition_key="Trips", row_key=row_key)
            
            # Handle date conversion
            trip_completed_on = trip_data.get('trip_completed_on')
            if trip_completed_on and isinstance(trip_completed_on, date):
                # Convert date to ISO format string
                trip_completed_on = trip_completed_on.isoformat()
            
            # Create the entity to update
            entity = {
                'PartitionKey': 'Trips',
                'RowKey': row_key,
                'Title': trip_data.get('title', existing_entity.get('Title')),
                'Description': trip_data.get('description', existing_entity.get('Description')),
                'TripCompletedOn': trip_completed_on if trip_completed_on else existing_entity.get('TripCompletedOn'),
                'LengthHours': trip_data.get('length_hours', existing_entity.get('LengthHours')),
                'Location': trip_data.get('location', existing_entity.get('Location')),
                'ElevationGain': trip_data.get('elevation_gain', existing_entity.get('ElevationGain')),
                'Difficulty': trip_data.get('difficulty', existing_entity.get('Difficulty')),
                'MapUrl': trip_data.get('map_url', existing_entity.get('MapUrl')),
                'ImageUrl': trip_data.get('image_url', existing_entity.get('ImageUrl')),
                'Participants': trip_data.get('participants', existing_entity.get('Participants')),
                'MetersAscend': trip_data.get('meters_ascend', existing_entity.get('MetersAscend')),
                'MetersDescend': trip_data.get('meters_descend', existing_entity.get('MetersDescend')),
                'UiaaGrade': trip_data.get('uiaa_grade', existing_entity.get('UiaaGrade')),
                'AlpineGrade': trip_data.get('alpine_grade', existing_entity.get('AlpineGrade')),
                'TripClass': trip_data.get('trip_class', existing_entity.get('TripClass')),
                'FerataGrade': trip_data.get('ferata_grade', existing_entity.get('FerataGrade')),
            }
            
            # Debug: Print the entity being updated
            print("Entity to update:", entity)
            
            # Handle coordinates if provided
            if 'parking_json' in trip_data and trip_data['parking_json']:
                entity['ParkingJson'] = trip_data['parking_json']
                print(f"Setting ParkingJson: {trip_data['parking_json']}")
            
            if 'high_point_json' in trip_data and trip_data['high_point_json']:
                entity['HighPointJson'] = trip_data['high_point_json']
                print(f"Setting HighPointJson: {trip_data['high_point_json']}")
            
            # Update the entity in Azure Table
            print("Calling update_entity with entity:", entity)
            table_client.update_entity(entity=entity)
            logger.info(f"Successfully updated trip with row_key: {row_key}")
            return True, ""
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error updating trip: {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            print(f"Exception: {error_msg}")
            print(f"Traceback: {traceback.format_exc()}")
            return False, error_msg

    def create_trip(self, trip_data):
        """Create a new trip in Azure Table Storage"""
        logger.info("Creating new trip")
        
        if not self.connection_string:
            logger.warning("No connection string available, cannot create trip")
            return False, "No connection string available", None
        
        try:
            table_client = self.get_table_client()
            
            # Generate a new row key based on timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            row_key = f"trip_{timestamp}"
            
            # Create a new entity with the trip data
            new_entity = {
                'PartitionKey': 'Trips',
                'RowKey': row_key,
                'Title': trip_data.get('title', ''),
                'Description': trip_data.get('description', ''),
                'Location': trip_data.get('location', ''),
                'Difficulty': trip_data.get('difficulty', ''),
                'MapUrl': trip_data.get('map_url', ''),
                'ImageUrl': trip_data.get('image_url', ''),
                'Participants': trip_data.get('participants', ''),
                'MetersAscend': trip_data.get('meters_ascend', None),
                'MetersDescend': trip_data.get('meters_descend', None),
                'UiaaGrade': trip_data.get('uiaa_grade', ''),
                'AlpineGrade': trip_data.get('alpine_grade', ''),
                'TripClass': trip_data.get('trip_class', ''),
                'FerataGrade': trip_data.get('ferata_grade', ''),
                'ParkingJson': trip_data.get('parking_json', ''),
                'HighPointJson': trip_data.get('high_point_json', ''),
                'Timestamp': datetime.now().isoformat(),  # Add current timestamp
            }
            
            # Handle date fields
            if 'trip_completed_on' in trip_data and trip_data['trip_completed_on']:
                if isinstance(trip_data['trip_completed_on'], date):
                    # Convert to string in the format Azure Table Storage expects
                    new_entity['TripCompletedOn'] = trip_data['trip_completed_on'].isoformat()
                else:
                    new_entity['TripCompletedOn'] = trip_data['trip_completed_on']
            
            # Handle numeric fields
            if 'length_hours' in trip_data and trip_data['length_hours'] is not None:
                new_entity['LengthHours'] = float(trip_data['length_hours'])
            
            if 'elevation_gain' in trip_data and trip_data['elevation_gain'] is not None:
                new_entity['ElevationGain'] = int(trip_data['elevation_gain'])
            
            # Create the entity in Azure Table Storage
            table_client.create_entity(new_entity)
            logger.info(f"Successfully created trip with row key: {row_key}")
            return True, None, row_key
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error creating trip: {error_msg}")
            import traceback
            logger.error(traceback.format_exc())
            return False, error_msg, None
