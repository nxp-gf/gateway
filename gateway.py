import json
from broker import MQTTBroker
import threading
import time,sys,argparse
import commands
from switch import PowerSwitchController


parser = argparse.ArgumentParser(description='The Banking IoT Gateway demo')

parser.add_argument("--server", choices=('local', 'remote'), default='remote',
                    help="Use the local server or the remote server.")
args = parser.parse_args()


if (args.server == 'local'):
    svrip = 'localhost'
    svrport = 1883
    svruser = None
    svrpasswd = None
else:
    svrip = '59.173.2.76'
    svrport = 61613
    svruser = 'admin'
    svrpasswd = 'password'

gwId = '12121212'
mac = 'BC:30:7D:08:AA:3B'
ssid = 'NXP-Banking-GW'
password = ''

TOPIC_GW2SVR_HEARTBEAT       = "tgt/server/evt/gw_heartbeat"
TOPIC_GW2SVR_GW_REG_REQ      = "tgt/server/evt/gw_reg_req"
TOPIC_GW2SVR_GW_WORK_RESP    = "tgt/server/evt/gw_work_resp"
TOPIC_GW2SVR_GW_STOP_RESP    = "tgt/server/evt/gw_stop_resp"
TOPIC_GW2SVR_GW_SYNC_RESP    = "tgt/server/evt/gw_sync_resp"
TOPIC_GW2SVR_GW_CHGPWR_RESP  = "tgt/server/evt/gw_chgpwr_resp"
TOPIC_GW2SVR_MAC_ADD_RESP    = "tgt/server/evt/mac_add_resp"
TOPIC_GW2SVR_MAC_DEL_RESP    = "tgt/server/evt/mac_delete_resp"
TOPIC_GW2SVR_CARD_DETECT     = "tgt/server/evt/card_detect_req_work_mode"
TOPIC_GW2SVR_CARD_ACV        = "tgt/server/evt/card_detect_req_sync_mode"

TOPIC_SVR2GW_GW_REG_RESP     = "tgt/"+gwId+"/evt/gw_reg_resp"
TOPIC_SVR2GW_GW_WORK_REQ     = "tgt/"+gwId+"/evt/gw_work_req"
TOPIC_SVR2GW_GW_STOP_REQ     = "tgt/"+gwId+"/evt/gw_stop_req"
TOPIC_SVR2GW_GW_SYNC_REQ     = "tgt/"+gwId+"/evt/gw_sync_req"
TOPIC_SVR2GW_GW_CHGPWR       = "tgt/"+gwId+"/evt/gw_chgpwr_req"
TOPIC_SVR2GW_MAC_ADD_REQ     = "tgt/"+gwId+"/evt/mac_add_req"
TOPIC_SVR2GW_MAC_DEL_REQ     = "tgt/"+gwId+"/evt/mac_delete_req"
TOPIC_SVR2GW_CARD_DETECT_RESP= "tgt/"+gwId+"/evt/card_detect_resp"

TOPIC_GW2LORA_CMD_CHGPWR     = "tgt/lora/evt/cmd_change_power"
TOPIC_GW2LORA_CMD_WORK       = "tgt/lora/evt/cmd_work"
TOPIC_GW2LORA_CMD_STOP       = "tgt/lora/evt/cmd_stop"
TOPIC_GW2LORA_CMD_SYNC       = "tgt/lora/evt/cmd_sync"
TOPIC_GW2LORA_DETECT_RESP    = "tgt/lora/evt/card_detect_resp_working_mode"
TOPIC_LORA2GW_CHGPWR_RESP    = "tgt/gw/evt/cmd_change_power_resp"
TOPIC_LORA2GW_WORK_RESP      = "tgt/gw/evt/cmd_work_resp"
TOPIC_LORA2GW_STOP_RESP      = "tgt/gw/evt/cmd_stop_resp"
TOPIC_LORA2GW_SYNC_RESP      = "tgt/gw/evt/cmd_sync_resp"
TOPIC_LORA2GW_HEARTBEAT      = "tgt/gw/evt/lora_heartbeat"
TOPIC_LORA2GW_CARD_DET       = "tgt/gw/evt/card_detect_req_working_mode"
TOPIC_LORA2GW_CARD_ACV       = "tgt/gw/evt/card_detect_req_sync_mode"


STATEINIT=0
STATESTOP=1
STATESYNC=2
STATEWORK=3

wifiCapbility = 1
DLNACapbility = 1
heartbeatTime = 5
wifiBandwidth = 1000


global heartBeatTimer
global svrBroker
global loraBroker
global state
global loraStatus
global loraErrmsg
global latitude
global longitude
global gwErrmsg
global powerA
global powerB
global powersw

#state = STATESTOP
state = STATEINIT
#state = STATEWORK
loraStatus = 0
loraErrmsg = "lora heartbeat not available"
latitude = 0
longitude = 0
powerA = 0
powerB = 0
gwErrmsg = ""
powersw = PowerSwitchController()

def svr2gw_reg_resp(topic, msg):
    global state
    state = STATESTOP
    heartBeatTimer = threading.Timer(heartbeatTime, gateway_heartbeat_req, (0,))
    heartBeatTimer.start()

def gw2svr_register_req():
    payload = {'gw_id':gwId, 'wifi':wifiCapbility, 'wifi_bandwidth':wifiBandwidth, 'dlna':DLNACapbility, 'mac':mac, 'ssid':ssid, 'password':password}
    svrBroker.pubMessage(TOPIC_GW2SVR_GW_REG_REQ, json.dumps(payload))

def gw2svr_work_resp(topic, msg):
    global state
    global gwErrmsg
    if topic == TOPIC_LORA2GW_WORK_RESP:
        payload = json.loads(msg)
        status = payload['status']
        err_msg = payload['err_msg']
        if state == STATESTOP:
            (ret, retmsg) = commands.getstatusoutput('gateway.sh init')
            if ret != 0:
                err_msg += retmsg
                gwErrmsg = retmsg
    else:
        status = 0
        err_msg = ''
    out = {'gw_id':gwId, 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_GW_WORK_RESP, json.dumps(out))
    state = STATEWORK

def gw2svr_stop_resp(topic, msg):
    global state
    global gwErrmsg
    if topic == TOPIC_LORA2GW_STOP_RESP:
        payload = json.loads(msg)
        status = payload['status']
        err_msg = payload['err_msg']
        (ret, retmsg) = commands.getstatusoutput('gateway.sh stop')
        if ret != 0:
            err_msg += retmsg
            gwErrmsg = retmsg
    else:
        status = 0
        err_msg = ''
    out = {'gw_id':gwId, 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_GW_STOP_RESP, json.dumps(out))
    state = STATESTOP

def gw2svr_sync_resp(topic, msg):
    global state
    global gwErrmsg
    if topic == TOPIC_LORA2GW_SYNC_RESP:
        payload = json.loads(msg)
        status = payload['status']
        err_msg = payload['err_msg']
        if state == STATESTOP:
            (ret, retmsg) = commands.getstatusoutput('gateway.sh init')
            if ret != 0:
                err_msg += retmsg
                gwErrmsg = retmsg
    else:
        status = 0
        err_msg = ''
    out = {'gw_id':gwId, 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_GW_SYNC_RESP, json.dumps(out))
    state = STATESYNC

def gw2svr_chgpwr_resp(topic, msg):
    payload = json.loads(msg)
    status = payload['status']
    err_msg = payload['err_msg']
    out = {'gw_id':gwId, 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_GW_CHGPWR_RESP, json.dumps(out))

def gw2lora_cmd_req(topic, msg):
    out = ''
    if topic == TOPIC_SVR2GW_GW_WORK_REQ:
        rettopic = TOPIC_GW2LORA_CMD_WORK
    elif topic == TOPIC_SVR2GW_GW_STOP_REQ:
        rettopic = TOPIC_GW2LORA_CMD_STOP
    elif topic == TOPIC_SVR2GW_GW_SYNC_REQ:
        rettopic = TOPIC_GW2LORA_CMD_SYNC
    else:
        payload = json.loads(msg)
    	rettopic = TOPIC_GW2LORA_CMD_CHGPWR
	powerA = payload['powerA']
	powerB = payload['powerB']
	out = json.dumps({'powerA':powerA, 'powerB':powerB})
    loraBroker.pubMessage(rettopic, out)

def gw2lora_card_detect_resp(topic, msg):
    payload = json.loads(msg)
    status = payload['status']
    err_msg = payload['err_msg']
    card_id = payload['card_id']
    out = {'card_id':card_id, 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2LORA_DETECT_RESP, json.dumps(out))

def lora_heartbeat(topic, payload):
    global loraStatus
    global loraErrmsg
    global longitude
    global latitude
    global powerA
    global powerB
    msg = json.loads(payload)
    loraStatus = msg['status']
    loraErrmsg = msg['err_msg']
    longitude = msg['longitude']
    latitude = msg['latitude']
    powerA = msg['powerA']
    powerB = msg['powerB']

def gateway_heartbeat_req(seqNumber):
    seqNumber += 1
    errmsg = gwErrmsg + loraErrmsg
    payload = {'gw_id':gwId,'seq_number':seqNumber,'gw_status':state,
               'gw_status_msg':errmsg,'longitude':longitude,'latitude':latitude,
	       'powerA':powerA, 'powerB':powerB}
    svrBroker.pubMessage(TOPIC_GW2SVR_HEARTBEAT, json.dumps(payload))
    heartBeatTimer = threading.Timer(heartbeatTime, gateway_heartbeat_req, (seqNumber,))
    heartBeatTimer.start()

def gw2svr_add_mac_resp(topic, payload):
    msg = json.loads(payload)
    print("Get mac register req:card_id(%s) mac(%s) membership_level(%d) wifi_bandwidth(%d)" % (msg['card_id'], msg['mac'], msg['membership_level'], msg['wifi_bandwidth']))
    (status, err_msg) = commands.getstatusoutput('gateway.sh macadd %s %d' % (msg['mac'], msg['membership_level']))
    payload = {'gw_id':gwId, 'card_id':msg['card_id'], 'mac':msg['mac'], 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_MAC_ADD_RESP, json.dumps(payload))
    powersw.switch('on')

def gw2svr_del_mac_resp(topic, payload):
    msg = json.loads(payload)
    print("gw2svr_del_mac_resp")
    print("Get mac delete req: card_id(%s) mac(%s) membership_level(%d)" % (msg['card_id'], msg['mac'], msg['membership_level']))
    (status, err_msg) = commands.getstatusoutput('gateway.sh macdel %s %d' % (msg['mac'], msg['membership_level']))
    payload = {'gw_id':gwId, 'card_id':msg['card_id'], 'mac':msg['mac'], 'status':status, 'err_msg':err_msg}
    svrBroker.pubMessage(TOPIC_GW2SVR_MAC_DEL_RESP, json.dumps(payload))
    powersw.switch('off')

def gw2svr_card_detect(topic, payload):
    if topic == TOPIC_LORA2GW_CARD_DET:
        rettopic = TOPIC_GW2SVR_CARD_DETECT
    else:
        rettopic = TOPIC_GW2SVR_CARD_ACV
    msg = json.loads(payload)
    out = {'gw_id':gwId, 'card_id':msg['card_id'], 'rssi':msg['RSSI'], 'snr':msg['SNR']}
    svrBroker.pubMessage(rettopic, json.dumps(out))

stateMachine = {TOPIC_SVR2GW_GW_REG_RESP     :[svr2gw_reg_resp, None, None, None],
                TOPIC_SVR2GW_GW_WORK_REQ     :[None, gw2lora_cmd_req, gw2lora_cmd_req, gw2lora_cmd_req],
                TOPIC_SVR2GW_GW_STOP_REQ     :[None, gw2lora_cmd_req, gw2lora_cmd_req, gw2lora_cmd_req],
                TOPIC_SVR2GW_GW_SYNC_REQ     :[None, gw2lora_cmd_req, gw2lora_cmd_req, gw2lora_cmd_req],
                TOPIC_SVR2GW_GW_CHGPWR       :[None, gw2lora_cmd_req, gw2lora_cmd_req, gw2lora_cmd_req],
                TOPIC_SVR2GW_MAC_ADD_REQ     :[None, None, None, gw2svr_add_mac_resp],
                TOPIC_SVR2GW_MAC_DEL_REQ     :[None, None, None, gw2svr_del_mac_resp],
                TOPIC_SVR2GW_CARD_DETECT_RESP:[None, None, None, gw2lora_card_detect_resp],

                TOPIC_LORA2GW_WORK_RESP      :[None, gw2svr_work_resp, gw2svr_work_resp, gw2svr_work_resp],
                TOPIC_LORA2GW_STOP_RESP      :[None, gw2svr_stop_resp, gw2svr_stop_resp, gw2svr_stop_resp],
                TOPIC_LORA2GW_SYNC_RESP      :[None, gw2svr_sync_resp, gw2svr_sync_resp, gw2svr_sync_resp],
                TOPIC_LORA2GW_CHGPWR_RESP    :[None, gw2svr_chgpwr_resp, gw2svr_chgpwr_resp, gw2svr_chgpwr_resp],
                TOPIC_LORA2GW_CARD_DET       :[None, gw2svr_card_detect, gw2svr_card_detect, gw2svr_card_detect],
                TOPIC_LORA2GW_CARD_ACV       :[None, gw2svr_card_detect, gw2svr_card_detect, gw2svr_card_detect],
		}

def state_machine_entrance(topic, msg):
    global state
    if stateMachine[topic][state] is not None:
        stateMachine[topic][state](topic,msg)

loraBroker = MQTTBroker('localhost', 1883)
loraBroker.loopStart()
loraBroker.waitConnect()
loraBroker.addHandler(TOPIC_LORA2GW_CARD_DET,  state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_CARD_ACV,  state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_WORK_RESP, state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_STOP_RESP, state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_SYNC_RESP, state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_CHGPWR_RESP, state_machine_entrance)
loraBroker.addHandler(TOPIC_LORA2GW_HEARTBEAT, lora_heartbeat)

svrBroker = MQTTBroker(svrip, svrport, svruser, svrpasswd)
svrBroker.loopStart()
svrBroker.waitConnect()
svrBroker.addHandler(TOPIC_SVR2GW_GW_REG_RESP, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_GW_WORK_REQ, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_GW_STOP_REQ, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_GW_SYNC_REQ, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_GW_CHGPWR, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_MAC_ADD_REQ, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_MAC_DEL_REQ, state_machine_entrance)
svrBroker.addHandler(TOPIC_SVR2GW_CARD_DETECT_RESP, state_machine_entrance)

gw2svr_register_req()

while 1:
    time.sleep(1)
