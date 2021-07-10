from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .views import CustomUserViewSet, RegisterUserViewSet, login ,FeedbackViewSet, getCardDetail, getCard, activeDonation, donationStatus, getDonation, updateDonation
from users.views import updateCardDetail, UpdateUserProfileViewSet, verifyPhoneView, donationForCampaign, donationForMasjid, donationHistory, stopRecurringDonation, forgetPin, updatePin
from users import views

router = routers.DefaultRouter()
router.register('users', RegisterUserViewSet)
router.register('feedback', FeedbackViewSet)
router.register('updateProfileImage', UpdateUserProfileViewSet)

urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
    path('user/login', login, name="login"),
    path('cardDetail', getCardDetail, name="getCardDetail"),
    path('getCard', getCard, name="getCard"),
    path('updateCardDetail', updateCardDetail, name="updateCardDetail"),
    path('verifyPhoneView', verifyPhoneView, name="verifyPhoneView"),
    path('donationForCampaign', donationForCampaign, name="donationForCampaign"),
    path('donationForMasjid', donationForMasjid, name="donationForMasjid"),
    path('donationHistory', donationHistory, name="donationHistory"),
    path('activeDonation', activeDonation, name="activeDonation"),
    path('donationStatus', donationStatus, name="donationStatus"),
    path('stopRecurringDonation', stopRecurringDonation, name="stopRecurringDonation"),
    path('getDonation', getDonation, name="getDonation"),
    path('updateDonation', updateDonation, name="updateDonation"),
    path('forgetPin', forgetPin, name="forgetPin"),
    path('updatePin', updatePin, name="updatePin"),
    
    
    
    
    path('', include(router.urls)),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)