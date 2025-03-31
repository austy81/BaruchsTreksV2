from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

def custom_login(request):
    """
    Custom login view with enhanced error handling and logging
    to diagnose authentication issues.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        # Log authentication attempt
        username = request.POST.get('username', '')
        logger.info(f"Login attempt for user: {username}")
        
        if form.is_valid():
            # Form is valid, extract username and password
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate the user
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Authentication successful
                logger.info(f"Authentication successful for user: {username}")
                login(request, user)
                
                # Redirect to the next page or default page
                next_page = request.POST.get('next', '')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect('trips:index')
            else:
                # Authentication failed despite valid form
                logger.warning(f"Authentication failed for user: {username} (valid form but authenticate returned None)")
                messages.error(request, "Invalid username or password. Please check your credentials.")
        else:
            # Form validation failed
            logger.warning(f"Form validation failed for user: {username}")
            for field, errors in form.errors.items():
                for error in errors:
                    logger.warning(f"Form error in {field}: {error}")
            
            # Check if the user exists but password is wrong
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_exists = User.objects.filter(username=username).exists()
                if user_exists:
                    logger.warning(f"User {username} exists but password is incorrect")
                    messages.error(request, "Password is incorrect. Please try again.")
                else:
                    logger.warning(f"User {username} does not exist")
                    messages.error(request, "Username does not exist. Please check your username.")
            except Exception as e:
                logger.error(f"Error checking user existence: {str(e)}")
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })
