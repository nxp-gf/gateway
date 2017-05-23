import paho.mqtt.client as mqtt
import time

class MQTTBroker:
    def __init__(self, ip='localhost', port=1883, usr=None, pwd=None, id=''):
        self.handlers = {}
        if id != '':
            self.client = mqtt.Client(id, clean_session=False)
        else:
            self.client = mqtt.Client()
        self.client.on_connect = self.__onMqttConnect
        self.client.on_message = self.__onMqttMessage
        self.client.on_disconnect = self.__onMqttDisConnect
        if usr is not None:
            self.client.username_pw_set(usr, pwd)
        self.client.connect(ip, port, 60)
        self.ip = ip
        self.port = port
        self.__connected = False

    def __del__(self):
        self.client.disconnect()

    def __onMqttMessage(self, client, userdata, msg):
        try:
            now = time.localtime()
            print('recv %d:%d:%d %s:%s' % (now.tm_hour, now.tm_min, now.tm_sec, msg.topic, msg.payload))
            self.handlers[msg.topic](msg.topic, msg.payload)
        except Exception,e:
            print Exception,":",e

    def __onMqttConnect(self, client, userdata, flags, rc):
        print('Connected to MQTT broker(%s) with error code:%s' % (self.ip, str(rc)))
        if rc == 0:
            self.__connected = True

    def __onMqttDisConnect(self, client, userdata, rc):
        print('DisConnected to MQTT broker(%s) with error code:%s' % (self.ip, str(rc)))
        if rc == 0:
            self.__connected = False

    def waitConnect(self):
        while self.__connected == False:
            time.sleep(0.1)

    def pubMessage(self, topic, msg):
       # print('publish topic:%s msg:%s' % (topic, msg))
        self.client.publish(topic, msg, qos=2)

    def addHandler(self, topic, callback):
        self.handlers.setdefault(topic, callback)
        self.client.subscribe(topic, qos=2)

    def delHandler(self, topic):
        self.client.unsubscribe(topic)
        self.handlers.pop(topic)

    def loopStart(self):
        self.client.loop_start()

