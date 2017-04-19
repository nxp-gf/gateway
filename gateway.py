import json
from broker import MQTTBroker
import threading
import time
import commands


TOPIC_GW2SVR_GET_REG_REQ     = "tgt/server/evt/get_reg_req"
TOPIC_GW2SVR_REG_GW_REQ      = "tgt/server/evt/gw_reg_req"
TOPIC_GW2SVR_INIT_GW_RESP    = "tgt/server/evt/init_gw_resp"
TOPIC_GW2SVR_DEL_GW_RESP     = "tgt/server/evt/delete_gw_resp"
TOPIC_GW2SVR_HEARTBEAT_REQ   = "tgt/server/evt/heartbeat_req"
TOPIC_GW2SVR_CARD_ACV_RESP   = "tgt/server/evt/card_activate_resp"
TOPIC_GW2SVR_CARD_DETECT_REQ = "tgt/server/evt/card_detect_req"
TOPIC_GW2SVR_MAC_REG_RESP    = "tgt/server/evt/app_mac_resp"
TOPIC_GW2SVR_MAC_DEL_RESP    = "tgt/server/evt/mac_delete_resp"

TOPIC_SVR2GW_GET_REG_RESP    = "tgt/1/evt/get_reg_resp"
TOPIC_SVR2GW_REG_GW_RESP     = "tgt/1/evt/gw_reg_resp"
TOPIC_SVR2GW_INIT_GW_REQ     = "tgt/1/evt/init_gw_req"
TOPIC_SVR2GW_DEL_GW_REQ      = "tgt/1/evt/delete_gw_req"
TOPIC_SVR2GW_HEARTBEAT_RESP  = "tgt/1/evt/heartbeat_resp"
TOPIC_SVR2GW_CARD_ACV_REQ    = "tgt/1/evt/card_activate_req"
TOPIC_SVR2GW_CARD_DETECT_RESP= "tgt/1/evt/card_detect_resp"
TOPIC_SVR2GW_MAC_REG_REQ     = "tgt/1/evt/app_mac_req"
TOPIC_SVR2GW_MAC_DEL_REQ     = "tgt/1/evt/mac_delete_req"

TOPIC_GW2LORA_CARD_ACV       = "tgt/lora/card_activate"
TOPIC_LORA2GW_CARD_DETECT    = "tgt/gw/card_detect"
TOPIC_LORA2GW_CARD_ACV_RESP  = "tgt/gw/card_activate_resp"

class WifiGateway:
    def __init__(self, svrip, svrport):
        self.gwId = 1
        self.wifiEnabled = 1
        self.DLNAEnabled = 1
        self.wifiBandwidth = 1000
        self.__loraBroker = MQTTBroker('localhost', 1883)
        self.__loraBroker.addHandler(TOPIC_LORA2GW_CARD_DETECT, self.lora_card_detect)
        self.__loraBroker.addHandler(TOPIC_LORA2GW_CARD_ACV_RESP, self.lora_card_activate_resp)
        self.__loraBroker.loopStart()

        self.__svrBroker = MQTTBroker(svrip, svrport)
        self.__svrBroker.addHandler(TOPIC_SVR2GW_GET_REG_RESP, self.svr_get_registration_info_resp)
        self.__svrBroker.addHandler(TOPIC_SVR2GW_REG_GW_RESP, self.svr_register_gateway_resp)
        self.__svrBroker.addHandler(TOPIC_SVR2GW_INIT_GW_REQ, self.svr_init_gateway_req)
        self.__svrBroker.addHandler(TOPIC_SVR2GW_DEL_GW_REQ, self.svr_delete_gateway_req)
        self.__svrBroker.addHandler(TOPIC_SVR2GW_HEARTBEAT_RESP, self.svr_gateway_heartbeat_resp)
        self.__svrBroker.addHandler(TOPIC_SVR2GW_CARD_ACV_REQ, self.svr_card_activate_req)
        self.__svrBroker.addHandler(TOPIC_SVR2GW_CARD_DETECT_RESP, self.svr_card_detect_resp)
        self.__svrBroker.addHandler(TOPIC_SVR2GW_MAC_REG_REQ, self.svr_mac_register_req)
        self.__svrBroker.addHandler(TOPIC_SVR2GW_MAC_DEL_REQ, self.svr_mac_delete_req)
        self.__svrBroker.loopStart()
        self.heartBeatTimer = threading.Timer(10, self.gateway_heartbeat_req, '')
        self.heartBeatTimer.start()
        self.seqNumber = 0
        (status, err_msg) = commands.getstatusoutput('gateway.sh init')
        self.register_gateway_req()

    def get_registration_info_req(self):
        payload = {'gw_id':self.gwId}
        self.__svrBroker.pubMessage(TOPIC_GW2SVR_GET_REG_REQ, json.dumps(payload))

    def register_gateway_req(self):
        payload = {'gw_id':self.gwId, 'wifi':self.wifiEnabled, 'wifi_bandwidth':self.wifiBandwidth, 'dlna':self.DLNAEnabled}
        self.__svrBroker.pubMessage(TOPIC_GW2SVR_GET_REG_REQ, json.dumps(payload))

    def init_gateway_resp(self, status, msg):
        payload = {'gw_id':self.gwId, 'status':status, 'err_msg':msg}
        self.__svrBroker.pubMessage(TOPIC_GW2SVR_INIT_GW_RESP, json.dumps(payload))

    def delete_gateway_resp(self, status, msg):
        payload = {'gw_id':self.gwId, 'status':status, 'err_msg':msg}
        self.__svrBroker.pubMessage(TOPIC_GW2SVR_DEL_GW_RESP, json.dumps(payload))

    def gateway_heartbeat_req(self):
        self.seqNumber += 1
        payload = {'gw_id':self.gwId, 'seq_number':self.seqNumber}
        self.__svrBroker.pubMessage(TOPIC_GW2SVR_HEARTBEAT_REQ, json.dumps(payload))
        self.heartBeatTimer = threading.Timer(10, self.gateway_heartbeat_req, '')
        self.heartBeatTimer.start()

    def card_activate_resp(self, card, status, msg):
        payload = {'gw_id':self.gwId, 'card_id':card, 'status':status, 'err_msg':msg}
        self.__svrBroker.pubMessage(TOPIC_GW2SVR_CARD_ACV_RESP, json.dumps(payload))

    def card_detect_req(self, card, signal):
        payload = {'gw_id':self.gwId, 'card_id':card, 'signal_intensity':signal}
        self.__svrBroker.pubMessage(TOPIC_GW2SVR_CARD_DETECT_REQ, json.dumps(payload))

    def mac_register_resp(self, card, status, msg):
        payload = {'gw_id':self.gwId, 'card_id':card, 'status':status, 'err_msg':msg}
        self.__svrBroker.pubMessage(TOPIC_GW2SVR_MAC_REG_RESP, json.dumps(payload))

    def mac_delete_resp(self, card, mac, status, msg):
        payload = {'gw_id':self.gwId, 'card_id':card, 'mac':mac, 'status':status, 'err_msg':msg}
        self.__svrBroker.pubMessage(TOPIC_GW2SVR_MAC_DEL_RESP, json.dumps(payload))

    def lora_card_detect(self, payload):
        msg = json.loads(payload)
        print("Get lora card detect:card(%d) signal(%d)" % (msg['card_id'], msg['signal']))
        self.card_detect_req(msg['card_id'], msg['signal'])

    def lora_card_activate_resp(self, payload):
        msg = json.loads(payload)
        print("Get lora activate resp:card(%d) status(%d) msg(%s)" % (msg['card_id'], msg['status'], msg['err_msg']))
        self.card_activate_resp(msg['card_id'], msg['status'], msg['err_msg'])

    def svr_get_registration_info_resp(self, payload):
        msg = json.loads(payload)
        print("Get registration info resp:status(%d) err_msg(%s)" % (msg['status'], msg['err_msg']))

    def svr_register_gateway_resp(self, payload):
        msg = json.loads(payload)
        print("Get register gateway resp:status(%d) err_msg(%s)" % (msg['status'], msg['err_msg']))

    def svr_init_gateway_req(self, payload):
        print("Get init gateway req")
        (status, err_msg) = commands.getstatusoutput('gateway.sh init')
        self.heartBeatTimer = threading.Timer(10, self.gateway_heartbeat_req, '')
        self.heartBeatTimer.start()
        self.init_gateway_resp(status, err_msg)

    def svr_delete_gateway_req(self, payload):
        print("Get delete gateway req")
        self.heartBeatTimer.cancel()
        (status, err_msg) = commands.getstatusoutput('gateway.sh stop')
        self.delete_gateway_resp(status, err_msg)

    def svr_gateway_heartbeat_resp(self, payload):
        msg = json.loads(payload)
        print("Get gateway heartbeat resp:seq_number(%d)" % (msg['seq_number']))

    def svr_card_activate_req(self, payload):
        msg = json.loads(payload)
        print("Get card activate req:card_id(%d)" % (msg['card_id']))

    def svr_card_detect_resp(self, payload):
        msg = json.loads(payload)
        print("Get card detect resp:card_id(%d) status(%d) err_msg(%s)" % (msg['card_id'],msg['status'], msg['err_msg']))

    def svr_mac_register_req(self, payload):
        msg = json.loads(payload)
        print("Get mac register req:card_id(%d) mac(%s) membership_level(%d) wifi_bandwidth(%d)" % (msg['card_id'], msg['mac'], msg['membership_level'], msg['wifi_bandwidth']))
        (status, err_msg) = commands.getstatusoutput('gateway.sh macadd %s %d' % (msg['mac'], msg['membership_level']))
        self.mac_register_resp(msg['card_id'], status, err_msg)

    def svr_mac_delete_req(self, payload):
        msg = json.loads(payload)
        print("Get mac delete req: card_id(%d) mac(%s)" % (msg['card_id'], msg['mac']))
        (status, err_msg) = commands.getstatusoutput('gateway.sh macdel %s' % msg['mac'])
        self.mac_delete_resp(msg['card_id'], msg['mac'], status, err_msg)


gw = WifiGateway('10.193.20.97', 1883)

while 1:
    time.sleep(10)
    print("running")
