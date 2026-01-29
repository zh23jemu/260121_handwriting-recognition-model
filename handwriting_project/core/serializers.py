from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_admin', 'password', 'is_active', 'date_joined')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_admin': {'read_only': False},  # 允许管理员修改
            'is_active': {'read_only': False}
        }
    
    def create(self, validated_data):
        """创建新用户"""
        # 提取密码
        password = validated_data.pop('password', None)
        # 创建用户
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """更新用户信息"""
        # 提取密码
        password = validated_data.pop('password', None)
        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # 更新密码
        if password:
            instance.set_password(password)
        instance.save()
        return instance

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