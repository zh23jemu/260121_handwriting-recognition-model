import torch
import torch.nn as nn

class CRNN(nn.Module):
    """
    CRNN（Convolutional Recurrent Neural Network）模型，用于手写汉字识别
    结合卷积神经网络提取图像特征，循环神经网络处理序列特征
    """
    def __init__(self, num_classes=1000):
        """
        初始化CRNN模型
        
        Args:
            num_classes: 分类数量，即汉字数量
        """
        super(CRNN, self).__init__()
        
        # 卷积层：提取图像特征
        self.cnn = nn.Sequential(
            # 第一层卷积
            nn.Conv2d(1, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 输出: 64 x H/2 x W/2
            
            # 第二层卷积
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),  # 输出: 128 x H/4 x W/4
            
            # 第三层卷积
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            
            # 第四层卷积
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 1), stride=(2, 1)),  # 输出: 256 x H/8 x W/4
            
            # 第五层卷积
            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            
            # 第六层卷积
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=(2, 1), stride=(2, 1)),  # 输出: 512 x H/16 x W/4
            
            # 第七层卷积
            nn.Conv2d(512, 512, kernel_size=2, stride=1, padding=0),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True)  # 输出: 512 x H/16 x W/4-1
        )
        
        # 循环层：处理序列特征
        # 初始化为None，在第一次前向传播时根据实际输入维度创建
        self.lstm1 = None
        self.lstm2 = nn.LSTM(512, 256, bidirectional=True, batch_first=False)   # 双向LSTM
        
        # 全连接层：分类输出
        self.fc = nn.Linear(512, num_classes)
        
        # 标记是否已经初始化LSTM
        self.lstm_initialized = False
    
    def forward(self, x):
        """
        前向传播
        
        Args:
            x: 输入图像，形状为 (batch_size, 1, height, width)
            
        Returns:
            输出特征，形状为 (seq_len, batch_size, num_classes)
        """
        # 打印输入尺寸
        print(f"Input size: {x.size()}")
        
        # 卷积特征提取
        conv_out = self.cnn(x)
        
        # 打印CNN输出尺寸
        print(f"CNN output size: {conv_out.size()}")
        
        # 调整维度以适应LSTM输入
        # conv_out形状: (batch_size, channels, height, width)
        batch_size, channels, height, width = conv_out.size()
        
        # 计算LSTM输入维度
        lstm_input_size = channels * height
        print(f"LSTM input size: {lstm_input_size}")
        
        # 将height和channels合并，作为序列长度
        # 输出形状: (width, batch_size, channels * height)
        rnn_in = conv_out.permute(3, 0, 1, 2)
        rnn_in = rnn_in.contiguous().view(width, batch_size, -1)
        
        # 打印RNN输入尺寸
        print(f"RNN input size: {rnn_in.size()}")
        
        # 动态初始化LSTM层
        if not self.lstm_initialized:
            print("Initializing LSTM layers...")
            # 根据实际输入维度创建LSTM层
            self.lstm1 = nn.LSTM(lstm_input_size, 256, bidirectional=True, batch_first=False)
            # 将模型移动到正确的设备
            device = next(self.parameters()).device
            self.lstm1 = self.lstm1.to(device)
            self.lstm_initialized = True
            print("LSTM layers initialized successfully")
        
        # 循环特征提取
        rnn_out1, _ = self.lstm1(rnn_in)
        rnn_out2, _ = self.lstm2(rnn_out1)
        
        # 全连接层分类
        output = self.fc(rnn_out2)
        
        return output

if __name__ == '__main__':
    # 测试模型
    model = CRNN(num_classes=3755)
    input = torch.randn(1, 1, 64, 256)  # 输入形状: (batch_size, channels, height, width)
    output = model(input)
    print(f"输入形状: {input.shape}")
    print(f"输出形状: {output.shape}")
    print(f"模型参数数量: {sum(p.numel() for p in model.parameters())}")