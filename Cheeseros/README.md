# AI Robot Photographer

## 개발 환경

- Ubuntu 22.04
- ROS2 Humble
- TurtleBot3 Burger
- Python3
- MediaPipe
- rosbridge_server

---

## 실행 순서

### 1. HTTPS Server

```bash
cd ~/robot_photographer
python3 server/https_server.py
```

---

### 2. rosbridge

```bash
source /opt/ros/humble/setup.bash

export ROS_DOMAIN_ID=11
export ROS_LOCALHOST_ONLY=0

ros2 launch rosbridge_server rosbridge_websocket_launch.xml \
ssl:=true \
certfile:=/home/robot/robot_photographer/cert/cert.pem \
keyfile:=/home/robot/robot_photographer/cert/key.pem \
port:=9090
```

---

### 3. TurtleBot3

```bash
source /opt/ros/humble/setup.bash

export ROS_DOMAIN_ID=11
export ROS_LOCALHOST_ONLY=0
export TURTLEBOT3_MODEL=burger

ros2 launch turtlebot3_bringup robot.launch.py
```

---

### 4. framing_node

```bash
source /opt/ros/humble/setup.bash

export ROS_DOMAIN_ID=11
export ROS_LOCALHOST_ONLY=0

python3 ~/ros/framing_node.py
```

---

### 5. Emergency Button

```bash
python3 ~/ros/emergency_button_node.py
```

---

### 6. 촬영 페이지

```
https://192.168.0.38:8443/web/photo_test_v2.html
```

---

### 7. Gallery

```
https://192.168.0.38:8443/web/gallery.html
```

---

## 주요 기능

- 사람 자동 추적
- 다인 그룹 촬영
- 전원 미소 판정
- 자동 촬영
- 베스트 컷 선택
- 실시간 갤러리
- TTS 안내
- GPIO 긴급정지
