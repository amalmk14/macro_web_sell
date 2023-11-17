
from django.core.exceptions import ObjectDoesNotExist
import re
from django.shortcuts import render, redirect,HttpResponseRedirect
from django.contrib import messages,auth
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import *
from django.core.mail import send_mail
from django.conf import settings
import random
from django.utils import timezone
from datetime import datetime,timedelta

# Create your views here.

# def signup(request):
#     if request.method == 'POST':
#         username=request.POST['username']
#         email=request.POST['email']
#         password1=request.POST['password1']
#         password2=request.POST['password2']
#
#         password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$')
#
#         if not password_pattern.match(password1):
#             messages.info(request,
#                           'Password must contain at least one uppercase letter, one lowercase letter, one number, one special character, and be at least 8 characters long.')
#             return redirect('login:signup')
#
#         if password1 == password2:
#             if Profile.objects.filter(name=username).exists():
#                 messages.info(request,'Username Already Taken')
#                 return redirect('login:signup')
#             elif Profile.objects.filter(email=email).exists():
#                 messages.info(request,'Email Already Taken')
#                 return redirect('login:signup')
#             else:
#                 user = Profile(name=username,password=password1,email=email)
#                 user.save();
#         else:
#             messages.info(request,'Password not matched')
#             return redirect('login:signup')
#         return redirect('login:signin')
#     return render(request,"signup.html")

def logout(request):
    request.session['is_logged_in'] = False
    return render(request,"home.html")


# def signin(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         users = Profile.objects.filter(name=username, password=password)
#         # if not username or not password:
#         #     error_message = "Both username and password are required."
#         #     return render(request, 'signin.html', {'error_message': error_message})
#
#         if users.exists():
#             request.session['username'] = username
#             request.session['is_logged_in'] = True
#
#             return HttpResponseRedirect(reverse('mainapp:home') + f'?username={username}')
#             # return redirect('mainapp:home')
#             # return render(request, 'home.html', {})  # Redirect to 'userhome' after successful login
#         else:
#             messages.info(request,"Invalid username or password.")
#             return redirect("login:signin")
#     return render(request, 'signin.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        users = Profile.objects.filter(name=username, password=password)
        if users.exists():
            user = users.first()
            if user.is_verified:
                request.session['username'] = username
                request.session['is_logged_in'] = True
                return HttpResponseRedirect(reverse('mainapp:home') + f'?username={username}')
            else:
                messages.info(request, "Account not verified. Please check your email for verification instructions.")
                return redirect("login:signin")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login:signin")
    return render(request, 'signin.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        # if not email:
        #     messages.error(request, "Please enter your email.")
        #     return redirect('login:signin')

        if Profile.objects.filter(email=email).exists():
            OTP = random.randint(100000, 999999)
            timestamp = datetime.now()
            print(OTP)
            user = Profile.objects.get(email=email)
            subject = 'OTP for Forgott Password'
            message = f'Hi {user.name},Your Forgott Password OTP is  {OTP}  Valid For 5 Minit. Do Not Share. if you not requested for otp then ignore it'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = {user.email}
            request.session['user_email'] = email
            send_mail(subject,message,email_from,recipient_list)
            messages.info(request, f"We will send an OTP to the email  '{email}'")
            if Storedotps.objects.filter(email_id=request.session.get('user_email', None)).exists():
                Storedotps.objects.filter(email_id=request.session.get('user_email', None)).update(otp=OTP,valid_from=timezone.now(),otp_active=True)

            else:
                otp_data = Storedotps.objects.create(email_id=user.email, otp=OTP, valid_from=timezone.now())
                otp_data.save()

            return render(request, "forgot_password.html", {'email': email})
        else:
            messages.error(request, "Email is not registered on our site.")
            return redirect('login:signin')

    return render(request, "forgot_password.html")


# otp experation
def is_otp_expired(otp_data):
    # expiration_duration = datetime.timedelta(minutes=5)
    # now = timezone.now()
    # print("expire checking...")
    # return now - otp_data.valid_from > expiration_duration
    expiration_duration = timedelta(minutes=5)
    now = timezone.now()
    return now - otp_data.valid_from > expiration_duration


def handle_otp(request):
    if request.method == 'POST':
        otp_valid = request.POST['otp']
        user_email = request.session.get('user_email', None)
        print(user_email)

        try:
            otp_data = Storedotps.objects.get(email_id=user_email, otp_active=True)
        except Storedotps.DoesNotExist:
            messages.error(request, "Invalid OTP or OTP has expired.")
            return redirect('login:forgot_password')

        if otp_valid == str(otp_data.otp):
            if not is_otp_expired(otp_data):
                otp_data.is_active = False
                print("otp valid")
                otp_data.save()

                return redirect('login:password_update')  # Redirect to a success page
            else:
                messages.error(request, "otp is expired")
                otp_data.is_active = False
                print("otp is expired")
                return redirect('login:forgot_password')
        else:
            messages.error(request, "Invalid OTP.")
            return redirect('login:forgot_password')
    return render(request, "forgot_password.html")


def password_update(request):
    if request.method == 'POST':
        password = request.POST['password']
        password1 = request.POST['password1']
        if password == password1:
            try:
                Profile.objects.filter(email=request.session.get('user_email')).update(password=password)
                messages.info(request,'Password Changed Successfully')
                return redirect('login:signin')
            except:
                messages.info(request, "something Went wrong.....")
                return render(request, "somethingwrong.html")
    return render(request, "password_change.html")

def bill(request):
    return render(request,"profile/bill.html")

def profile_page(request):
    # name = request.session['username']
    name = request.session.get('username')
    if name:
        profile_object = Profile.objects.get(name=name)
        email = profile_object.email
        phone = profile_object.phone
        country = profile_object.country

    if request.method == 'POST':
        phone = request.POST['phone']
        country = request.POST['country']
        profile_object.phone = phone
        profile_object.country = country
        profile_object.save()
        return redirect('login:profile_page')
    return render(request,'profile/profile.html',{'name':name,'email':email,'phone':phone,'country':country})

def profile_password(request):
    name = request.session.get('username')
    if name:
        profile_object = Profile.objects.get(name=name)

    if request.method == 'POST':
        password = request.POST['password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        if new_password1 == new_password2:
            if profile_object.password == password:  # Check if old password matches
                profile_object.password = new_password1  # Assign the new password
                profile_object.save()  # Save the changes to the database
                messages.info(request, 'Password changed successfully')
                return redirect('login:profile_page')
            else:
                messages.info(request, 'Old password not matched')
                return redirect('login:profile')
        else:
            messages.info(request, 'New Password and Confirm Password are not matched')
            return redirect('login:profile_page')


def profile_forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        OTP = random.randint(100000, 999999)
        timestamp = datetime.now()
        print(OTP)
        user = Profile.objects.get(email=email)
        subject = 'OTP for Forgott Password'
        message = f'Hi {user.name},Your Forgott Password OTP is  {OTP}  Valid For 5 Minit. Do Not Share. if you not requested for otp then ignore it'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = {user.email}
        request.session['user_email'] = email
        send_mail(subject,message,email_from,recipient_list)
        messages.info(request, f"We will send an OTP to the email  '{email}'")
        if Storedotps.objects.filter(email_id=request.session.get('user_email', None)).exists():
            Storedotps.objects.filter(email_id=request.session.get('user_email', None)).update(otp=OTP,valid_from=timezone.now(),otp_active=True)

        else:
            otp_data = Storedotps.objects.create(email_id=user.email, otp=OTP, valid_from=timezone.now())
            otp_data.save()

    return render(request, "profile/profile_forgot_password.html", {'email': email})

def profile_handle_otp(request):
    if request.method == 'POST':
        otp_valid = request.POST['otp']
        user_email = request.session.get('user_email', None)
        print(user_email)

        try:
            otp_data = Storedotps.objects.get(email_id=user_email, otp_active=True)
        except Storedotps.DoesNotExist:
            messages.error(request, "Invalid OTP or OTP has expired.")
            return redirect('login:profile_forgot_password')

        if otp_valid == str(otp_data.otp):
            if not is_otp_expired(otp_data):
                otp_data.is_active = False
                print("otp valid")
                otp_data.save()

                return redirect('login:profile_password_update')  # Redirect to a success page
            else:
                messages.error(request, "otp is expired")
                otp_data.is_active = False
                print("otp is expired")
                return redirect('login:profile_forgot_password')
        else:
            messages.error(request, "Invalid OTP.")
            return redirect('login:profile_forgot_password')
    return render(request, "profile/profile_forgot_password.html")

def profile_password_update(request):
    if request.method == 'POST':
        password = request.POST['password']
        password1 = request.POST['password1']
        if password == password1:
            try:
                Profile.objects.filter(email=request.session.get('user_email')).update(password=password)
                messages.info(request,'Password Changed Successfully')
                return redirect('login:profile_page')
            except:
                messages.info(request, "something Went wrong.....")
                return render(request, "somethingwrong.html")
    return render(request, "profile/profile_password_change.html")



from .utils import generate_token

# ... (your view code)

# Example usage in the signup view:
token = generate_token()



# from .utils import generate_token

# def signup(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password1 = request.POST['password1']
#         password2 = request.POST['password2']
#
#         password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$')
#
#         if not password_pattern.match(password1):
#             messages.info(request, 'Password must contain at least one uppercase letter, one lowercase letter, one number, one special character, and be at least 8 characters long.')
#             return redirect('login:signup')
#
#         if password1 == password2:
#             if Profile.objects.filter(name=username).exists():
#                 messages.info(request, 'Username Already Taken')
#                 return redirect('login:signup')
#             elif Profile.objects.filter(email=email).exists():
#                 messages.info(request, 'Email Already Taken')
#                 return redirect('login:signup')
#             else:
#                 # Create the user
#                 user = Profile(name=username, password=password1, email=email)
#                 user.save()
#
#                 # Generate and save the email verification token
#                 token = generate_token()
#                 verification_token = EmailVerificationToken(user=user, token=token)
#                 verification_token.save()
#
#                 # Send email with the verification link
#                 verification_link = reverse('login:verify_email', kwargs={'token': token})
#                 verification_url = request.build_absolute_uri(verification_link)
#
#                 subject = 'Verify Your Email'
#                 message = f'Hi {user.name}, please click the following link to verify your email: {verification_url}'
#                 email_from = settings.EMAIL_HOST_USER
#                 recipient_list = [user.email]
#
#                 send_mail(subject, message, email_from, recipient_list)
#
#                 messages.info(request, 'Account created successfully. Please check your email for verification.')
#                 return redirect('login:signin')
#         else:
#             messages.info(request, 'Password not matched')
#             return redirect('login:signup')
#
#     return render(request, "signup.html")


# login/views.py

# from django.db import transaction
#
# # ...
#
# @transaction.atomic
# def signup(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password1 = request.POST['password1']
#         password2 = request.POST['password2']
#
#         password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$')
#
#         if not password_pattern.match(password1):
#             messages.info(request, 'Password must contain at least one uppercase letter, one lowercase letter, one number, one special character, and be at least 8 characters long.')
#             return redirect('login:signup')
#
#         with transaction.atomic():
#             existing_user_username = Profile.objects.filter(name=username).first()
#             existing_user_email = Profile.objects.filter(email=email).first()
#
#             if existing_user_username:
#                 if existing_user_username.is_verified:
#                     messages.info(request, 'Username Already Taken')
#                     return redirect('login:signup')
#                 else:
#                     # Delete the existing user's data
#                     existing_user_username.delete()
#
#             if existing_user_email:
#                 if existing_user_email.is_verified:
#                     messages.info(request, 'Email Already Taken')
#                     return redirect('login:signup')
#                 else:
#                     # Delete the existing user's data
#                     existing_user_email.delete()
#
#             # Generate and save the email verification token
#             token = generate_token()
#             verification_token = EmailVerificationToken(token=token)
#
#             # Create the user with is_verified set to False
#             user = Profile(name=username, password=password1, email=email, is_verified=False)
#             user.save()
#
#             # Link the verification token to the user
#             verification_token.user = user  # Make sure to set the user
#             verification_token.save()
#
#             # Send email with the verification link
#             verification_link = reverse('login:verify_email', kwargs={'token': token})
#             verification_url = request.build_absolute_uri(verification_link)
#
#             # ... (rest of your email sending code)
#
#             messages.info(request, 'Account created successfully. Please check your email for verification.')
#             return redirect('login:signin')
#
#     return render(request, "signup.html")


# login/views.py
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse

# ...

@transaction.atomic
def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$')

        if not password_pattern.match(password1):
            messages.info(request, 'Password must contain at least one uppercase letter, one lowercase letter, one number, one special character, and be at least 8 characters long.')
            return redirect('login:signup')

        with transaction.atomic():
            existing_user_username = Profile.objects.filter(name=username).first()
            existing_user_email = Profile.objects.filter(email=email).first()

            if existing_user_username:
                if existing_user_username.is_verified:
                    messages.info(request, 'Username Already Taken')
                    return redirect('login:signup')
                else:
                    # Delete the existing user's data
                    existing_user_username.delete()

            if existing_user_email:
                if existing_user_email.is_verified:
                    messages.info(request, 'Email Already Taken')
                    return redirect('login:signup')
                else:
                    # Delete the existing user's data
                    existing_user_email.delete()

            # Generate and save the email verification token
            token = generate_token()
            verification_token = EmailVerificationToken(token=token)

            # Create the user with is_verified set to False
            user = Profile(name=username, password=password1, email=email, is_verified=False)
            user.save()

            # Link the verification token to the user
            verification_token.user = user  # Make sure to set the user
            verification_token.save()

            # Construct the verification link
            verification_link = reverse('login:verify_email', kwargs={'token': token})
            verification_url = request.build_absolute_uri(verification_link)

            # Send email with the verification link
            subject = 'Verify Your Email'
            message = render_to_string('email/verification_email.txt', {'user': user, 'verification_url': verification_url})
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            send_mail(subject, message, email_from, recipient_list)

            messages.info(request, 'Account created successfully. Please check your email for verification.')
            return redirect('login:signin')

    return render(request, "signup.html")



from django.shortcuts import render, redirect
from django.http import Http404
from .models import EmailVerificationToken

def verify_email(request, token):
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        raise Http404("Token not found")

    # Mark the user as verified
    verification_token.user.is_verified = True
    verification_token.user.save()

    # Delete the verification token
    verification_token.delete()

    return render(request, "verification_success.html")
