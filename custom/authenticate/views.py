import json
import os
import random
import string
from datetime import timedelta

import requests
from cryptography.fernet import Fernet
import custom.settings
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timezone import datetime

from custom import settings
from .models import Session, Account, AccountDetail

# Create your views here.
cipher_suite = Fernet(settings.ENCRYPT_KEY3)
c_suite=Fernet(settings.ENCRYPT_KEY4)
c_suite2=Fernet(settings.ENCRYPT_KEY)
def home(request):
    return render(request,'home.html',locals())

def signup(request):
    if not request.session.session_key:
        request.session.save()
    s=request.session._session_key
    k=findkey(s)
    if k is not None:
        if Account.objects.filter(pk=k).exists():
            return redirect('authenticate:user')
    username=request.POST.get("user")
    if username is not None:
        clientKey=request.POST['g-recaptcha-response']
        secretKey=os.getenv('secretKey')
        captchadata={
        'secret':secretKey,
        'response':clientKey
        }
        r=requests.post('https://www.google.com/recaptcha/api/siteverify',data=captchadata)
        response=json.loads(r.text)
        verify=response['success']
        if verify==False:
            return render(request,'signup.html',{'error_message67':"error"})
        password=request.POST.get('pass')
        f_name=request.POST.get('fname')
        l_name=request.POST.get('lname')
        email=request.POST.get('email')
        if Account.objects.filter(Username=username).exists():
            return render(request,'signup.html',{'u':username,'error':'username already exists'})
        if Account.objects.filter(Emailaddress=email).exists():
            return render(request,'signup.html',{'e':email,'error_':'Email already exists'})
        Account.objects.create(First_name=f_name,Last_name=l_name,Username=username,Emailaddress=email,Password=make_password(password))
        return redirect('authenticate:login')
    return render(request,'signup.html',locals())

def login(request):
    if not request.session.session_key:
        request.session.save()
    s=request.session._session_key
    k=findkey(s)
    if k is not None:
        if Account.objects.filter(pk=k).exists():
            return redirect('authenticate:user')
            #return redirect('accounting:userhome')
    username=request.POST.get("userid")
    passwordgiven=request.POST.get("psw")
    if username is not None:

        clientKey=request.POST['g-recaptcha-response']
        secretKey=os.getenv('secretKey')
        captchadata={
        'secret':secretKey,
        'response':clientKey
        }
        r=requests.post('https://www.google.com/recaptcha/api/siteverify',data=captchadata)
        response=json.loads(r.text)
        verify=response['success']
        if verify==False:
            return render(request,'login.html',{'error_message67':"error"})
        try:
            account=Account.objects.get(Username=username)
            k=check_password(passwordgiven,account.Password)
            if k is True:
                ac_id=str(account.id)
                create_session(s,ac_id)
                return redirect('authenticate:user')
            else:
                return render(request,'login.html',{'error_message':'wrong password'})
        except:
            return render(request,'login.html',{'u_message':'wrong username or password'})
    else:
        return render(request,'login.html',locals())

def findkey(s):
    if Session.objects.filter(session_key=s).exists():
        session_get=Session.objects.get(session_key=s)
        email_id=session_get.session_id
        decoded=email_id.encode()
        decoded_text = cipher_suite.decrypt(decoded)
        e=decoded_text.decode()
        return e
    else:
        return None


def create_session(s,ac_id):
    encode=ac_id.encode()
    encoded_text = cipher_suite.encrypt(b"%s"%(encode))
    encoded_email=encoded_text.decode("utf-8")
    if Session.objects.filter(session_key=s).exists():
        return None
    else:
        Session.objects.create(user_id=ac_id,session_id=encoded_email,session_key=s)
def userhome(request):
    if not request.session.session_key:
        request.session.save()
    s=request.session._session_key
    k=findkey(s)
    if k is None:
        return redirect('authenticate:login')
    a=Account.objects.get(pk=k)
    ac=AccountDetail.objects.get(account=k)
    para={'name':a.First_name,'username':a.Username,'email':a.Emailaddress,'c':a.created_on,'t':ac.verify_account,'id':k}
    return render(request,'user.html',para)

def verifymail(request):
    t=request.POST.get('type')
    if t=="start":
        if not request.session.session_key:
            request.session.save()
        s=request.session._session_key
        k=findkey(s)
        if k is None:
            return redirect('authenticate:login')
        a=Account.objects.get(pk=k)
        ac=AccountDetail.objects.get(account=k)
        if ac.verify_account==True:
                data={
                    'done':'given'
                }
                return JsonResponse(data)
        ids=str(a.id)
        encoded_id=ids.encode()
        encoded_id_text=c_suite.encrypt(b"%s"%(encoded_id))
        encoded_id=encoded_id_text.decode("utf-8")
        ac_detail=AccountDetail.objects.filter(account=ids)
        res = ''.join(random.choices(string.ascii_uppercase +
                            string.digits, k = 9))
        res_make=make_password(res)
        ac_detail.update(verify_time=datetime.now(),verify=res_make)
        current_site=get_current_site(request)
        message=render_to_string('account_activation_eamil.html',{
                'user':a,
                'domian':current_site.domain,
                'name':current_site.name,
                'uid':encoded_id,
                'token':account_activation_token.make_token(a),
                'res':res,
            })
        email=a.Emailaddress
        subject="Your activation link for connect"
        send_mail(subject,message,EMAIL_HOST_USER,[email], fail_silently = False)
        #print(message)
        data={
                    'is_taken':'Log in'
                }
        return JsonResponse(data)
    else:
        return HttpResponse("Invalid Link")
def activate(request, uidb64, token,res):
    try:
        decoded=uidb64.encode()
        decoded_text = c_suite.decrypt(decoded)
        e=decoded_text.decode()
        a=Account.objects.get(pk=e)
        user=a
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    from custom.authenticate.tokens import account_activation_token
    if user is not None and account_activation_token.check_token(a, token):
        user_id=user.id
        account=AccountDetail.objects.filter(account=user_id)
        acc=AccountDetail.objects.get(account=user_id)
        if acc.verify_account==True:
            return HttpResponse("%s\nYour account already verified<br>")
        check=check_password(res,acc.verify)
        t=acc.verify_time
        tim=datetime.now(timezone.utc)
        times=tim+timedelta(hours=5.5)
        diff=times-t
        minutes=divmod(diff.seconds,60)
        m=minutes[0]
        if m>30:
            return HttpResponse("Activation link is invalid<br>")
        if check==True:
            account.update(verify_account=True,verify=None)
            return HttpResponse("Your email verified now<br>")
        else:
            return HttpResponse("Your link is invalid<br>")
    else:
        return HttpResponse('Activation link is invalid!')



def logout(request):
    name=request.POST.get('name')
    if name=="start":
        if not request.session.session_key:
                request.session.save()
        s=request.session._session_key
        if Session.objects.filter(session_key=s).exists():
            s=Session.objects.filter(session_key=s)
            s.delete()
            data={
                'is_done':'ok'
            }
            return JsonResponse(data)
    else:
        return HttpResponse("Invalid Link")

def changepassword(request):
    if not request.session.session_key:
            request.session.save()
    s=request.session._session_key
    k=findkey(s)
    if k is None:
        return redirect('authenticate:login')
    a=Account.objects.get(pk=k)
    ac=AccountDetail.objects.get(account=k)
    para={'name':a.First_name,'username':a.Username,'email':a.Emailaddress,'c':a.created_on,'t':ac.verify_account,'id':k}
    return render(request,'change.html',para)


def final(request):
    if request.method=="POST":
        i=request.POST.get("id")
        a=Account.objects.get(pk=i)
        ac=AccountDetail.objects.get(account=i)
        old=request.POST.get('opass')
        passw=request.POST.get('pass')
        k=check_password(old,a.Password)
        if k is True:
            para={'name':a.First_name,'username':a.Username,'email':a.Emailaddress,'c':a.created_on,'t':ac.verify_account,'id':i}
            acco=Account.objects.filter(pk=i)
            acco.update(Password=make_password(passw))
            return redirect('authenticate:user')
        else:
            para={'name':a.First_name,'username':a.Username,'email':a.Emailaddress,'c':a.created_on,'t':ac.verify_account,'id':i,'error':'error'}

        return render(request,'change.html',para)
    else:
        return redirect('authenticate:chnage')

def forgot(request):
    return render(request,'forgot.html',locals())
def resetpassword(request):
    k=request.POST.get('type')
    if k=='start':
        email=request.POST.get('email')
        if Account.objects.filter(Emailaddress=email).exists():
            account=Account.objects.get(Emailaddress=email)
            ids=str(account.id)
            encoded_id=ids.encode()
            encoded_id_text=c_suite2.encrypt(b"%s"%(encoded_id))
            encoded_id=encoded_id_text.decode("utf-8")
            ac_detail=AccountDetail.objects.filter(account=ids)
            res = ''.join(random.choices(string.ascii_uppercase +
                            string.digits, k = 10))
            res_make=make_password(res)
            ac_detail.update(reset_time=datetime.now(),reset=res_make)
            current_site=get_current_site(request)
            message=render_to_string('password_reset_email.html',{
                    'user':account,
                    'domian':current_site.domain,
                    'uid':encoded_id,
                    'name':current_site.name,
                    'token':password_reset_token.make_token(account),
                    'res':res,
            })
            email=account.Emailaddress
            subject="Reset Password link"
            send_mail(subject,message,EMAIL_HOST_USER,[email], fail_silently = False)
            print(message)
            data={
                    'is_taken':'Log in'
                }
            return JsonResponse(data)
        else:
            data={
                'is_created':"hello"
            }
            return JsonResponse(data)
    else:
        return HttpResponse('This error comes because you call the url before the submit the passsword')

def createnewpassword(request,uidb64, token,res):
    try:
        decoded=uidb64.encode()
        decoded_text = c_suite2.decrypt(decoded)
        e=decoded_text.decode()
        account=Account.objects.get(pk=e)
        user=account
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and password_reset_token.check_token(account, token):
        user_id=user.id
        account=AccountDetail.objects.filter(account=user_id)
        acc=AccountDetail.objects.get(account=user_id)
        if acc.reset is None:
            return redirect('authenticate:login')
        check=check_password(res,acc.reset)
        t=acc.reset_time
        tim=datetime.now(timezone.utc)
        times=tim+timedelta(hours=5.5)
        diff=times-t
        minutes=divmod(diff.seconds,60)
        m=minutes[0]
        if m>30:
            return HttpResponse("link is invalid")
        if check==True:
            return render(request,'password.html',{'user_id':user_id,'res':res})
        else:
            return HttpResponse("Your link is invalid")
    else:
        return HttpResponse('Activation link is invalid!')

def changeit(request):
    t=request.POST.get('type')
    if t=='start':
        res=request.POST.get('res')
        id=request.POST.get('id')
        password=request.POST.get('pass')
        acc=AccountDetail.objects.filter(account=id)
        ac=AccountDetail.objects.get(account=id)
        if ac.reset is None:
            return redirect('authenticate:login')
        check=check_password(res,ac.reset)
        if check==True:
            password_hash=make_password(password)
            a=Account.objects.filter(pk=id)
            a.update(Password=password_hash)
            acc.update(reset=None)
            if Session.objects.filter(user_id=id).exists():
                s=Session.objects.filter(user_id=id)
                s.delete()

            return render(request,'password.html',{'e':'e'})
        else:
            return HttpResponse('Invalid Link')
    else:
        return HttpResponse('Something wrong..........')
#s=os.environ.get('DB_PASS')
#print(s,2)

#print(os.environ['db_pass'])
#os.getenv()
