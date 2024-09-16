<template>
	<view>
		<textarea v-model="messageContent" placeholder="输入消息..."></textarea>
		<button @click="sendPostMessage">发送消息</button>
		<text>Received Messages:</text>
		<view v-for="(msg, index) in messages" :key="index">{{ msg }}</view>
		<button @click="sendMessage('Hello from UniApp!')">Send Message</button>

	</view>
</template>

<script>
	import {
		io
	} from 'socket.io-client';

	export default {
		data() {
			return {
				socket: null,
				messageContent: '',
				messages: [] // 用于存储接收到的消息  
			};
		},
		onLoad() {
			this.connectSocket();
		},
		methods: {
			// POST发送消息到后端
			sendPostMessage() {
				uni.request({
					url: 'http://127.0.0.1:5000/publish',
					method: 'POST',
					data: {
						message: this.messageContent
					},
					success: (res) => {
						console.log('Message sent:', res.data);
						this.messageContent = '';
					},
					fail: (err) => {
						console.error('Error sending message:', err);
					}
				});
			},
			connectSocket() {
				this.socket = io('http://127.0.0.1:5000'); // 替换为你的后端地址和端口  

				this.socket.on('connect', () => {
					console.log('Socket.IO connected');
				});

				this.socket.on('mqtt_message', (data) => {
					console.log('Received MQTT message:', data);

					// 确保 data 对象存在 message 属性  
					if (data && data.message) {
						this.messages.push(data.message); // 将消息添加到列表  
					} else {
						console.warn('Received message format is incorrect:', data);
					}
				});

				this.socket.on('connect_error', (error) => {
					console.error('Socket.IO connection error:', error);
				});

				this.socket.on('disconnect', () => {
					console.log('Socket.IO disconnected');
				});
			},
			sendMessage(message) {
				console.log('Sending message:', message); // 添加调试信息  
				this.socket.emit('send_message', {
					message
				});
			}
		}
	};
</script>

<style>
	/* 你的样式代码 */
	view {
		margin: 10px 0;
	}

	button {
		margin-top: 20px;
	}
</style>