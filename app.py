#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手写汉字识别 Flask Web应用
使用EasyOCR进行汉字识别
"""

import os
import base64
import uuid
import time
import numpy as np
import cv2
from flask import Flask, render_template, request, jsonify
import easyocr
from PIL import Image
import io

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("正在加载EasyOCR模型...")
start_time = time.time()
reader = easyocr.Reader(['ch_sim'], gpu=False, verbose=False)
print(f"模型加载完成，耗时: {time.time() - start_time:.2f}秒")


def preprocess_image(image_np):
    """图像预处理：增强对比度"""
    try:
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        enhanced = cv2.equalizeHist(blurred)

        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)

        return enhanced
    except Exception as e:
        print(f"图像预处理错误: {e}")
        return image_np


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def base64_to_image(base64_str):
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    return image


def process_ocr_result(result):
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
        print(f"处理OCR结果错误: {e}")

    return texts, confidences


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/recognize', methods=['POST'])
def recognize():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': '请求数据为空'}), 400

        image_data = data.get('image', '')
        if not image_data:
            return jsonify({'success': False, 'error': '图片数据为空'}), 400

        image = base64_to_image(image_data)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_np = np.array(image)

        processed_np = preprocess_image(image_np)

        timestamp = int(time.time() * 1000)
        filename = f"temp_{timestamp}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        Image.fromarray(processed_np).save(filepath)

        result = reader.readtext(processed_np)
        print(f"EasyOCR返回: {result}")
        texts, confidences = process_ocr_result(result)

        return jsonify({
            'success': True,
            'texts': texts,
            'confidences': confidences,
            'image_url': f'/static/uploads/{filename}'
        })

    except Exception as e:
        import traceback
        print(f"OCR错误: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400

        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            image = Image.open(filepath)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image_np = np.array(image)

            result = reader.readtext(image_np)
            texts, confidences = process_ocr_result(result)

            return jsonify({
                'success': True,
                'texts': texts,
                'confidences': confidences,
                'image_url': f'/static/uploads/{filename}'
            })

        return jsonify({'success': False, 'error': '不支持的文件格式'}), 400

    except Exception as e:
        import traceback
        print(f"上传识别错误: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_uploaded_files():
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        return jsonify({'success': True, 'message': '清理完成'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)