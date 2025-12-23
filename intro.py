import cv2
import time
import subprocess
import sys
import os
import numpy as np
from ffpyplayer.player import MediaPlayer

def play_intro_video(video_path, fade_duration=2, stop_audio_before=2):
    if not os.path.exists(video_path):
        print(f" Error: Video file not found at {video_path}")
        return

    print(" Playing Intro Video...")

    cap = cv2.VideoCapture(video_path)
    player = MediaPlayer(video_path)

    if not cap.isOpened():
        print(" Error: Could not open video.")
        return

    cv2.namedWindow("Intro Video", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Intro Video", 1280, 720)
    cv2.moveWindow("Intro Video", 0, 0)

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    video_duration = frame_count / fps if fps > 0 else 10

    stop_audio_at = video_duration - stop_audio_before
    fade_start_time = video_duration - fade_duration

    start_time = time.time()
    frame_delay = int(1000 / fps) if fps > 0 else 30
    audio_stopped = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        elapsed_time = time.time() - start_time

        # Fade-In Effect(First `fade_duration` seconds)
        if elapsed_time <= fade_duration:
            alpha = elapsed_time / fade_duration
            overlay = np.zeros_like(frame, dtype=np.uint8)
            frame = cv2.addWeighted(frame, alpha, overlay, 1 - alpha, 0)

        # Fade-Out Effect (Last `fade_duration` seconds)
        elif elapsed_time >= fade_start_time:
            alpha = max(0, (video_duration - elapsed_time) / fade_duration)
            overlay = np.zeros_like(frame, dtype=np.uint8)
            frame = cv2.addWeighted(frame, alpha, overlay, 1 - alpha, 0)

        # Stop Audio Before End
        if elapsed_time >= stop_audio_at and not audio_stopped:
            player.set_volume(0)  # Smoothly mute audio
            audio_stopped = True

        audio_frame, val = player.get_frame()

        cv2.imshow("Intro Video", frame)

        if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
            break

        if val == 'eof':
            break

    cap.release()
    cv2.destroyAllWindows()
    time.sleep(1)

# Path to the intro video
video_path = r"C:\Users\Vaishnavi kotian\Downloads\FRAS_intro.mp4"
play_intro_video(video_path, fade_duration=2, stop_audio_before=1)

# Short pause before launching main.py
print(" Launching Face Recognition System...")
time.sleep(1)

# Launch main.py
subprocess.run([sys.executable, "main.py"])
