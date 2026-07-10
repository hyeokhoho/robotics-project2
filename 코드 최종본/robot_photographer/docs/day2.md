# Day2 개발일지

## 목표

스마트폰 웹앱과 TurtleBot ROS 제어 연동

## 구현 완료

- 다인 단체사진용 Group Bounding Box 적용
- 최대 7명 Pose 인식
- 특정 인물 추적이 아닌 단체 중심 구도 제어
- TTS 안내 안정화
- 촬영 시퀀스 중 TTS 중복 방지
- rosbridge WSS 연결
- framing_node.py 구현
- /subject 기반 /cmd_vel 생성
- TurtleBot3 bringup 연동
- /shoot 기반 자동 촬영 연동

## 주요 토픽

- /subject
- /all_smiling
- /cmd_vel
- /shoot
- /tts_text
- /photo

## 다인 정책

여러 사람이 검출되면 한 명을 선택하지 않고, 검출된 사람들의 Pose Bounding Box를 모두 합친 Group Bounding Box를 사용한다.

- cx: 그룹 전체 중심
- size: 그룹 전체 높이 비율
- personCount: 검출된 사람 수

이 정책을 사용하여 A/B 인물이 번갈아 선택되어 로봇이 흔들리는 문제를 줄였다.

## 개선 사항

- TTS가 이전 말을 끊거나 뒤늦게 반복되는 문제 완화
- 촬영 중에는 안내 TTS 차단
- 카운트다운 TTS 우선 처리
- 단체사진 구도 기준 SIZE_TARGET 조정
