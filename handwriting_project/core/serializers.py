from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_admin', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_admin': {'read_only': True}
        }
    
    def create(self, validated_data):
        """创建新用户"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """验证用户凭据"""
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("无效的登录凭据")