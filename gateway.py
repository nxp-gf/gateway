import json
from broker import MQTTBroker
import threading
import time
import commands


TOPIC_GW2SVR_GET_REG_REQ     = "tgt/server/evt/get_reg_req"
TOPIC_GW2SVR_REG_GW_REQ      = "tgt/server/evt/gw_reg_req"
TOPIC_GW2SVR_DEL_GW_RESP     = "tgt/server/evt/delete_gw_resp"
TOPIC_GW2SVR_HEARTBEAT_REQ   = "tgt/server/evt/heartbeat_req"
TOPIC_GW2SVR_CARD_ACV_RESP   = "tgt/server/evt/card_activate_resp"
TOPIC_GW2SVR_CARD_DETECT_REQ = "tgt/server/evt/card_detect_req"
TOPIC_GW2SVR_MAC_REG_RESP    = "tgt/server/evt/app_mac_resp"
TOPIC_GW2SVR_MAC_DEL_RESP    = "tgt/server/evt/mac_delete_resp"

TOPIC_SVR2GW_GET_REG_RESP    = "tgt/1/evt/get_reg_resp"
TOPIC_SVR2GW_REG_GW_RESP     = "tgt/1/evt/gw_reg_resp"
TOPIC_SVR2GW_DEL_GW_REQ      = "tgt/1/evt/delete_gw_req"
TOPIC_SVR2GW_HEARTBEAT_RESP  = "tgt/1/evt/heartbeat_resp"
TOPIC_SVR2GW_CARD_ACV_REQ    = "tgt/1/evt/card_activate_req"
TOPIC_SVR2GW_CARD_DETECT_RESP= "tgt/1/evt/card_detect_resp"
TOPIC_SVR2GW_MAC_REG_REQ     = "tgt/1/evt/app_mac_req"
TOPIC_SVR2GW_MAC_DEL_REQ     = "tgt/1/evt/mac_delete_req"

class WifiGateway:
    def __init__(self, svrip, svrport):
        self.gwId = 1
        self.wifiEnabled = 1
        self.DLNAEnabled = 1
        self.wifiBandwidth = 1000
        self.broker = MQTTBroker(svrip, svrport)
        self.broker.addHandler(TOPIC_SVR2GW_GET_REG_RESP, self.get_registration_info_resp)
        self.broker.addHandler(TOPIC_SVR2GW_REG_GW_RESP, self.register_gateway_resp)
        self.broker.addHandler(TOPIC_SVR2GW_DEL_GW_REQ, self.delete_gateway_req)
        self.broker.addHandler(TOPIC_SVR2GW_HEARTBEAT_RESP, self.gateway_heartbeat_resp)
        self.broker.addHandler(TOPIC_SVR2GW_CARD_ACV_REQ, self.card_activate_req)
        self.broker.addHandler(TOPIC_SVR2GW_CARD_DETECT_RESP, self.card_detect_resp)
        self.broker.addHandler(TOPIC_SVR2GW_MAC_REG_REQ, self.mac_register_req)
        self.broker.addHandler(TOPIC_SVR2GW_MAC_DEL_REQ, self.mac_delete_req)
        self.heartBeatTimer = threading.Timer(10, self.gateway_heartbeat_req, '')
        self.heartBeatTimer.start()
        self.seqNumber = 0
        self.register_gateway_req()

    def get_registration_info_req(self):
        payload = {'gw_id':self.gwId}
        self.broker.pubMessage(TOPIC_GW2SVR_GET_REG_REQ, json.dumps(payload))

    def register_gateway_req(self):
        payload = {'gw_id':self.gwId, wifi:self.wifiEnabled, 'wifi_bandwidth':self.wifiBandwidth, 'dlna':self.DLNAEnabled}
        self.broker.pubMessage(TOPIC_GW2SVR_GET_REG_REQ, json.dumps(payload))

    def delete_gateway_resp(self, status, err, msg):
        payload = {'gw_id':self.gwId, 'status':status, 'err_type':err, 'err_msg':msg}
        self.broker.pubMessage(TOPIC_GW2SVR_DEL_GW_RESP, json.dumps(payload))

    def gateway_heartbeat_req(self):
        self.seqNumber += 1
        payload = {'gw_id':self.gwId, 'seq_number':self.seqNumber}
        self.broker.pubMessage(TOPIC_GW2SVR_HEARTBEAT_REQ, json.dumps(payload))
        self.heartBeatTimer = threading.Timer(10, self.gateway_heartbeat_req, '')
        self.heartBeatTimer.start()

    def card_activate_resp(self, card, status, err, msg):
        payload = {'gw_id':self.gwId, 'card_id':card, 'status':status, 'err_type':err, 'err_msg':msg}
        self.broker.pubMessage(TOPIC_GW2SVR_CARD_ACV_RESP, json.dumps(payload))

    def card_detect_req(self, card, signal):
        payload = {'gw_id':self.gwId, 'card_id':card, 'signal_intensity':signal}
        self.broker.pubMessage(TOPIC_GW2SVR_CARD_DETECT_REQ, json.dumps(payload))

    def mac_register_resp(self, card, status, err, msg):
        payload = {'gw_id':self.gwId, 'card_id':card, 'status':status, 'err_type':err, 'err_msg':msg}
        self.broker.pubMessage(TOPIC_GW2SVR_MAC_REG_RESP, json.dumps(payload))

    def mac_delete_resp(self, card, mac, status, err, msg):
        payload = {'gw_id':self.gwId, 'card_id':card, 'mac':mac, 'status':status, 'err_type':err, 'err_msg':msg}
        self.broker.pubMessage(TOPIC_GW2SVR_MAC_DEL_RESP, json.dumps(payload))

    def get_registration_info_resp(self, payload):
        msg = json.loads(payload)
        print("Get registration info resp:status(%d) err_type(%d) err_msg(%s)" % (msg['status'], msg['err_type'], msg['err_msg']))

    def register_gateway_resp(self, payload):
        msg = json.loads(payload)
        print("Get register gateway resp:status(%d) err_type(%d) err_msg(%s)" % (msg['status'], msg['err_type'], msg['err_msg']))

    def delete_gateway_req(self, payload):
        print("Get delete gateway req")
        status = 0
        (err, err_msg) = commands.getstatusoutput('gateway.sh stop')
        if (err != 0):
            status = 1
        self.delete_gateway_resp(status, err, msg):

    def gateway_heartbeat_resp(self, payload):
        msg = json.loads(payload)
        print("Get gateway heartbeat resp:seq_number(%d)" % (msg['seq_number']))

    def card_activate_req(self, payload):
        msg = json.loads(payload)
        print("Get card activate req:card_id(%d)" % (msg['card_id']))

    def card_detect_resp(self, payload):
        msg = json.loads(payload)
        print("Get card detect resp:card_id(%d) status(%d) err_type(%d) err_msg(%s)" % (msg['card_id'],msg['status'], msg['err_type'], msg['err_msg']))

    def mac_register_req(self, payload):
        msg = json.loads(payload)
        print("Get mac register req:card_id(%d) mac(%s) membership_level(%d) wifi_bandwidth(%d)" % (msg['card_id'], msg['mac'], msg['membership_level'], msg['wifi_bandwidth']))

    def mac_delete_req(self, payload):
        msg = json.loads(payload)
        print("Get mac delete req: card_id(%d) mac(%s)" % (msg['card_id'], msg['mac']))


gw = WifiGateway('localhost', 1883)
gw.broker.loopForever()
