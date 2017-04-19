#!/bin/sh

set -e

case $1 in
init)
    mosquitto_pub -t tgt/1/evt/init_gw_req -m '{"gw_id":1}'
    echo init
    ;;
stop)
    mosquitto_pub -t tgt/1/evt/delete_gw_req -m '{"gw_id":1}'
    echo stop
    ;;
macadd)
    mosquitto_pub -t tgt/1/evt/app_mac_req -m "{\"gw_id\":1, \"card_id\":1, \"mac\":\"$2\", \"membership_level\":$3, \"wifi_bandwidth\":10}"
    echo macadd
    ;;
macdel)
    mosquitto_pub -t tgt/1/evt/mac_delete_req -m "{\"gw_id\":1, \"card_id\":1, \"mac\":\"$2\"}"
    echo macdel
    ;;
lvlmod)
    echo lvlmod
    ;;
*)
    ;;
esac
