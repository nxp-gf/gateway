#!/bin/sh

set -e

case $1 in
init)
    echo init
    wifi start
    tc qdisc add dev wlan0 root handle 200: cbq bandwidth 1000kbit avpkt 512
    tc class add dev wlan0 parent 200:0 classid 200:1 cbq bandwidth 500kbit rate 500kbit prio 1 avpkt 512 bounded
    tc class add dev wlan0 parent 200:0 classid 200:2 cbq bandwidth 300kbit rate 300kbit prio 2 avpkt 512 bounded
    tc class add dev wlan0 parent 200:0 classid 200:3 cbq bandwidth 150kbit rate 150kbit prio 3 avpkt 512 bounded
    tc class add dev wlan0 parent 200:0 classid 200:4 cbq bandwidth 50kbit rate 50kbit prio 4 avpkt 512 bounded
    ;;
stop)
    echo stop
    wifi stop
    tc qdisc del dev wlan0 root handle 200:
    ;;
macadd)
    echo macadd $2 $3
    echo '$2'  >> /var/run/hostapd-wlan0.maclist
    hostapd_cli set accept_mac_file /var/run/hostapd-wlan0.maclist
    str=`echo $2 | sed s/://g`
    tc filter add dev wlan0 parent 200:0 protocol ip prio $3 u32 match u32 0x${str:4} 0xffffffff at -12 flowid 200:$3
    ;;
macdel)
    echo macdel $2
    sed -i 's/^$2/-&/g' hostapd-wlan0.maclist
    hostapd_cli set accept_mac_file /var/run/hostapd-wlan0.maclist
    sed -i '/^$2/d' hostapd-wlan0.maclist
    str=`echo $2 | sed s/://g`
    tc filter del dev wlan0 parent 200:0 protocol ip prio $3 u32 match u32 0x${str:4} 0xffffffff at -12 flowid 200:$3
    ;;
lvlmod)
    echo lvlmod $2 $3
    tc class replace dev wlan0 parent 200:0 classid 200:$2 cbq bandwidth $(3)mbps rate $(3)mbps prio $2 avpkt 512 bounded
    ;;
*)
    ;;
esac
