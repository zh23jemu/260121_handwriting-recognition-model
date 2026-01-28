import cv2
import numpy as np
from PIL import Image
import io

class ImagePreprocessor:
    """
    图像预处理类，用于处理手写汉字图像
    """
    
    @staticmethod
    def grayscale(image):
        """
        将图像转换为灰度图
        
        Args:
            image: PIL图像对象
            
        Returns:
            PIL图像对象: 灰度图
        """
        return image.convert('L')
    
    @staticmethod
    def resize(image, target_size=(64, 256)):
        """
        调整图像大小
        
        Args:
            image: PIL图像对象
            target_size: 目标大小，默认(64, 256)
            
        Returns:
            PIL图像对象: 调整大小后的图像
        """
        # 确保图像被调整到正确的大小
        resized = image.resize(target_size, Image.Resampling.LANCZOS)
        print(f"Resized image size: {resized.size}")
        return resized
    
    @staticmethod
    def binarize(image, threshold=127):
        """
        图像二值化
        
        Args:
            image: PIL图像对象（灰度图）
            threshold: 二值化阈值，默认127
            
        Returns:
            PIL图像对象: 二值化图像
        """
        return image.point(lambda p: 0 if p < threshold else 255, '1')
    
    @staticmethod
    def adaptive_binarize(image, block_size=11, C=2):
        """
        自适应二值化
        
        Args:
            image: PIL图像对象（灰度图）
            block_size: 块大小
            C: 常数
            
        Returns:
            PIL图像对象: 自适应二值化图像
        """
        # 转换为OpenCV格式
        img_cv = np.array(image)
        # 自适应阈值二值化
        binary = cv2.adaptiveThreshold(
            img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, block_size, C
        )
        # 转换回PIL格式
        return Image.fromarray(binary)
    
    @staticmethod
    def denoise(image):
        """
        图像降噪
        
        Args:
            image: PIL图像对象（二值图）
            
        Returns:
            PIL图像对象: 降噪后的图像
        """
        # 转换为OpenCV格式
        img_cv = np.array(image)
        # 开运算降噪
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(img_cv, cv2.MORPH_OPEN, kernel)
        # 闭运算填充
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        # 转换回PIL格式
        return Image.fromarray(closing)
    
    @staticmethod
    def normalize(image):
        """
        图像归一化
        
        Args:
            image: PIL图像对象
            
        Returns:
            PIL图像对象: 归一化图像
        """
        # 转换为numpy数组
        img_np = np.array(image)
        # 归一化到[0, 1]
        img_norm = img_np / 255.0
        # 转换回PIL格式
        img_norm = (img_norm * 255).astype(np.uint8)
        return Image.fromarray(img_norm)
    
    @staticmethod
    def center(image):
        """
        图像居中
        
        Args:
            image: PIL图像对象
            
        Returns:
            PIL图像对象: 居中后的图像
        """
        # 转换为numpy数组
        img_np = np.array(image)
        # 查找图像边界
        coords = cv2.findNonZero(img_np)
        x, y, w, h = cv2.boundingRect(coords)
        # 裁剪图像
        cropped = img_np[y:y+h, x:x+w]
        # 创建新图像，居中放置裁剪后的图像
        new_img = np.ones_like(img_np) * 255
        start_y = (new_img.shape[0] - h) // 2
        start_x = (new_img.shape[1] - w) // 2
        new_img[start_y:start_y+h, start_x:start_x+w] = cropped
        # 转换回PIL格式
        return Image.fromarray(new_img)
    
    @classmethod
    def preprocess(cls, image, steps=None):
        """
        完整的图像预处理流程
        
        Args:
            image: PIL图像对象
            steps: 预处理步骤列表，默认使用所有步骤
            
        Returns:
            tuple: (预处理后的图像, 预处理步骤记录)
        """
        if steps is None:
            steps = ['grayscale', 'adaptive_binarize', 'denoise', 'center', 'resize', 'normalize']
        
        processed_image = image
        step_records = []
        
        # 执行指定的预处理步骤
        for step in steps:
            if hasattr(cls, step):
                processed_image = getattr(cls, step)(processed_image)
                step_records.append(step)
        
        return processed_image, step_records
    
    @staticmethod
    def pil_to_bytes(image):
        """
        将PIL图像转换为字节流
        
        Args:
            image: PIL图像对象
            
        Returns:
            bytes: 图像字节流
        """
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def bytes_to_pil(image_bytes):
        """
        将字节流转换为PIL图像
        
        Args:
            image_bytes: 图像字节流
            
        Returns:
            PIL图像对象
        """
        return Image.open(io.BytesIO(image_bytes))