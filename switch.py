from socket import *
import os,time
import paho.mqtt.client as mqtt

offFrame=bytearray([
0x5a,0xa5,0xaa,0x55,0x5a,0xa5,0xaa,0x55,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x68,0xd2,0x00,0x00,0x11,0x27,0x6a,0x00,0xe5,0x82,
0xba,0x7f,0x11,0x0d,0x43,0xb4,0x01,0x00,0x00,0x00,0xb1,0xbe,0x00,0x00,
0x60,0xee,0x99,0x3f,0xfc,0xf7,0xf6,0x80,0xe2,0xd1,0x71,0x31,0xdc,0x04,
0x6a,0xc8])

onFrame=bytearray([
0x5a,0xa5,0xaa,0x55,0x5a,0xa5,0xaa,0x55,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x0f,0xd0,0x00,0x00,0x11,0x27,0x6a,0x00,0x89,0x82,
0xba,0x7f,0x11,0x0d,0x43,0xb4,0x01,0x00,0x00,0x00,0xb2,0xbe,0x00,0x00,
0x13,0x7f,0xf1,0x6c,0x25,0xd9,0xd0,0xb8,0xe1,0x29,0xaf,0x4b,0x9e,0x37,
0x6b,0x3f])

powerIp = "192.168.1.100"


class PowerSwitchController:
    def __init__(self, port=80):
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.addr = (powerIp, port)
        self.sock.settimeout(5)
        self.off = offFrame
        self.on = onFrame

    def __del__(self):
        self.sock.close()

    def __switchOn(self):
        self.sock.sendto(self.on, self.addr)
        buf, addr = self.sock.recvfrom(1024)

    def __switchOff(self):
        self.sock.sendto(self.off, self.addr)
        buf, addr = self.sock.recvfrom(1024)

    def switch(self, action):
        try:
            if action == 'on':
                self.__switchOn()
            elif action == 'off':
                self.__switchOff()
        except Exception,e:
            print ('rcv:Switch power to %s failed: %s' %(action, e))


if __name__ == '__main__':
    ps = PowerSwitchController()
    print("Switch to on")
    ps.switch('on')
    time.sleep(1)
    print("Switch to off")
    ps.switch('off')
    
