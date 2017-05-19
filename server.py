import json,time
from broker import MQTTBroker
import threading
import commands

gwId = 1

TOPIC_GW2SVR_HEARTBEAT       = "tgt/server/evt/gw_heartbeat"
TOPIC_GW2SVR_GW_REG_REQ      = "tgt/server/evt/gw_reg_req"
TOPIC_GW2SVR_GW_WORK_RESP    = "tgt/server/evt/gw_work_resp"
TOPIC_GW2SVR_GW_STOP_RESP    = "tgt/server/evt/gw_stop_resp"
TOPIC_GW2SVR_GW_SYNC_RESP    = "tgt/server/evt/gw_sync_resp"
TOPIC_GW2SVR_MAC_ADD_RESP    = "tgt/server/evt/mac_add_resp"
TOPIC_GW2SVR_MAC_DEL_RESP    = "tgt/server/evt/mac_delete_resp"
TOPIC_GW2SVR_CARD_DETECT     = "tgt/server/evt/card_detect_req"
TOPIC_GW2SVR_CARD_ACV        = "tgt/server/evt/card_detect_req_sync_mode"
TOPIC_GW2SVR_GW_CHGPWR_RESP  = "tgt/server/evt/gw_chgpwr_resp"

TOPIC_SVR2GW_GW_CHGPWR       = "tgt/"+str(gwId)+"/evt/gw_chgpwr_reg"
TOPIC_SVR2GW_GW_REG_RESP     = "tgt/"+str(gwId)+"/evt/gw_reg_resp"
TOPIC_SVR2GW_GW_WORK_REQ     = "tgt/"+str(gwId)+"/evt/gw_work_req"
TOPIC_SVR2GW_GW_STOP_REQ     = "tgt/"+str(gwId)+"/evt/gw_stop_req"
TOPIC_SVR2GW_GW_SYNC_REQ     = "tgt/"+str(gwId)+"/evt/gw_sync_req"
TOPIC_SVR2GW_MAC_ADD_REQ     = "tgt/"+str(gwId)+"/evt/mac_add_req"
TOPIC_SVR2GW_MAC_DEL_REQ     = "tgt/"+str(gwId)+"/evt/mac_delete_req"
TOPIC_SVR2GW_CARD_DETECT_RESP= "tgt/"+str(gwId)+"/evt/card_detect_resp"



class Server:
    def __init__(self):
        self.broker = MQTTBroker('localhost', 1883)
        self.broker.addHandler(TOPIC_GW2SVR_HEARTBEAT, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_GW_REG_REQ, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_GW_WORK_RESP, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_GW_STOP_RESP, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_GW_SYNC_RESP, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_MAC_ADD_RESP, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_MAC_DEL_RESP, self.dump_gw_msg)
        self.broker.addHandler(TOPIC_GW2SVR_CARD_DETECT, self.card_detect_resp)
        self.broker.addHandler(TOPIC_GW2SVR_CARD_ACV, self.dump_gw_msg)
        self.broker.loopStart()
    def card_detect_resp(self, topic, payload):
        print('Get msg from gateway: ' + payload)
        topic = TOPIC_SVR2GW_CARD_DETECT_RESP
	msg = json.loads(payload)
	card_id = msg['card_id']
	out = {"gw_id":1, "card_id":card_id, "status":0, "err_msg":""}
	self.broker.pubMessage(topic, json.dumps(out))

	self.f = open('card-history.txt', 'w')

    def card_detect_resp(self, topic, payload):
        print('Get msg from gateway: ' + payload)
        topic = TOPIC_SVR2GW_CARD_DETECT_RESP
	msg = json.loads(payload)
	card_id = msg['card_id']
	RSSI = msg['RSSI']
	SNR = msg['SNR']
	now = time.localtime()
	out = {"gw_id":1, "card_id":card_id, "status":0, "err_msg":""}
	self.broker.pubMessage(topic, json.dumps(out))

	TIMEFORMAT='%Y-%m-%d %X'
	logmsg = time.strftime(TIMEFORMAT, now) + ',' + str(card_id) + ',' + str(RSSI) + ',' + str(SNR) + '\n'
	print(logmsg)
	self.f.write(logmsg)
	self.f.flush()

    def dump_gw_msg(self, topic, payload):
        print('Get msg from gateway: ' + payload)

    def publish(self, topic, msg):
        self.broker.pubMessage(topic, msg)

    def __del__(self):
        self.f.close()

svr = Server()
while 1:
    instr = raw_input("input cmd:").split()
    if len(instr) == 0:
    	continue

    char = instr[0]
    if char == 'q':
        break
    elif char == 'reg':
       svr.publish(TOPIC_SVR2GW_GW_REG_RESP, "{\"gw_id\": 1, \"status\" : 0, \"err_msg\" : \"xxx\"}")
    elif char == 'work':
       svr.publish(TOPIC_SVR2GW_GW_WORK_REQ, "{\"gw_id\": 1}")
    elif char == 'stop':
       svr.publish(TOPIC_SVR2GW_GW_STOP_REQ, "{\"gw_id\": 1}")
    elif char == 'sync':
       svr.publish(TOPIC_SVR2GW_GW_SYNC_REQ, "{\"gw_id\": 1}")
    elif char == 'resp':
       svr.publish(TOPIC_SVR2GW_CARD_DETECT_RESP, "{\"gw_id\": 1, \"card_id\":1, \"status\":0, \"err_msg\":\"\"")
    elif char == 'add':
       svr.publish(TOPIC_SVR2GW_MAC_ADD_REQ, "{\"gw_id\": 1}")
    elif char == 'del':
       svr.publish(TOPIC_SVR2GW_MAC_DEL_REQ, "{\"gw_id\": 1}")
    elif char == 'pwr' and len(instr) == 3:
       svr.publish(TOPIC_SVR2GW_GW_CHGPWR, "{\"gw_id\": 1, \"powerA\":"+instr[1]+", \"powerB\":"+instr[2]+"}")
    
