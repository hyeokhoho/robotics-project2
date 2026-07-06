# 토픽 인터페이스 정의서 (Topic Interface Definition)

본 문서는 프로젝트 'Cheese ros'의 각 노드 간 통신을 위한 토픽 인터페이스를 정의합니다. 모든 팀원은 이 명세에 따라 데이터를 발행(Publish)하고 구독(Subscribe)해야 합니다.

| 토픽명 | 메시지 타입 | 발행자 (Publisher) | 구독자 (Subscriber) | 주기 | 성격 | QoS |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `/cmd_vel` | `geometry_msgs/Twist` | 웹/AI 노드 | 로봇 제어(로봇) | 10Hz | 연속 | RELIABLE |
| `/face_info` | `std_msgs/Float32MultiArray` | AI A(인식) | 로봇 제어 | 10Hz | 연속 | RELIABLE |
| `/smile_status` | `std_msgs/Bool` | AI B(미소) | 로봇 제어 | 변화 시 | 엣지 | RELIABLE |
| `/lcd_text` | `std_msgs/String` | 로봇 제어 | 웹/LCD | 변화 시 | 엣지 | RELIABLE |
| `/capture_trigger`| `std_msgs/Empty` | 로봇 제어 | 웹/카메라 | 변화 시 | 엣지 | RELIABLE |

---

## 상세 설명
1. **/cmd_vel**: 로봇의 선속도(linear.x)와 각속도(angular.z)를 전달하여 P 제어를 수행합니다.
2. **/face_info**: [인물 중심 x좌표, 인물 크기(width)] 데이터를 배열로 전송합니다.
3. **/smile_status**: 모든 인물이 미소 상태일 때 `True`, 아닐 때 `False`를 발행합니다.
4. **/lcd_text**: 로봇 상태(예: "촬영 중", "웃으세요!")를 LCD 및 웹 화면에 텍스트로 뿌려줍니다.
5. **/capture_trigger**: 사진 촬영 명령을 웹앱에 전달하여 갤러리에 저장하도록 유도합니다.

**주의사항**:
- **연속 데이터**(`/cmd_vel`, `/face_info`)는 10Hz 주기로 계속 발행되어야 하며, 데이터 유실을 방지하기 위해 `RELIABLE`을 사용합니다.
- **엣지 데이터**(`/smile_status` 등)는 상태가 변할 때만 발행하여 시스템 부하를 줄입니다.
