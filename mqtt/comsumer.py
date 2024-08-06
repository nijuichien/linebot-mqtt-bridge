import paho.mqtt.client as mqtt
import logging
import time

# 設置日誌
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MQTT broker設置
broker_address = "localhost"  # 如果在同一台機器上運行，使用 localhost
broker_port = 1883
topic = "linebot"

# 當連接到MQTT broker時的回調函數
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logger.info("Successfully connected to MQTT broker")
        logger.info(f"Subscribing to topic: {topic}")
        client.subscribe(topic)
    else:
        logger.error(f"Failed to connect, return code: {rc}")

# 當收到消息時的回調函數
def on_message(client, userdata, msg):
    logger.info(f"Received message '{msg.payload.decode()}' on topic '{msg.topic}'")

# 當訂閱完成時的回調函數
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    logger.info(f"Subscribed to topic: {topic}")

# 當斷開連接時的回調函數
def on_disconnect(client, userdata, rc, reason=None, properties=None):
    if rc != 0:
        logger.warning(f"Unexpected disconnection. RC: {rc}, Reason: {reason}")
    else:
        logger.info("Disconnected successfully")

# 主程序
def main():
    try:
        # 創建MQTT客戶端實例
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        # 設置回調函數
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_subscribe = on_subscribe
        client.on_disconnect = on_disconnect

        logger.info(f"Connecting to broker at {broker_address}:{broker_port}")
        
        # 連接到MQTT broker
        client.connect(broker_address, broker_port, 60)

        # 開始網絡循環
        logger.info("Starting network loop...")
        client.loop_start()

        # 保持程序運行
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting...")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Disconnected from broker")

if __name__ == "__main__":
    main()