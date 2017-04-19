#!/bin/sh

set -e

case $1 in
init)
    echo init
    wifi up
    sleep 5
    tc qdisc add dev wlan0 root handle 1: cbq bandwidth 1000mbit avpkt 512
    tc class add dev wlan0 parent 1:0 classid 1:10 cbq bandwidth 1000mbit rate 1000mbit prio 8 avpkt 512 bounded
    tc class add dev wlan0 parent 1:10 classid 1:1 cbq bandwidth 1000mbit rate 500mbit prio 1 avpkt 512 bounded
    tc class add dev wlan0 parent 1:10 classid 1:2 cbq bandwidth 1000mbit rate 300mbit prio 2 avpkt 512 bounded
    tc class add dev wlan0 parent 1:10 classid 1:3 cbq bandwidth 1000mbit rate 150mbit prio 3 avpkt 512 bounded
    tc class add dev wlan0 parent 1:10 classid 1:4 cbq bandwidth 1000mbit rate 50mbit prio 4 avpkt 512 bounded
    ;;
stop)
    echo stop
    wifi down
    ;;
macadd)
    echo macadd $2 $3
    echo $2  >> /var/run/hostapd-wlan0.maclist
    hostapd_cli set accept_mac_file /var/run/hostapd-wlan0.maclist
    str=`echo $2 | sed s/://g`
    tc filter add dev wlan0 parent 1:0 protocol ip prio $3 u32 match u32 0x${str:4} 0xffffffff at -12 flowid 1:$3
    ;;
macdel)
    echo macdel $2
    sed -i 's/^$2/-&/g' /var/run/hostapd-wlan0.maclist
    hostapd_cli set accept_mac_file /var/run/hostapd-wlan0.maclist
    sed -i '/^$2/d' /var/run/hostapd-wlan0.maclist
    str=`echo $2 | sed s/://g`
    tc filter del dev wlan0 parent 1:0 protocol ip prio $3 u32 match u32 0x${str:4} 0xffffffff at -12 flowid 1:$3
    ;;
lvlmod)
    echo lvlmod $2 $3
    tc class replace dev wlan0 parent 1:0 classid 1:$2 cbq bandwidth 1000mbit rate $(3)mbps prio $2 avpkt 512 bounded
    ;;
*)
    ;;
esac
