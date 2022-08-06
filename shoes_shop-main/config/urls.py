"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.admin import user_control
from shop.admin import shop_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user_control/', user_control.urls),
    path('shop_admin/', shop_admin.urls),
    path('', include('shop.urls')),
]

handler404 = 'shop.views.error_404'
handler500 = 'shop.views.error_500'
handler403 = 'shop.views.error_403'
handler400 = 'shop.views.error_400'

if settings.DEBUG:
    urlpatterns +=  static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns +=  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
