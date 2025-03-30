from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('', views.index, name='index'),
    path('all/', views.all_trips, name='all_trips'),
    path('trip/new/', views.trip_edit, name='trip_create'),
    path('trip/<str:trip_id>/', views.trip_detail, name='trip_detail'),
    path('trip/<str:trip_id>/edit/', views.trip_edit, name='trip_edit'),
    path('debug/', views.debug_azure, name='debug_azure'),
    path('debug-logging/', views.debug_logging, name='debug_logging'),
]
