from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """自定义用户模型，扩展Django默认用户模型"""
    is_admin = models.BooleanField(default=False, verbose_name=_('是否管理员'))
    
    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-id']
    
    def __str__(self):
        return self.username
