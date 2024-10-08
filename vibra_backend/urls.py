"""
URL configuration for vibra_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
# vibra_backend/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from user_messages.views import MessagePage
from login.views import LoginView
from core.views import UserListView
from notifications.views import NotificationView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls')),
    path('for_you/', include('for_you.urls')),
    path('action/', include('action.urls')),
    path('conversations/', include('user_messages.urls')),
    path('users/', UserListView.as_view(), name='user-list'),
    path('login/', LoginView.as_view({'post': 'create', 'get': 'retrieve'}), name='login_view'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
