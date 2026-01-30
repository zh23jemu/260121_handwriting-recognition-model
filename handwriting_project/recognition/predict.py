import torch
from torchvision import transforms
from PIL import Image
import os
import sys
import pickle
from models.crnn import CRNN

class ModelPredictor:
    """
    模型预测类，用于加载训练好的模型并进行预测
    """
    
    def __init__(self, model_path=None, char_dict_path=None):
        """
        初始化模型预测器
        
        Args:
            model_path: 模型文件路径，默认使用saved_models/crnn_final.pth
            char_dict_path: 汉字字典路径，默认使用项目根目录的char_dict
        """
        # 检查CUDA是否可用
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 加载汉字字典
        # 修正字符字典路径，使用绝对路径
        if char_dict_path is None:
            char_dict_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'char_dict')
        print(f"Char dict path: {char_dict_path}")
        print(f"Char dict file exists: {os.path.exists(char_dict_path)}")
        self.char_dict, self.idx2char = self._load_char_dict(char_dict_path)
        
        # 模型路径
        if model_path is None:
            # 使用绝对路径，确保能正确找到模型文件
            # 直接指定完整的绝对路径
            model_path = r'C:\!coding\260121_handwriting-recognition-model\handwriting_project\models\saved_models\crnn_common_best.pth'
            print(f"Model path: {model_path}")
            print(f"Model file exists: {os.path.exists(model_path)}")
        
        # 加载模型
        self.model = self._load_model(model_path)
        
        # 图像转换
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
    
    def _load_char_dict(self, char_dict_path):
        """
        加载汉字字典
        
        Args:
            char_dict_path: 汉字字典路径
            
        Returns:
            tuple: (char_to_idx, idx_to_char)
        """
        with open(char_dict_path, 'rb') as f:
            char_dict = pickle.load(f)
        
        # 创建反向映射
        idx_to_char = {v: k for k, v in char_dict.items()}
        
        return char_dict, idx_to_char
    
    def _load_model(self, model_path):
        """
        加载训练好的模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            CRNN: 加载好的模型
        """
        # 初始化模型
        model = CRNN(num_classes=len(self.char_dict))
        
        # 加载模型参数
        if os.path.exists(model_path):
            try:
                # 尝试加载模型权重，忽略不匹配的参数
                state_dict = torch.load(model_path, map_location=self.device)
                # 过滤掉不匹配的权重参数
                filtered_state_dict = {k: v for k, v in state_dict.items() if not k.startswith('lstm1.')}
                model.load_state_dict(filtered_state_dict, strict=False)
                print(f"Model loaded from {model_path} (filtered lstm1 parameters)")
            except Exception as e:
                print(f"Error loading model: {str(e)}")
                print("Using random initialized model instead.")
        else:
            print(f"Warning: Model file {model_path} not found. Using random initialized model.")
        
        # 设置模型为评估模式
        model.to(self.device)
        model.eval()
        
        return model
    
    def predict(self, image):
        """
        预测图像中的汉字
        
        Args:
            image: PIL图像对象
            
        Returns:
            dict: 预测结果，包含识别结果、置信度和候选字列表
        """
        # 图像转换
        image_tensor = self.transform(image).unsqueeze(0)  # 添加batch维度
        image_tensor = image_tensor.to(self.device)
        
        # 预测
        with torch.no_grad():
            outputs = self.model(image_tensor)
            # 取最后一个时间步的输出
            outputs = outputs[-1, :, :]
            
            # 计算置信度
            probabilities = torch.softmax(outputs, dim=1)
            max_prob, predicted_idx = torch.max(probabilities, dim=1)
            
            # 获取识别结果
            predicted_char = self.idx2char[predicted_idx.item()]
            confidence = max_prob.item()
            
            # 获取候选字列表（前5个）
            top_probs, top_idxs = torch.topk(probabilities, k=5, dim=1)
            candidates = []
            for prob, idx in zip(top_probs[0], top_idxs[0]):
                candidates.append({
                    'char': self.idx2char[idx.item()],
                    'confidence': prob.item()
                })
        
        return {
            'result': predicted_char,
            'confidence': confidence,
            'candidates': candidates
        }
    
    def predict_batch(self, images):
        """
        批量预测图像中的汉字
        
        Args:
            images: PIL图像对象列表
            
        Returns:
            list: 预测结果列表
        """
        # 图像转换
        image_tensors = [self.transform(image) for image in images]
        image_tensors = torch.stack(image_tensors).to(self.device)
        
        # 预测
        with torch.no_grad():
            outputs = self.model(image_tensors)
            # 取最后一个时间步的输出
            outputs = outputs[-1, :, :]
            
            # 计算置信度
            probabilities = torch.softmax(outputs, dim=1)
            max_probs, predicted_idxs = torch.max(probabilities, dim=1)
            
            # 获取识别结果
            results = []
            for i in range(len(images)):
                predicted_char = self.idx2char[predicted_idxs[i].item()]
                confidence = max_probs[i].item()
                
                # 获取候选字列表（前5个）
                top_probs, top_idxs = torch.topk(probabilities[i], k=5, dim=0)
                candidates = []
                for prob, idx in zip(top_probs, top_idxs):
                    candidates.append({
                        'char': self.idx2char[idx.item()],
                        'confidence': prob.item()
                    })
                
                results.append({
                    'result': predicted_char,
                    'confidence': confidence,
                    'candidates': candidates
                })
        
        return results