from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
from django.db.models.functions import TruncMonth
import json
from django.db import transaction

from app01 import myform
from app01 import models


# Create your views here.
def register(request):
    regform = myform.RegForm()
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        regform = myform.RegForm(request.POST)
        if regform.is_valid():
            clean_data = regform.cleaned_data
            print(clean_data)
            clean_data.pop('confirm_password')
            file_obj = request.FILES.get('avatar')
            if file_obj:
                clean_data['avatar'] = file_obj
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = regform.errors
        print(back_dic)
        return JsonResponse(back_dic)
    return render(request, 'register.html', locals())


def get_random():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    with open(r'app01/static/img/aaa.png', 'rb') as f:
        data = f.read()
    print(data)
    img_obj = Image.new('RGB', (350, 30), get_random())
    io_obj = BytesIO()
    # img_obj = ImageDraw()
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype('app01/static/font/111.ttf', 30)
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        tmp = random.choice([random_upper, random_lower, random_int])
        img_draw.text((i * 60, -2), tmp, get_random(), img_font)
        code += tmp
    print(code)
    img_obj.save(io_obj, 'png')
    request.session['code'] = code

    return HttpResponse(io_obj.getvalue())


def login(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}
        username = request.POST.get('username')
        print(username)
        password = request.POST.get('password')
        code = request.POST.get('code')

        user_obj = auth.authenticate(username=username, password=password)
        print(user_obj)
        if user_obj:
            code_save = request.session.get('code')
            if code.upper() == code_save.upper():
                auth.login(request, user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '验证码错误'
                print(back_dic)
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '用户名或密码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html', locals())


def home(request):
    article_queryset = models.Article.objects.all()

    category_list = models.Category.objects.annotate(count_num=Count('pk')).values_list('name', 'count_num')
    tag_list = models.Tag.objects.annotate(count_num=Count('pk')).values_list('name', 'count_num')
    date_list = models.Article.objects.annotate(month=TruncMonth('create_time')).values('month').annotate(
        c=Count('pk')).values_list('month', 'c')

    return render(request, 'home.html', locals())


@login_required
def set_password(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            is_right = request.user.check_password(old_password)
            print(new_password)
            print(confirm_password)
            if is_right:
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['msg'] = '修改密码成功'
                else:
                    back_dic['code'] = 2000
                    back_dic['msg'] = '两次密码不一致'
            else:
                back_dic['code'] = 3000
                back_dic['msg'] = '原密码不正确'
        return JsonResponse(back_dic)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/login/')


def site(request, username, **kwargs):
    user_obj = models.UserInfo.objects.filter(username=username).first()

    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    article_lists = models.Article.objects.filter(blog=blog)

    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_lists = article_lists.filter(category=param)
        elif condition == 'tag':
            article_lists = article_lists.filter(tags=param)
        else:
            year, month = param.split('-')
            article_lists = article_lists.filter(create_time__year=year, create_time__month=month)
    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    article = models.Article.objects.filter(blog=blog, pk=article_id).first()
    comments_list = models.Comment.objects.filter(article=article)

    return render(request, 'article_detail.html', locals())


def up_or_down(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        print(back_dic)
        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            print('article_id')
            article = models.Article.objects.filter(pk=article_id).first()
            if not article.blog.userinfo == request.user:
                is_click = models.UpOrDown.objects.filter(user=request.user, article=article)
                print('is_click', is_click)
                if not is_click:
                    is_up = request.POST.get('is_up')
                    is_up = json.loads(is_up)
                    print('is_up', is_up)
                    models.UpOrDown.objects.create(user=request.user, article=article, is_up=is_up)
                    if is_up:
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                        back_dic['msg'] = '点踩成功'
                else:
                    back_dic['code'] = 2000
                    back_dic['msg'] = '已经点过'
            else:
                back_dic['code'] = 3000
                back_dic['msg'] = '自己不可以给自己点'
        else:
            back_dic['code'] = 2300
            back_dic['msg'] = '请先 <a href="/login/">登录</a>'

        return JsonResponse(back_dic)

def comments(request):
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg':''}
        if request.user.is_authenticated:
            print(request.POST)
            article_id = request.POST.get('article_id')
            print('article_id', article_id)
            article = models.Article.objects.filter(pk=article_id).first()
            parent_id = request.POST.get('parent')
            content = request.POST.get('content')
            with transaction.atomic():
                models.Article.objects.filter(pk=article_id).update(comment_num = F('comment_num') + 1)
                models.Comment.objects.create(content=content, parent_id=parent_id, user=request.user, article=article)
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = '请登录'
        return JsonResponse(back_dic)
