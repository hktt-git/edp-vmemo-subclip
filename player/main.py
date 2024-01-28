from moviepy.editor import *
import pygame
from pygame.locals import *

MOVIE_DIRECTORY = "./movie"

def imdisplay(imarray, screen=None):
    """Splashes the given image array on the given pygame screen """
    a = pygame.surfarray.make_surface(imarray.swapaxes(0, 1))
    if screen is None:
        screen = pygame.display.set_mode(imarray.shape[:2][::-1])
    screen.blit(a, (0, 0))
    pygame.display.flip()

pygame.init()
screen = pygame.display.set_mode((600, 400))

circle_position = pygame.Vector2()

clock = pygame.time.Clock()

F_RATE = 30

font = pygame.font.SysFont("Yu Gothic", 20)

text = font.render("Enterキーがクリックされました", True, (0,0,200))

TEXT_VISIBLE_DURATION = 2 * 1e3

text_start = None

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

  clip = VideoFileClip(f"{MOVIE_DIRECTORY}/sample_copy.mp4")

  audio = clip.audio
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
  
  result = []
  
  t0 = time.time()
  for t in np.arange(1.0 / fps, clip.duration-.001, 1.0 / fps):
      
      img = clip.get_frame(t)
      
      for event in pygame.event.get():
          if event.type == pygame.QUIT or \
                  (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
              if audio:
                  videoFlag.clear()
              print("Interrupt")
              return result
                  
          elif event.type == pygame.MOUSEBUTTONDOWN:
              x, y = pygame.mouse.get_pos()
              rgb = img[y, x]
              result.append({'time': t, 'position': (x, y),
                              'color': rgb})
              print("time, position, color : ", "%.03f, %s, %s" %
                    (t, str((x, y)), str(rgb)))
                  
      t1 = time.time()
      time.sleep(max(0, t - (t1-t0)))
      imdisplay(img, screen)
  
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      exit()
    if event.type == KEYDOWN:
      if event.key == K_RETURN:
        # pygame.draw.rect(screen, (255, 255, 255), (0, 0, 100, 100))
        text_start = pygame.time.get_ticks()
        print("enter")
