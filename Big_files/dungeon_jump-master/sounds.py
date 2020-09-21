import pygame

pygame.mixer.init()

jump_sound = pygame.mixer.Sound('sounds/jump.wav')
step_sound = pygame.mixer.Sound('sounds/step.wav')
fireball_sound = pygame.mixer.Sound('sounds/fireball.wav')
explosion_sound = pygame.mixer.Sound('sounds/fireball_explosion.wav')


def adjust_volume(volume):
    jump_sound.set_volume(volume)
    step_sound.set_volume(volume)
    fireball_sound.set_volume(volume)
    explosion_sound.set_volume(volume)


adjust_volume(0.5)
