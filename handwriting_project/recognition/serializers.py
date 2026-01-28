from rest_framework import serializers
from .models import RecognitionRecord
from django.core.files.base import ContentFile
import base64
import uuid
from PIL import Image
from io import BytesIO

class RecognitionRecordSerializer(serializers.ModelSerializer):
    """
    识别记录序列化器
    """
    class Meta:
        model = RecognitionRecord
        fields = ('id', 'user', 'image', 'preprocessed_image', 'result', 'confidence', 'candidates', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

class ImageUploadSerializer(serializers.Serializer):
    """
    图像上传序列化器
    """
    image = serializers.ImageField(required=True, help_text='上传的手写汉字图像')
    preprocessing_steps = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='自定义预处理步骤列表'
    )

class ImageBase64Serializer(serializers.Serializer):
    """
    Base64图像上传序列化器
    """
    image_base64 = serializers.CharField(required=True, help_text='Base64编码的图像')
    preprocessing_steps = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='自定义预处理步骤列表'
    )
    
    def validate_image_base64(self, value):
        """
        验证Base64图像
        
        Args:
            value: Base64编码的图像字符串
            
        Returns:
            PIL.Image: 解码后的图像对象
        """
        try:
            # 去掉Base64前缀
            if value.startswith('data:image'):
                value = value.split(',')[1]
            
            # 解码Base64
            image_data = base64.b64decode(value)
            
            # 转换为PIL图像
            image = Image.open(BytesIO(image_data))
            
            return image
        except Exception as e:
            raise serializers.ValidationError(f'无效的Base64图像: {str(e)}')

class RecognitionResultSerializer(serializers.Serializer):
    """
    识别结果序列化器
    """
    result = serializers.CharField(required=True, help_text='识别结果')
    confidence = serializers.FloatField(required=True, help_text='置信度')
    candidates = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text='候选字列表'
    )
    preprocessing_steps = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text='执行的预处理步骤'
    )
    preprocessed_image = serializers.ImageField(read_only=True, help_text='预处理后的图像')