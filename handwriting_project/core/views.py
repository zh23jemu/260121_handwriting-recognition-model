from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer
from .models import User

class RegisterView(generics.CreateAPIView):
    """用户注册视图"""
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class LoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """用户登出视图"""
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserView(generics.RetrieveAPIView):
    """获取当前用户信息视图"""
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user

class UserListView(generics.ListCreateAPIView):
    """获取用户列表视图（管理员权限）"""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """只有管理员可以查看所有用户"""
        if self.request.user.is_admin:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def create(self, request, *args, **kwargs):
        """只有管理员可以创建用户"""
        if not request.user.is_admin:
            return Response(
                {'error': '只有管理员可以创建用户'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().create(request, *args, **kwargs)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情视图（管理员权限）"""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """管理员可以查看所有用户，普通用户只能查看自己"""
        if self.request.user.is_admin:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def update(self, request, *args, **kwargs):
        """只有管理员可以更新用户信息"""
        if not request.user.is_admin:
            # 普通用户只能更新自己的信息，且不能修改管理员权限
            instance = self.get_object()
            if instance.id != request.user.id:
                return Response(
                    {'error': '只能更新自己的信息'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            # 移除管理员权限字段
            if 'is_admin' in request.data:
                del request.data['is_admin']
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """只有管理员可以删除用户"""
        if not request.user.is_admin:
            return Response(
                {'error': '只有管理员可以删除用户'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)