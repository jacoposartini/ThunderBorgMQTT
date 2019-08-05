import cv2
import paho.mqtt.client as mqtt
import base64
import numpy as np
import pygame
import time

class ControllerMQTT(mqtt.Client):
    def init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((320,240),0)
        pygame.display.set_caption("ThunderBorg controller")

    def run(self):
        self.init()
        self.username_pw_set("username", "password")
        self.connect('192.168.1.4', 1883, 60)
        self.subscribe('topic/cam', 0)
        while True:
            try:
                self.loop_start()
                self.get_event()
                time.sleep(0.05)
            except KeyboardInterrupt:
                self.loop_stop()
                break

    def get_event(self):
        #print(pygame.event.get())
        for event in pygame.event.get():
            msg = None
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.key(event.key):
                    msg = self.key(event.key)+"1"
            elif event.type == pygame.KEYUP:
                if self.key(event.key):
                    msg = self.key(event.key)+"0"
            if msg:
                self.publish('topic/cmd', msg, qos=2)
                print(msg)

    def key(self, event_key):
        if (event_key == pygame.K_LEFT
        or event_key == pygame.K_a):
            key = "L"
        elif (event_key == pygame.K_UP
        or event_key == pygame.K_w):
            key = "F"
        elif (event_key == pygame.K_DOWN
        or event_key == pygame.K_s):
            key = "B"
        elif (event_key == pygame.K_RIGHT
        or event_key == pygame.K_d):
            key = "R"
        else:
            key = False
        return key

    def on_connect(self, mqttc, obj, flags, rc):
        print("CONNECTED TO BROKER")

    def on_message(self, mqttc, obj, msg):
        frame = str(msg.payload)
        img = base64.b64decode(frame)
        npimg = np.fromstring(img, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        source = np.rot90(source, -1)
        source = pygame.surfarray.make_surface(source)
        self.screen.blit(source,(0,0)) # "show image" on the screen
        pygame.display.update()

TBMQTT = ControllerMQTT()
TBMQTT.run()
