import os
import requests

import json 
from bluepy import btle

print("@start")

config = json.load(open(os.path.join(os.path.dirname(__file__),"config.json"),"r"))
peripheral = btle.Peripheral()
peripheral.connect(config["mac_address"])

print("@connected")

service = peripheral.getServiceByUUID(config["uuid1"])
chr = service.getCharacteristics(config["uuid2"])[0]


class StateMachine(btle.DefaultDelegate):

    opencount = 0

    state = 0

    notify_count =0

    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.opencount = 0
        self.notify_count =0


    def handleNotification(self,handle,data):
        print(self,handle,data)

        if data == b'\x01' : 
            self.state = 1 
        else :
            self.state = 0


    def setState(self,data):
        if data == config["open_state"] :
            self.opencount+=1
            if self.opencount >= config["max_count"]:
                self.notifyAlert()
        else :
            self.opencount = 0
            self.notify_count = 0            

        print( self.opencount)           

    def notifyAlert(self):
        print("@alert ")

        if self.notify_count < config["notify_max_count"] :
            requests.post(config["url"],data={"value1":config["message"]}) 
        self.notify_count += 1

print("@before notify   ")


sm = StateMachine()

peripheral.withDelegate(sm)
desc = chr.getDescriptors(config["uuid3"])[0]
desc.write(b'\x01\x00')

print("@start notify")

requests.post(config["url"],data={"value1":"start"}) 

while True :
    peripheral.waitForNotifications(config["check_interval"])
    sm.setState(sm.state)

    print(".")

