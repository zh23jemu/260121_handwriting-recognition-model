import torch
import torch.nn as nn
import torch.nn.functional as F

class CNNMLP(nn.Module):
    """
    CNN+MLP模型，用于手写汉字识别
    结构：卷积层 -> 池化层 -> 卷积层 -> 池化层 -> 全连接层 -> 输出层
    """
    
    def __init__(self, num_classes):
        """
        初始化CNN+MLP模型
        
        Args:
            num_classes: 类别数量
        """
        super(CNNMLP, self).__init__()
        
        # 卷积层1
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # 卷积层2
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # 卷积层3
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # 全连接层
        self.fc1 = nn.Linear(128 * 16 * 16, 512)  # 假设输入图像大小为128x128
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, 256)
        self.dropout2 = nn.Dropout(0.5)
        self.fc3 = nn.Linear(256, num_classes)
    
    def forward(self, x):
        """
        前向传播
        
        Args:
            x: 输入图像，形状为(batch_size, 1, height, width)
            
        Returns:
            output: 模型输出，形状为(batch_size, num_classes)
        """
        # 卷积层1
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)
        
        # 卷积层2
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        
        # 卷积层3
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.pool3(x)
        
        # 展平
        x = x.view(x.size(0), -1)
        
        # 全连接层
        x = F.relu(self.fc1(x))
        x = self.dropout1(x)
        x = F.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.fc3(x)
        
        return x