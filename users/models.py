from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date


class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    username = models.CharField(max_length=100, unique=False, null=True, blank=True)
    email = models.EmailField(unique=True, null=False)
    name = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=35, null=False)
    gender = models.CharField(max_length=50, null=True)
    dob = models.DateField(null=True, auto_now = False)
    address  = models.CharField(max_length=500, null=True)
    status  = models.BooleanField(default=False)
    masjid_name = models.CharField(max_length=255, null=True)
    masjid_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    card_info = models.BooleanField(default=False)
    cardName = models.CharField(max_length=55, null=True)
    donation_reference = models.CharField(max_length=50, null=True)
    updated_at = models.DateTimeField(null = True)
    stripe_customer_id = models.CharField(max_length=255, null=True)
    card_token = models.CharField(max_length=100, null=True)
    masjidCardName = models.CharField(max_length=100, null=True)
    verify_user  = models.BooleanField(default=False)
    masjidCardNumber = models.CharField(max_length=100, null=True)
    masjidAddress  = models.CharField(max_length=500, null=True)
    lat = models.CharField(max_length=100, null=True)
    lng = models.CharField(max_length=100, null=True)
    profile_pic = models.ImageField(upload_to='profile_pic', null=True)

    @property
    def full_name(self):
        name = ''
        if self.first_name:
            name += self.first_name
        if self.last_name:
            name += " " + self.last_name

        return name



class Feedback(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_id')
    comment = models.CharField(max_length=250, null=True)
    feedback = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.userid.email

class Donation(models.Model):
    userId = models.IntegerField(null=True)
    object_id = models.CharField(max_length=255, null=True)
    masjid_id = models.IntegerField(null=True)
    amount = models.CharField(max_length=255, null=True)
    donation_reference = models.CharField(max_length=50, null=True)
    donation_for = models.CharField(max_length=50, null=True)
    payment_type = models.CharField(max_length=50, null=False)
    recurring_period = models.CharField(max_length=50, null=True)
    detail = models.CharField(max_length=255, null=True)
    starting_at = models.DateField(auto_now=False, null=True)
    next_at = models.DateField(auto_now=False, null=True)
    payment_status = models.BooleanField(default=True)
    charge_id = models.CharField(max_length=255, null=True)
    customer_id = models.CharField(max_length=255, null=True)
    cardToken = models.CharField(max_length=500, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(null = True)





