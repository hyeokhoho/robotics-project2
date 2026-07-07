# INTERFACE

## /subject

Type

std_msgs/String

Example

```json
{
    "cx":0.42,
    "size":0.38
}

## 다인 촬영 정책

여러 명이 검출될 경우 특정 한 명을 선택하지 않고, 모든 Pose Bounding Box를 합친 Group Bounding Box를 사용한다.

```json
{
  "cx": 0.50,
  "size": 0.42
}


## 7. Git에 추가

```bash
cd ~/robot_photographer
git add .
git status
