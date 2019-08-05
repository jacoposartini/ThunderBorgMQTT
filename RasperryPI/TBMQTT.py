import ThunderBorg
import sys
import paho.mqtt.client as mqtt
import cv2
import base64

class ThunderBorgMQTT(mqtt.Client):
    def init(self):
        # Init ThunderBorg
        self.TB = ThunderBorg.ThunderBorg()
        self.TB.Init()
        if not self.TB.foundChip:
            boards = ThunderBorg.ScanForThunderBorg()
            if len(boards) == 0:
                print ('No ThunderBorg found, check you are attached :)')
            else:
                print ('No ThunderBorg at address %02X, but we did find boards:' % (TB.i2cAddress))
                for board in boards:
                    print ('    %02X (%d)' % (board, board))
                print ('If you need to change the IC address change the setup line so it is correct, e.g.')
                print ('TB.i2cAddress = 0x%02X' % (boards[0]))
            sys.exit()
        self.TB.SetCommsFailsafe(False)# Disable the communications failsafe
        self.TB.SetLedShowBattery(False)
        # Init action values
        self.Forward = False
        self.Backward = False
        self.Left = False
        self.Right = False
        # Init the Camera
        self.camera = cv2.VideoCapture(0)

    def streaming(self):
        grabbed, frame = self.camera.read()  # Grab the current frame
        frame = cv2.resize(frame, (320, 240))  # Resize the frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encoded, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        self.publish('topic/cam', jpg_as_text, qos=0)

    def run(self):
        self.init()
        self.username_pw_set("username", "password")
        self.connect('192.168.1.4', 1883, 60)
        self.subscribe('topic/cmd', 2)
        while True:
            try:
                self.streaming()
                self.loop_start()
            except KeyboardInterrupt:
                self.camera.release()
                cv2.destroyAllWindows()
                self.loop_stop()
                # Set the LED to red to show we have finished
                TB.SetLeds(1,0,0)
                break

    def on_connect(self, mqttc, obj, flags, rc):
        self.TB.SetLeds(0,1,0)# Set LED to GREEN

    def on_message(self, mqttc, obj, msg):
        #print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        cmd = str(msg.payload)
        if "1" in cmd:
            x = True
        elif "0" in cmd:
            x = False
        if "F" in cmd:
            self.Forward = x
        elif "B" in cmd:
            self.Backward = x
        elif "L" in cmd:
            self.Left = x
        elif "R" in cmd:
            self.Right = x
        self.perform_move()

    def perform_move(self):
        maxPower = 0.95
        if self.Left and self.Forward:
            driveLeft = 0
            driveRight = 1
        elif self.Right and self.Forward:
            driveLeft = 1
            driveRight = 0
        elif self.Left and self.Backward:
            driveLeft = 0
            driveRight = -1
        elif self.Right and self.Backward:
            driveLeft = 1
            driveRight = -0
        elif self.Forward:
            driveLeft = 1
            driveRight = 1
        elif self.Backward:
            driveLeft = -1
            driveRight = -1
        elif self.Right:
            driveLeft = 1
            driveRight = -1
        elif self.Left:
            driveLeft = -1
            driveRight = 1
        else:
            driveLeft = 0
            driveRight = 0
        print("L:"+driveLeft+" | R:"+driveRight)
        # Set the motors running
        self.TB.SetMotor1(driveLeft  * maxPower)
        self.TB.SetMotor2(driveRight * maxPower)

TBMQTT = ThunderBorgMQTT()
TBMQTT.run()
