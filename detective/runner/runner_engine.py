import cv2
import mediapipe as mp
from queue import Queue
import sys, os, platform
from detective import Config
from detective.communication.server import do_server
from detective.runner import music_engine
import threading

# 打印当前的 sys.path

# 添加一个新的路径到 sys.path


# 现在尝试导入位于新路径中的模块


def add_path():
    # 使用os.path.join确保路径的正确性，并替换环境变量
    path_to_add = os.path.join(os.environ["HOME"], os.environ["USER"], "detectivePy")

    # 将路径添加到sys.path
    sys.path.append(path_to_add)


if platform.system() == "Windows":
    sys.path.append("d:/A_Data_of_2024_Full/MicroPC/project/detectivePy")
    print("Current sys.path:", sys.path)
elif platform.system() == "Linux":
    add_path()

config = Config()
from .. import (
    working_detect,
    relax_detect,
    gesture_detect,
    gpio_state_change,
    music_play,
)

if config.get_param("use_pi"):
    from detective.runner import state_machine


def run_application(config):
    # initializations
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()
    mpDraw = mp.solutions.drawing_utils

    # Use the parsed configuration
    use_pi = config.get_param("use_pi")
    plugin = config.get_param("plugin")
    LED_pin = config.get_param("LED_pin")
    detect_other = config.get_param("default_detect_mode") == "others"
    use_camera = config.get_param("use_camera")
    video_path = config.get_param("video_path")
    image_path = config.get_param("image_path")
    music_path = config.get_param("music_path")
    server_email = config.get_param("server_email")
    server_password = config.get_param("server_email_password")
    smtp_server = config.get_param("smtp_server")
    smtp_port = config.get_param("smtp_port")
    target_email = config.get_param("target_email")
    protocol = [server_email, server_password, smtp_server, smtp_port, target_email]
    print("Protocol:", protocol)
    use_vis = config.get_param("use_visualization")
    packet_transfer = config.get_param("packet_tansfer")  # true: windows
    send_delay = config.get_param("send_delay")
    effective_detection_duration = config.get_param("effective_detection_duration")
    max_num_hands = config.get_param("max_num_hands")
    min_detection_confidence = config.get_param("min_detection_confidence")
    min_tracking_confidence = config.get_param("min_tracking_confidence")
    which_detect = config.get_param("which_detect")
    pin_data = config.get_param("pin_data")
    server_ip = config.get_param("server_ip")
    server_port = config.get_param("server_port")

    if use_camera:
        cap = cv2.VideoCapture(0)
        print("Using camera")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    else:
        cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Cannot open video file")
        exit()

    if which_detect == "gesture":
        gesture_detect(cap, server_ip, server_port, use_vis)
    if which_detect == "body":
        if detect_other:
            resent_gesture_queue = Queue(maxsize=1)

            server_thread = threading.Thread(
                target=do_server,
                args=(
                    resent_gesture_queue,
                    server_ip,
                    server_port,
                ),
            )
            working_detect_thread = threading.Thread(
                target=working_detect,
                args=(
                    mpPose,
                    pose,
                    mpDraw,
                    cap,
                    image_path,
                    protocol,
                    LED_pin,
                    send_delay,
                    effective_detection_duration,
                    use_vis,
                    packet_transfer,
                ),
            )
            if use_pi:
                state_machine_obj = state_machine.StateMachine("stop", pin_data)
                gpio_controller_thread = threading.Thread(
                    target=gpio_state_change,
                    args=(
                        state_machine_obj,
                        resent_gesture_queue,
                    ),
                )
            music_player = music_engine.MusicPlayer(music_path)
            music_thread = threading.Thread(
                target=music_play,
                args=(
                    music_player,
                    resent_gesture_queue,
                ),
            )

            client_thread = None
            if plugin == "working_detect":
                client_thread = working_detect_thread
            if use_pi and plugin == "gpio_state_change":
                client_thread = gpio_controller_thread
            if plugin == "music_player":
                client_thread = music_thread

            server_thread.start()
            client_thread.start()
            working_detect_thread.start()
            server_thread.join()
            client_thread.join()
            working_detect_thread.join()

        else:
            # 检测自己
            # 参照上述程序，将其改为多线程
            relax_detect(
                mpPose,
                pose,
                mpDraw,
                cap,
                image_path=image_path,
                send_delay=send_delay,
                effective_detection_duration=effective_detection_duration,
                protocol=protocol,
                pin=LED_pin,
                use_vis=use_vis,
                pack_trans=packet_transfer,
            )


if __name__ == "__main__":
    config = Config()
    run_application(config)


# 需要添加 线程，对于进行手势识别的树莓派来说，需要两个线程：线程1：进行手势识别，并讲每一个时刻的手势记录到一个全局变量。线程2：读取全局变量，根据全局变量的值，设定 PINstate。
