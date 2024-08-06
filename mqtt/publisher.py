import paho.mqtt.client as mqtt
import time


class MQClient():

    # MQTT broker設置
    broker_address = "mosquitto"
    broker_port = 1883
    topic = "linebot"
    # 創建MQTT客戶端實例
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def __init__(self) -> None:
        # 設置回調函數
        self.client.on_connect = self.on_connect

        # 連接到MQTT broker
        self.client.connect(self.broker_address, self.broker_port, 60)
    # 當連接到MQTT broker時的回調函數
    def on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"Connected with result code {rc}")

    def start(self):
        self.client.loop_start()
    def publish(self, message):
        try:
            self.client.publish(self.topic, message)
            print(f"Published: {message}")
        except KeyboardInterrupt:
            print("Stopping...")
    
    def close(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    client = MQClient()
    try:
        while True:
            message = f"Hello, MQTT! Time: {time.time()}"
            client.publish(message)
            time.sleep(5)  # 每5秒發布一次消息
    except KeyboardInterrupt:
        client.close()
# 發布消息
# try:
#     while True:
#         message = f"Hello, MQTT! Time: {time.time()}"
#         client.publish(topic, message)
#         print(f"Published: {message}")
#         time.sleep(5)  # 每5秒發布一次消息
# except KeyboardInterrupt:
#     print("Stopping...")

# 停止網絡循環並斷開連接
# client.loop_stop()
# client.disconnect()