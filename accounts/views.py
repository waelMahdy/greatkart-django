from django.http import HttpResponse
from django.shortcuts import redirect, render

from accounts.form import RegisterationForm
from accounts.models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required

#verification email
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from greatkart import settings
#threading
import threading


class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)
    def run(self):
        self.email_message.send()    


# Create your views here.

def register(request):
    
    if request.method=='POST':
        form = RegisterationForm(data=request.POST)
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split('@',1)[0]
            user=Account.objects.create_user(username=username,first_name=first_name,last_name= last_name,email=email,password=password) 
            user.phone_number =phone_number 
            user.save()
            #USER ACTIVATION
            current_site=get_current_site(request)
            mail_subject='Activate Your Account'
            message=render_to_string('accounts/account_verification_mail.html',{
                "user":user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                })
            email_message=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER, [email])
            EmailThread(email_message).start()
            #messages.info(request,f"Account created for {username}! activate your account check out your  email.")
            return redirect('/accounts/login/?command=verification&email='+email)

            
    else:
        form=RegisterationForm()
    context={
      'form':form,
     }
    return render(request,'accounts/register.html',context)

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
        token_generator=default_token_generator.check_token(user,token)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and token_generator :
        user.is_active=True
        user.save()
        messages.success(request,"Your Account is activated.")
        
        return redirect("login")

    else:
        messages.error(request,"The activation link is expired or used.")
       
        return redirect("register",)


def login(request): 
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(username=email,password=password)    
        if user is not None:
           auth.login(request,user)
           messages.success(request,"You are now logged in.")
           return redirect('dashboard')
        else:
            messages.error(request,"Invalid Email or Password")
            return redirect('login')
    return render(request,'accounts/login.html') 
@login_required(login_url='login')  # u can't access this fun unless u r logged in
def logout(request):
    auth.logout(request)
    messages.info(request,"Logged out successfully")
    return redirect('login')
@login_required(login_url="login")
def dashboard(request):
    return  render(request,'accounts/dashboard.html')
def forgotPassword(request):
    if request.method=="POST":
        email=request.POST["email"]
        if Account.objects.filter(email = email).exists():
            user=Account.objects.get(email__iexact=email)
            current_site=get_current_site(request)

            # RESET PASSWOR EMAIL
            mail_subject='Reset your password'
            message=render_to_string('accounts/reset_password_email.html',{
                "user":user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                })
            email_message=EmailMessage(mail_subject,message,settings.EMAIL_HOST_USER, [email])
            EmailThread(email_message).start()
            messages.success(request,'Password reset email has been sent to your email address')
            return redirect('login')

        else:
            messages.error(request,"Email does not exist!")
            return redirect('forgotPassword')



    return render(request,'accounts/forgot-password.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
        token_generator=default_token_generator.check_token(user,token)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and token_generator :
        request.session['uid']=uid 
        messages.success(request,'Please reset your password')  
        return redirect('resetPassword') 
    else:
        messages.error(request,'Invalid link or Expired Link')
        return redirect('login')
def resetPassword(request):
    if request.method=='POST':
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user= Account._default_manager.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password has been updated')
            return redirect('login')
        else:
            messages.error(request,'Both Password Field Must be Same')
            return redirect('resetPassword')
    return render(request,'accounts/reset_password.html')    
   
