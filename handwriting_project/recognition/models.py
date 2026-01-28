from django.db import models
from core.models import User

class RecognitionRecord(models.Model):
    """
    识别记录模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    image = models.ImageField(upload_to='recognition/images/', verbose_name='原始图像')
    preprocessed_image = models.ImageField(upload_to='recognition/preprocessed/', verbose_name='预处理后图像')
    result = models.CharField(max_length=10, verbose_name='识别结果')
    confidence = models.FloatField(verbose_name='置信度')
    candidates = models.JSONField(verbose_name='候选字列表')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '识别记录'
        verbose_name_plural = '识别记录'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.result} ({self.created_at})'