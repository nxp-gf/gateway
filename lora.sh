#!/bin/sh

set -e

case $1 in
detect)
    echo detect
    mosquitto_pub -t "tgt/gw/card_detect" -m '{"card_id":1, "signal":10}'
    ;;
resp)
    echo resp
    mosquitto_pub -t "tgt/gw/card_activate_resp" -m '{"card_id":1, "status":0, "err_msg":"xxxxxx"}'
    ;;
*)
    ;;
esac
