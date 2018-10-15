from django.db import models

# Create your models here.
class FootBall(models.Model):
	section = models.CharField(max_length=12)
	name = models.CharField(max_length=20)
	


class User(models.Model):
    GENDER_CHOICES = (
        ('男', '男'),
        ('女', '女'),
    )
    name = models.CharField(max_length=30, unique=True, verbose_name='姓 名')
    birthday = models.DateField(blank=True, null=True, verbose_name='生 日')
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES, verbose_name='性 别')
    account = models.IntegerField(default=0, verbose_name='工 号')
    age = models.IntegerField(default=18, verbose_name='年 龄')

from django.contrib import admin


class HostAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'age',
        'birthday',
        'gender',
        'account',
    ]
    search_fields = ('name',)


admin.site.register(User, HostAdmin)
admin.AdminSite.site_header = '运维系统管理后台'
admin.AdminSite.site_title = '运维系统'
