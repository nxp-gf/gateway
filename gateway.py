import json
from broker import MQTTBroker
import threading
import time
import commands

svrip = 'localhost'
svrport = 1883
svruser = None 
svrpasswd = None
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

TOPIC_SVR2GW_GW_REG_RESP     = "tgt/"+str(gwId)+"/evt/gw_reg_resp"
TOPIC_SVR2GW_GW_WORK_REQ     = "tgt/"+str(gwId)+"/evt/gw_work_req"
TOPIC_SVR2GW_GW_STOP_REQ     = "tgt/"+str(gwId)+"/evt/gw_stop_req"
TOPIC_SVR2GW_GW_SYNC_REQ     = "tgt/"+str(gwId)+"/evt/gw_sync_req"
TOPIC_SVR2GW_MAC_ADD_REQ     = "tgt/"+str(gwId)+"/evt/mac_add_req"
TOPIC_SVR2GW_MAC_DEL_REQ     = "tgt/"+str(gwId)+"/evt/mac_delete_req"
TOPIC_SVR2GW_CARD_DETECT_RESP= "tgt/"+str(gwId)+"/evt/card_detect_resp"

TOPIC_GW2LORA_CMD_WORK       = "tgt/lora/evt/cmd_work"
TOPIC_GW2LORA_CMD_STOP       = "tgt/lora/evt/cmd_stop"
TOPIC_GW2LORA_CMD_SYNC       = "tgt/lora/evt/cmd_sync"
TOPIC_LORA2GW_WORK_RESP      = "tgt/gw/evt/cmd_work_resp"
TOPIC_LORA2GW_STOP_RESP      = "tgt/gw/evt/cmd_stop_resp"
TOPIC_LORA2GW_SYNC_RESP      = "tgt/gw/evt/cmd_sync_resp"
TOPIC_LORA2GW_HEARTBEAT      = "tgt/gw/evt/lora_heartbeat"
TOPIC_LORA2GW_CARD_DET       = "tgt/gw/evt/card_detect_req_working_mode"
TOPIC_LORA2GW_CARD_ACV       = "tgt/gw/evt/card_detect_resp_sync_mode"


STATEINIT=0
STATESTOP=1
STATESYNC=2
STATEWORK=3

wifiCapbility = 1
DLNACapbility = 1
loraStatus = 0
heartbeatTime = 3
wifiBandwidth = 1000
seqNumber = 0
state = STATEINIT
latitude = 0
longitude = 0
loraErrmsg = "lora heartbeat not available"
gwErrmsgp = ""

global heartBeatTimer
global svrBroker
global loraBroker

def svr2gw_reg_resp(topic, msg):
    state = STATESTOP
    heartBeatTimer = threading.Timer(10, self.gateway_heartbeat_req, '')
    heartBeatTimer.start()

def gw2svr_register_req():
    payload = {'gw_id':gwId, 'wifi':wifiCapbility, 'wifi_bandwidth':wifiBandwidth, 'dlna':DLNACapbility}
    svrBroker.pubMessage(TOPIC_GW2SVR_GW_REG_REQ, json.dumps(payload))

def gw2svr_work_resp(topic, msg):
    if topic == TOPIC_LORA2GW_WORK_RESP:
        payload = json.loads(msg)
        status = payload['status']
        err_msg = payload['err_msg']
        if state == STATESTOP:
            (ret, retmsg) = commands.getstatusoutput('gateway.sh init')
            if ret != 0:
                err_msg += retmsg
                gwErrmsgp = retmsg
    else:
        status = 0
        err_msg = ''
    out = {'gw_id':gwId, 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_GW_WORK_RESP, json.dumps(out))
    state = STATEWORK

def gw2svr_stop_resp(topic, msg):
    if topic == TOPIC_LORA2GW_STOP_RESP:
        payload = json.loads(msg)
        status = payload['status']
        err_msg = payload['err_msg']
        (ret, retmsg) = commands.getstatusoutput('gateway.sh stop')
        if ret != 0:
            err_msg += retmsg
            gwErrmsgp = retmsg
    else:
        status = 0
        err_msg = ''
    out = {'gw_id':gwId, 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_GW_STOP_RESP, json.dumps(out))
    state = STATESTOP

def gw2svr_sync_resp(topic, msg):
    if topic == TOPIC_LORA2GW_SYNC_RESP:
        payload = json.loads(msg)
        status = payload['status']
        err_msg = payload['err_msg']
        if state == STATESTOP:
            (ret, retmsg) = commands.getstatusoutput('gateway.sh init')
            if ret != 0:
                err_msg += retmsg
                gwErrmsgp = retmsg
    else:
        status = 0
        err_msg = ''
    out = {'gw_id':gwId, 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_GW_SYNC_RESP, json.dumps(out))
    state = STATERESP

def gw2lora_cmd_req(topic, msg):
    if topic == TOPIC_SVR2GW_GW_WORK_REQ:
        rettopic = TOPIC_GW2LORA_CMD_WORK
    elif topic == TOPIC_SVR2GW_GW_STOP_REQ:
        rettopic = TOPIC_GW2LORA_CMD_STOP
    else:
        rettopic = TOPIC_GW2LORA_CMD_SYNC
    loraBroker.pubMessage(rettopic, "")

def lora_heartbeat(payload):
    msg = json.loads(payload)
    print("Get lora heartbeat:status(%d) err_msg(%s)" % (msg['status'], msg['err_msg']))
    loraStatus = msg['status']
    loraErrmsg = msg['err_msg']
    longitude = msg['longitude']
    latitude = msg['latitude']

def gateway_heartbeat_req():
    seqNumber += 1
    errmsg = gwErrmsgp + loraErrmsg
    payload = {'gw_id':gwId,'seq_number':seqNumber,'gw_status':state,'gw_status_msg':errmsg,'longitude':longitude,'latitude':latitude}
    svrBroker.pubMessage(TOPIC_GW2SVR_HEARTBEAT, json.dumps(payload))
    heartBeatTimer = threading.Timer(heartbeatTime, gateway_heartbeat_req, '')
    heartBeatTimer.start()

def gw2svr_add_mac_resp(topic, payload):
    msg = json.loads(payload)
    print("Get mac register req:card_id(%d) mac(%s) membership_level(%d) wifi_bandwidth(%d)" % (msg['card_id'], msg['mac'], msg['membership_level'], msg['wifi_bandwidth']))
    (status, err_msg) = commands.getstatusoutput('gateway.sh macadd %s %d' % (msg['mac'], msg['membership_level']))
    payload = {'gw_id':gwId, 'card_id':msg['card_id'], 'mac':msg['mac'], 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_MAC_ADD_RESP, json.dumps(payload))

def gw2svr_del_mac_resp(topic, payload):
    msg = json.loads(payload)
    print("Get mac delete req: card_id(%d) mac(%s)" % (msg['card_id'], msg['mac']))
    (status, err_msg) = commands.getstatusoutput('gateway.sh macdel %s' % msg['mac'])
    payload = {'gw_id':gwId, 'card_id':msg['card_id'], 'mac':msg['mac'], 'status':status, 'err_msg':msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_MAC_DEL_RESP, json.dumps(payload))

def gw2svr_card_detect(topic, payload):
    if topic == TOPIC_LORA2GW_CARD_DET:
        rettopic = TOPIC_GW2SVR_CARD_DETECT
    else:
        rettopic = TOPIC_GW2SVR_CARD_ACV
    svrBroker.pubMessage(rettopic, '')

stateMachine = {TOPIC_SVR2GW_GW_REG_RESP:[svr2gw_reg_resp, None,               None,               None],
                TOPIC_SVR2GW_GW_WORK_REQ:[None,            gw2lora_cmd_req,    gw2lora_cmd_req,    gw2svr_work_resp],
                TOPIC_SVR2GW_GW_STOP_REQ:[None,            gw2svr_stop_resp,   gw2lora_cmd_req,    gw2lora_cmd_req],
                TOPIC_SVR2GW_GW_SYNC_REQ:[None,            gw2lora_cmd_req,    gw2svr_sync_resp,   gw2lora_cmd_req],
                TOPIC_SVR2GW_MAC_ADD_REQ:[None,            None,               None,               gw2svr_add_mac_resp],
                TOPIC_SVR2GW_MAC_DEL_REQ:[None,            None,               None,               gw2svr_del_mac_resp],
                TOPIC_LORA2GW_WORK_RESP :[None,            gw2svr_work_resp,   gw2svr_sync_resp,   None],
                TOPIC_LORA2GW_STOP_RESP :[None,            None,               gw2svr_stop_resp,   gw2svr_stop_resp],
                TOPIC_LORA2GW_SYNC_RESP :[None,            gw2svr_sync_resp,   None,               None],
                TOPIC_LORA2GW_CARD_DET  :[None,            gw2svr_card_detect, gw2svr_card_detect, gw2svr_card_detect],
                TOPIC_LORA2GW_CARD_ACV  :[None,            gw2svr_card_detect, gw2svr_card_detect, gw2svr_card_detect]}

def state_machine_entrance(topic, msg):
    stateMachine[topic][state](topic,msg)

loraBroker = MQTTBroker('localhost', 1883)
loraBroker.addHandler(TOPIC_LORA2GW_CARD_DET,  state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_CARD_ACV,  state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_WORK_RESP, state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_STOP_RESP, state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_SYNC_RESP, state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_HEARTBEAT, lora_heartbeat)
loraBroker.loopStart()

svrBroker = MQTTBroker(svrip, svrport, svruser, svrpasswd)
svrBroker.addHandler(TOPIC_SVR2GW_GW_REG_RESP, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_GW_WORK_REQ, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_GW_STOP_REQ, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_GW_SYNC_REQ, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_MAC_ADD_REQ, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_MAC_DEL_REQ, state_machine_entrance)
svrBroker.loopStart()
gw2svr_register_req()

while 1:
    time.sleep(10)
    print("running")
