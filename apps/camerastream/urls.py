from django.contrib import admin  
from django.urls import path  
from .views import *  

urlpatterns = [  
    path('camers/', camerslist, name='camers'), 
    path('camers/add_camers', addnew_camera, name='addnewcamera'),    
    path('stream/camera/<int:id>', index, name='index'),
    path('httpstream/camera/<int:id>', livecam_feed, name='stream'),
    path('stream/result/', recognition, name='recognition'),
    path('train/', train, name='train')
] 
