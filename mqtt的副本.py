from flask import Flask, jsonify, request  
from flask_socketio import SocketIO, emit  
import paho.mqtt.client as mqtt  
from flask_cors import CORS  

app = Flask(__name__)  
# 允许所有来源  
socketio = SocketIO(app, cors_allowed_origins="*")  
CORS(app)  

# MQTT 配置  
MQTT_BROKER = '47.99.113.166'  
MQTT_PORT = 1883  
MQTT_TOPIC = 'light/control'  

# 连接到 MQTT 服务器并设置回调  
def on_connect(client, userdata, flags, rc):  
    print("Connected to MQTT Broker")  
    client.subscribe(MQTT_TOPIC)  # 订阅主题  

def on_message(client, userdata, msg):  
    message = msg.payload.decode()  
    print(f"Message received: {message}")  
    # 使用结构化的消息格式  
    socketio.emit('mqtt_message', {'type': 'mqtt_message', 'message': message})  # 向所有连接的客户端发送消息  

mqtt_client = mqtt.Client()  
mqtt_client.on_connect = on_connect  
mqtt_client.on_message = on_message  
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)  
mqtt_client.loop_start()  

@app.route('/publish', methods=['POST'])  
def publish():  
    message = request.json.get('message')  
    if message:  # 确保消息存在  
        print(f'Received message: {message}')  
        mqtt_client.publish(MQTT_TOPIC, message)  
        return jsonify({"status": "Message sent", "message": message}), 200  # 返回 200 状态码  
    return jsonify({"status": "Error", "message": "No message provided"}), 400  # 返回 400 错误状态  

@socketio.on('send_message')  
def handle_send_message(data):  
    message = data.get('message')  # 使用 get 方法以避免 KeyError  
    if message:  # 确保消息存在  
        mqtt_client.publish(MQTT_TOPIC, message)  
        emit('response_message', {'status': 'Message sent', 'message': message}, broadcast=True)  # 使用 broadcast 让所有连接的客户端都能收到  
    else:  
        emit('response_message', {'status': 'Error', 'message': 'No message provided'}, broadcast=True)  # 发送错误通知  

if __name__ == '__main__':  
    socketio.run(app, debug=True)