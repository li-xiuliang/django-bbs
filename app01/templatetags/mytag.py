from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth

from app01 import models

register = template.Library()

@register.inclusion_tag('left_menu.html')
def get_side(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('pk')).values_list('name', 'count_num', 'pk')
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('pk')).values_list('name','count_num', 'pk')
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(c=Count('pk')).values_list('month', 'c')
    return locals()