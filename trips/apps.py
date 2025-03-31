from django.apps import AppConfig
import os
import logging

logger = logging.getLogger(__name__)

class TripsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trips'
    
    def ready(self):
        """
        Run code when the Django application is ready.
        This will be executed once during startup.
        """
        # Only run in production environment (not during local development)
        # Check for common environment variables used in production
        is_production = os.environ.get('WEBSITE_HOSTNAME') is not None  # Azure App Service
        
        if is_production:
            try:
                # Import and run the command to setup auth tables
                from django.core.management import call_command
                logger.info("Running setup_auth_tables command in production environment")
                call_command('setup_auth_tables')
            except Exception as e:
                logger.error(f"Error running setup_auth_tables command: {str(e)}", exc_info=True)
