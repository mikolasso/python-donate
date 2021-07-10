from django.db import models
from masjid.models import Masjid
from django.dispatch import receiver
from users.models import CustomUser
import os

class Campaign(models.Model):
    title = models.CharField(max_length=50,null=False)
    target_amount = models.IntegerField(null = False, default=0)
    raised_amount = models.IntegerField(null = False, default=0)
    start_date = models.DateField(null=True, auto_now = False)
    end_date = models.DateField(null=True, auto_now = False)
    masjid_id = models.ForeignKey(Masjid, on_delete=models.CASCADE, related_name='masjid_id')
    userId = models.IntegerField(null = True)
    detail = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,null=True, default="In Review")
    updated_at = models.DateTimeField(null = True)


class CampaignFiles(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='campaign_data')
    image = models.ImageField(upload_to='campaign_images', null=True)
    video = models.FileField(upload_to='campaign_videos', null=True)

    def __str__(self):
        return self.campaign.title

@receiver(models.signals.post_delete, sender=CampaignFiles)
def auto_delete_file_on_delete(sender, instance, **kwargs):
        """
        Deletes file from filesystem
        when corresponding `MediaFile` object is deleted.
        """
        if instance.image:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)

@receiver(models.signals.pre_save, sender=CampaignFiles)
def auto_delete_file_on_change(sender, instance, **kwargs):
        """
        Deletes old file from filesystem
        when corresponding `MediaFile` object is updated
        with new file.
        """
        if not instance.pk:
            return False

        try:
            old_file = sender.objects.get(pk=instance.pk).image
        except sender.DoesNotExist:
            return False

        new_file = instance.image
        if not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)