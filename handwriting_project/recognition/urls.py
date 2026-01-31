from django.urls import path
from .views import (
    ImageRecognitionView,
    RecognitionHistoryView,
    RecognitionDetailView
)

urlpatterns = [
    # 图像识别API
    path('recognize/', ImageRecognitionView.as_view(), name='image_recognition'),
    
    # 识别历史API
    path('history/', RecognitionHistoryView.as_view(), name='recognition_history'),
    
    # 单个识别记录详情API
    path('history/<int:record_id>/', RecognitionDetailView.as_view(), name='recognition_detail'),
]