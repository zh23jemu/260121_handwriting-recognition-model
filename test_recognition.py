import requests
import json
import os

# 登录获取token
def login():
    url = 'http://localhost:8000/api/auth/login/'
    data = {
        'username': 'admin',
        'password': 'admin123'
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=data, headers=headers)
    print(f"Login status: {response.status_code}")
    if response.status_code == 200:
        return response.json()['access']
    else:
        print(f"Login failed: {response.text}")
        return None

# 测试识别API
def test_recognition(token):
    url = 'http://localhost:8000/api/recognition/recognize/'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # 使用一个简单的测试图像
    # 创建一个简单的测试图像文件
    test_image_path = 'test_image.png'
    from PIL import Image, ImageDraw
    img = Image.new('L', (100, 100), 255)
    draw = ImageDraw.Draw(img)
    draw.text((20, 40), '一', fill=0, font=None)
    img.save(test_image_path)
    
    try:
        with open(test_image_path, 'rb') as f:
            files = {
                'image': ('test_image.png', f, 'image/png')
            }
            response = requests.post(url, headers=headers, files=files)
            print(f"Recognition status: {response.status_code}")
            print(f"Recognition response: {response.text}")
    finally:
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

if __name__ == '__main__':
    print("Testing handwriting recognition API...")
    token = login()
    if token:
        print("Login successful, testing recognition...")
        test_recognition(token)
    else:
        print("Login failed, cannot test recognition.")
