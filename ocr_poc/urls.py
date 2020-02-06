"""ocr_poc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static
from ocr_main import views

# from django.views.generic.base import TemplateView  # 新增

router = DefaultRouter()

router.register(r'image', views.ImageViewSet)
router.register(r'amazon_link', views.AmazonLinkViewSet)
router.register(r'choice', views.ChoiceViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('choice/', views.choice),
    path('img/<int:num>/', views.main_list),
    path('main/', views.multi_file, name='main'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('accounts/', include('django.contrib.auth.urls')),  # 新增
    path('accounts/', include('allauth.urls')),

    # path('home/', TemplateView.as_view(template_name='home.html'), name='home'),  # 新增
    path('home/', views.HomePage.as_view(), name='home'),
    path('', views.HomePage.as_view()),
    # path(r'', views.HomePage.as_view(), name='home'),
    path('register/', views.register, name='register'),

]

# django2 為 path
# path('img/<int:num>/', views.main_list),

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
