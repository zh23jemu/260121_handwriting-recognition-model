# 手写汉字识别系统

## 项目介绍

手写汉字识别系统是一个基于深度学习的智能识别系统，能够准确识别手写汉字。系统采用CRNN（卷积循环神经网络）模型，结合前端Vue.js框架和后端Django REST Framework，实现了从图像预处理到模型识别的完整流程。

## 功能特性

- **手写汉字识别**：支持手绘输入和图像上传两种方式
- **用户管理**：完整的用户注册、登录和权限管理系统
- **管理员功能**：用户管理、模型训练等管理员专属功能
- **识别历史**：记录用户的识别历史，支持导出功能
- **模型训练**：支持重新训练模型以提高识别准确率
- **响应式设计**：适配不同屏幕尺寸的设备

## 技术栈

### 前端
- Vue.js 3
- Vue Router
- Axios
- Vite

### 后端
- Django 4.2
- Django REST Framework
- PyTorch
- JWT Authentication
- MySQL/SQLite

### 深度学习模型
- CRNN (Convolutional Recurrent Neural Network)
- CTC Loss
- Adam Optimizer

## 项目结构

```
handwriting-recognition-model/
├── frontend/               # 前端项目
│   ├── public/             # 静态资源
│   ├── src/                # 源代码
│   │   ├── components/     # 组件
│   │   ├── router/         # 路由
│   │   ├── views/          # 页面
│   │   ├── App.vue         # 根组件
│   │   └── main.js         # 入口文件
│   ├── package.json        # 前端依赖
│   └── vite.config.js      # Vite配置
├── handwriting_project/    # 后端项目
│   ├── core/               # 用户管理模块
│   ├── models/             # 模型定义和训练
│   │   ├── saved_models/   # 保存的模型
│   ├── recognition/        # 识别功能模块
│   ├── manage.py           # Django管理脚本
│   └── settings.py         # Django配置
├── char_dict               # 字符字典
├── common_chars.txt        # 常用汉字列表
├── requirements.txt        # Python依赖
└── docker-compose.yml      # Docker配置
```

## 安装与部署

### 方法一：本地部署

#### 1. 环境准备
- Python 3.8+
- Node.js 16+
- MySQL 8.0+

#### 2. 前端安装
```bash
# 进入前端目录
cd frontend
# 安装依赖
npm install
# 构建生产版本
npm run build
```

#### 3. 后端安装
```bash
# 安装Python依赖
pip install -r requirements.txt

# 运行数据库迁移
cd handwriting_project
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser
```

#### 4. 启动服务
```bash
# 启动后端开发服务器
python manage.py runserver

# 启动前端开发服务器（在另一个终端）
cd frontend
npm run dev
```

### 方法二：Docker部署

#### 1. 安装Docker
- 下载并安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)

#### 2. 启动服务
```bash
# 在项目根目录运行
docker-compose up -d
```

#### 3. 访问系统
- 前端：http://localhost:5173
- 后端API：http://localhost:8000
- Django管理后台：http://localhost:8000/admin

## 使用指南

### 1. 基本使用
1. **注册/登录**：首次使用需要注册账号
2. **手写识别**：在识别页面绘制或上传手写汉字
3. **查看结果**：系统会显示识别结果和置信度
4. **查看历史**：在历史记录页面查看过去的识别记录

### 2. 管理员功能
1. **登录管理员账号**：使用具有管理员权限的账号登录
2. **访问管理员控制台**：点击页面右上角的"管理员控制台"按钮
3. **用户管理**：在控制台中点击"用户管理"，可添加、编辑、删除用户
4. **模型训练**：点击"模型训练"，可重新训练识别模型

### 3. 模型训练
1. **准备数据集**：确保数据集中包含足够的手写汉字样本
2. **配置训练参数**：在模型训练页面设置训练参数
3. **开始训练**：点击"开始训练"按钮
4. **查看训练结果**：训练完成后可查看准确率和损失曲线

## 模型信息

- **模型类型**：CRNN (Convolutional Recurrent Neural Network)
- **训练数据**：基于常用汉字的手写样本
- **识别范围**：支持1000个常用汉字
- **准确率**：约87.9%（测试集）

## 常见问题

### 1. 识别失败
- 检查图像是否清晰
- 确保只包含单个汉字
- 尝试调整图像大小和清晰度

### 2. 模型训练失败
- 检查数据集格式是否正确
- 确保有足够的训练样本
- 检查服务器资源是否充足

### 3. 用户管理问题
- 只有管理员可以创建和管理用户
- 普通用户只能修改自己的个人信息

## 开发与扩展

### 添加新功能
1. **前端**：在 `frontend/src/views/` 目录添加新页面
2. **后端**：在相应的应用目录添加新的视图和模型
3. **路由**：更新前端路由和后端URL配置

### 模型优化
1. **数据增强**：增加训练数据的多样性
2. **模型调整**：修改模型结构和超参数
3. **迁移学习**：利用预训练模型提高性能

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 联系方式

如有问题或建议，请联系项目维护者。

---

*项目开发时间：2026年1月*
