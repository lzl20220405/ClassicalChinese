from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.html import conditional_escape
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, requires_csrf_token
from django.http import HttpResponse
from django.http import JsonResponse
from . import models
from riddle.models import Article
import hashlib
import datetime
import random

def hashcode(s, salt='classicalchinese'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()

def index(request, name):
    message = ""
    try:
        user = models.User.objects.get(name=name)
    except:
        user = None
    if not(user):
        limits = 1
        return render(request, 'login/index.html', {'user':user, "limits":limits})
    elif not(request.session.get('is_login', '')) or request.session.get('user_name','') != user.name:
        limits = 1
        return render(request, 'login/index.html', {'user':user, "limits":limits})
    else:
        limits = 0 
        try:
            if user.not_read_comment_articleid:
                user_message = user.not_read_comment_articleid.split(" ")
                user_message_article = []
                user_message_list = []

                for i in user_message:
                    user_message_article.append(Article.objects.get(id=i))

                for i in range(len(user_message)):
                    user_message_list.append(("A"+str(int(user_message[i])+100), user_message_article[i]))
                user_message_sum = len(user_message_list)
            else:
                user_message_list = None
                user_message_sum = 0
        except:
            user_message_list = None
            user_message_sum = 0

    if request.method == "POST":
        big_detail = request.POST.get('big_detail', '')
        if big_detail:
            user.big_detail = big_detail
            user.save() 

        small_description = conditional_escape(request.POST.get('small_description', ''))
        if small_description:
            user.small_description = small_description
            user.save()

        try:
            avatar = request.FILES['avatar']
        except:
            avatar = None
        if avatar:
            user.avatar = avatar
            user.save()

    return render(request, 'login/index.html', {'user':user, "limits":limits, "user_message_list": user_message_list, "user_message_sum": user_message_sum})


@csrf_exempt
def upload_image(request):
    import os

    if request.method == "POST":
        file_obj = request.FILES['file']
        file_name_suffix = file_obj.name.split(".")[-1]
        if file_name_suffix not in ["jpg", "png", "gif", "jpeg"]:
            return JsonResponse({"message": "?????????????????????"})

        upload_time = timezone.now()
        path = os.path.join(
            settings.MEDIA_ROOT,
            'tinymce',
            str(upload_time.year),
            str(upload_time.month),
            str(upload_time.day)
        )

        if not os.path.exists(path):
            os.makedirs(path)

        file_path = os.path.join(path, file_obj.name)

        file_url = f'{settings.MEDIA_URL}tinymce/{upload_time.year}/{upload_time.month}/{upload_time.day}/{file_obj.name}'
        if os.path.exists(file_path):
            return JsonResponse({'message': '???????????????', 'location': file_url})

        with open(file_path, 'wb+') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        return JsonResponse({'message': '??????????????????', 'location': file_url})
    return JsonResponse({'detail': '???????????????'})

def login(request):
    visitnum = int(conditional_escape(request.session.get('visit_num', 0)))
    if visitnum <= 3:
        request.session['visit_num'] = visitnum+1
    else:
        turn_visit_num = conditional_escape(request.POST.get('turn_visit_num',0))
        if turn_visit_num:
            request.session['visit_num'] = 1
    
    try:
        remember_signature = request.get_signed_cookie(key=hashcode('rrebmeeemrbmemre'), salt=hashcode(hashcode('stallats')), max_age=7*24*3600)
        if remember_signature == hashcode(hashcode('rremmmeemrbbeere')):
            href = conditional_escape(request.COOKIES.get('redirect_href',None))
            if href:
                return redirect(href)
            else:
                username = conditional_escape(request.get_signed_cookie(key=hashcode('username'), salt=hashcode(hashcode('username')), max_age=7*24*3600))
                return redirect('/login/index/%s/'%(username))
    except:
        pass
    
    if request.method == "POST":     
        username = conditional_escape(request.POST.get("username",''))
        password = conditional_escape(request.POST.get("password",''))
        message = '?????????????????????????????????????????????'
        if username.strip() and password:
            try:
                user = models.User.objects.get(name=username)
            except:
                try:
                    user = models.User.objects.get(email=username)
                except:
                    message = '??????????????????????????????'
                    return render(request, 'login/login.html', {'message':message})
            if user.password == hashcode(password):
                if not(user.has_confirmed):
                    message = '??????????????????????????????'
                    return render(request, 'login/login.html', {'message':message})
                request.session['is_login'] = 1
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name

                response = redirect('/login/index/%s/'%(user.name))
                remember = request.POST.get('remember', '')
                href = conditional_escape(request.COOKIES.get('redirect_href','')) 
                if remember:
                    response.set_signed_cookie(key=hashcode('rrebmeeemrbmemre'), value=hashcode(hashcode('rremmmeemrbbeere')), salt=hashcode(hashcode('stallats')), max_age=7*24*3600)
                    response.set_signed_cookie(key=hashcode('username'), value=hashcode(user.name), salt=hashcode(hashcode('username')), max_age=7*24*3600)
                if href:
                    return redirect(href)
                else:
                    return response
            else:
                message = '??????????????????????????????'
                return render(request, 'login/login.html', {'message':message})            
    else:
        message = ''
    
    return render(request, 'login/login.html', {'message':message})

def password_verification(password):
    message = ''
    if len(password) < 8:
        message = '??????????????????????????? 8 ??????'
        return message
    for chars in password:
        if '\u4e00' <= chars and chars <= '\u9fff':
            message = '???????????????????????????????????????'
            return message
    en = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    capital_en = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    number = ['1','2','3','4','5','6','7','8','9']
    flag = 0
    for letter in en:
        if letter in password:
            flag = flag + 1
            break
    for letter in capital_en:
        if letter in password:
            flag = flag + 1
            break
    for num in number:
        if num in password:
            flag = flag+1
            break
    if flag < 2:
        message = '???????????????????????????????????????????????????????????????????????????'
        return message
    return message

def email_verification(email):
    message = ''
    emaillist = list(email)
    if emaillist.count('@') != 1:
        message = '????????????????????????????????????'
        return message
    if emaillist.index('@') == 0 or emaillist.index('@') == len(emaillist)-1:
        message = '????????????????????????????????????'
        return message
    return message

def make_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hashcode(user.name, now)
    tag = hashcode(user.name, "tag")
    get_str = ''
    for x in range(6):
        num = random.randint(0,len(code)-1)
        get_str = get_str + code[num]
    models.ConfirmString.objects.create(code=get_str, user=user, tag=tag)
    return (get_str,tag)

def send_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = "?????? www.ClassicalChinese.com ?????????????????????"
    text_content = '''???????????? www.ClassicalChinese.com, ??????????????????????????????????????????????????????????????????
                    ?????????????????????????????????????????????????????????????????? HTML ?????????????????????????????????????????????????????????'''
    html_content = '''
                    <p>????????????<a href="http://{}/Chinese/article/1/" target=_blank> www.ClassicalChinese.com </a>???
                    ????????????????????????????????????????????????????????????????????????????????????????????????</p>
                    <p>?????????????????????</p><h1> {} </h1>
                    <p>???????????????????????? {} ??????</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def register(request):
    if request.method == 'POST':
        username = conditional_escape(request.POST.get('username',''))
        password = conditional_escape(request.POST.get('password',''))
        password_repeat = conditional_escape(request.POST.get('password_again',''))
        email = conditional_escape(request.POST.get('email',''))
        message = "?????????????????????????????????????????????"
        if username.strip() and password and password_repeat and email:
            if password != password_repeat:
                message = "??????????????????????????????"
                return render(request, 'login/register.html', {'message':message})
            else:
                user_list = models.User.objects.filter(name=username)
                if user_list:
                    message = "???????????????????????????"
                    return render(request, 'login/register.html', {'message':message})
                email_list = models.User.objects.filter(email=email)
                if email_list:
                    message = "??????????????????????????????"
                    return render(request, 'login/register.html', {'message':message})
                if password_verification(password):
                    message = password_verification(password)
                    return render(request, 'login/register.html', {'message':message})
                if email_verification(email):
                    message = email_verification(email)
                    return render(request, 'login/register.html', {'message':message})                   
                
                new_user = models.User()
                new_user.name = username
                new_user.password = hashcode(password_repeat)
                new_user.email = email
                new_user.save()

                code,tag = make_confirm_string(new_user)
                send_email(email, code)
                request.session['tag'] = tag

                return redirect('/login/confirm/')
        else:
            return render(request, 'login/register.html', {'message':message})
    return render(request, 'login/register.html')

def user_confirm(request):
    message = ''
    if request.method == "POST":
        tag = conditional_escape(request.session.get('tag', ''))
        email_password = conditional_escape(request.POST.get('email_password',''))
        try:
            confirm = models.ConfirmString.objects.get(tag=tag)
        except:
            return render(request, 'login/confirm.html', {'message':message})
        
        c_time = confirm.c_time
        now = datetime.datetime.now()
        if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
            confirm.user.delete()
            del request.session['tag']
            message = '??????????????????????????????????????????!'
            return render(request, 'login/confirm.html', {'message':message})
        if email_password == confirm.code:
            confirm.user.has_confirmed = True
            confirm.user.save()
            confirm.delete()
            del request.session['tag']
            return redirect('/login/login/')
        else:
            message = '???????????????????????????'
            return render(request, 'login/confirm.html', {'message':message})
    return render(request, 'login/confirm.html', {'message':message})

def logout(request):
    try:
        response = redirect('/login/login/')
        response.delete_cookie(key=hashcode('rrebmeeemrbmemre'))
        request.session.flush()
        redirect_href = conditional_escape(request.COOKIES.get('redirect_href',''))
        if redirect_href:
            return redirect(redirect_href)
        else:
            return response
    except:
        request.session.flush()
        redirect_href = conditional_escape(request.COOKIES.get('redirect_href',''))
        if redirect_href:
            return redirect(redirect_href)
        else:
            return redirect('/login/login/')

def make_reset_password_confirm_string(user):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hashcode(user.name, now)
    repeat_reset_list = models.ResetString.objects.filter(user=user)
    if repeat_reset_list:
        for repeat_reset in repeat_reset_list:
            repeat_reset.delete()

    models.ResetString.objects.create(code=code, user=user)
    return code

def send_reset_password_email(email, code):
    from django.core.mail import EmailMultiAlternatives
    subject = "?????? www.ClassicalChinese.com ?????????????????????"
    text_content = '''???????????? www.ClassicalChinese.com, ??????????????????????????????????????????????????????????????????
                    ?????????????????????????????????????????????????????????????????? HTML ?????????????????????????????????????????????????????????'''
    html_content = '''
                    <p>????????????<a href="http://{}/Chinese/article/1/" target=_blank> www.ClassicalChinese.com </a>???
                    ????????????????????????????????????????????????????????????????????????????????????????????????</p>
                    <h2>?????????????????????????????????<a href="http://{}/login/resetpassword/?code={}">??????????????????</a></h2>
                    <p>????????????????????? {} ??????</p>
                    '''.format('127.0.0.1:8000', '127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def reset(request):
    message = ''
    if request.method == 'POST':
        email = conditional_escape(request.POST.get('email', ''))
        message = '?????????????????????????????????????????????'
        if email:
            if email_verification(email):
                message = email_verification(email)
                return render(request, 'login/reset.html', {'message':message})
            try:
                user = models.User.objects.get(email=email)
            except:
                message = '???????????????????????????????????????'
                return render(request, 'login/reset.html', {'message':message})
            
            code = make_reset_password_confirm_string(user)
            send_reset_password_email(email, code)

            message = '???????????????????????????????????????????????????????????????????????????'
            return render(request, 'login/reset.html', {'message':message})

        return render(request, 'login/reset.html', {'message':message})
    return render(request, 'login/reset.html', {'message':message})

def resetpassword(request):
    code = conditional_escape(request.GET.get('code', ''))
    message = ''
    if request.method == 'POST':
        message = '?????????????????????????????????????????????'
        try:
            confirm = models.ResetString.objects.get(code=code)
        except:
            message = '??????????????????????????????'
            return render(request, 'login/resetpassword.html', {'message':message, 'code':''})

        c_time = confirm.c_time
        user = confirm.user
        password = conditional_escape(request.POST.get('password', ''))
        password_repeat = conditional_escape(request.POST.get('password_repeat', ''))
        now = datetime.datetime.now()
        if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
            message = '??????????????????????????????????????????'
            confirm.delete()
            return render(request, 'login/resetpassword.html', {'message':message, 'code':code})
        
        if password and password_repeat:
            if password != password_repeat:
                message = '??????????????????????????????'
                return render(request, 'login/resetpassword.html', {'message':message, 'code':code})
            if password_verification(password):
                message = password_verification(password)
                return render(request, 'login/resetpassword.html', {'message':message, 'code':code})

            user.password = hashcode(password_repeat)
            user.save()
            confirm.delete()

            response = redirect('/login/login/')
            try:
                response.delete_cookie(key=hashcode('rrebmeeemrbmemre'))
                request.session.flush()
            except:
                request.session.flush()
            return response

        return render(request, 'login/resetpassword.html', {'message':message, 'code':code}) 
    return render(request, 'login/resetpassword.html', {'message':message, 'code':code}) 

@requires_csrf_token
def page_not_found(request, exception):
    return render(request, 'login/404.html')