from django.db import models
from users.models import CustomUser

class Masjid(models.Model):
    masjid_user = models.IntegerField(null=True)
    name = models.CharField(max_length=50,null=False)
    email = models.EmailField(max_length=50,null=True)
    address = models.CharField(max_length=225,null=False)
    
    def __str__(self):
        return self.name



class SalahTime(models.Model):
    masjid = models.ForeignKey(Masjid, on_delete=models.CASCADE, related_name='masjid_prayers_time')
    fajar_azan = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    fajar_prayer = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    Dhuhr_azan = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    Dhuhr_prayer = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    Asr_azan = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    Asr_prayer = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    Maghrib_azan = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    Maghrib_prayer = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    Isha_azan = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    Isha_prayer = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    jummah_azan = models.TimeField(auto_now=False, auto_now_add=False, null = True)
    jummah_prayer = models.TimeField(auto_now=False, auto_now_add=False, null = True)

    def __str__(self):
        return self.masjid.name
    