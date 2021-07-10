from rest_framework import routers
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from campaign.views import CampaignViewsets, CampaignFilesViewSet, addCampaign, getAllCampaign


router = routers.DefaultRouter()
router.register('campaignList', CampaignFilesViewSet)
router.register('campaignFiles', CampaignViewsets)

urlpatterns = [ 
    path('', include(router.urls)),
    path('addCampaign/', addCampaign, name="addCampaign"),
    path('campaigns/', getAllCampaign, name="getAllCampaign"),
    
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)