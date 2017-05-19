import paho.mqtt.client as mqtt
import time

class MQTTBroker:
    def __init__(self, ip='localhost', port=1883, usr=None, passwd=None):
        self.handlers = {}
        self.client = mqtt.Client()
        self.client.on_connect = self.__onMqttConnect
        self.client.on_message = self.__onMqttMessage
        if usr is not None:
            self.client.username_pw_set(usr, passwd)
        self.client.connect(ip, port, 60)
        self.ip = ip
        self.port = port

    def __onMqttMessage(self, client, userdata, msg):
        try:
<<<<<<< HEAD
            now = time.localtime()
            print('recv %d:%d:%d %s:%s' % (now.tm_hour, now.tm_min, now.tm_sec, msg.topic, msg.payload))
=======
>>>>>>> 717840a30f8f29ee932ffec442a6a09b5ecf8f44
            self.handlers[msg.topic](msg.topic, msg.payload)
        except Exception,e:
            print Exception,":",e

    def __onMqttConnect(self, client, userdata, flags, rc):
        print('Connected to MQTT broker(%s) with error code:%s' % (self.ip, str(rc)))

    def pubMessage(self, topic, msg):
<<<<<<< HEAD
        #print('publish topic:%s msg:%s' % (topic, msg))
        self.client.publish(topic, msg, qos=1)
=======
        print('publish topic:%s msg:%s' % (topic, msg))
        self.client.publish(topic, msg)
>>>>>>> 717840a30f8f29ee932ffec442a6a09b5ecf8f44

    def addHandler(self, topic, callback):
        self.handlers.setdefault(topic, callback)
        self.client.subscribe(topic, qos=1)

    def delHandler(self, topic):
        self.client.unsubscribe(topic)
        self.handlers.pop(topic)

    def loopStart(self):
        self.client.loop_start()

