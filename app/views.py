# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
from django.views.generic.base import TemplateView
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.response import Response
from django import template
from app.models import *
from rest_framework import status
from django.contrib.auth import update_session_auth_hash
from app.forms import *
from users.models import *
from campaign.models import Campaign
import collections, functools, operator 
from django.utils.safestring import mark_safe
import json
from masjid.models import Masjid, SalahTime
import requests
from datetime import datetime
import stripe
from users.models import *
import smtplib 
from urllib import request
from rest_framework.decorators import api_view
# import pyotp
from email.utils import formataddr
from email.mime.text import MIMEText
from core.settings import api_base_url, host_url
# from django.contrib.gis.utils import GeoIP
stripe.api_key = "sk_test_UvbSbh6FV9UkIul1duI3oQDT00H3n6HQG0"         ## my secret key

# stripe.api_key = "sk_test_jMicx1OM8URRS3Ye6eWzAh8s"
product_id = "prod_IUnz6t3HU1kTkg"

# totp = pyotp.TOTP('base32secret3232',interval=60)
# print(totp.now())




@login_required(login_url="/login/")
def index(request):
    if request.user.is_superuser:
        context = {}
        return render(request, "superAdmin/index.html",context)
    else:
        context = {}
        return render(request, "index.html",context)

@login_required(login_url="/login/")
def donation(request):
    donationList = []
    donationDict = {}
    user = request.user.id
    if request.user.is_superuser:
        context = {}
        return render(request, "superAdmin/donation-a.html",context)
    else:
        all_donations = Donation.objects.filter(userId=user)
        print(all_donations)
        for obj in all_donations:
            get_user = CustomUser.objects.get(id=obj.userId)
            donationDict = {
                "doneeName":get_user.full_name,
                "doneeEmail":get_user.email,
                "doneeAmount":obj.amount,
                "donationReference":obj.donation_reference,
                "paymentDate":obj.starting_at,
                "donationFor":obj.donation_for,
            }
            donationList.append(donationDict)
        print(donationList)
        context = {"donationList":donationList}
        return render(request, "donation.html",context)

@login_required(login_url="/login/")
def pages(request):
    user = request.user
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'error-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'error-500.html' )
        return HttpResponse(html_template.render(context, request))
        

@login_required(login_url="/login/")
def updateProfile(request, pk):
    success = False
    msg = None
    msg1 = None
    get_user = CustomUser.objects.get(id=pk)
    phone = get_user.phone
    user_email = get_user.email
    user_id_id = get_user.id
    if request.user.is_superuser:
        form1 = UpdateSettingForm(request.POST or None, request.FILES or None,instance=user)
        if request.method == 'POST':
            form1 = UpdateSettingForm(request.POST or None, request.FILES or None, instance=user)
            if form1.is_valid():
                user = form1.save()
                password = form1.cleaned_data.get('New_password')
                password2 = form1.cleaned_data.get('Confirm_password')
                email1 = request.POST.get("email")
                if request.user.is_superuser:
                    if password:
                        if password==password2:
                            user.set_password(password)
                            return redirect("/logout/")
                        else:
                            msg = "Passwords do not match."
                    else:
                        msg = "Profile updated successfully"
                        return redirect("/update_profile/{}/".format(user_id_id))
                    user.save()
                else:
                    if password:
                        if password==password2:
                            user.set_password(password)
                            return redirect("/logout/")
                        else:
                            msg = "Passwords do not match."
                    else:
                        msg = "Profile updated successfully"
                        return redirect("/update_profile/{}/".format(user_id_id))
                    user.save()
                    if user_email != email1:
                        new_user = CustomUser.objects.filter(id=pk).update(email_verification=False)
                        if new_user:
                            return redirect("/logout/")

        context = {'form1': form1,"msg":msg, "phone":phone, "user":user}
        return render(request, 'superAdmin/setting-a.html', context)
    else:
        form1 = UpdateSettingForm(request.POST or None, request.FILES or None,instance=get_user)
        if request.method == 'POST':
            form1 = UpdateSettingForm(request.POST or None, request.FILES or None, instance=get_user)
            email1 = request.POST.get("email")
            phone_number = request.POST.get("phone")
            get_users = CustomUser.objects.filter(email=email1).exclude(email=user_email)
            get_phone = CustomUser.objects.filter(phone=phone_number).exclude(phone=phone)
            if get_users:
                msg = "Email already exist."
            elif get_phone:
                msg = "Phone number already exist."
            else:
                if form1.is_valid():
                    user = form1.save()
                    password1 = form1.cleaned_data.get('Current_password')
                    password2 = form1.cleaned_data.get('New_password')
                    password = form1.cleaned_data.get('Confirm_password')
                    masjid_name = form1.cleaned_data.get('masjid_name')
                    profile_pic = form1.cleaned_data.get('profile_pic')
                    if password2 or password:
                        if password2 == password:
                            if password1:
                                if user.check_password(password1):
                                    setpass = user.set_password(password)
                                    success = True
                                    msg1 = "Profile has been updated successfully."
                                else:
                                    msg = "Incorrect current password."
                            else:
                                msg = "Enter your current password."    
                        else:
                            msg = "Passwords do not match."
                    else:
                        msg1 = "Profile updated successfully."
                    user.save()
                    try:
                        masjid = Masjid.objects.get(masjid_user=pk)
                    except Masjid.DoesNotExist:
                        masjid = None
                    if masjid_name:
                        masjid = Masjid.objects.filter(masjid_user=pk).update(name=masjid_name)
                    if success:
                        return redirect("/logout/")
                else:
                    msg = "Form is not valid."

        context = {'form1': form1,"msg":msg, "msg1":msg1, "phone":phone, "get_user":get_user}
        return render(request, 'setting.html', context)
    


@login_required(login_url="/login/")
def salaTime(request, pk):
    msg = None
    user = request.user.id
    masjid = Masjid.objects.get(masjid_user=user)
    try:
        salah_time = SalahTime.objects.get(masjid=masjid)
    except SalahTime.DoesNotExist:
        salah_time = None
    if request.method == 'POST':
        fajar_azan = request.POST.get("fajar_azan")
        fajar_salah = request.POST.get("fajar_salah")
        dhuhr_azan = request.POST.get("dhuhr_azan")
        dhuhr_salah = request.POST.get("dhuhr_salah")
        asr_azan = request.POST.get("asr_azan")
        asr_salah = request.POST.get("asr_salah")
        maghrib_azan = request.POST.get("maghrib_azan")
        maghrib_salah = request.POST.get("maghrib_salah")
        isha_azan = request.POST.get("isha_azan")
        isha_salah = request.POST.get("isha_salah")
        jumma_azan = request.POST.get("jumma_azan")
        jumma_salah = request.POST.get("jumma_salah")
        if salah_time:
            salah_obj = SalahTime.objects.filter(masjid=masjid.id).update(fajar_azan=fajar_azan, fajar_prayer=fajar_salah, Dhuhr_azan=dhuhr_azan, Dhuhr_prayer=dhuhr_salah, Asr_azan=asr_azan, 
            Asr_prayer=asr_salah, Maghrib_azan=maghrib_azan, Maghrib_prayer=maghrib_salah, Isha_azan=isha_azan, Isha_prayer=isha_salah, jummah_azan=jumma_azan, jummah_prayer=jumma_salah)
        else:
            salah_obj = SalahTime.objects.create(fajar_azan=fajar_azan, fajar_prayer=fajar_salah, Dhuhr_azan=dhuhr_azan, Dhuhr_prayer=dhuhr_salah, Asr_azan=asr_azan, masjid=masjid,
            Asr_prayer=asr_salah, Maghrib_azan=maghrib_azan, Maghrib_prayer=maghrib_salah, Isha_azan=isha_azan, Isha_prayer=isha_salah, jummah_azan=jumma_azan, jummah_prayer=jumma_salah)
        msg = "Salah time updated successfully."
    try:
        salah_time_obj = SalahTime.objects.get(masjid=masjid)
    except SalahTime.DoesNotExist:
        salah_time_obj = None
    context = {"salah_time":salah_time_obj, "msg":msg}
    return render(request, 'salah.html', context)