from django import forms
from users.models import CustomUser
from .models import Campaign, CampaignFiles

class addCampaignForm(forms.ModelForm):
    image1 = forms.ImageField(required=False, widget=forms.FileInput(attrs={'id': 'add-image', 'class':'fusk'}))
    # Confirm_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    # masjidCardNumber = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '0000 0000 0000 0000'}))
    # masjidCardName = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Jhon Doe'}))
    # title = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'title'}))
    # phone= forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'tel', 'class':'getphone', }))
    # profile_pic= forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'file' }))
    
    class Meta:
        model = Campaign
        fields = ('title',)
        labels = {}
    # def __init__(self, *args, **kwargs):
    #     super(addCampaignForm, self).__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         visible.field.widget.attrs['class'] = 'form-control'