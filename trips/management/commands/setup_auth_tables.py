from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ensures authentication tables are properly created'

    def handle(self, *args, **options):
        self.stdout.write('Checking authentication tables...')
        
        # Check if auth_user table exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';")
            table_exists = cursor.fetchone()
        
        if not table_exists:
            self.stdout.write(self.style.WARNING('auth_user table not found. Creating authentication tables...'))
            
            try:
                # Apply auth migrations specifically
                call_command('migrate', 'auth', verbosity=1)
                call_command('migrate', 'admin', verbosity=1)
                call_command('migrate', 'contenttypes', verbosity=1)
                call_command('migrate', 'sessions', verbosity=1)
                
                self.stdout.write(self.style.SUCCESS('Authentication tables created successfully!'))
                
                # Check if we need to create a superuser
                with connection.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM auth_user;")
                    user_count = cursor.fetchone()[0]
                
                if user_count == 0:
                    self.stdout.write(self.style.WARNING('No users found. Please create a superuser.'))
                    call_command('createsuperuser', interactive=True)
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating authentication tables: {str(e)}'))
                logger.error(f'Error creating authentication tables: {str(e)}', exc_info=True)
                raise
        else:
            self.stdout.write(self.style.SUCCESS('Authentication tables already exist.'))
