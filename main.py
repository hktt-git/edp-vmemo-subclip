import pygame
from pygame.locals import *

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
  
  for event in pygame.event.get():
    if event.type == QUIT:
      pygame.quit()
      exit()
    if event.type == KEYDOWN:
      if event.key == K_RETURN:
        # pygame.draw.rect(screen, (255, 255, 255), (0, 0, 100, 100))
        text_start = pygame.time.get_ticks()
        print("enter")
