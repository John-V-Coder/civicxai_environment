from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path('', lambda request: HttpResponse("Welcome to Civic XAI Backend")),
    path('admin/', admin.site.urls),
    path('api/', include('explainable_ai.urls')),
]
