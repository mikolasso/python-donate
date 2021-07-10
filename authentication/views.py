# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User,auth
from django.forms.utils import ErrorList
from django.http import HttpResponse, JsonResponse
from .forms import *
from masjid.models import *
from users.models import CustomUser
from users.models import *
import time
import requests
from core.settings import api_base_url, host_url



def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        form = LoginForm(request.POST or None)

        msg = None

        if request.method == "POST":

            if form.is_valid():
                email = form.cleaned_data.get("email")
                password = form.cleaned_data.get("password")
                user = authenticate(email=email, password=password)
                user1 = CustomUser.objects.filter(email=email)
                if user1:
                    user2 = CustomUser.objects.get(email=email)
                    if user2.is_superuser:
                        CustomUser.objects.filter(email=email).update(status=True)
                        if user is not None:
                            login(request, user)
                            return redirect("/")
                        else:    
                            msg = 'Email or Password is incorrect.'  
                    else:
                        if user is not None:
                            login(request, user)
                            if user2.masjidCardNumber:
                                return redirect("/")
                            else:
                                return redirect("/addAccounts/{}/".format(user2.id))
                        else:
                            msg = 'Email or password is incorrect.'  
                else:
                    msg = "Account does not exist."
                
            else:
                msg = 'Error validating the form.   '    

    return render(request, "accounts/login.html", {"form": form, "msg" : msg})


def register_user(request):
    msg     = None
    success = False
    get_user = None
    userdatalist = request.GET.getlist('list[]')
    if userdatalist:
        print(userdatalist)
        masjid_name = userdatalist[0]
        email = userdatalist[1]
        phone_number = userdatalist[2]
        password1 = userdatalist[3]
        password2 = userdatalist[4]
        address = userdatalist[5]
        lat = userdatalist[6]
        lng = userdatalist[7]
        time.sleep(2)
        # masjid_name = request.POST.get("masjid_name")
        # address = request.POST.get("address")
        # phone_number = request.POST.get("phone_number")
        # email = request.POST.get("email")
        # password1 = request.POST.get("password1")
        # password2 = request.POST.get("password2")
        # address2 = request.POST.get("address2")
        try:
            user1 = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user1 = None
        try:
            user2 = CustomUser.objects.get(phone=phone_number)
        except CustomUser.DoesNotExist:
            user2 = None
        if user1:
            msg = "Email already exist."
        elif user2:
            msg = "Phone number already exist."
        elif password1 != password2:
            msg = "Passwords don't match."
        elif len(password1) < 8:
            msg = "This password is too short."
        elif lat == None or lng == None:
            msg = "Please select map location."
        else:
            user = CustomUser.objects.create_user(masjid_name=masjid_name, name=masjid_name, address=address, phone=phone_number, email=email, password=password1, lat=lat, lng=lng, username=email)
            if user:
                user.save()
                get_user = CustomUser.objects.get(email=email)
                if get_user:
                    masjid = Masjid.objects.create(name=masjid_name, address=address, masjid_user=get_user.id)
                    if masjid:
                        success = True
                        get_user = get_user.id
        data = { 'msg': msg, "success" : success, 'get_user': get_user }
        return JsonResponse(data)

    return render(request, "accounts/register.html", {"msg" : msg, "success" : success })


def register_user2(request, pk):
    msg     = None
    success = False
    if request.method == "POST":
        account_name = request.POST.get("account_name")
        account_no = request.POST.get("account_no")
        validatelist=[]
        for i in account_no:
            validatelist.append(int(i))
        for i in range(0,len(account_no),2):
            validatelist[i] = validatelist[i]*2
            if validatelist[i] >= 10:
                validatelist[i] = validatelist[i]//10 + validatelist[i]%10
        if sum(validatelist)%10 == 0:
            get_user = CustomUser.objects.filter(id=pk).update(masjidCardName=account_name, masjidCardNumber=account_no)
            success = True
        else:
            msg = "Invalid account number."
        # if generate_iban_check_digits(my_iban) == my_iban[2:4] and valid_iban(my_iban):
        #     get_user = CustomUser.objects.filter(id=pk).update(masjidCardName=account_name, masjidCardNumber=my_iban)
        #     success = True
        # else:
        #     print('Invalid account Number')
        if success:
            return redirect("/")

    return render(request, "accounts/register2.html", {"msg" : msg, "success" : success })



import string
LETTERS = {ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)}


def _number_iban(iban):
    return (iban[4:] + iban[:4]).translate(LETTERS)


def generate_iban_check_digits(iban):
    number_iban = _number_iban(iban[:2] + '00' + iban[4:])
    return '{:0>2}'.format(98 - (int(number_iban) % 97))


def valid_iban(iban):
    return int(_number_iban(iban)) % 97 == 1