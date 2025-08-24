'''Ecommerce application on t-shirt'''
#pylint:disable=C0303
import random
import logging
import requests
from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Account import message,forms,models

# Create your views here.
def user_register_view(request):
    """This function allow user to create an account in this application
    after the email varification through otp"""
    if request.method =="POST":
        form=forms.RegisterForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data.get('email')
            referral_code=form.cleaned_data.get('referral_code')
            referred_by=None
            if referral_code:
                try:
                    referred_by=models.Custom_user.objects.get(referral_code=referral_code)
                except models.Custom_user.DoesNotExist:  # pylint:disable=no-member
                   form.add_error(None,message.error_referral_code)
            user = form.save(commit = False)
            user.referred_by=referred_by
            user.is_active = False
            user.set_password(form.cleaned_data['password'])
            user.save()
            subject=" Otp for Registration"
            otp=str(random.randint(100000,999999))
            msg=f"use this otp to open your account {otp}"
            sender=settings.EMAIL_HOST_USER
            models.Send_email_otp.objects.create(email=email,otp=otp)
            send_mail(subject,msg,sender,[email],fail_silently=True)
            messages.success(request, message.success_otp_send)
            return redirect("verify")
    else:
        form = forms.RegisterForm()
    return render(request, 'register.html',{'form':form})

def varification_view(request):
    """ this function is use for varify the email address  """
    if request.method=="POST":
        otp=request.POST.get('otp')
        try:
            otp_obj=models.Send_email_otp.objects.get(otp=otp)
            if otp and otp_obj:
                try:
                    user=models.Custom_user.objects.filter(email=otp_obj.email).first()
                    print(user)
                    user.is_active=True
                    user.save()
                    models.Send_email_otp.objects.get(otp=otp).delete()
                    messages.success(request,message.success_user_activate)
                    return redirect('login')
                except models.Custom_user.DoesNotExist: #pylint:disable=no-member
                    messages.warning(request,message.error_user_founded)
                    return redirect('otp')
            else:
                messages.success(request,message.error_otp_matched)
                return redirect('otp')
        except models.Send_email_otp.DoesNotExist: #pylint:disable=no-member
            messages.success(request,message.error_otp_matched)
            return redirect('otp')
    return render(request,'varify_otp.html')

def user_login_view(request):
    """ Allowing users to login through email . """
    request.session['user_session']=request.session.session_key
    if request.method =="POST":
        form=forms.LoginForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user=authenticate(email=email,password=password)
            if user is not None:
                login(request,user)
                messages.success(request,message.success_user_login)
                return redirect('home')
            form.add_error(None,message.error_user_founded)
    else:
        form=forms.LoginForm()
    return render(request,'login.html',{'form':form})

def forget_password_view(request):
    """ this function send the link on the email for forget password """
    if request.method=="POST":
        form=forms.EmailForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data.get('email')
            subject=" Password Froget link"
            otp=str(random.randint(100000,999999))
            msg=f"""use this link for change your password 
            http://127.0.0.1:8000/varify-forget-password/{otp}/
            """
            sender=settings.EMAIL_HOST_USER
            models.Send_email_otp.objects.create(email=email,otp=otp)
            send_mail(subject,msg,sender,[email],fail_silently=False)
            messages.success(request,message.success_link_send)
    else:
        form=forms.EmailForm()
    return render(request,"forget_password.html",{"form":form})

def forget_password(request,otp):
    """ this function varify the link and change the user password."""
    if request.method=="POST":
        form=forms.Forget_Password(request.POST)
        if form.is_valid():
            password=form.cleaned_data['password']
            try:
                otp_obj=models.Send_email_otp.objects.get(otp=otp)
            except models.Send_email_otp.DoesNotExist: #pylint:disable=no-member
                messages.warning(request,message.error_otp_matched)
                return redirect('forget')

            try:
                user=models.Custom_user.objects.filter(email=otp_obj.email).first()
                user.password=make_password(password)
                user.save()
                models.Send_email_otp.objects.get(otp=otp).delete()
                messages.success(request,message.success_password_changed)
                return redirect('login')
            except models.Custom_user.DoesNotExist: #pylint:disable=no-member
                messages.warning(request,message.error_user_founded)
                return redirect('forget_link',otp)
    else:
        form=forms.Forget_Password()
    return render(request,"verify_forget_link.html",{"form":form})

def logout_view(request):
    """ this function logout the user """
    logout(request)
    messages.warning(request,message.success_user_logout)
    return redirect("home")

@login_required(login_url='login')
def change_password(request):
    """ This function allows authenticated users to change their password. """
    if request.method == "POST":
        form = forms.Change_Password(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['password']
            user = request.user
            if check_password(old_password, user.password):
                user.password = make_password(new_password)
                user.save()
                update_session_auth_hash(request, user) 
                messages.success(request, message.success_password_changed)
                return redirect("Change_Password")
            form.add_error(None, message.error_old_password)
    else:
        form = forms.Change_Password() 
    return render(request, "change_password.html", {'form': form})

@login_required(login_url='login')
def user_profile(request):
    '''show the profile of the user'''
    try:
        coupon=models.Coupon.objects.filter(user=request.user)
    except models.Coupon.DoesNotExist:
        messages.error(request,message.error_invalid)
    try:
        reffered_users=models.Custom_user.objects.filter(referred_by=request.user)
    except models.Custom_user.DoesNotExist:
        message.error(request,message.error_referral_user)
    return render(request,'profile.html',{'coupon':coupon,"reffered_users":reffered_users})

@login_required(login_url='login')
def user_profile_update(request):
    """this function allow user to update their
    detail """
    user = request.user
    if request.method=="POST":
        form=forms.ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,message.success_profile_edit)
            return redirect('profile')
    else:
        form=forms.ProfileForm( instance=user)
    return render(request,'profile_edit.html',{'form':form})

@login_required(login_url='login')
def profile_image_change(request):
    """this function allow authenticated user to change their 
    profile picture"""
    user=request.user
    if request.method=="POST":
        form=forms.ProfileImageForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            print(form.cleaned_data.get('user_image'))
            form.save()
            messages.success(request,message.success_profile_image_change)
            return redirect('profile')
    else:
        form=forms.ProfileImageForm(instance=user)
    return render(request,'profileimage.html',{'form':form})
#product section start








# user authentication by google (two factor authentication)
def google_login(request):
    """allow user to login through gmail account"""
    print(request)
    scope="openid email profile"
    auth_url=(
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URL}"
        f"&scope={scope}"
        f"&access_type=offline"
        f"&prompt= consent"
    )
    return redirect(auth_url)

def google_callback(request):
    '''this function callback to the google for exchange the 
    client credencials with access token'''
    code=request.GET.get('code')
    if not code:
        messages.warning(request,message.error_invalid_code)
        return redirect('login')
    token_url= "https://oauth2.googleapis.com/token"
    data={
        'code':code,
        'client_id':settings.GOOGLE_CLIENT_ID,
        'client_secret':settings.CLIENT_SECRET,
        'redirect_uri':settings.GOOGLE_REDIRECT_URL,
        'grant_type': "authorization_code",
    }
    try:
        token_res=requests.post(token_url,data=data,timeout=1).json()
    except requests.exceptions.Timeout:
        logging.error('timeout raised.. recovering....')
    access_token=token_res.get('access_token')
    if not access_token:
        messages.warning(request,message.error_invalid_access)
        return redirect('login')
    user_infomation_url="https://www.googleapis.com/oauth2/v1/userinfo"
    try:
        user_info=requests.get(user_infomation_url,
                    headers={'Authorization': f'Bearer {access_token}'},timeout=1).json()
    except requests.exceptions.Timeout:
        logging.error('fatching data timeout. recovering....')
    email=user_info.get('email')
    name=user_info.get('name')
    if email:
        user,_=models.Custom_user.objects.get_or_create(email=email,defaults={'email':email,
                                                'first_name':name,'username':name})
        login(request,user)
    return redirect('home')
