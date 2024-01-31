from moviepy.editor import *
from moviepy.video.fx.resize import resize
import threading
import time
import pygame
from pygame.locals import *
import numpy as np
import serial
import serial.tools.list_ports

MOVIE_DIRECTORY = "./movie"
OUTPUT_DIRECTORY = "./output"
OUTPUT_CLIP_DURATION = 5

def imdisplay(imarray, screen=None):
    """Splashes the given image array on the given pygame screen """
    a = pygame.surfarray.make_surface(imarray.swapaxes(0, 1))
    if screen is None:
        screen = pygame.display.set_mode(imarray.shape[:2][::-1])
    # screen.blit(a, (0, 0))
    pygame.transform.scale(a, DISPLAY_SIZE, screen)


ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)
    print(" device       :", p.device)
    print(" name         :", p.name)
    print(" description  :", p.description)
    print(" hwid         :", p.hwid)
    print(" vid          :", p.vid)
    print(" pid          :", p.pid)
    print(" serial_number:", p.serial_number)
    print(" location     :", p.location)
    print(" manufactuer  :", p.manufacturer)
    print(" product      :", p.product)
    print(" interface    :", p.interface)
    print("")

if not len(ports):
   print("Serial device not found")
   exit()

portname = ports[0].name

serialPort = serial.Serial(portname, 115200, timeout=0)

# while True: 
#   line = serialPort.readline()

#   if not len(line):
#     time.sleep(0.1)
#     continue

#   print(line)

pygame.init()

DISPLAY_SIZE = pygame.display.get_desktop_sizes()[-1]
print(DISPLAY_SIZE)

screen = pygame.display.set_mode(DISPLAY_SIZE, FULLSCREEN & SCALED)

circle_position = pygame.Vector2()

clock = pygame.time.Clock()

F_RATE = 30

font = pygame.font.SysFont("Yu Gothic", 50, True)

text = font.render("Vmemoを記録中です", True, (0,0,200))

TEXT_VISIBLE_DURATION = 2 * 1e3

text_start = None


clip = VideoFileClip(f"{MOVIE_DIRECTORY}/sample_copy.mp4")
video_for_edit = VideoFileClip(f"{MOVIE_DIRECTORY}/sample.mp4")

# clip = resize(clip, DISPLAY_SIZE)
fps=15

audio = clip.audio
audio_fps=22050
audio_buffersize=3000
audio_nbytes=2

# the sound will be played in parrallel. We are not
# parralellizing it on different CPUs because it seems that
# pygame and openCV already use several cpus it seems.

# two synchro-flags to tell whether audio and video are ready
videoFlag = threading.Event()
audioFlag = threading.Event()
# launch the thread
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

counter = 1

for t in np.arange(1.0 / fps, clip.duration-.001, 1.0 / fps):
    
    img = clip.get_frame(t)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT or \
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            if audio:
                videoFlag.clear()
            print("Interrupt")
            exit()
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            rgb = img[y, x]
            print("time, position, color : ", "%.03f, %s, %s" %
                  (t, str((x, y)), str(rgb)))
                
    t1 = time.time()
    time.sleep(max(0, t - (t1-t0)))
    imdisplay(img, screen)

    if text_start is not None and pygame.time.get_ticks() - text_start < TEXT_VISIBLE_DURATION:
      rect_size = (text.get_width(), text.get_height())
      rect_upper_left_pos = (0, 0)
      pygame.draw.rect(screen, (255,255,255), (DISPLAY_SIZE[0] - rect_size[0] - rect_upper_left_pos[0], rect_upper_left_pos[1], rect_size[0], rect_size[1]))
      screen.blit(text, (DISPLAY_SIZE[0] - rect_size[0] - rect_upper_left_pos[0], rect_upper_left_pos[1]))
    else:
      text_start = None

    serialData = serialPort.readline()

    if len(serialData):
       code = int(serialData)
       if code == 73:
        text_start = pygame.time.get_ticks()

        def task():
          global counter
          clip_end_position = t1 - t0
          print(clip_end_position)
          clip_start_position = max(clip_end_position - OUTPUT_CLIP_DURATION, 0)
          clipped_video = video_for_edit.subclip(clip_start_position, clip_end_position)
          clipped_video.write_videofile(f"{OUTPUT_DIRECTORY}/output{counter}.mp4")
          counter += 1

        thread = threading.Thread(target=task)
        thread.start()

    pygame.display.flip()


while True:
  clock.tick(F_RATE)
  
  screen.fill((0, 0, 0))
  
  pygame.draw.circle(screen, (255, 255, 255), circle_position, 20)
  
  if text_start is not None and pygame.time.get_ticks() - text_start < TEXT_VISIBLE_DURATION:
    screen.blit(text, (40,30))
  else:
    text_start = None
  
  pygame.display.update()
  
  circle_position += 1, 1

  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      exit()
    if event.type == KEYDOWN:
      if event.key == K_RETURN:
        # pygame.draw.rect(screen, (255, 255, 255), (0, 0, 100, 100))
        text_start = pygame.time.get_ticks()
        print("enter")
