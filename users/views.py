from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin
from datetime import datetime, timedelta
from twilio.rest import Client
import twilio
from rest_framework import status
from .serializers import UserSerializer, RegisterUserSerializer, FeedbackSerializer, UpdateUserProfileSerializer
from rest_framework.decorators import api_view
from .models import CustomUser, Feedback, Donation
from django.http import HttpResponse
from campaign.models import Campaign
from masjid.models import Masjid
from datetime import date
from rest_framework.response import Response
import stripe
from datetime import datetime
stripe.api_key = "sk_test_UvbSbh6FV9UkIul1duI3oQDT00H3n6HQG0"


class CustomUserViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class RegisterUserViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterUserSerializer

    def create(self, request, *args, **kwargs):
        get_user_email  = request.POST.get('email')
        get_user_phone  = request.POST.get('phone')
        masjid_id  = request.POST.get('masjid_id')
        if not get_user_email:
            return Response({"message": "Email is required.",  "status": status.HTTP_204_NO_CONTENT})
        if not get_user_phone:
            return Response({"message": "Phone is required.",  "status": status.HTTP_204_NO_CONTENT})
        # if not masjid_id:
        #     return Response({"message": "masjid_id is required.",  "status": status.HTTP_204_NO_CONTENT})
        # elif masjid_id is None:
        #     return Response({"message": "masjid_id field may not be blank.",  "status": status.HTTP_204_NO_CONTENT})
        get_existing_email = CustomUser.objects.filter(email = get_user_email).last()
        get_existing_phone = CustomUser.objects.filter(phone = get_user_phone).last()
        try:
            masjid = Masjid.objects.get(id=masjid_id)
        except Masjid.DoesNotExist:
            masjid = None
        if get_existing_email is not None:
            return Response({"message": "Email already exist.",  "status": status.HTTP_429_TOO_MANY_REQUESTS})      
        elif get_existing_phone is not None:
                return Response({"message": "Phone already exist.",  "status": status.HTTP_429_TOO_MANY_REQUESTS})
        # elif masjid is None:
        #     return Response({"message": "masjid_id does not exist.",  "status": status.HTTP_429_TOO_MANY_REQUESTS})
        else:
            response = super().create(request, *args, **kwargs)
            get_existing_obj = CustomUser.objects.filter(email = get_user_email).filter(phone = get_user_phone).last()
            serializer = self.get_serializer(get_existing_obj)
            user_obj = serializer.data
            if masjid:
                masjid_obj = Masjid.objects.get(id=masjid_id)
                get_cuser = CustomUser.objects.filter(id = masjid_obj.masjid_user).last()
                if get_cuser.profile_pic:
                    return Response({
                        "message": "User created successfully.",
                        "status": status.HTTP_201_CREATED,
                        "data": { 
                            "id": user_obj['id'],        
                            "first_name": user_obj['first_name'],
                            "last_name": user_obj['last_name'],
                            "email": user_obj['email'],
                            "phone": user_obj['phone'],
                            "gender": user_obj['gender'],
                            "dob": user_obj['dob'],
                            "address": user_obj['address'],
                            "password":user_obj['password'],
                            "masjid_detail": {
                                "id":masjid_obj.id,
                                "name":masjid_obj.name,
                                "address":masjid_obj.address,
                                "profile_pic":get_cuser.profile_pic.url
                            }
                        }
                    })
                else:
                    return Response({
                        "message": "User created successfully.",
                        "status": status.HTTP_201_CREATED,
                        "data": { 
                            "id": user_obj['id'],        
                            "first_name": user_obj['first_name'],
                            "last_name": user_obj['last_name'],
                            "email": user_obj['email'],
                            "phone": user_obj['phone'],
                            "gender": user_obj['gender'],
                            "dob": user_obj['dob'],
                            "address": user_obj['address'],
                            "password":user_obj['password'],
                            "masjid_detail": {
                                "id":masjid_obj.id,
                                "name":masjid_obj.name,
                                "address":masjid_obj.address,
                                "profile_pic":None
                            }
                        }
                    })
            else:
                return Response({
                    "message": "User created successfully.",
                    "status": status.HTTP_201_CREATED,
                    "data": { 
                        "id": user_obj['id'],        
                        "first_name": user_obj['first_name'],
                        "last_name": user_obj['last_name'],
                        "email": user_obj['email'],
                        "phone": user_obj['phone'],
                        "gender": user_obj['gender'],
                        "dob": user_obj['dob'],
                        "address": user_obj['address'],
                        "password":user_obj['password'],
                        "masjid_detail": {}
                    }
                })
    def update(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        get_user_email  = request.data['email']
        get_user_phone  = request.data['phone']
        masjid_id  = request.POST.get('masjid_id')
        if not get_user_email:
            return Response({"message": "Email is required.",  "status": status.HTTP_204_NO_CONTENT})
        if not get_user_phone:
            return Response({"message": "Phone is required.",  "status": status.HTTP_204_NO_CONTENT})  
        get_existing_email = CustomUser.objects.filter(email = get_user_email).exclude(id=pk).last()
        get_existing_phone = CustomUser.objects.filter(phone = get_user_phone).exclude(id=pk).last()
        try:
            masjid = Masjid.objects.get(id=masjid_id)
        except Masjid.DoesNotExist:
            masjid = None
        if get_existing_email is not None:
            return Response({"message": "Email already exist.",  "status": status.HTTP_429_TOO_MANY_REQUESTS})      
        elif get_existing_phone is not None:
            return Response({"message": "Phone already exist.",  "status": status.HTTP_429_TOO_MANY_REQUESTS})
        else:
            response = super().update(request, *args, **kwargs)
            get_existing_obj = CustomUser.objects.filter(id=pk).last()
            serializer = self.get_serializer(get_existing_obj)
            user_obj = serializer.data
            if masjid:
                masjid_obj = Masjid.objects.get(id=masjid_id)
                get_cuser = CustomUser.objects.filter(id = masjid_obj.masjid_user).last()
                if get_cuser.profile_pic:
                    return Response({
                        "message": "User updated successfully.",
                        "status": status.HTTP_201_CREATED,
                        "data": { 
                            "id": user_obj['id'],        
                            "first_name": user_obj['first_name'],
                            "last_name": user_obj['last_name'],
                            "email": user_obj['email'],
                            "phone": user_obj['phone'],
                            "gender": user_obj['gender'],
                            "dob": user_obj['dob'],
                            "address": user_obj['address'],
                            "password":user_obj['password'],
                            "masjid_detail": {
                                "id":masjid_obj.id,
                                "name":masjid_obj.name,
                                "address":masjid_obj.address,
                                "profile_pic":get_cuser.profile_pic.url
                            }
                        }
                    })
                else:
                    return Response({
                        "message": "User updated successfully.",
                        "status": status.HTTP_201_CREATED,
                        "data": { 
                            "id": user_obj['id'],        
                            "first_name": user_obj['first_name'],
                            "last_name": user_obj['last_name'],
                            "email": user_obj['email'],
                            "phone": user_obj['phone'],
                            "gender": user_obj['gender'],
                            "dob": user_obj['dob'],
                            "address": user_obj['address'],
                            "password":user_obj['password'],
                            "masjid_detail": {
                                "id":masjid_obj.id,
                                "name":masjid_obj.name,
                                "address":masjid_obj.address,
                                "profile_pic":None
                            }
                        }
                    })
            else:
                return Response({
                    "message": "User updated successfully.",
                    "status": status.HTTP_201_CREATED,
                    "data": { 
                        "id": user_obj['id'],        
                        "first_name": user_obj['first_name'],
                        "last_name": user_obj['last_name'],
                        "email": user_obj['email'],
                        "phone": user_obj['phone'],
                        "gender": user_obj['gender'],
                        "dob": user_obj['dob'],
                        "address": user_obj['address'],
                        "password":user_obj['password'],
                        "masjid_detail": {}
                    }
                })
class UpdateUserProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UpdateUserProfileSerializer
    def update(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        profile_pic  = request.data['profile_pic']
        if not profile_pic:
            return Response({"message": "profile_pic is required.",  "status": status.HTTP_204_NO_CONTENT})
        elif profile_pic is None:
            return Response({"message": "profile_pic field may not be blank.",  "status": status.HTTP_204_NO_CONTENT})
        else:
            response = super().update(request, *args, **kwargs)
            get_existing_obj = CustomUser.objects.filter(id=pk).last()
            serializer = self.get_serializer(get_existing_obj)
            return Response({
                "status": status.HTTP_200_OK,
                "message": "Profile Image updated Successfully.",
                "data" : serializer.data
            })


@api_view(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        phone= request.POST.get('phone')
        password = request.POST.get('password')
        user = CustomUser.objects.filter(phone=phone, password=password)
        if user.exists():
            user_data = CustomUser.objects.get(phone=phone)
            try:
                masjid = Masjid.objects.get(id=user_data.masjid_id)
            except Masjid.DoesNotExist:
                masjid = None
            if masjid:
                user_masjid = CustomUser.objects.get(id=masjid.masjid_user)
                if user_masjid.profile_pic:
                    if user_data.profile_pic:
                        return Response({
                            "status": 1, 
                            "message": "User successfully logged in.",
                            "data": { 
                                "id": user_data.id,        
                                "first_name": user_data.first_name,
                                "last_name": user_data.last_name,
                                "email": user_data.email,
                                "phone": user_data.phone,
                                "gender": user_data.gender,
                                "dob": user_data.dob,
                                "address": user_data.address,
                                "card_info":user_data.card_info,
                                "profile_pic":user_data.profile_pic.url,
                                "masjid_detail":{
                                    "id":masjid.id,
                                    "name":masjid.name,
                                    "profile_pic":user_masjid.profile_pic.url
                                }
                            }
                        })
                    else:
                        profile_pic = None
                        return Response({
                            "status": 1, 
                            "message": "User successfully logged in.",
                            "data": { 
                                "id": user_data.id,        
                                "first_name": user_data.first_name,
                                "last_name": user_data.last_name,
                                "email": user_data.email,
                                "phone": user_data.phone,
                                "gender": user_data.gender,
                                "dob": user_data.dob,
                                "address": user_data.address,
                                "card_info":user_data.card_info,
                                "profile_pic":profile_pic,
                                "masjid_detail":{
                                    "id":masjid.id,
                                    "name":masjid.name,
                                    "profile_pic":user_masjid.profile_pic.url
                                }
                            }
                        })
                else:
                    if user_data.profile_pic:
                        return Response({
                            "status": 1, 
                            "message": "User successfully logged in.",
                            "data": { 
                                "id": user_data.id,        
                                "first_name": user_data.first_name,
                                "last_name": user_data.last_name,
                                "email": user_data.email,
                                "phone": user_data.phone,
                                "gender": user_data.gender,
                                "dob": user_data.dob,
                                "address": user_data.address,
                                "card_info":user_data.card_info,
                                "profile_pic":user_data.profile_pic.url,
                                "masjid_detail":{
                                    "id":masjid.id,
                                    "name":masjid.name,
                                    "profile_pic":None
                                }
                            }
                        })
                    else:
                        profile_pic = None
                        return Response({
                            "status": 1, 
                            "message": "User successfully logged in.",
                            "data": { 
                                "id": user_data.id,        
                                "first_name": user_data.first_name,
                                "last_name": user_data.last_name,
                                "email": user_data.email,
                                "phone": user_data.phone,
                                "gender": user_data.gender,
                                "dob": user_data.dob,
                                "address": user_data.address,
                                "card_info":user_data.card_info,
                                "profile_pic":profile_pic,
                                "masjid_detail":{
                                    "id":masjid.id,
                                    "name":masjid.name,
                                    "profile_pic":None
                                }
                            }
                        })
            else:
                if user_data.profile_pic:
                    return Response({
                        "status": 1, 
                        "message": "User successfully logged in.",
                        "data": { 
                            "id": user_data.id,        
                            "first_name": user_data.first_name,
                            "last_name": user_data.last_name,
                            "email": user_data.email,
                            "phone": user_data.phone,
                            "gender": user_data.gender,
                            "dob": user_data.dob,
                            "address": user_data.address,
                            "card_info":user_data.card_info,
                            "profile_pic":user_data.profile_pic.url,
                            "masjid_detail":{},
                        }
                    })
                else:
                    profile_pic = None
                    return Response({
                        "status": 1, 
                        "message": "User successfully logged in.",
                        "data": { 
                            "id": user_data.id,        
                            "first_name": user_data.first_name,
                            "last_name": user_data.last_name,
                            "email": user_data.email,
                            "phone": user_data.phone,
                            "gender": user_data.gender,
                            "dob": user_data.dob,
                            "address": user_data.address,
                            "card_info":user_data.card_info,
                            "profile_pic":profile_pic,
                            "masjid_detail":{}
                        }
                    })
        else:
            return Response({
                "status": 0,
                "message": "Invalid Phone  or Pin",
                })
        
    return Response({"message": "User Not Logged in"})



class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer




@api_view(['POST'])
def getCardDetail(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        cardName = request.POST.get('cardName')
        cardNumber = request.POST.get('cardNumber')
        exp_month = request.POST.get('exp_month')
        exp_year = request.POST.get('exp_year')
        cvv = request.POST.get('cvv')
        donation_reference = request.POST.get('donation_reference')
        if user_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id is required",
            })
        elif not user_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id field may not be blank."
            })
        elif cardName is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardName is required"
            })
        elif not cardName:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardName field may not be blank."
            })
        elif cardName is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardName is required"
            })
        elif not exp_month:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "exp_month field may not be blank."
            })
        elif exp_year is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "exp_year is required."
            })
        elif not exp_year:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "exp_year field may not be blank."
            })
        elif cvv is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cvv is required",
            })
        elif not cvv:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cvv field may not be blank."
            })
        elif not (len(cvv) == 3) or not type(int(cvv) == int):
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid cvv Number",
            })
            
        elif donation_reference is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_reference is required",
            })
        elif not donation_reference:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_reference field may not be blank.",
            })
        elif cardNumber is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardNumber is required",
            })
        elif not cardNumber:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardNumber field may not be blank.",
            })
        elif not (len(cardNumber) == 16) or not type(int(cardNumber) == int):
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid Card Number",
            })
        else:
            try:
                user_obj = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                user_obj = None
            if user_obj is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "user does not exist."
                })
            else:
                validatelist=[]
                for i in cardNumber:
                    validatelist.append(int(i))
                for i in range(0,len(cardNumber),2):
                    validatelist[i] = validatelist[i]*2
                    if validatelist[i] >= 10:
                        validatelist[i] = validatelist[i]//10 + validatelist[i]%10
                if sum(validatelist)%10 == 0:
                    user = CustomUser.objects.get(id=user_id)
                    obj = None
                    if user.email:
                        obj = user.email
                    else:
                        obj = user.phone
                    customer = stripe.Customer.create(
                        email = obj
                    )
                    if customer:
                        try:
                            token = stripe.Token.create(
                                card={
                                    "number": cardNumber,
                                    "exp_month": exp_month,
                                    "exp_year": exp_year,
                                    "cvc": cvv,
                                },
                            )
                        except stripe.error.CardError as e:
                            return Response({
                                "status": e.http_status,
                                "message":  e.user_message,
                            })
                        if token:
                            try:
                                cardToken = stripe.Customer.create_source(
                                    customer.id,
                                    source=token.id,
                                    metadata={"donation_reference":donation_reference}
                                )
                            except stripe.error.CardError as e:
                                return Response({
                                    "status": e.http_status,
                                    "message":  e.user_message,
                                })
                            if cardToken:
                                user = CustomUser.objects.filter(id=user_id).update(stripe_customer_id=customer.id, card_token=cardToken.id, card_info=True, cardName=cardName,donation_reference=donation_reference)
                                if user:
                                    return Response({
                                        "status": status.HTTP_200_OK,
                                        "data": cardToken,
                                    })
                else:
                    return Response({
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid Card Number",
                    })
    else:
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Method not allowed",
        })




@api_view(['PUT'])
def updateCardDetail(request):
    if request.method == 'PUT':
        user_id = request.POST.get('user_id')
        cardName = request.POST.get('cardName')
        cardNumber = request.POST.get('cardNumber')
        exp_month = request.POST.get('exp_month')
        exp_year = request.POST.get('exp_year')
        cvv = request.POST.get('cvv')
        donation_reference = request.POST.get('donation_reference')
        if user_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id is required",
            })
        elif not user_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id field may not be blank."
            })
        elif cardName is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardName is required"
            })
        elif not cardName:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardName field may not be blank."
            })
        elif cardName is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardName is required"
            })
        elif not exp_month:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "exp_month field may not be blank."
            })
        elif exp_year is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "exp_year is required."
            })
        elif not exp_year:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "exp_year field may not be blank."
            })
        elif cvv is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cvv is required",
            })
        elif not cvv:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cvv field may not be blank."
            })
        elif not (len(cvv) == 3) or not type(int(cvv) == int):
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid cvv Number",
            })
        elif donation_reference is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_reference is required",
            })
        elif not donation_reference:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_reference field may not be blank.",
            })
        elif cardNumber is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardNumber is required",
            })
        elif not cardNumber:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "cardNumber field may not be blank.",
            })
        elif not (len(cardNumber) == 16) or not type(int(cardNumber) == int):
            return Response({
                "status": status.HTTP_400_BAD_REQUEST,
                "message": "Invalid Card Number",
            })
        else:
            validatelist=[]
            for i in cardNumber:
                validatelist.append(int(i))
            for i in range(0,len(cardNumber),2):
                validatelist[i] = validatelist[i]*2
                if validatelist[i] >= 10:
                    validatelist[i] = validatelist[i]//10 + validatelist[i]%10
            if sum(validatelist)%10 == 0:
                user = CustomUser.objects.get(id=user_id)
                obj = None
                if user.email:
                    obj = user.email
                else:
                    obj = user.phone
                if user:
                    try:
                        token = stripe.Token.create(
                            card={
                                "number": cardNumber,
                                "exp_month": exp_month,
                                "exp_year": exp_year,
                                "cvc": cvv,
                            },
                        )
                    except stripe.error.CardError as e:
                        return Response({
                            "status": e.http_status,
                            "message":  e.user_message,
                        })
                    if token:
                        try:
                            cardToken = stripe.Customer.create_source(
                                user.stripe_customer_id,
                                source=token.id,
                                metadata={"donation_reference":donation_reference}
                            )
                        except stripe.error.CardError as e:
                            return Response({
                                "status": e.http_status,
                                "message":  e.user_message,
                            })
                        if cardToken:
                            del_card = stripe.Customer.delete_source(
                                user.stripe_customer_id,
                                user.card_token,
                            )
                            if del_card:
                                user = CustomUser.objects.filter(id=user_id).update(card_token=cardToken.id, card_info=True, cardName=cardName,donation_reference=donation_reference)
                                if user:
                                    return Response({
                                        "status": status.HTTP_200_OK,
                                        "data": cardToken,
                                    })
                            
            else:
                return Response({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Invalid Card Number",
                })
    else:
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Method not allowed",
        })

@api_view(['POST'])
def getCard(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id is required",
            })
        elif not user_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id field may not be blank."
            })
        else:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                user = None
            if user is not None:
                if user.stripe_customer_id and user.card_token:
                    card = stripe.Customer.retrieve_source(
                        user.stripe_customer_id,
                        user.card_token,
                    )
                    if card:
                        return Response({
                            "status": status.HTTP_200_OK,
                            "cardName": user.cardName,
                            "cardDetail": card,
                        })
                else:
                    return Response({
                        "status": status.HTTP_204_NO_CONTENT,
                        "data": "No any content."
                    })
            else:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "data": "User id does not exist"
                })
    else:
        return Response({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Method not allowed",
        })



def sendMessage(phone, code):
    # Create an SNS client
    account_sid = 'AC778aa918c733c6f732093d5307360dc8'
    auth_token = 'd5d8b1a992585ca4121c6c7069a300d5'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=code,
        from_='+13128789656',
        to=phone
    )

@api_view(['POST'])
def verifyPhoneView(request):
    account_sid = 'AC778aa918c733c6f732093d5307360dc8'
    auth_token = 'd5d8b1a992585ca4121c6c7069a300d5'
    client = Client(account_sid, auth_token)
    if request.method == 'POST':
        requestPhone = request.POST.get('phone')
        code = request.POST.get('code')
        if requestPhone is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "phone is required",
            })
        elif not requestPhone:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "phone field may not be blank."
            })
        elif code is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "code is required",
            })
        elif not code:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "code field may not be blank."
            })
        else:
            try:
                user = CustomUser.objects.get(phone=requestPhone)
            except CustomUser.DoesNotExist:
                user = None
            if user is None:
                try:
                    # sendMessage(requestPhone, code)
                    message = client.messages.create(
                        body=code,
                        from_='+13128789656',
                        to=requestPhone
                    )
                except twilio.base.exceptions.TwilioRestException as e:
                    return Response({"detail": "The requested resource was not found" + requestPhone, "status": status.HTTP_404_NOT_FOUND})  
                if message:
                    return Response({"detail": "Message has been sent to " + requestPhone, "status": status.HTTP_200_OK})
            else:
                return Response({"detail": "User already exists.", "status": status.HTTP_409_CONFLICT})
            
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})



@api_view(['POST'])
def forgetPin(request):
    account_sid = 'AC778aa918c733c6f732093d5307360dc8'
    auth_token = 'd5d8b1a992585ca4121c6c7069a300d5'
    client = Client(account_sid, auth_token)
    if request.method == 'POST':
        requestPhone = request.POST.get('phone')
        code = request.POST.get('code')
        if requestPhone is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "phone is required",
            })
        elif not requestPhone:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "phone field may not be blank."
            })
        elif code is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "code is required",
            })
        elif not code:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "code field may not be blank."
            })
        else:
            try:
                user = CustomUser.objects.get(phone=requestPhone)
            except CustomUser.DoesNotExist:
                user = None
            if user:
                try:
                    message = client.messages.create(
                        body=code,
                        from_='+13128789656',
                        to=requestPhone
                    )
                except twilio.base.exceptions.TwilioRestException as e:
                    return Response({"detail": "The requested resource was not found" + requestPhone, "status": status.HTTP_404_NOT_FOUND})  
                if message:
                    return Response({"detail": "Message has been sent to " + requestPhone, "status": status.HTTP_200_OK})
            else:
                return Response({"detail": "User does not exists.", "status": status.HTTP_409_CONFLICT})
            
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})



@api_view(['POST'])
def updatePin(request):
    account_sid = 'AC778aa918c733c6f732093d5307360dc8'
    auth_token = 'd5d8b1a992585ca4121c6c7069a300d5'
    client = Client(account_sid, auth_token)
    if request.method == 'POST':
        requestPhone = request.POST.get('phone')
        code = request.POST.get('pin')
        if requestPhone is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "phone is required",
            })
        elif not requestPhone:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "phone field may not be blank."
            })
        elif code is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "Pin is required",
            })
        elif not code:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "Pin field may not be blank."
            })
        else:
            try:
                user = CustomUser.objects.get(phone=requestPhone)
            except CustomUser.DoesNotExist:
                user = None
            if user:
                c_user = CustomUser.objects.filter(phone=requestPhone).update(password=code)
                if c_user:
                    return Response({"detail": "Pin has been set updated successfully", "status": status.HTTP_200_OK})
            else:
                return Response({"detail": "User does not exists.", "status": status.HTTP_409_CONFLICT})
            
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})


@api_view(['POST'])
def donationForCampaign(request):
    if request.method == 'POST':
        campaign_id = request.POST.get('campaign_id')
        user_id = request.POST.get('user_id')
        amount = int(request.POST.get('amount'))
        if campaign_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "campaign_id is required",
            })
        elif not campaign_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "campaign_id field may not be blank."
            })
        elif user_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id is required",
            })
        elif not user_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id field may not be blank."
            })
        elif amount is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "amount is required",
            })
        elif not amount:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "amount field may not be blank."
            })
        elif not type(amount) == int:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "amount field must be integer."
            })
        else:
            try:
                campaign_obj = Campaign.objects.get(id=campaign_id)
            except Campaign.DoesNotExist:
                campaign_obj = None
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                user = None
            if campaign_obj is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "campaign does not exist."
                })
            elif user is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "user does not exist."
                })
            else:
                if user:
                    if user.stripe_customer_id:
                        campaign = Campaign.objects.get(id=campaign_id)
                        amount1 = int(amount * 100)
                        # print(amount)
                        donation_for = "campaign"
                        payment_type = "one_time"
                        today = date.today()
                        current_date = today.strftime("%Y-%m-%d")
                        if amount1 > 99999900:
                            return Response({"detail": "Amount too large", "status": status.HTTP_400_BAD_REQUEST})
                        else:
                            try:
                                charge = stripe.Charge.create(
                                    amount=amount1,
                                    currency="usd",
                                    customer=user.stripe_customer_id,
                                    description=campaign.title,
                                )
                            except stripe.error.CardError as e:
                                return Response({
                                    "status": e.http_status,
                                    "message":  e.user_message,
                                })
                            if charge.status == "succeeded":
                                donation = Donation.objects.create(userId=user_id, object_id=campaign_id, amount=amount, donation_reference=charge.source.metadata.donation_reference, donation_for=donation_for, payment_type=payment_type, 
                                starting_at=current_date, charge_id=charge.id, customer_id=user.stripe_customer_id, cardToken=user.card_token, masjid_id=campaign.masjid_id.id)
                                if donation:
                                    campaign_amount = campaign.target_amount - amount
                                    campaign_obj = Campaign.objects.filter(id=campaign_id).update(target_amount=campaign_amount)
                                    if campaign_obj:
                                        return Response({
                                            "status": status.HTTP_200_OK,
                                            "chargeDetail": charge,
                                        })
                                else:
                                    return Response({"detail": "Donation failed!", "status": status.HTTP_400_BAD_REQUEST})
                            else:
                                return Response({"detail": "Donation failed!", "status": status.HTTP_400_BAD_REQUEST})
                    else:
                        return Response({"detail": "Enter card details.", "status": status.HTTP_400_BAD_REQUEST})
                        
                else:
                    return Response({"detail": "User does not exists.", "status": status.HTTP_204_NO_CONTENT})
            
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})



@api_view(['POST'])
def donationForMasjid(request):
    if request.method == 'POST':
        masjid_id = request.POST.get('masjid_id')
        user_id = request.POST.get('user_id')
        amount = request.POST.get('amount')
        starting_at = request.POST.get('starting_at')
        payment_type = request.POST.get('payment_type')
        recurring_period = request.POST.get('recurring_period')
        if masjid_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "masjid_id is required",
            })
        elif not masjid_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "masjid_id field may not be blank."
            })
        elif user_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id is required",
            })
        elif not user_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id field may not be blank."
            })
        elif amount is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "amount is required",
            })
        elif not amount:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "amount field may not be blank."
            })
        elif payment_type is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "payment_type is required",
            })
        elif not payment_type:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "payment_type field may not be blank."
            })
        elif starting_at is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "starting_at is required",
            })
        elif not starting_at:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "starting_at field may not be blank."
            })
        else:
            try:
                masjid_obj = Masjid.objects.get(id=masjid_id)
            except Masjid.DoesNotExist:
                masjid_obj = None
            try:
                user_obj = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                user_obj = None
            if masjid_obj is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "masjid does not exist."
                })
            elif user_obj is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "user does not exist."
                })
            if payment_type == "recurring" or payment_type == "one_time":
                if payment_type == "recurring":
                    if recurring_period is None:
                        return Response({
                            "status": status.HTTP_204_NO_CONTENT,
                            "message": "recurring_period is required",
                        })
                    elif not recurring_period:
                        return Response({
                            "status": status.HTTP_204_NO_CONTENT,
                            "message": "recurring_period field may not be blank."
                        })
                else:
                    payment_type = "one_time"
            else:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "Invalid payment_type."
                })
            if user_obj:
                if user_obj.stripe_customer_id:
                    masjid = Masjid.objects.get(id=masjid_id)
                    amount = int(amount)
                    amount1 = int(amount * 100)
                    donation_for = "masjid"
                    if amount1 > 99999900:
                        return Response({"detail": "Amount too large", "status": status.HTTP_400_BAD_REQUEST})
                    else:
                        try:
                            charge = stripe.Charge.create(
                                amount=amount1,
                                currency="usd",
                                customer=user_obj.stripe_customer_id,
                                description=masjid.name,
                            )
                        except stripe.error.CardError as e:
                            return Response({
                                "status": e.http_status,
                                "message":  e.user_message,
                            })
                        if charge.status == "succeeded":
                            if payment_type == "one_time":
                                donation = Donation.objects.create(userId=user_id, object_id=masjid_id, amount=amount, donation_reference=charge.source.metadata.donation_reference, donation_for=donation_for, payment_type=payment_type, 
                                starting_at=starting_at, charge_id=charge.id, customer_id=user_obj.stripe_customer_id, cardToken=user_obj.card_token, masjid_id=masjid_id, payment_status=False)
                            else:
                                date1 = str(starting_at)
                                if recurring_period == "weekly":
                                    datetime_object = datetime.strptime(date1, '%Y-%m-%d')
                                    date_obj = datetime_object.date()
                                    Next_Date = date_obj + timedelta(days=7)
                                    donation = Donation.objects.create(userId=user_id, object_id=masjid_id, amount=amount, donation_reference=charge.source.metadata.donation_reference, donation_for=donation_for, payment_type=payment_type, 
                                    starting_at=starting_at, charge_id=charge.id, customer_id=user_obj.stripe_customer_id, cardToken=user_obj.card_token, recurring_period=recurring_period, masjid_id=masjid_id, next_at=Next_Date)
                                    # recurring_donation = RecurringDonation.objects.create(user_id=user_id, payment_type=payment_type, starting_at=starting_at, recurring_period=recurring_period, next_at=Next_Date, customer_id=user_obj.stripe_customer_id, masjid_id=masjid_id)
                                elif recurring_period == "fortnightly":
                                    datetime_object = datetime.strptime(date1, '%Y-%m-%d')
                                    date_obj = datetime_object.date()
                                    Next_Date = date_obj + timedelta(days=15)
                                    donation = Donation.objects.create(userId=user_id, object_id=masjid_id, amount=amount, donation_reference=charge.source.metadata.donation_reference, donation_for=donation_for, payment_type=payment_type, 
                                    starting_at=starting_at, charge_id=charge.id, customer_id=user_obj.stripe_customer_id, cardToken=user_obj.card_token, recurring_period=recurring_period, masjid_id=masjid_id, next_at=Next_Date)
                                    # recurring_donation = RecurringDonation.objects.create(user_id=user_id, payment_type=payment_type, starting_at=starting_at, recurring_period=recurring_period, next_at=Next_Date, customer_id=user_obj.stripe_customer_id, masjid_id=masjid_id)
                                elif recurring_period == "monthly":
                                    datetime_object = datetime.strptime(date1, '%Y-%m-%d')
                                    date_obj = datetime_object.date()
                                    Next_Date = date_obj + timedelta(days=30)
                                    donation = Donation.objects.create(userId=user_id, object_id=masjid_id, amount=amount, donation_reference=charge.source.metadata.donation_reference, donation_for=donation_for, payment_type=payment_type, 
                                    starting_at=starting_at, charge_id=charge.id, customer_id=user_obj.stripe_customer_id, cardToken=user_obj.card_token, recurring_period=recurring_period, masjid_id=masjid_id, next_at=Next_Date)
                                    # recurring_donation = RecurringDonation.objects.create(user_id=user_id, payment_type=payment_type, starting_at=starting_at, recurring_period=recurring_period, next_at=Next_Date, customer_id=user_obj.stripe_customer_id, masjid_id=masjid_id)
                            if donation:
                                return Response({
                                    "status": status.HTTP_200_OK,
                                    "chargeDetail": charge,
                                })
                            else:
                                return Response({"detail": "Donation failed!", "status": status.HTTP_400_BAD_REQUEST})
                        else:
                            return Response({"detail": "Donation failed!", "status": status.HTTP_400_BAD_REQUEST})
                else:
                    return Response({"detail": "Enter card details", "status": status.HTTP_400_BAD_REQUEST})
                    
            else:
                return Response({"detail": "User does not exists.", "status": status.HTTP_204_NO_CONTENT})
            
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})




@api_view(['POST'])
def donationHistory(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id is required",
            })
        elif not user_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id field may not be blank."
            })
        else:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                user = None
            if user is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "user does not exist."
                })
            else:
                donHisList = []
                donHistDict = {}
                all_donation = Donation.objects.filter(userId=user_id)
                for obj in all_donation:
                    get_masjid = Masjid.objects.get(id=obj.masjid_id)
                    donHistDict = {
                        "id":obj.id,
                        "masjidId":get_masjid.id,
                        "masjidName":get_masjid.name,
                        "masjidAddress":get_masjid.address,
                        "donationAmount":obj.amount,
                        "donationType":obj.payment_type,
                        "donationFor":obj.donation_for,
                        "donationDate":obj.starting_at,
                        "donationReference":obj.donation_reference,
                    }
                    donHisList.append(donHistDict)
                return Response({
                    "status": status.HTTP_200_OK,
                    "message": 'success',
                    "data": donHisList
                })
                
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})



@api_view(['POST'])
def activeDonation(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id is required",
            })
        elif not user_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "user_id field may not be blank."
            })
        else:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                user = None
            if user is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "user does not exist."
                })
            else:
                donHisList = []
                donHistDict = {}
                all_donation = Donation.objects.filter(userId=user_id, payment_type="recurring")
                Next_Date = None
                if all_donation:
                    for obj in all_donation:
                        date1 = str(obj.starting_at)
                        if obj.recurring_period == "weekly":
                            datetime_object = datetime.strptime(date1, '%Y-%m-%d')
                            date_obj = datetime_object.date()
                            Next_Date = date_obj + timedelta(days=7)
                        elif obj.recurring_period == "fortnightly":
                            datetime_object = datetime.strptime(date1, '%Y-%m-%d')
                            date_obj = datetime_object.date()
                            Next_Date = date_obj + timedelta(days=15)
                        elif obj.recurring_period == "monthly":
                            datetime_object = datetime.strptime(date1, '%Y-%m-%d')
                            date_obj = datetime_object.date()
                            Next_Date = date_obj + timedelta(days=30)
                        get_masjid = Masjid.objects.get(id=obj.masjid_id)
                        donHistDict = {
                            "id":obj.id,
                            "masjidId":get_masjid.id,
                            "masjidName":get_masjid.name,
                            "masjidAddress":get_masjid.address,
                            "donationAmount":obj.amount,
                            "donationType":obj.payment_type,
                            "donationFor":obj.donation_for,
                            "recurringPeriod":obj.recurring_period,
                            "startingDate":obj.starting_at,
                            "NextDonationDate":Next_Date,
                            "donationReference":obj.donation_reference,
                            "donationStatus":obj.payment_status,
                        }
                        donHisList.append(donHistDict)
                    return Response({
                        "status": status.HTTP_200_OK,
                        "message":"success",
                        "data": donHisList
                    })
                else:
                    return Response({
                        "status": status.HTTP_200_OK,
                        "message": "detail not found",
                        "data": []
                    })  
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})



@api_view(['POST'])
def donationStatus(request):
    if request.method == 'POST':
        donation_id = request.POST.get('donation_id')
        payment_status = request.POST.get('payment_status')
        if donation_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_id is required",
            })
        elif not donation_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_id field may not be blank."
            })
        if payment_status is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "payment_status is required",
            })
        elif not payment_status:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "payment_status field may not be blank."
            })
        else:
            if payment_status:
                if payment_status == "true" or payment_status == True:
                    payment_status = True
                elif payment_status == "false" or payment_status == False:
                    payment_status = False
                else:
                    return Response({
                        "status": status.HTTP_204_NO_CONTENT,
                        "message": "Invalid payment_status."
                    })
            try:
                donation = Donation.objects.get(id=donation_id)
            except Donation.DoesNotExist:
                donation = None
            if donation is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "donation does not exist."
                })
            else:
                if donation:
                    don_obj = Donation.objects.filter(id=donation_id).update(payment_status=payment_status)
                    if don_obj:
                        return Response({
                            "status": status.HTTP_200_OK,
                            "message": "donation status updated successfully"
                        }) 
                else:
                    return Response({
                        "status": status.HTTP_200_OK,
                        "message": "detail not found"
                    })  
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})


@api_view(['POST'])
def stopRecurringDonation(request):
    if request.method == 'POST':
        donation_id = request.POST.get('donation_id')
        if donation_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_id is required",
            })
        elif not donation_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_id field may not be blank."
            })
        else:
            try:
                donation = Donation.objects.get(id=donation_id)
            except Donation.DoesNotExist:
                donation = None
            if donation is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "donation does not exist."
                })
            else:
                if donation:
                    don_obj = Donation.objects.filter(id=donation_id).update(payment_type="one_time", recurring_period=None, payment_status=False)
                    if don_obj:
                        Donation.objects.filter(id=donation_id).delete()
                        return Response({
                            "status": status.HTTP_200_OK,
                            "message": "donation stopped successfully"
                        }) 
                else:
                    return Response({
                        "status": status.HTTP_200_OK,
                        "message": "detail not found"
                    })  
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})


@api_view(['POST'])
def getDonation(request):
    if request.method == 'POST':
        donation_id = request.POST.get('donation_id')
        if donation_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_id is required",
            })
        elif not donation_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_id field may not be blank."
            })
        else:
            try:
                donation = Donation.objects.get(id=donation_id)
            except Donation.DoesNotExist:
                donation = None
            if donation is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "donation does not exist."
                })
            else:
                if donation:
                    get_masjid = Masjid.objects.get(id=donation.masjid_id)
                    return Response({
                        "status": status.HTTP_200_OK,
                        "message": "success",
                        "data":{
                            "id":donation.id,
                            "masjidId":get_masjid.id,
                            "masjidName":get_masjid.name,
                            "masjidAddress":get_masjid.address,
                            "donationAmount":donation.amount,
                            "donationType":donation.payment_type,
                            "recurringPeriod":donation.recurring_period,
                            "donationFor":donation.donation_for,
                            "startingDate":donation.starting_at,
                            "donationReference":donation.donation_reference,
                        }
                    }) 
                else:
                    return Response({
                        "status": status.HTTP_200_OK,
                        "message": "detail not found"
                    })  
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})




@api_view(['POST'])
def updateDonation(request):
    if request.method == 'POST':
        donation_id = request.POST.get('donation_id')
        masjid_id = request.POST.get('masjid_id')
        amount = request.POST.get('amount')
        starting_at = request.POST.get('starting_at')
        payment_type = request.POST.get('payment_type')
        recurring_period = request.POST.get('recurring_period')
        if donation_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_id is required",
            })
        elif not donation_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "donation_id field may not be blank."
            })
        elif masjid_id is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "masjid_id is required",
            })
        elif not masjid_id:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "masjid_id field may not be blank."
            })
        elif amount is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "amount is required",
            })
        elif not amount:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "amount field may not be blank."
            })
        elif payment_type is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "payment_type is required",
            })
        elif not payment_type:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "payment_type field may not be blank."
            })
        elif starting_at is None:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "starting_at is required",
            })
        elif not starting_at:
            return Response({
                "status": status.HTTP_204_NO_CONTENT,
                "message": "starting_at field may not be blank."
            })
        else:
            amount = int(amount)
            amount1 = int(amount * 100)
            try:
                masjid_obj = Masjid.objects.get(id=masjid_id)
            except Masjid.DoesNotExist:
                masjid_obj = None
            try:
                donation = Donation.objects.get(id=donation_id)
            except Donation.DoesNotExist:
                donation = None
            if donation is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "donation does not exist."
                })
            elif masjid_obj is None:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "masjid does not exist."
                })
            elif amount1 > 99999900:
                return Response({"detail": "Amount too large", "status": status.HTTP_400_BAD_REQUEST})

            if payment_type == "recurring" or payment_type == "one_time":
                if payment_type == "recurring":
                    payment_type = "recurring"
                    if recurring_period is None:
                        return Response({
                            "status": status.HTTP_204_NO_CONTENT,
                            "message": "recurring_period is required",
                        })
                    elif not recurring_period:
                        return Response({
                            "status": status.HTTP_204_NO_CONTENT,
                            "message": "recurring_period field may not be blank."
                        })
                else:
                    payment_type = "one_time"
            else:
                return Response({
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "Invalid payment_type."
                })
            if donation:
                if payment_type == "one_time":
                    don_obj = Donation.objects.filter(id=donation_id).update(masjid_id=masjid_id, amount=amount, starting_at=starting_at, payment_type=payment_type)
                else:
                    date1 = str(starting_at)
                    if recurring_period == "weekly":
                        datetime_object = datetime.strptime(date1, '%Y-%m-%d')
                        date_obj = datetime_object.date()
                        Next_Date = date_obj + timedelta(days=7)
                        don_obj = Donation.objects.filter(id=donation_id).update(masjid_id=masjid_id, amount=amount, starting_at=starting_at, payment_type=payment_type, recurring_period=recurring_period, next_at=Next_Date)
                    elif recurring_period == "fortnightly":
                        datetime_object = datetime.strptime(date1, '%Y-%m-%d')
                        date_obj = datetime_object.date()
                        Next_Date = date_obj + timedelta(days=15)
                        don_obj = Donation.objects.filter(id=donation_id).update(masjid_id=masjid_id, amount=amount, starting_at=starting_at, payment_type=payment_type, recurring_period=recurring_period, next_at=Next_Date)
                    elif recurring_period == "monthly":
                        datetime_object = datetime.strptime(date1, '%Y-%m-%d')
                        date_obj = datetime_object.date()
                        Next_Date = date_obj + timedelta(days=30)
                        don_obj = Donation.objects.filter(id=donation_id).update(masjid_id=masjid_id, amount=amount, starting_at=starting_at, payment_type=payment_type, recurring_period=recurring_period, next_at=Next_Date)
                if don_obj:
                    obj = Donation.objects.get(id=donation_id)
                    get_masjid = Masjid.objects.get(id=obj.masjid_id)
                    return Response({
                        "status": status.HTTP_200_OK,
                        "message": "donation updated successfully",
                        "data":{
                            "id":obj.id,
                            "masjidId":get_masjid.id,
                            "masjidName":get_masjid.name,
                            "masjidAddress":get_masjid.address,
                            "donationAmount":obj.amount,
                            "donationType":obj.payment_type,
                            "recurringPeriod":obj.recurring_period,
                            "donationFor":obj.donation_for,
                            "startingDate":obj.starting_at,
                            "nextPayment":obj.next_at,
                            "donationReference":obj.donation_reference,
                        }
                    }) 
            else:
                return Response({
                    "status": status.HTTP_200_OK,
                    "message": "detail not found"
                })  
    else:
        return Response({"detail": "Invalid Request!",  "status": status.HTTP_400_BAD_REQUEST})




def donationCharge():
    payment_type = "recurring"
    donation_obj = Donation.objects.filter(payment_type=payment_type)
    today = date.today()
    today_date = str(today.strftime("%Y-%m-%d"))
    if donation_obj:
        for obj in donation_obj:
            if obj.payment_status == True:
                if str(obj.starting_at) == today_date or str(obj.next_at) == today_date:
                    get_user = CustomUser.objects.get(id=obj.userId)
                    get_masjid = Masjid.objects.get(id=obj.masjid_id)
                    if get_user:
                        try:
                            charge = stripe.Charge.create(
                                amount=obj.amount,
                                currency="usd",
                                customer=get_user.stripe_customer_id,
                                description=get_masjid.name,
                            )
                        except stripe.error.CardError as e:
                            return Response({
                                "status": e.http_status,
                                "message":  e.user_message,
                            })
                        if charge.status == "succeeded":
                            if obj.recurring_period == "weekly":
                                datetime_object = datetime.strptime(today_date, '%Y-%m-%d')
                                date_obj = datetime_object.date()
                                Next_Date = date_obj + timedelta(days=7)
                                donation = Donation.objects.filter(id=obj.id).update(next_at=Next_Date)
                            elif obj.recurring_period == "fortnightly":
                                datetime_object = datetime.strptime(today_date, '%Y-%m-%d')
                                date_obj = datetime_object.date()
                                Next_Date = date_obj + timedelta(days=15)
                                donation = Donation.objects.filter(id=obj.id).update(next_at=Next_Date)
                            elif obj.recurring_period == "monthly":
                                datetime_object = datetime.strptime(today_date, '%Y-%m-%d')
                                date_obj = datetime_object.date()
                                Next_Date = date_obj + timedelta(days=30)
                                donation = Donation.objects.filter(id=obj.id).update(next_at=Next_Date)
                            else:
                                pass  
