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
TOPIC_SVR2GW_DEL_GW_REQ      = "tgt/1/evt/delete_gw_req"
TOPIC_SVR2GW_HEARTBEAT_RESP  = "tgt/1/evt/heartbeat_resp"
TOPIC_SVR2GW_CARD_ACV_REQ    = "tgt/1/evt/card_activate_req"
TOPIC_SVR2GW_CARD_DETECT_RESP= "tgt/1/evt/card_detect_resp"
TOPIC_SVR2GW_MAC_REG_REQ     = "tgt/1/evt/app_mac_req"
TOPIC_SVR2GW_MAC_DEL_REQ     = "tgt/1/evt/mac_delete_req"

class Server:
    def __init__(self):
        self.broker = MQTTBroker('localhost', 1883)
        self.broker.addHandler(TOPIC_GW2SVR_GET_REG_REQ, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_REG_GW_REQ, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_INIT_GW_RESP, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_DEL_GW_RESP, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_HEARTBEAT_REQ, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_CARD_ACV_RESP, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_CARD_DETECT_REQ, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_MAC_REG_RESP, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_MAC_DEL_RESP, self.dump_gw_msg)
        self.broker.loopStart()

    def dump_gw_msg(self, payload):
        print('Get msg from gateway: ' + payload)


svr = Server()
while 1:
    time.sleep(10)
