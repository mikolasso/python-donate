from rest_framework import routers
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from masjid.views import MasjidViewSet, SalahTimeViewSet, getAllMasjid


router = routers.DefaultRouter()
router.register('masjid_list', MasjidViewSet)
router.register('salah_time', SalahTimeViewSet)

urlpatterns = [ 
    path('', include(router.urls)),
    path('getMasjidList', getAllMasjid, name="getAllMasjid"),  
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)