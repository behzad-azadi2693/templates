from ast import Index
from django.urls import path
from .views import IndexView, index

app_name = 'shop'

urlpatterns = [
    path('', IndexView.as_view(), name='index')
]
