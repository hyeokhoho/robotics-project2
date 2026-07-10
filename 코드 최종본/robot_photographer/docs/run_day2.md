# Day2 실행 방법

## 1. HTTPS 서버

```bash
cd ~/robot_photographer
python3 server/https_server.py

2. rosbridge WSS
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=11
export ROS_LOCALHOST_ONLY=0

ros2 launch rosbridge_server rosbridge_websocket_launch.xml \
ssl:=true \
certfile:=/home/robot/robot_photographer/cert/cert.pem \
keyfile:=/home/robot/robot_photographer/cert/key.pem \
port:=9090

3. TurtleBot3 bringup
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=11
export ROS_LOCALHOST_ONLY=0
export TURTLEBOT3_MODEL=burger

ros2 launch turtlebot3_bringup robot.launch.py

4. framing_node
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=11
export ROS_LOCALHOST_ONLY=0

python3 ~/ros/framing_node.py

5. 촬영 웹앱
https://192.168.0.38:8443/web/photo_test_v2.html

6. 갤러리
https://192.168.0.38:8443/web/gallery.html
