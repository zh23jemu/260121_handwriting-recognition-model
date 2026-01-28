import torch
import torch.optim as optim
import torch.nn as nn
import matplotlib.pyplot as plt
import seaborn as sns
import os
from tqdm import tqdm
from sklearn.metrics import accuracy_score, confusion_matrix
from crnn import CRNN
from cnn_mlp import CNNMLP
from dataset import DataLoaderFactory

class ModelTrainer:
    """
    模型训练器类
    """
    def __init__(self, model, train_dir, test_dir, save_dir='./saved_models'):
        """
        初始化模型训练器
        
        Args:
            model: 要训练的模型
            train_dir: 训练数据目录
            test_dir: 测试数据目录
            save_dir: 模型保存目录
        """
        self.model = model
        self.train_dir = train_dir
        self.test_dir = test_dir
        self.save_dir = save_dir
        
        # 创建保存目录
        os.makedirs(self.save_dir, exist_ok=True)
        
        # 设备选择
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # 损失函数和优化器
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # 学习率调度器
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.1, patience=5
        )
        
        # 训练历史
        self.train_loss_history = []
        self.test_loss_history = []
        self.train_accuracy_history = []
        self.test_accuracy_history = []
    
    def train_epoch(self, dataloader):
        """
        训练一个epoch
        
        Args:
            dataloader: 训练数据加载器
            
        Returns:
            avg_loss: 平均损失
            accuracy: 准确率
        """
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with tqdm(dataloader, desc='Training') as pbar:
            for images, labels in pbar:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                # 前向传播
                outputs = self.model(images)
                
                # 根据模型类型调整输出
                if isinstance(self.model, CRNN):
                    # CRNN输出形状: (seq_len, batch_size, num_classes)
                    # 取最后一个时间步的输出作为预测结果
                    outputs = outputs[-1, :, :]
                # CNNMLP输出形状: (batch_size, num_classes)，无需调整
                
                # 计算损失
                loss = self.criterion(outputs, labels)
                
                # 反向传播和优化
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                # 统计损失
                running_loss += loss.item()
                
                # 计算准确率
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
                pbar.set_postfix({'Loss': running_loss/len(pbar), 'Accuracy': correct/total})
        
        avg_loss = running_loss / len(dataloader)
        accuracy = correct / total
        return avg_loss, accuracy
    
    def evaluate(self, dataloader):
        """
        评估模型
        
        Args:
            dataloader: 测试数据加载器
            
        Returns:
            avg_loss: 平均损失
            accuracy: 准确率
        """
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            with tqdm(dataloader, desc='Evaluating') as pbar:
                for images, labels in pbar:
                    images = images.to(self.device)
                    labels = labels.to(self.device)
                    
                    # 前向传播
                    outputs = self.model(images)
                    
                    # 根据模型类型调整输出
                    if isinstance(self.model, CRNN):
                        # CRNN输出形状: (seq_len, batch_size, num_classes)
                        # 取最后一个时间步的输出作为预测结果
                        outputs = outputs[-1, :, :]
                    # CNNMLP输出形状: (batch_size, num_classes)，无需调整
                    
                    # 计算损失
                    loss = self.criterion(outputs, labels)
                    running_loss += loss.item()
                    
                    # 计算准确率
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
                    
                    pbar.set_postfix({'Loss': running_loss/len(pbar), 'Accuracy': correct/total})
        
        avg_loss = running_loss / len(dataloader)
        accuracy = correct / total
        return avg_loss, accuracy
    
    def train(self, epochs=50, batch_size=32):
        """
        训练模型
        
        Args:
            epochs: 训练轮数
            batch_size: 批次大小
        """
        # 获取数据加载器
        train_dataloader = DataLoaderFactory.get_dataloader(
            self.train_dir, batch_size=batch_size, shuffle=True
        )
        test_dataloader = DataLoaderFactory.get_dataloader(
            self.test_dir, batch_size=batch_size, shuffle=False
        )
        
        for epoch in range(epochs):
            print(f'\nEpoch {epoch+1}/{epochs}')
            print('-' * 50)
            
            # 训练一个epoch
            train_loss, train_accuracy = self.train_epoch(train_dataloader)
            
            # 评估模型
            test_loss, test_accuracy = self.evaluate(test_dataloader)
            
            # 更新学习率
            self.scheduler.step(test_loss)
            
            # 保存训练历史
            self.train_loss_history.append(train_loss)
            self.test_loss_history.append(test_loss)
            self.train_accuracy_history.append(train_accuracy)
            self.test_accuracy_history.append(test_accuracy)
            
            # 保存模型
            if (epoch + 1) % 10 == 0:
                model_type = 'crnn' if isinstance(self.model, CRNN) else 'cnn_mlp'
                model_path = os.path.join(self.save_dir, f'{model_type}_epoch_{epoch+1}.pth')
                torch.save(self.model.state_dict(), model_path)
                print(f'Model saved to {model_path}')
        
        # 保存最终模型
        model_type = 'crnn' if isinstance(self.model, CRNN) else 'cnn_mlp'
        final_model_path = os.path.join(self.save_dir, f'{model_type}_final.pth')
        torch.save(self.model.state_dict(), final_model_path)
        print(f'Final model saved to {final_model_path}')
        
        # 生成可视化图表
        self.generate_plots()
    
    def generate_plots(self):
        """
        生成训练可视化图表
        """
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        
        # 损失值变化
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.plot(self.train_loss_history, label='Training Loss')
        plt.plot(self.test_loss_history, label='Test Loss')
        plt.title('Loss History')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        # 准确率变化
        plt.subplot(1, 2, 2)
        plt.plot(self.train_accuracy_history, label='Training Accuracy')
        plt.plot(self.test_accuracy_history, label='Test Accuracy')
        plt.title('Accuracy History')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        
        # 保存图表
        plt.tight_layout()
        model_type = 'crnn' if isinstance(self.model, CRNN) else 'cnn_mlp'
        plot_path = os.path.join(self.save_dir, f'{model_type}_training_history.png')
        plt.savefig(plot_path, dpi=300)
        print(f'Training history plot saved to {plot_path}')
        plt.close()

class ModelEvaluator:
    """
    模型评估器类
    """
    def __init__(self, model, test_dir):
        """
        初始化模型评估器
        
        Args:
            model: 要评估的模型
            test_dir: 测试数据目录
        """
        self.model = model
        self.test_dir = test_dir
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def evaluate(self, batch_size=32):
        """
        评估模型
        
        Args:
            batch_size: 批次大小
            
        Returns:
            accuracy: 准确率
        """
        dataloader = DataLoaderFactory.get_dataloader(
            self.test_dir, batch_size=batch_size, shuffle=False
        )
        
        self.model.eval()
        correct = 0
        total = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            with tqdm(dataloader, desc='Evaluating') as pbar:
                for images, labels in pbar:
                    images = images.to(self.device)
                    labels = labels.to(self.device)
                    
                    # 前向传播
                    outputs = self.model(images)
                    
                    # 根据模型类型调整输出和计算准确率
                    if isinstance(self.model, CRNN):
                        # CRNN输出形状: (seq_len, batch_size, num_classes)
                        _, predicted = torch.max(outputs, 2)
                        predicted = predicted.view(-1)
                        labels = labels.view(-1)
                        
                        # 保存所有预测和标签
                        all_preds.extend(predicted.cpu().numpy())
                        all_labels.extend(labels.cpu().numpy())
                        
                        # 只计算有效标签的准确率
                        mask = labels != 0
                        if mask.sum() > 0:
                            correct += (predicted[mask] == labels[mask]).sum().item()
                            total += mask.sum().item()
                    else:
                        # CNNMLP输出形状: (batch_size, num_classes)
                        _, predicted = torch.max(outputs.data, 1)
                        
                        # 保存所有预测和标签
                        all_preds.extend(predicted.cpu().numpy())
                        all_labels.extend(labels.cpu().numpy())
                        
                        # 计算准确率
                        total += labels.size(0)
                        correct += (predicted == labels).sum().item()
        
        accuracy = correct / total if total > 0 else 0
        print(f'\nFinal Accuracy: {accuracy:.4f}')
        
        # 生成混淆矩阵
        self.generate_confusion_matrix(all_preds, all_labels)
        
        return accuracy
    
    def generate_confusion_matrix(self, all_preds, all_labels):
        """
        生成混淆矩阵
        
        Args:
            all_preds: 所有预测结果
            all_labels: 所有真实标签
        """
        # 只考虑有效标签
        mask = [label != 0 for label in all_labels]
        filtered_preds = [all_preds[i] for i, m in enumerate(mask) if m]
        filtered_labels = [all_labels[i] for i, m in enumerate(mask) if m]
        
        # 生成混淆矩阵
        cm = confusion_matrix(filtered_labels, filtered_preds, normalize='true')
        
        # 绘制混淆矩阵
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=False, cmap='Blues')
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        
        # 保存混淆矩阵
        model_type = 'crnn' if isinstance(self.model, CRNN) else 'cnn_mlp'
        cm_path = os.path.join('./saved_models', f'{model_type}_confusion_matrix.png')
        plt.savefig(cm_path, dpi=300)
        print(f'Confusion matrix saved to {cm_path}')
        plt.close()

def compare_models(train_dir, test_dir, epochs=5, batch_size=64):
    """
    对比CRNN和CNN+MLP模型的性能
    
    Args:
        train_dir: 训练数据目录
        test_dir: 测试数据目录
        epochs: 训练轮数
        batch_size: 批次大小
    """
    print("=== 开始模型对比实验 ===\n")
    
    # 训练和评估CRNN模型
    print("1. 训练和评估CRNN模型")
    crnn_model = CRNN(num_classes=3755)
    crnn_trainer = ModelTrainer(crnn_model, train_dir, test_dir)
    crnn_trainer.train(epochs=epochs, batch_size=batch_size)
    crnn_evaluator = ModelEvaluator(crnn_model, test_dir)
    crnn_accuracy = crnn_evaluator.evaluate()
    
    # 训练和评估CNN+MLP模型
    print("\n2. 训练和评估CNN+MLP模型")
    cnn_mlp_model = CNNMLP(num_classes=3755)
    cnn_mlp_trainer = ModelTrainer(cnn_mlp_model, train_dir, test_dir)
    cnn_mlp_trainer.train(epochs=epochs, batch_size=batch_size)
    cnn_mlp_evaluator = ModelEvaluator(cnn_mlp_model, test_dir)
    cnn_mlp_accuracy = cnn_mlp_evaluator.evaluate()
    
    # 生成对比报告
    print("\n=== 模型对比报告 ===")
    print(f"CRNN模型准确率: {crnn_accuracy:.4f}")
    print(f"CNN+MLP模型准确率: {cnn_mlp_accuracy:.4f}")
    
    if crnn_accuracy > cnn_mlp_accuracy:
        print("结论: CRNN模型性能优于CNN+MLP模型")
    elif cnn_mlp_accuracy > crnn_accuracy:
        print("结论: CNN+MLP模型性能优于CRNN模型")
    else:
        print("结论: 两种模型性能相当")
    
    print("\n所有模型训练和评估完成！")

if __name__ == '__main__':
    # 训练参数
    train_dir = '../../data/train'
    test_dir = '../../data/test'
    epochs = 5
    batch_size = 64
    
    # 执行模型对比
    compare_models(train_dir, test_dir, epochs=epochs, batch_size=batch_size)
