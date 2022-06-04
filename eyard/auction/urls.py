"""auction URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path,include
from django.conf import settings
from OAS import views as auctions_views
from django.conf.urls.static import static

from django.conf import settings



admin.site.site_header = "eYard Sale Management System"
admin.site.site_title = "eYard Sale System"
admin.site.index_title = "Admin Panel"


urlpatterns = [
    path('admin/', admin.site.urls),
    path('mybids/', auctions_views.my_bids, name="my_bids"),
    path('auctions/', include('OAS.urls')),
    path('accounts/',include('django.contrib.auth.urls')),
    path('',include('OAS.urls')),
] +static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
