# ThunderBorgMQTT
## Install
Clone the source code:
```
git clone https://github.com/jacoposartini/SQLite3_HBMQTT_Plugins.git
```
Install requirements:
```
pip install -r requirements.txt
```
## Setting
Before running, you must have set up your PiCamera and your MQTT client settings:
```
  self.username_pw_set("username", "password")
  self.connect('your_broker_address', 1883, 60)
  self.subscribe('your_topic/cam', 0)
```
## Run
In your raspberry pi run ```RasperryPI/TBMQTT.py``` and in the remote host run ```TBMQTT_Remote_Controller.py```.
## To drive ThunderBorg
Use the arrow keys or alternatively aswd after clicking on the window.
