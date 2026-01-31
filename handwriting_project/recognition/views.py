from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.base import ContentFile
from django.http import HttpResponse
import csv
import uuid
from datetime import datetime
from PIL import Image
from io import BytesIO

from .serializers import (
    ImageUploadSerializer,
    ImageBase64Serializer,
    RecognitionRecordSerializer,
    RecognitionResultSerializer
)
from .preprocessing import ImagePreprocessor
from .predict import ModelPredictor
from .models import RecognitionRecord

class ImageRecognitionView(views.APIView):
    """
    图像识别视图
    处理图像上传、预处理和识别请求
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化模型预测器
        self.predictor = ModelPredictor()
        # 初始化图像预处理器
        self.preprocessor = ImagePreprocessor()
    
    def post(self, request, *args, **kwargs):
        """
        处理图像上传和识别请求
        
        Args:
            request: HTTP请求对象，包含上传的图像和预处理步骤
            
        Returns:
            Response: 包含识别结果的HTTP响应
        """
        # 检查请求类型
        if 'image' in request.data:
            # 常规图像上传
            serializer = ImageUploadSerializer(data=request.data)
        elif 'image_base64' in request.data:
            # Base64图像上传
            serializer = ImageBase64Serializer(data=request.data)
        else:
            return Response(
                {'error': '请求中缺少image或image_base64字段'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证请求数据
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取预处理步骤
        preprocessing_steps = serializer.validated_data.get('preprocessing_steps', None)
        
        # 获取图像
        if 'image' in serializer.validated_data:
            # 常规图像上传
            image = Image.open(serializer.validated_data['image'])
        else:
            # Base64图像
            image = serializer.validated_data['image_base64']
        
        try:
            # 模型预测（直接使用原始图像，让predict方法自己处理预处理）
            prediction_result = self.predictor.predict(image)
            
            # 保存原始图像
            original_image_name = f"original_{uuid.uuid4()}.png"
            original_image_io = BytesIO()
            image.save(original_image_io, format='PNG')
            original_image_content = ContentFile(original_image_io.getvalue(), name=original_image_name)
            
            # 保存预处理后的图像（从prediction_result中获取）
            preprocessed_image_name = f"preprocessed_{uuid.uuid4()}.png"
            preprocessed_image_content = None
            if prediction_result.get('preprocessed_image'):
                import base64
                preprocessed_image_data = base64.b64decode(prediction_result['preprocessed_image'])
                preprocessed_image_content = ContentFile(preprocessed_image_data, name=preprocessed_image_name)
            
            # 创建识别记录
            recognition_record = RecognitionRecord(
                user=request.user,
                image=original_image_content,
                preprocessed_image=preprocessed_image_content,
                result=prediction_result['result'],
                confidence=prediction_result['confidence'],
                candidates=prediction_result['candidates']
            )
            recognition_record.save()
            
            # 序列化识别结果
            result_serializer = RecognitionResultSerializer({
                'result': prediction_result['result'],
                'confidence': prediction_result['confidence'],
                'candidates': prediction_result['candidates'],
                'preprocessing_steps': ['grayscale', 'adaptive_binarize', 'denoise', 'resize', 'normalize'],
                'preprocessed_image': prediction_result.get('preprocessed_image')
            })
            
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'识别过程中发生错误: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RecognitionHistoryView(views.APIView):
    """
    识别历史视图
    处理识别历史记录的查询请求
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        获取用户的识别历史记录
        
        Args:
            request: HTTP请求对象，可包含分页参数
            
        Returns:
            Response: 包含识别历史记录的HTTP响应
        """
        # 获取用户的识别历史记录
        records = RecognitionRecord.objects.filter(user=request.user).order_by('-created_at')
        
        # 序列化识别记录
        serializer = RecognitionRecordSerializer(records, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class RecognitionDetailView(views.APIView):
    """
    识别详情视图
    处理单个识别记录的查询请求
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, record_id, *args, **kwargs):
        """
        获取单个识别记录的详细信息
        
        Args:
            request: HTTP请求对象
            record_id: 识别记录ID
            
        Returns:
            Response: 包含识别记录详细信息的HTTP响应
        """
        try:
            # 获取识别记录
            record = RecognitionRecord.objects.get(id=record_id, user=request.user)
            
            # 序列化识别记录
            serializer = RecognitionRecordSerializer(record)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RecognitionRecord.DoesNotExist:
            return Response(
                {'error': '识别记录不存在'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'获取识别记录失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PreprocessingDemoView(views.APIView):
    """
    预处理演示视图
    用于演示不同预处理步骤的效果
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        演示图像预处理效果
        
        Args:
            request: HTTP请求对象，包含上传的图像和预处理步骤
            
        Returns:
            Response: 包含预处理结果的HTTP响应
        """
        # 检查请求类型
        if 'image' in request.data:
            # 常规图像上传
            serializer = ImageUploadSerializer(data=request.data)
        elif 'image_base64' in request.data:
            # Base64图像上传
            serializer = ImageBase64Serializer(data=request.data)
        else:
            return Response(
                {'error': '请求中缺少image或image_base64字段'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 验证请求数据
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取预处理步骤
        preprocessing_steps = serializer.validated_data.get('preprocessing_steps', None)
        
        # 获取图像
        if 'image' in serializer.validated_data:
            # 常规图像上传
            image = Image.open(serializer.validated_data['image'])
        else:
            # Base64图像
            image = serializer.validated_data['image_base64']
        
        try:
            # 图像预处理
            preprocessed_image, step_records = self.preprocessor.preprocess(image, preprocessing_steps)
            
            # 保存预处理后的图像
            preprocessed_image_name = f"demo_preprocessed_{uuid.uuid4()}.png"
            preprocessed_image_io = BytesIO()
            preprocessed_image.save(preprocessed_image_io, format='PNG')
            preprocessed_image_content = ContentFile(preprocessed_image_io.getvalue(), name=preprocessed_image_name)
            
            # 保存预处理后的图像到临时记录
            # 注意：这里不保存完整的识别记录，只保存预处理后的图像用于演示
            from django.core.files.storage import default_storage
            preprocessed_image_path = default_storage.save(f"demo/{preprocessed_image_name}", preprocessed_image_content)
            preprocessed_image_url = default_storage.url(preprocessed_image_path)
            
            return Response({
                'preprocessing_steps': step_records,
                'preprocessed_image_url': preprocessed_image_url
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'预处理演示失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExportHistoryView(views.APIView):
    """
    导出历史记录视图
    用于将识别历史导出为CSV格式
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        导出识别历史为CSV文件
        
        Args:
            request: HTTP请求对象
            
        Returns:
            HttpResponse: CSV文件响应
        """
        # 获取用户的识别历史记录
        records = RecognitionRecord.objects.filter(user=request.user).order_by('-created_at')
        
        # 创建HTTP响应，设置内容类型为CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="recognition_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # 创建CSV写入器
        writer = csv.writer(response)
        
        # 写入CSV表头
        writer.writerow([
            'ID', '识别结果', '置信度', '候选字', '预处理步骤', 
            '原始图像URL', '预处理后图像URL', '创建时间'
        ])
        
        # 写入数据行
        for record in records:
            # 处理候选字
            candidates = '; '.join([f"{c['char']}({c['confidence']:.4f})" for c in record.candidates])
            
            # 写入一行数据
            writer.writerow([
                record.id,
                record.result,
                f"{record.confidence:.4f}",
                candidates,
                '; '.join(['grayscale', 'adaptive_binarize', 'denoise', 'center', 'resize', 'normalize']),  # 简化处理步骤
                request.build_absolute_uri(record.image.url),
                request.build_absolute_uri(record.preprocessed_image.url),
                record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response