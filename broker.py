import paho.mqtt.client as mqtt

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
            self.handlers[msg.topic](msg.topic, msg.payload)
        except Exception,e:
            print Exception,":",e

    def __onMqttConnect(self, client, userdata, flags, rc):
        print('Connected to MQTT broker(%s) with error code:%s' % (self.ip, str(rc)))

    def pubMessage(self, topic, msg):
        print('publish topic:%s msg:%s' % (topic, msg))
        self.client.publish(topic, msg)

    def addHandler(self, topic, callback):
        self.handlers.setdefault(topic, callback)
        self.client.subscribe(topic, qos=1)

    def delHandler(self, topic):
        self.client.unsubscribe(topic)
        self.handlers.pop(topic)

    def loopStart(self):
        self.client.loop_start()

