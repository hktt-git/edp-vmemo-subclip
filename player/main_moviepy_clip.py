from moviepy.editor import *
from moviepy.video.fx.resize import resize
import threading
import time
# import qrcode
import pygame
from pygame.locals import *
  
MOVIE_DIRECTORY = "./movie"

def main():
    OUTPUT_DIRECTORY = "./output"
    OUTPUT_CLIP_DURATION = 5

    time_start = time.perf_counter()

    video_for_edit = VideoFileClip(f"{MOVIE_DIRECTORY}/sample_copy.mp4")

    player_thread = threading.Thread(target=play_video)

    print("start")

    player_thread.start()

    time.sleep(1)

    counter = 1

    while True:
      input()
      
      clip_end_position = time.perf_counter() - time_start
      
      print(clip_end_position)
      
      clip_start_position = max(clip_end_position - OUTPUT_CLIP_DURATION, 0)
      
      clipped_video = video_for_edit.subclip(clip_start_position, clip_end_position)
      
      clipped_video.write_videofile(f"{OUTPUT_DIRECTORY}/output{counter}.mp4")
      
      url = f"https://youtu.be/w52V8AVYt-A?si=Zikj4eqShU2BCw3S&t={round(clip_start_position)}"
      
      print(url)
      
      # qrcode.make(url).save(f"{OUTPUT_DIRECTORY}/qrcode{counter}.png")
      
      counter += 1

def play_video():
  video = VideoFileClip(f"{MOVIE_DIRECTORY}/sample.mp4")
  
  time_start = time.perf_counter()

  video_show = resize(video, (1280, 720))
  
  video_show.preview(fullscreen=True)
  
if __name__ == "__main__":
    main()