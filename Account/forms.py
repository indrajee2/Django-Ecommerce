from django import forms
from Account.models import Custom_user,Product,Address,Comment
from Account import message

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    confirm_password = forms.CharField(widget = forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))
    referral_code=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Referral Code'}))
    class Meta:
        model = Custom_user
        fields =["username", "email", "password"]
        widgets={
            'username': forms.TextInput(attrs={'class':'form-control','placeholder':'username'}),
            'email': forms.EmailInput(attrs={'class':'form-control','placeholder':'Email address @yopmail.com'}),

        }

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data.get('referral_code'))
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=60,widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            try:
                user = Custom_user.objects.get(email=email)
                if not user.is_active:
                    raise forms.ValidationError(message.Error_Account_Verify)
            except Custom_user.DoesNotExist:
                raise forms.ValidationError(message.error_email_invalid)
        return cleaned_data

class EmailForm(forms.Form):
    email=forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}),required=True)

    def clean(self):
        clean_data= super().clean()
        email=clean_data.get('email')
        try:
            Custom_user.objects.get(email=email)
        except Custom_user.DoesNotExist:
            raise forms.ValidationError(message.error_email_invalid)
        return clean_data
        
        
class Forget_Password(forms.Form):
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))
    
    def clean(self):
        cleaned_data= super().clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')
      
        if password != confirm_password:
            raise forms.ValidationError(message.error_password_matched)
        return cleaned_data
       
class Change_Password(forms.Form):
    old_password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Old Password'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'New Password'}))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))
    
    def clean(self):
        cleaned_data=super().clean()
        password=cleaned_data.get('password')
        old_password=cleaned_data.get('old_password')
        confirm_password=cleaned_data.get('confirm_password')
        if old_password == password:
            raise forms.ValidationError(message.error_old_pass_same)
        if password != confirm_password:
            raise forms.ValidationError(message.error_password_matched)
        return cleaned_data
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model=Custom_user
        fields=['username','first_name','middle_name','last_name','phone']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control '}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control '}),
            'phone': forms.TextInput(attrs={'class': 'form-control '}),
        }
        def clean(self):
            cleaned_data = super().clean()
            phone = cleaned_data.get('phone')
            if phone:
                if  len(str(phone)) < 9 or len(str(phone)) > 10:
                    raise forms.ValidationError("Invalid phone number.")
            return cleaned_data

        
class ProfileImageForm(forms.ModelForm):
    class Meta:
        model=Custom_user
        fields=['user_image']
        widgets={
            'user_image':forms.FileInput(attrs={'class':'form-control'})
        }
        
class ProductUploadForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['name','price','discounted_price','description','image']
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control','placeholder':'Title'}),
            'price':forms.TextInput(attrs={'class':'form-control','placeholder':'Price'}),
            'discounted_price':forms.TextInput(attrs={'class':'form-control','placeholder':'Discounted Price'}),
            'description':forms.Textarea(attrs={'class':'form-control','placeholder':'Description'}),
            'image':forms.FileInput(attrs={'class':'form-control'}),
            
        }
        
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['state', 'city', 'pincode', 'landmark', 'address', 'phone']
        widgets = {
            'state': forms.TextInput(attrs={'class': 'form-control input-custom','placeholder':'State'}),
            'city': forms.TextInput(attrs={'class': 'form-control input-custom','placeholder':'City'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control input-custom','placeholder':'Landmark'}),
            'address': forms.TextInput(attrs={'class': 'form-control input-custom','placeholder':'Address'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control input-custom','placeholder':'pincode'}),
            'phone': forms.TextInput(attrs={'class': 'form-control input-custom','placeholder':'phone'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        pincode = cleaned_data.get('pincode')
        if phone:
            if  len(str(phone)) < 9 or len(str(phone)) > 10:
                raise forms.ValidationError("Invalid phone number.")

        if pincode:
            if  len(str(pincode)) < 5 or len(str(pincode)) > 6:
                raise forms.ValidationError("Invalid pincode.")
        return cleaned_data
            
class CouponForm(forms.Form):
    coupon_card=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}))
    
