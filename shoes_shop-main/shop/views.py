from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
# Create your views here.
from django.urls import translate_url

class IndexView(TemplateView):
    template_name = 'index.html'

def error_404(request, exception):

        return render(request,'404.html')

def error_500(request,  exception):
        return render(request,'500.html', data)
        
def error_403(request, exception):

        return render(request,'403.html')

def error_400(request,  exception):
        return render(request,'400.html', data)   
