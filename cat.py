import tkinter as tk  
from tkinter import filedialog, messagebox  
from PIL import Image, ImageTk  
import cv2  
import numpy as np  
from tensorflow.keras.models import load_model  

MODEL_PATH = 'mobilenetv2.h5'  
IMAGE_SIZE = (224, 224)  
LABELS = ['cat', 'dog', 'other']  

# 加载预训练的模型  
try:  
    model = load_model(MODEL_PATH, compile=False)  
    print("模型加载成功！")  
except Exception as e:  
    print(f"加载模型时出错: {e}")  

def preprocess_image(image_path):  
    """预处理图像以适应模型输入"""  
    try:  
        img = cv2.imread(image_path)  
        img = cv2.resize(img, IMAGE_SIZE)  
        img = img.astype('float32') / 255.0  
        img = np.expand_dims(img, axis=0)  
        return img  
    except Exception as e:  
        messagebox.showerror("错误", f"图像预处理失败: {e}")  
        return None  

def identify_image():  
    """识别选定的图片"""  
    file_path = filedialog.askopenfilename(  
        title="选择一张图片",   
        filetypes=[  
            ("Image files", "*.jpg"),   
            ("Image files", "*.jpeg"),   
            ("Image files", "*.png"),  
            ("All files", "*.*")  
        ]  
    )  
    if file_path:  
        img = preprocess_image(file_path)  
        if img is not None:  
            btn_select.config(state=tk.DISABLED)  
            predictions = model.predict(img)  
            class_index = np.argmax(predictions[0])  
            label = LABELS[class_index]  
            show_image(file_path)  
            messagebox.showinfo("识别结果", f"识别到的动物: {label}")  
            btn_select.config(state=tk.NORMAL)  

def show_image(image_path):  
    """显示选定的图像"""  
    image = Image.open(image_path)  
    image = image.resize((300, 300), Image.LANCZOS)  # 使用 LANCZOS 代替 ANTIALIAS  
    img_tk = ImageTk.PhotoImage(image)  
    img_label.configure(image=img_tk)  
    img_label.image = img_tk  

root = tk.Tk()  
root.title("猫的识别器")  

btn_select = tk.Button(root, text="选择图片", command=identify_image)  
btn_select.pack(pady=20)  

img_label = tk.Label(root)  
img_label.pack(pady=20)  

root.mainloop()