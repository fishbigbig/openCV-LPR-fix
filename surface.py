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

app = Flask(__name__)  

@app.route('/upload', methods=['POST'])  
def upload():  
    # 从 POST 请求中获取图像文件  
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
        for resize_rate in resize_rates:  
            result, roi, color = predictor.predict(img_bgr, resize_rate)  
            if result:  
                break  

        return jsonify({"result": result, "roi": roi.tolist(), "color": color}), 200  
    except Exception as e:  
        return jsonify({"error": str(e)}), 500  


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

if __name__ == '__main__':  
    predictor = predict.CardPredictor()  
    predictor.train_svm()  
    app.run(debug=True)  # 启动Flask应用
    win = tk.Tk()  
    surface = Surface(win)  
    win.protocol('WM_DELETE_WINDOW', close_window)  
    win.mainloop()
