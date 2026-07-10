#!/usr/bin/env python3
import json
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist


CX_TARGET = 0.5
SIZE_TARGET = 0.5

GAIN_ANG = 1.2
GAIN_LIN = 0.5

SUBJ_TIMEOUT = 1.0
SMILE_HOLD = 1.5
SHOOT_COOLDOWN = 5.0

# 구도 완성 판정: 좁게
CX_IN_DEADBAND = 0.06
SIZE_IN_DEADBAND = 0.06

# 구도 해제 판정: 넓게
CX_OUT_DEADBAND = 0.10
SIZE_OUT_DEADBAND = 0.10

# 사람이 잠깐 흔들린 정도는 무시하고, 이 시간 이상 벗어나면 다시 구도 조정
REFRAME_DELAY = 0.3

# 촬영 직전 정지 유지 시간
STABLE_STOP_TIME = 0.3

# 속도 제한
MAX_LINEAR = 0.15
MAX_ANGULAR = 0.5

# 너무 작은 속도는 0으로 처리
MIN_LINEAR = 0.02
MIN_ANGULAR = 0.04

# TTS 반복 방지
TTS_COOLDOWN = 2.0


def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


def apply_dead_min(value, min_abs):
    if abs(value) < min_abs:
        return 0.0
    return value


class FramingNode(Node):
    def __init__(self):
        super().__init__("framing_node")

        self.sub_subject = self.create_subscription(
            String,
            "/subject",
            self.on_subject,
            10
        )

        self.sub_smile = self.create_subscription(
            Bool,
            "/all_smiling",
            self.on_smile,
            10
        )

        self.pub_vel = self.create_publisher(Twist, "/cmd_vel", 10)
        self.pub_shoot = self.create_publisher(Bool, "/shoot", 10)
        self.pub_tts = self.create_publisher(String, "/tts_text", 10)

        self.cx = 0.5
        self.size = 0.0
        self.last_subject_time = 0.0

        self.all_smiling = False
        self.smiling_since = None

        self.is_framed = False
        self.framed_since = None

        self.out_of_frame_since = None

        self.last_shot_time = 0.0
        self.last_tts_time = 0.0
        self.last_tts_text = ""

        self.timer = self.create_timer(0.1, self.tick)

        self.get_logger().info("framing_node 시작")

    def say(self, text):
        now = time.time()

        if text == self.last_tts_text and now - self.last_tts_time < TTS_COOLDOWN:
            return

        msg = String()
        msg.data = text
        self.pub_tts.publish(msg)

        self.last_tts_text = text
        self.last_tts_time = now

    def on_subject(self, msg):
        try:
            data = json.loads(msg.data)

            self.cx = float(data.get("cx", 0.5))
            self.size = float(data.get("size", 0.0))
            self.last_subject_time = time.time()

        except Exception as e:
            self.get_logger().warn(f"/subject JSON 파싱 실패: {e}")

    def on_smile(self, msg):
        self.all_smiling = bool(msg.data)

        if self.all_smiling:
            if self.smiling_since is None:
                self.smiling_since = time.time()
        else:
            self.smiling_since = None

    def err_x(self):
        return self.cx - CX_TARGET

    def err_s(self):
        return self.size - SIZE_TARGET

    def inside_frame_band(self):
        return (
            abs(self.err_x()) < CX_IN_DEADBAND and
            abs(self.err_s()) < SIZE_IN_DEADBAND
        )

    def outside_frame_band(self):
        return (
            abs(self.err_x()) > CX_OUT_DEADBAND or
            abs(self.err_s()) > SIZE_OUT_DEADBAND
        )

    def update_framed_state(self):
        now = time.time()

        if not self.is_framed:
            if self.inside_frame_band():
                self.is_framed = True
                self.framed_since = now
                self.out_of_frame_since = None
                self.publish_stop()
                self.say("좋아요! 모두 카메라를 보고 크게 웃어주세요.")
            return

        # 이미 구도 완성 상태일 때
        if self.outside_frame_band():
            if self.out_of_frame_since is None:
                self.out_of_frame_since = now

            # 잠깐 흔들림은 무시, 일정 시간 이상 벗어나면 다시 조정
            if now - self.out_of_frame_since > REFRAME_DELAY:
                self.is_framed = False
                self.framed_since = None
                self.smiling_since = None
        else:
            self.out_of_frame_since = None

    def make_cmd_vel(self):
        cmd = Twist()

        # 구도 완성 상태에서는 로봇 완전 정지
        if self.is_framed:
            return cmd

        err_x = self.err_x()
        err_s = self.err_s()

        if abs(err_x) > CX_IN_DEADBAND:
            ang = -GAIN_ANG * err_x
            ang = clamp(ang, -MAX_ANGULAR, MAX_ANGULAR)
            cmd.angular.z = apply_dead_min(ang, MIN_ANGULAR)

        if abs(err_s) > SIZE_IN_DEADBAND:
            lin = -GAIN_LIN * err_s
            lin = clamp(lin, -MAX_LINEAR, MAX_LINEAR)
            cmd.linear.x = apply_dead_min(lin, MIN_LINEAR)

        return cmd

    def guide_person(self):
        if self.is_framed:
            return

        err_x = self.err_x()
        err_s = self.err_s()

        # 로봇이 구도 조정 중이지만, 사람에게도 보조 안내
        if abs(err_x) > CX_OUT_DEADBAND:
            if err_x < 0:
                self.say("오른쪽으로 한 걸음 이동하세요.")
            else:
                self.say("왼쪽으로 한 걸음 이동하세요.")
        elif abs(err_s) > SIZE_OUT_DEADBAND:
            if err_s < 0:
                self.say("조금 가까이 오세요.")
            else:
                self.say("조금 뒤로 가세요.")

    def publish_stop(self):
        self.pub_vel.publish(Twist())

    def try_shoot(self):
        now = time.time()

        if not self.is_framed:
            return

        if self.framed_since is None:
            return

        # 촬영 전 정지 유지
        if now - self.framed_since < STABLE_STOP_TIME:
            return

        if self.smiling_since is None:
            return

        if now - self.smiling_since < SMILE_HOLD:
            return

        if now - self.last_shot_time < SHOOT_COOLDOWN:
            return

        self.last_shot_time = now
        self.smiling_since = None

        self.publish_stop()

        shoot = Bool()
        shoot.data = True
        self.pub_shoot.publish(shoot)

        self.say("찰칵! 촬영했습니다.")

    def tick(self):
        now = time.time()

        alive = (now - self.last_subject_time) < SUBJ_TIMEOUT

        if not alive:
            self.is_framed = False
            self.framed_since = None
            self.out_of_frame_since = None
            self.smiling_since = None
            self.publish_stop()
            return

        self.update_framed_state()

        cmd = self.make_cmd_vel()
        self.pub_vel.publish(cmd)

        self.guide_person()

        self.try_shoot()


def main():
    rclpy.init()
    node = FramingNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
