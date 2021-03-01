from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class UserInfo(AbstractUser):
    phone = models.BigIntegerField(verbose_name='手机号', null=True, blank=True)
    avatar = models.FileField(verbose_name='头像',upload_to='avatar', default='avatar/default.png')
    create_time = models.DateField(verbose_name='创建时间', auto_now_add=True)

    blog = models.OneToOneField(to='Blog', null=True)

class Blog(models.Model):
    title = models.CharField(verbose_name='站点名称', max_length=32)
    desc = models.CharField(verbose_name='站点标题', max_length=255)
    theme = models.CharField(verbose_name='站点样式', max_length=255)

    def __str__(self):
        return self.title


class Article(models.Model):
    name = models.CharField(verbose_name='文章名', max_length=32)
    desc = models.CharField(verbose_name='文章摘要', max_length=255)
    content = models.TextField(verbose_name='文章内容')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    up_num = models.IntegerField(verbose_name='点赞数', default=0)
    down_num = models.IntegerField(verbose_name='点踩数', default=0)
    comment_num = models.IntegerField(verbose_name='评论数', default=0)

    blog = models.ForeignKey(to='Blog', null=True)
    category = models.ForeignKey(to='Category', null=True)
    tags = models.ManyToManyField(to='Tag',
                                 through='Article2Tag',
                                 through_fields=('article', 'tag'))

    def __str__(self):
        return self.name

class UpOrDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    is_up = models.BooleanField(verbose_name='点赞')

class Category(models.Model):
    name = models.CharField(verbose_name='分类名', max_length=32)
    blog = models.ForeignKey(to='Blog', null=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(verbose_name='标签名', max_length=32)
    blog = models.ForeignKey(to='Blog', null=True)

    def __str__(self):
        return self.name

class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')

class Comment(models.Model):
    name = models.CharField(verbose_name='评论名', max_length=32)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    parent = models.ForeignKey(to='self', null=True)
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')

    def __str__(self):
        return self.name




