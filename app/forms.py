from django import forms
from users.models import CustomUser
            
            
class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    Confirm_password = forms.CharField(required=False, widget=forms.PasswordInput)
    class Meta:
        model = CustomUser
        fields = ('name', 'email','password')
        labels = {
            'name': 'Name', 
            'email':'Email',
            'password': 'Password',
            'Confirm_password':'Confirm Password',
        }
    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            
class UpdateSettingForm(forms.ModelForm):
    Current_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}))
    New_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    Confirm_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))
    masjidCardNumber = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '0000 0000 0000 0000'}))
    masjidCardName = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Jhon Doe'}))
    masjid_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Masjid Name'}))
    phone= forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'tel', 'class':'getphone', }))
    # profile_pic= forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'file' }))
    
    class Meta:
        model = CustomUser
        fields = ('masjid_name','email','profile_pic', "masjidCardNumber", "masjidCardName", "phone")
        labels = {
            'masjid_name': 'Masjid Name',
            'email': 'Email',
            'Current_password':'Current Password',
            'New_password':'New Password',
            'Confirm_password':'Confirm Password',
            'profile_pic': 'Profile picture',
        }
    def __init__(self, *args, **kwargs):
        super(UpdateSettingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            


class UpdatePasswordForm(forms.ModelForm):
    New_password = forms.CharField(required=False, widget=forms.PasswordInput)
    Confirm_password = forms.CharField(required=False, widget=forms.PasswordInput)
    class Meta:
        model = CustomUser
        fields = ()
        labels = {
        }
    def __init__(self, *args, **kwargs):
        super(UpdatePasswordForm, self).__init__(*args, **kwargs)
        self.fields['New_password'].widget.attrs['placeholder'] = 'New password'
        self.fields['Confirm_password'].widget.attrs['placeholder'] = 'Confirm password'
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'