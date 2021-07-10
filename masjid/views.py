from django.shortcuts import render
from .models import Masjid, SalahTime
from .serializers import MasjidSerializer, SalahTimeSerializer
from rest_framework import viewsets
from rest_framework.decorators import api_view
from masjid.models import Masjid
from rest_framework.response import Response
from rest_framework import status
from rest_framework_extensions.mixins import NestedViewSetMixin
from users.models import CustomUser


class MasjidViewSet(viewsets.ModelViewSet):
    queryset = Masjid.objects.all()
    serializer_class = MasjidSerializer

class SalahTimeViewSet(viewsets.ModelViewSet):
    queryset = SalahTime.objects.all()
    serializer_class = SalahTimeSerializer

@api_view(['GET'])
def getAllMasjid(request):
    if request.method == 'GET':
        masjids = Masjid.objects.all()
        masjid_dict = {}
        masjid_list = []
        if masjids:
            for obj in masjids:
                masjid_id = obj.id
                try:
                    salatime_obj = SalahTime.objects.get(masjid_id=masjid_id)
                except SalahTime.DoesNotExist:
                    salatime_obj = None
                try:
                    masjid_user = CustomUser.objects.get(id=obj.masjid_user)
                except CustomUser.DoesNotExist:
                    masjid_user = None
                salatime_obj_dict = {}
                if salatime_obj:
                    salatime_obj_dict = {
                        "id": salatime_obj.id,
                        "fajar_azan":salatime_obj.fajar_azan ,
                        "fajar_prayer":salatime_obj.fajar_prayer ,
                        "dhuhr_azan":salatime_obj.Dhuhr_azan ,
                        "dhuhr_prayer":salatime_obj.Dhuhr_prayer ,
                        "asr_azan":salatime_obj.Asr_azan ,
                        "asr_prayer":salatime_obj.Asr_prayer ,
                        "maghrib_azan":salatime_obj.Maghrib_azan ,
                        "maghrib_prayer":salatime_obj.Maghrib_prayer ,
                        "isha_azan":salatime_obj.Isha_azan ,
                        "isha_prayer":salatime_obj.Isha_prayer ,
                        "jummah_azan":salatime_obj.jummah_azan ,
                        "jummah_prayer":salatime_obj.jummah_prayer ,
                    }
                if masjid_user.profile_pic:
                    masjid_dict = {
                        "id":obj.id,
                        "name":obj.name,
                        "address":obj.address,
                        "profile_pic":masjid_user.profile_pic.url,
                        "salatime": salatime_obj_dict,
                    }
                    masjid_list.append(masjid_dict)
                else:
                    masjid_dict = {
                        "id":obj.id,
                        "name":obj.name,
                        "address":obj.address,
                        "profile_pic":None,
                        "salatime": salatime_obj_dict,
                    }
                    masjid_list.append(masjid_dict)
            return Response({
                "status": status.HTTP_200_OK, 
                "masjid_list":masjid_list
            })
        else:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "No any masjid found",
                })
        
    return Response({"message": "Method not allowed"})
