import os
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

class HandwritingDataset(Dataset):
    """
    手写汉字数据集加载器
    """
    def __init__(self, data_dir, transform=None):
        """
        初始化数据集
        
        Args:
            data_dir: 数据目录路径
            transform: 图像变换
        """
        self.data_dir = data_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        
        # 加载数据
        self._load_data()
    
    def _load_data(self):
        """
        加载数据路径和标签
        """
        for label_dir in os.listdir(self.data_dir):
            label_path = os.path.join(self.data_dir, label_dir)
            if os.path.isdir(label_path):
                for image_file in os.listdir(label_path):
                    if image_file.endswith('.png'):
                        image_path = os.path.join(label_path, image_file)
                        self.image_paths.append(image_path)
                        self.labels.append(int(label_dir))
    
    def __len__(self):
        """
        获取数据集大小
        """
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        """
        获取单个样本
        
        Args:
            idx: 样本索引
            
        Returns:
            image: 预处理后的图像张量
            label: 标签
        """
        # 读取图像
        image_path = self.image_paths[idx]
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # 图像预处理
        if self.transform:
            image = self.transform(image)
        else:
            # 默认变换
            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((64, 256)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5], std=[0.5])
            ])
            image = transform(image)
        
        label = self.labels[idx]
        return image, label

class DataLoaderFactory:
    """
    数据加载器工厂类
    """
    @staticmethod
    def get_dataloader(data_dir, batch_size=32, shuffle=True, num_workers=0):
        """
        获取数据加载器
        
        Args:
            data_dir: 数据目录路径
            batch_size: 批次大小
            shuffle: 是否打乱数据
            num_workers: 工作线程数
            
        Returns:
            DataLoader: 数据加载器
        """
        dataset = HandwritingDataset(data_dir)
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=num_workers,
            collate_fn=DataLoaderFactory.collate_fn
        )
        return dataloader
    
    @staticmethod
    def collate_fn(batch):
        """
        自定义批次处理函数
        
        Args:
            batch: 批次数据
            
        Returns:
            images: 图像张量
            labels: 标签列表
        """
        images, labels = zip(*batch)
        images = torch.stack(images, 0)
        labels = torch.tensor(labels)
        return images, labels

if __name__ == '__main__':
    # 测试数据集
    import sys
    sys.path.append('..')
    
    data_dir = '../../../data/train'  # 训练数据目录
    dataloader = DataLoaderFactory.get_dataloader(data_dir, batch_size=4)
    
    for images, labels in dataloader:
        print(f"图像形状: {images.shape}")
        print(f"标签: {labels}")
        break