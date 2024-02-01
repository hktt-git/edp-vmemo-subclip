import threading
import time
import glob

import pygame
from pygame.locals import *
import numpy as np

from moviepy.editor import *

import serial.tools.list_ports
import serial

from dotenv import load_dotenv
import os

import shutil

import queue

TEMP_DIR = "./temp"
TEMP_OUTPUT_DIR = f"{TEMP_DIR}/output"
temp_playng_dir = f"{TEMP_DIR}/playing"
temp_editing_dir = f"{TEMP_DIR}/editing"

def open_playing_clip(movie_directory):
    movie_files = glob.glob(f"{movie_directory}/*.mp4")

    clips = list(map(lambda file: VideoFileClip(file), movie_files))

    names = list(map(os.path.basename, movie_files))

    timestamps = list()

    t = 0

    for clip in clips:
        t += clip.duration
        timestamps.append(t)

    merged_clip = concatenate_videoclips(clips)

    aud = merged_clip.audio.set_fps(clips[0].audio.fps)
    merged_clip = merged_clip.without_audio().set_audio(aud)

    return (merged_clip, list(map(lambda x,y: (x,y), names, timestamps)))

time_ref = 0

def player(clip: VideoClip, screen: pygame.Surface, lock: threading.RLock, flag: threading.Event, fps=15):
    global time_ref
    
    def imdisplay(imarray, screen):
        a = pygame.surfarray.make_surface(imarray.swapaxes(0, 1))
        b = screen.copy()
        pygame.transform.scale(a, b.get_size(), b)
        with lock:
            screen.blit(b, (0, 0))

    videoFlag = threading.Event()
    audioFlag = threading.Event()

    audio = clip.audio
    audio_fps=22050
    audio_buffersize=3000
    audio_nbytes=2

    while True:
        videoFlag.clear()
        audioFlag.clear()
        
        audiothread = threading.Thread(target=clip.audio.preview,
                                        args=(audio_fps,
                                              audio_buffersize,
                                              audio_nbytes,
                                              audioFlag, videoFlag))
        
        audiothread.start()

        img = clip.get_frame(0)

        imdisplay(img, screen)
        
        if audio:  # synchronize with audio
            videoFlag.set()  # say to the audio: video is ready
            audioFlag.wait()  # wait for the audio to be ready

        t0 = time.time()

        for t in np.arange(1.0 / fps, clip.duration-.001, 1.0 / fps):
            img = clip.get_frame(t)

            t1 = time.time()
            time.sleep(max(0, t - (t1-t0)))

            imdisplay(img, screen)
            time_ref = t

            if flag.is_set():
                videoFlag.clear()
                return
        
        videoFlag.clear()
        audiothread.join()

def subclipper(request: queue.Queue, clip: VideoClip, clip_names: list, duration: float, output: str):
    while True:
        clip_end_position = request.get()

        print(clip_end_position)

        clip_start_position = max(clip_end_position - duration, 0)
        
        clipped_video = clip.subclip(clip_start_position, clip_end_position)
        
        output_filename = "output.mp4"
        
        for name, timestamp in clip_names:
            output_filename = name
            
            if clip_start_position < timestamp:
                break
        
        counter = 1
        while True:
            output_filename_with_index = f"{os.path.splitext(output_filename)[0]}{counter}.mp4"
            temp_file_path = f"{TEMP_OUTPUT_DIR}/{output_filename_with_index}"
            file_path = f"{output}/{output_filename_with_index}"
            
            if not os.path.exists(file_path):
                break
            counter += 1


        if not os.path.exists(TEMP_OUTPUT_DIR):
            os.mkdir(TEMP_OUTPUT_DIR)

        if not os.path.exists(output):
            os.mkdir(output)

        clipped_video.write_videofile(temp_file_path)

        shutil.copy(temp_file_path, file_path)

        request.get()

def game_loop(clip: VideoClip, serial: serial.Serial, display:int, subclip_req: queue.Queue):
    global time_ref
    
    pygame.init()

    dp_size = pygame.display.get_desktop_sizes()[display]
    screen = pygame.display.set_mode(dp_size, FULLSCREEN & SCALED, display=display)
    
    player_lock = threading.RLock()
    player_screen = screen.copy()
    player_flag = threading.Event()
    player_thread = threading.Thread(target=player, args=(clip, player_screen, player_lock, player_flag))
    player_thread.start()

    # font = pygame.font.SysFont("Yu Gothic", 50, True)
    # text = font.render("Vmemoを記録中です", True, (0,0,200))
    
    progress_image = pygame.image.load("progress.png")
    mag = (screen.get_height() / 10) / progress_image.get_height()
    progress_image = pygame.transform.smoothscale(progress_image, (progress_image.get_width() * mag, progress_image.get_height() * mag))

    ticker = pygame.time.Clock()

    def before_return():
        player_flag.set()
        pygame.quit()

    while True:
        ticker.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
                    (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                print("Interrupt")
                before_return()
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                print("MOUSEBUTTONDOWN")

        serialData = serial.readline()

        if len(serialData):
            try:
                code = int(serialData)
            except:
                print("decode error")
            if code == 73:
                # text_start = pygame.time.get_ticks()
                if not subclip_req.qsize():
                        subclip_req.put(time_ref)
                        subclip_req.put("owatta?")
                        print("enqueue")

        with player_lock:
            screen.blit(player_screen, (0, 0))

        if subclip_req.qsize():
            # rect_size = (text.get_width(), text.get_height())
            # rect_upper_left_pos = (0, 40)
            # pygame.draw.rect(screen, (255,255,255), (dp_size[0] - rect_size[0] - rect_upper_left_pos[0], rect_upper_left_pos[1], rect_size[0], rect_size[1]))
            # screen.blit(text, (dp_size[0] - rect_size[0] - rect_upper_left_pos[0], rect_upper_left_pos[1]))
            screen.blit(progress_image, (screen.get_width() - progress_image.get_width(), screen.get_height() / 20))
            
        pygame.display.flip()

def main():
    load_dotenv()

    VMEMO_MOVIE_DIR = os.getenv("VMEMO_MOVIE_DIR")
    VMEMO_OUTPUT_DIR = os.getenv("VMEMO_OUTPUT_DIR")
    VMEMO_CLIP_DURATION = float(os.getenv("VMEMO_CLIP_DURATION"))
    VMEMO_DISPLAY = int(os.getenv("VMEMO_DISPLAY"))
    VMEMO_SERIAL_PORT = os.getenv("VMEMO_SERIAL_PORT")

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    shutil.copytree(VMEMO_MOVIE_DIR, temp_playng_dir)
    shutil.copytree(VMEMO_MOVIE_DIR, temp_editing_dir)

    playing_clip, _ = open_playing_clip(temp_playng_dir)
    editing_clip, clip_names = open_playing_clip(temp_editing_dir)

    print(clip_names)

    ports = list(serial.tools.list_ports.comports())
    print(list(map(lambda p: p.name, ports)))
    
    try:
        if VMEMO_SERIAL_PORT == "" and len(ports):
            serialPort = serial.Serial(ports[0].name, 115200, timeout=0)
        else:
            serialPort = serial.Serial(VMEMO_SERIAL_PORT, 115200, timeout=0)
        print(serialPort.name)
        if not serialPort.is_open:
            serialPort.open()
    except:
        print("Cannot open serial port")
        return

    subclip_req = queue.Queue()
    subclipper_thread = threading.Thread(target=subclipper, args=[subclip_req, editing_clip, clip_names, VMEMO_CLIP_DURATION, VMEMO_OUTPUT_DIR])
    subclipper_thread.start()

    game_loop(playing_clip, serialPort, VMEMO_DISPLAY, subclip_req)

# Ctrl+C 対策
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    main()
