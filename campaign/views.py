from django.shortcuts import render
from campaign.serializers import CampaignSerializer, CampaignFilesSerializer
from campaign.models import Campaign, CampaignFiles
from rest_framework import viewsets
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import parser_classes
from django.contrib.auth.decorators import login_required
import requests
from users.models import CustomUser
from campaign.forms import addCampaignForm
from django.views.decorators.csrf import csrf_protect
from masjid.models import Masjid
import datetime
from rest_framework import status
from rest_framework.decorators import api_view
from datetime import date

class CampaignViewsets(viewsets.ModelViewSet):
    serializer_class = CampaignFilesSerializer
    queryset = CampaignFiles.objects.all()


class CampaignFilesViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    queryset = Campaign.objects.all()

@login_required(login_url="/login/")
def campaign(request):
    user = request.user
    if request.user.is_superuser:
        context = {}
        return render(request, "superAdmin/campaign-a.html",context)
    else:
        all_campaign = Campaign.objects.filter(userId=user.id)
        context = {"all_campaign":all_campaign}
        return render(request, "campaign.html",context)

@login_required(login_url="/login/")
def addCampaign(request):
    user = request.user.id
    msg = None
    msg1 = None
    if request.method == 'POST':
        try:
            masjid_id = Masjid.objects.get(masjid_user=user)
        except Masjid.DoesNotExist:
            masjid_id = None
        files = request.FILES
        title = request.POST.get("title",None)
        target_amount = request.POST.get("target_amount",None)
        raised_amount = request.POST.get("raised_amount",None)
        start_date = request.POST.get("start_date",None)
        end_date = request.POST.get("end_date",None)
        detail = request.POST.get("campaign_detail",None)
        target_amount = int(target_amount)
        raised_amount = int(raised_amount)
        if target_amount > raised_amount:
            msg1 = "Error! Target amount must be less or equal to raised amount."
        else:
            campaign = Campaign.objects.create(title=title, target_amount=target_amount, raised_amount=raised_amount, start_date=start_date, end_date=end_date, detail=detail, masjid_id=masjid_id, userId=user)
            if campaign:
                get_campaign = Campaign.objects.get(id=campaign.id)
                if files:
                    img1 = files.get("image", None)
                    img2 = files.get("image1", None)
                    img3 = files.get("image2", None)
                    video1 = files.get("video", None)
                    video2 = files.get("video1", None)
                    video3 = files.get("video2", None)
                    all_files = [[img1, video1], [img2, video2], [img3, video3]]
                    for obj in all_files:
                        im = obj[0]
                        vi = obj[1]
                        if im or vi is not None:
                            CampaignFiles.objects.create(image=im, video=vi, campaign=get_campaign)
                msg = 'Campaign added successfully.'
        data = {'msg': msg, 'msg1': msg1}
        return JsonResponse(data)
    else:
        return HttpResponse('Request method is not a POST')

@api_view(['GET'])
def getAllCampaign(request):
    if request.method == 'GET':
        all_campaign =  Campaign.objects.all()
        campaignList = []
        campaignDict = {}
        today = date.today()
        current_date = today.strftime("%Y-%m-%d")
        if all_campaign:
            for obj in all_campaign:
                endDate = str(obj.end_date)
                if endDate >= current_date:
                    try:
                        get_campaign = Campaign.objects.get(id=obj.id)
                    except Campaign.DoesNotExist:
                        get_campaign = None
                    if get_campaign:
                        allCampaignFiles =  CampaignFiles.objects.filter(campaign=get_campaign)
                        campaignFilesList = []
                        campaignFilesDict = {}
                        try:
                            masjid = Masjid.objects.get(id=obj.masjid_id.id)
                        except Masjid.DoesNotExist:
                            masjid = None
                        if allCampaignFiles:
                            for obj1 in allCampaignFiles:
                                if not obj1.image and obj1.video:
                                    campaignFilesDict = {
                                        "id":obj1.id,
                                        "image":None,
                                        "video":obj1.video.url,
                                        "campaign": get_campaign.id
                                    }
                                elif obj1.image and not obj1.video:
                                    campaignFilesDict = {
                                        "id":obj1.id,
                                        "image":obj1.image.url,
                                        "video":None,
                                        "campaign": get_campaign.id
                                    }
                                elif not obj1.image and not obj1.video:
                                    campaignFilesDict = {
                                        "id":obj1.id,
                                        "image":None,
                                        "video":None,
                                        "campaign": get_campaign.id
                                    }
                                else:
                                    campaignFilesDict = {
                                        "id":obj1.id,
                                        "image":obj1.image.url,
                                        "video":obj1.video.url,
                                        "campaign": get_campaign.id
                                    }
                                campaignFilesList.append(campaignFilesDict)
                            campaignDict = {
                                "id":obj.id,
                                "title":obj.title,
                                "target_amount":obj.target_amount,
                                "raised_amount":obj.raised_amount,
                                "start_date":obj.start_date,
                                "end_date":obj.end_date,
                                "detail":obj.detail,
                                "masjid_id":obj.masjid_id.id,
                                "campaign_data":campaignFilesList,
                            }
                            campaignList.append(campaignDict)
                        else:
                            campaignDict = {
                                "id":obj.id,
                                "title":obj.title,
                                "target_amount":obj.target_amount,
                                "raised_amount":obj.raised_amount,
                                "start_date":obj.start_date,
                                "end_date":obj.end_date,
                                "detail":obj.detail,
                                "masjid_id":obj.masjid_id.id ,
                                "campaign_data":campaignFilesList,
                            }
                            campaignList.append(campaignDict)
            return Response(
                campaignList
            )
        else:  
            return Response({
                campaignList
            })
    else:
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Method not allowed",
        })


# past_date = "2021-04-05"
# today = date.today()
# current_date = today.strftime("%Y-%m-%d")
# print(current_date)
# if current_date < past_date:
#     print(True)
# else:
#     print(False)