"""
手写汉字识别调试脚本
"""
import cv2
import numpy as np
from PIL import Image
import easyocr

def preprocess_handwriting(image_path):
    """手写体专用预处理"""
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')

    width, height = image.size
    image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
    image_np = np.array(image)

    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

    gray = cv2.GaussianBlur(gray, (3, 3), 0.5)

    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(max(contours, key=cv2.contourArea))
        padding = 20
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(thresh.shape[1] - x, w + 2 * padding)
        h = min(thresh.shape[0] - y, h + 2 * padding)
        thresh = thresh[y:y+h, x:x+w]

    return thresh, image

def test_easyocr_params(image, original_image):
    """测试EasyOCR不同参数"""
    print("\n" + "="*50)
    print("开始测试EasyOCR...")
    print("="*50)

    reader = easyocr.Reader(['ch_sim'], gpu=False, verbose=False)

    test_configs = [
        {"name": "默认参数", "params": {}},
        {"name": "width_ths=0.3", "params": {"width_ths": 0.3}},
        {"name": "height_ths=0.3", "params": {"height_ths": 0.3}},
        {"name": "低置信度阈值", "params": {"min_size": 20}},
    ]

    for config in test_configs:
        print(f"\n测试: {config['name']}")
        try:
            if config['params']:
                result = reader.readtext(np.array(original_image), **config['params'])
            else:
                result = reader.readtext(np.array(original_image))
            print(f"  结果: {result}")
            if result:
                for item in result:
                    if len(item) >= 3:
                        text = item[1]
                        conf = item[2]
                        print(f"    识别: '{text}' 置信度: {conf:.4f}")
        except Exception as e:
            print(f"  错误: {e}")

def test_on_sample_images():
    """测试样本图片"""
    import os

    sample_dir = r"C:\!coding\260121_handwriting-recognition-model\data_other\train\00059"
    if not os.path.exists(sample_dir):
        print(f"样本目录不存在: {sample_dir}")
        return

    images = [f for f in os.listdir(sample_dir) if f.endswith('.png')][:5]

    if not images:
        print("没有找到样本图片")
        return

    print("\n" + "="*50)
    print("测试样本图片")
    print("="*50)

    reader = easyocr.Reader(['ch_sim'], gpu=False, verbose=False)

    for img_file in images:
        img_path = os.path.join(sample_dir, img_file)
        print(f"\n测试图片: {img_file}")

        thresh, original = preprocess_handwriting(img_path)

        try:
            result = reader.readtext(thresh)
            print(f"  预处理后识别: {result}")

            result2 = reader.readtext(np.array(original))
            print(f"  原图识别: {result2}")
        except Exception as e:
            print(f"  错误: {e}")

def main():
    print("手写汉字识别调试工具")
    print("="*50)

    test_on_sample_images()

    print("\n" + "="*50)
    print("问题诊断:")
    print("="*50)
    print("1. EasyOCR主要针对印刷体设计，手写体识别率较低")
    print("2. 手写体笔画变化大，OCR难以准确识别")
    print("3. 建议: 考虑使用专门的手写识别模型(如CRNN)")

if __name__ == "__main__":
    main()
