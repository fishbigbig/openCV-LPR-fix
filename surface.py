import tkinter as tk  
from tkinter import ttk  
import predict  
import cv2  
from PIL import Image, ImageTk  
import threading  
import time  
import requests  
import numpy as np
from flask import Flask, request, jsonify  
import os  
import re  # 导入正则表达式模块
from datetime import datetime  # 确保导入 datetime 模块

app = Flask(__name__)  

# 获取当前日期并格式化为 "YYYY-MM-DD"
current_date = datetime.now().strftime("%Y-%m-%d")
UPLOAD_FOLDER = os.path.join('uploads', current_date)  # 指定上传文件保存的文件夹

# 确保日期文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def sanitize_file_name(plate_number):
    """去掉车牌号中的非法字符，只保留字母、数字和汉字"""
    return re.sub(r'[^A-Za-z0-9\u4e00-\u9fa5]', '', plate_number)

@app.route('/upload', methods=['POST'])  
def upload():  
    if 'file' not in request.files:  
        return jsonify({"error": "No file part!"}), 400  

    file = request.files['file']  

    if file.filename == '':  
        return jsonify({"error": "No selected file!"}), 400  

    try:  
        # 读取图像文件并进行处理
        img_array = np.frombuffer(file.read(), np.uint8)  
        img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  

        # 处理图像并返回识别结果
        resize_rates = (1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4)  
        plate_number = None  # 用于存储识别出来的车牌号
        roi = None  # 用于存储车牌区域
        color = None  # 用于存储颜色信息

        for resize_rate in resize_rates:  
            result, roi, color = predictor.predict(img_bgr, resize_rate)  
            if result:  
                plate_number = result  # 假设result是车牌号
                break  

        if plate_number is None:
            return jsonify({"error": "No plate detected!"}), 400

        # 如果 plate_number 是列表，将其转换为字符串
        if isinstance(plate_number, list):
            plate_number = ''.join(plate_number)  # 将列表中的元素合并为字符串

        # 构造文件名并保存文件
        sanitized_plate_number = sanitize_file_name(plate_number)

        # 如果清理后的车牌号为空，则返回错误
        if not sanitized_plate_number:
            return jsonify({"error": "Invalid plate number!"}), 400


         # 获取当前时间并格式化为 "YYYYMMDD_HHMMSS"  
        current_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")  
        
        # 构造文件名  
        file_name = f"{sanitized_plate_number}_{current_time}.jpg"  
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        
        # 保存原始图像
        if cv2.imwrite(file_path, img_bgr):
            return jsonify({"result": sanitized_plate_number, "roi": roi.tolist(), "color": color}), 200
        else:
            return jsonify({"error": "Failed to save image."}), 500

    except Exception as e:  
        return jsonify({"error": str(e)}), 500 

# @app.route('/upload', methods=['POST'])  
# def upload():  
#     # 从 POST 请求中获取图像文件  
#     if 'file' not in request.files:  
#         return jsonify({"error": "No file part!"}), 400  

#     file = request.files['file']  

#     if file.filename == '':  
#         return jsonify({"error": "No selected file!"}), 400  

#     try:  
#         # 读取图像文件并进行处理
#         img_array = np.frombuffer(file.read(), np.uint8)  
#         img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  

#         # 处理图像并返回识别结果
#         resize_rates = (1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4)  
#         for resize_rate in resize_rates:  
#             result, roi, color = predictor.predict(img_bgr, resize_rate)  
#             if result:  
#                 break  

#         return jsonify({"result": result, "roi": roi.tolist(), "color": color}), 200  
#     except Exception as e:  
#         return jsonify({"error": str(e)}), 500  


@app.route('/upload_url', methods=['POST'])  
def upload_url():  
    # 从 POST 请求中获取 URL  
    data = request.get_json()  
    image_url = data.get('url')  

    if not image_url:  
        return jsonify({"error": "No URL provided!"}), 400  

    try:  
        # 处理图像并返回识别结果
        result, roi, color = process_image(image_url)  
        
        return jsonify({"result": result, "roi": roi.tolist(), "color": color}), 200  
    except Exception as e:  
        return jsonify({"error": str(e)}), 500  
    
def process_image(url):  
    # 从 URL 加载图像
    response = requests.get(url, timeout=10)  
    response.raise_for_status()  

    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)  
    img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  

    # 在这里添加图像处理和预测代码
    resize_rates = (1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4)  
    for resize_rate in resize_rates:  
        r, roi, color = predictor.predict(img_bgr, resize_rate)  
        if r:  
            break  

    return r, roi, color

class Surface(ttk.Frame):  
    # 省略其他部分...

    def load_image_from_url(self, url):  
        try:  
            response = requests.get(url, timeout=10)  
            response.raise_for_status()  
            
            img_array = np.asarray(bytearray(response.content), dtype=np.uint8)  
            img_bgr = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  
            
            self.imgtk = self.get_imgtk(img_bgr)  
            self.image_ctl.configure(image=self.imgtk)  
            
            resize_rates = (1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4)  
            for resize_rate in resize_rates:  
                print("resize_rate:", resize_rate)  
                r, roi, color = self.predictor.predict(img_bgr, resize_rate)  
                if r:  
                    break  
            self.show_roi(r, roi, color)  
        
        except requests.exceptions.RequestException as e:  
            print(f"加载图片失败: {e}")  

    # 省略其他部分...
#窗口模式
# if __name__ == '__main__':  
#     predictor = predict.CardPredictor()  
#     predictor.train_svm()  
#     win = tk.Tk()  
#     surface = Surface(win)  
#     win.protocol('WM_DELETE_WINDOW', close_window)  
#     win.mainloop()

#api模式
if __name__ == '__main__':
    predictor = predict.CardPredictor()  
    predictor.train_svm()  
    app.run(debug=True)
