from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.base import ContentFile
from datetime import datetime
from PIL import Image
from io import BytesIO
import numpy as np
import cv2
import base64
import uuid
import time
import easyocr
import os

from .models import RecognitionRecord

class ImageRecognitionView(views.APIView):
    """
    图像识别视图
    处理图像上传、预处理和识别请求
    """
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化EasyOCR系统
        print("Initializing OCR System for handwriting recognition")
        print("Loading EasyOCR model...")
        
        # 尝试初始化EasyOCR
        try:
            # 加载EasyOCR模型，使用中文简体
            # detail=0 返回简化结果格式，更容易解析
            self.reader = easyocr.Reader(['ch_sim'], gpu=False, verbose=False)
            print("EasyOCR engine initialized successfully")
        except Exception as e:
            print(f"Error: EasyOCR engine initialization failed. Error: {str(e)}")
            self.reader = None
        
        print("OCR system ready for handwriting recognition")
    
    def _preprocess_image(self, image):
        """
        图像预处理：和app.py一致
        """
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_np = np.array(image)
        
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        enhanced = cv2.equalizeHist(blurred)
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        
        return enhanced
    
    def _process_ocr_result(self, result):
        """
        处理OCR结果
        
        Args:
            result: EasyOCR返回的结果
            
        Returns:
            tuple: (texts, confidences)
        """
        texts = []
        confidences = []
        
        if result is None:
            return texts, confidences
        
        try:
            for item in result:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    text = item[1] if isinstance(item[1], str) else str(item[1])
                    confidence = float(item[2]) if len(item) > 2 and isinstance(item[2], (int, float, np.floating)) else 0.0
                    texts.append(text)
                    confidences.append(confidence)
        except Exception as e:
            print(f"Error processing OCR result: {e}")
        
        return texts, confidences
    
    def post(self, request, *args, **kwargs):
        """
        处理图像上传和识别请求
        
        Args:
            request: HTTP请求对象，包含上传的图像
            
        Returns:
            Response: 包含识别结果的HTTP响应
        """
        # 检查请求类型
        if 'image' not in request.data:
            return Response(
                {'error': '请求中缺少image字段'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 获取图像
            image = Image.open(request.data['image'])
            
            # 图像预处理
            processed_image = self._preprocess_image(image)
            
            # 将预处理后的图像转换为base64编码
            preprocessed_image_base64 = None
            try:
                # 将numpy数组转换回PIL图像
                processed_pil_image = Image.fromarray(processed_image)
                
                # 将图像保存到BytesIO对象
                buffer = BytesIO()
                processed_pil_image.save(buffer, format='PNG')
                
                # 转换为base64编码
                preprocessed_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                print("Preprocessed image converted to base64 successfully")
            except Exception as e:
                print(f"Error converting preprocessed image to base64: {str(e)}")
                preprocessed_image_base64 = None
            
            # 使用EasyOCR进行OCR
            result = None
            texts = []
            confidences = []
            
            if self.reader:
                try:
                    result = self.reader.readtext(processed_image, batch_size=4)
                    print(f"EasyOCR result: {result}")
                    texts = []
                    confidences = []
                    if result and isinstance(result, list):
                        for item in result:
                            if isinstance(item, list) and len(item) >= 2:
                                text = str(item[1]) if item[1] is not None else ''
                                conf = float(item[2]) if len(item) > 2 and item[2] is not None else 0.0
                                if text:
                                    texts.append(text)
                                    confidences.append(conf)
                    print(f"Parsed texts: {texts}, confidences: {confidences}")
                except Exception as e:
                    print(f"Error during OCR processing: {str(e)}")
                    texts, confidences = [], []
            else:
                print("EasyOCR not initialized, cannot perform recognition")
            
            # 处理识别结果
            predicted_char = ""
            confidence = 0.0
            candidates = []
            
            if texts:
                best_text = texts[0]
                best_confidence = confidences[0] if confidences else 0.85
                print(f"Best OCR Result: '{best_text}' with confidence: {best_confidence}")
                
                predicted_char = best_text[0]
                confidence = best_confidence
                print(f"Selected character: '{predicted_char}'")
                
                candidates = [
                    {'char': predicted_char, 'confidence': best_confidence}
                ]
                
                if len(best_text) > 1:
                    for i, char in enumerate(best_text[1:4]):
                        if char and isinstance(char, str) and char.strip():
                            candidates.append({
                                'char': char,
                                'confidence': round(best_confidence - (i+1)*0.05, 4)
                            })
            
            print(f"Final result: char='{predicted_char}', confidence={confidence}, candidates_count={len(candidates)}")
                
            if not texts:
                return Response(
                    {'error': '未能识别出文字，请上传更清晰的手写图像'},
                    status=status.HTTP_200_OK
                )
            
            # 保存识别记录
            try:
                # 保存原始图像
                original_image_name = f"original_{uuid.uuid4()}.png"
                original_image_io = BytesIO()
                image.save(original_image_io, format='PNG')
                original_image_content = ContentFile(original_image_io.getvalue(), name=original_image_name)
                
                # 保存预处理后的图像
                preprocessed_image_name = f"preprocessed_{uuid.uuid4()}.png"
                preprocessed_image_content = None
                if preprocessed_image_base64:
                    preprocessed_image_data = base64.b64decode(preprocessed_image_base64)
                    preprocessed_image_content = ContentFile(preprocessed_image_data, name=preprocessed_image_name)
                
                # 创建识别记录
                recognition_record = RecognitionRecord(
                    user=request.user,
                    image=original_image_content,
                    preprocessed_image=preprocessed_image_content,
                    result=predicted_char,
                    confidence=confidence,
                    candidates=candidates
                )
                recognition_record.save()
                print(f"Recognition record saved: {recognition_record.id}")
            except Exception as e:
                print(f"Error saving recognition record: {str(e)}")
            
            response_data = {
                'result': predicted_char,
                'confidence': round(float(confidence), 4),
                'candidates': candidates,
                'preprocessing_steps': ['grayscale', 'gaussian_blur', 'histogram_equalization'],
                'preprocessed_image': preprocessed_image_base64
            }
            
            print(f"Response data: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"识别过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
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
            request: HTTP请求对象
            
        Returns:
            Response: 包含识别历史记录的HTTP响应
        """
        try:
            # 获取用户的识别历史记录
            records = RecognitionRecord.objects.filter(user=request.user).order_by('-created_at')
            
            # 构建响应数据
            history_data = []
            for record in records:
                history_data.append({
                    'id': record.id,
                    'result': record.result,
                    'confidence': record.confidence,
                    'candidates': record.candidates,
                    'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            return Response(history_data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error loading history: {str(e)}")
            return Response(
                {'error': f'获取历史记录失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            
            # 构建响应数据
            detail_data = {
                'id': record.id,
                'result': record.result,
                'confidence': record.confidence,
                'candidates': record.candidates,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return Response(detail_data, status=status.HTTP_200_OK)
        except RecognitionRecord.DoesNotExist:
            return Response(
                {'error': '识别记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error loading record detail: {str(e)}")
            return Response(
                {'error': f'获取识别记录失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
