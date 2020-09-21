import pygame

screen_w = 512
screen_h = 704
pygame.display.init()
screen = pygame.display.set_mode((screen_w, screen_h))

background_img = pygame.image.load('frames/background.png').convert_alpha()
platform_img = pygame.image.load('frames/platform.png').convert_alpha()
heart_img = pygame.image.load('frames/ui_heart_full.png').convert_alpha()
blue_flask_img = pygame.image.load('frames/flask_big_blue.png').convert_alpha()
red_flask_img = pygame.image.load('frames/flask_big_red.png').convert_alpha()
fire_img = pygame.image.load('frames/fire.png').convert_alpha()

demon_run_right_img = [pygame.image.load('frames/big_demon_run_anim_r0.png').convert_alpha(),
                       pygame.image.load('frames/big_demon_run_anim_r1.png').convert_alpha(),
                       pygame.image.load('frames/big_demon_run_anim_r2.png').convert_alpha(),
                       pygame.image.load('frames/big_demon_run_anim_r3.png').convert_alpha()]
demon_run_left_img = [pygame.image.load('frames/big_demon_run_anim_l0.png').convert_alpha(),
                      pygame.image.load('frames/big_demon_run_anim_l1.png').convert_alpha(),
                      pygame.image.load('frames/big_demon_run_anim_l2.png').convert_alpha(),
                      pygame.image.load('frames/big_demon_run_anim_l3.png').convert_alpha()]

knight_m_run_right_img = [pygame.image.load('frames/knight_m_run_anim_r0.png').convert_alpha(),
                          pygame.image.load('frames/knight_m_run_anim_r1.png').convert_alpha(),
                          pygame.image.load('frames/knight_m_run_anim_r2.png').convert_alpha(),
                          pygame.image.load('frames/knight_m_run_anim_r3.png').convert_alpha()]
knight_m_run_left_img = [pygame.image.load('frames/knight_m_run_anim_l0.png').convert_alpha(),
                         pygame.image.load('frames/knight_m_run_anim_l1.png').convert_alpha(),
                         pygame.image.load('frames/knight_m_run_anim_l2.png').convert_alpha(),
                         pygame.image.load('frames/knight_m_run_anim_l3.png').convert_alpha()]
knight_m_stat_img = [pygame.image.load('frames/knight_m_stat_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/knight_m_stat_anim_l0.png').convert_alpha()]
knight_m_jump_img = [pygame.image.load('frames/knight_m_hit_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/knight_m_hit_anim_l0.png').convert_alpha()]

elf_m_run_right_img = [pygame.image.load('frames/elf_m_run_anim_r0.png').convert_alpha(),
                       pygame.image.load('frames/elf_m_run_anim_r1.png').convert_alpha(),
                       pygame.image.load('frames/elf_m_run_anim_r2.png').convert_alpha(),
                       pygame.image.load('frames/elf_m_run_anim_r3.png').convert_alpha()]
elf_m_run_left_img = [pygame.image.load('frames/elf_m_run_anim_l0.png').convert_alpha(),
                      pygame.image.load('frames/elf_m_run_anim_l1.png').convert_alpha(),
                      pygame.image.load('frames/elf_m_run_anim_l2.png').convert_alpha(),
                      pygame.image.load('frames/elf_m_run_anim_l3.png').convert_alpha()]
elf_m_stat_img = [pygame.image.load('frames/elf_m_stat_anim_r0.png').convert_alpha(),
                  pygame.image.load('frames/elf_m_stat_anim_l0.png').convert_alpha()]
elf_m_jump_img = [pygame.image.load('frames/elf_m_hit_anim_r0.png').convert_alpha(),
                  pygame.image.load('frames/elf_m_hit_anim_l0.png').convert_alpha()]

wizard_m_run_right_img = [pygame.image.load('frames/wizard_m_run_anim_r0.png').convert_alpha(),
                          pygame.image.load('frames/wizard_m_run_anim_r1.png').convert_alpha(),
                          pygame.image.load('frames/wizard_m_run_anim_r2.png').convert_alpha(),
                          pygame.image.load('frames/wizard_m_run_anim_r3.png').convert_alpha()]
wizard_m_run_left_img = [pygame.image.load('frames/wizard_m_run_anim_l0.png').convert_alpha(),
                         pygame.image.load('frames/wizard_m_run_anim_l1.png').convert_alpha(),
                         pygame.image.load('frames/wizard_m_run_anim_l2.png').convert_alpha(),
                         pygame.image.load('frames/wizard_m_run_anim_l3.png').convert_alpha()]
wizard_m_stat_img = [pygame.image.load('frames/wizard_m_stat_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/wizard_m_stat_anim_l0.png').convert_alpha()]
wizard_m_jump_img = [pygame.image.load('frames/wizard_m_hit_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/wizard_m_hit_anim_l0.png').convert_alpha()]

dragon_m_run_right_img = [pygame.image.load('frames/dragon_m_run_anim_r0.png').convert_alpha(),
                          pygame.image.load('frames/dragon_m_run_anim_r1.png').convert_alpha(),
                          pygame.image.load('frames/dragon_m_run_anim_r2.png').convert_alpha(),
                          pygame.image.load('frames/dragon_m_run_anim_r3.png').convert_alpha()]
dragon_m_run_left_img = [pygame.image.load('frames/dragon_m_run_anim_l0.png').convert_alpha(),
                         pygame.image.load('frames/dragon_m_run_anim_l1.png').convert_alpha(),
                         pygame.image.load('frames/dragon_m_run_anim_l2.png').convert_alpha(),
                         pygame.image.load('frames/dragon_m_run_anim_l3.png').convert_alpha()]
dragon_m_stat_img = [pygame.image.load('frames/dragon_m_stat_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/dragon_m_stat_anim_l0.png').convert_alpha()]
dragon_m_jump_img = [pygame.image.load('frames/dragon_m_hit_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/dragon_m_hit_anim_l0.png').convert_alpha()]

knight_f_run_right_img = [pygame.image.load('frames/knight_f_run_anim_r0.png').convert_alpha(),
                          pygame.image.load('frames/knight_f_run_anim_r1.png').convert_alpha(),
                          pygame.image.load('frames/knight_f_run_anim_r2.png').convert_alpha(),
                          pygame.image.load('frames/knight_f_run_anim_r3.png').convert_alpha()]
knight_f_run_left_img = [pygame.image.load('frames/knight_f_run_anim_l0.png').convert_alpha(),
                         pygame.image.load('frames/knight_f_run_anim_l1.png').convert_alpha(),
                         pygame.image.load('frames/knight_f_run_anim_l2.png').convert_alpha(),
                         pygame.image.load('frames/knight_f_run_anim_l3.png').convert_alpha()]
knight_f_stat_img = [pygame.image.load('frames/knight_f_stat_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/knight_f_stat_anim_l0.png').convert_alpha()]
knight_f_jump_img = [pygame.image.load('frames/knight_f_hit_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/knight_f_hit_anim_l0.png').convert_alpha()]

elf_f_run_right_img = [pygame.image.load('frames/elf_f_run_anim_r0.png').convert_alpha(),
                       pygame.image.load('frames/elf_f_run_anim_r1.png').convert_alpha(),
                       pygame.image.load('frames/elf_f_run_anim_r2.png').convert_alpha(),
                       pygame.image.load('frames/elf_f_run_anim_r3.png').convert_alpha()]
elf_f_run_left_img = [pygame.image.load('frames/elf_f_run_anim_l0.png').convert_alpha(),
                      pygame.image.load('frames/elf_f_run_anim_l1.png').convert_alpha(),
                      pygame.image.load('frames/elf_f_run_anim_l2.png').convert_alpha(),
                      pygame.image.load('frames/elf_f_run_anim_l3.png').convert_alpha()]
elf_f_stat_img = [pygame.image.load('frames/elf_f_stat_anim_r0.png').convert_alpha(),
                  pygame.image.load('frames/elf_f_stat_anim_l0.png').convert_alpha()]
elf_f_jump_img = [pygame.image.load('frames/elf_f_hit_anim_r0.png').convert_alpha(),
                  pygame.image.load('frames/elf_f_hit_anim_l0.png').convert_alpha()]

wizard_f_run_right_img = [pygame.image.load('frames/wizard_f_run_anim_r0.png').convert_alpha(),
                          pygame.image.load('frames/wizard_f_run_anim_r1.png').convert_alpha(),
                          pygame.image.load('frames/wizard_f_run_anim_r2.png').convert_alpha(),
                          pygame.image.load('frames/wizard_f_run_anim_r3.png').convert_alpha()]
wizard_f_run_left_img = [pygame.image.load('frames/wizard_f_run_anim_l0.png').convert_alpha(),
                         pygame.image.load('frames/wizard_f_run_anim_l1.png').convert_alpha(),
                         pygame.image.load('frames/wizard_f_run_anim_l2.png').convert_alpha(),
                         pygame.image.load('frames/wizard_f_run_anim_l3.png').convert_alpha()]
wizard_f_stat_img = [pygame.image.load('frames/wizard_f_stat_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/wizard_f_stat_anim_l0.png').convert_alpha()]
wizard_f_jump_img = [pygame.image.load('frames/wizard_f_hit_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/wizard_f_hit_anim_l0.png').convert_alpha()]

dragon_f_run_right_img = [pygame.image.load('frames/dragon_f_run_anim_r0.png').convert_alpha(),
                          pygame.image.load('frames/dragon_f_run_anim_r1.png').convert_alpha(),
                          pygame.image.load('frames/dragon_f_run_anim_r2.png').convert_alpha(),
                          pygame.image.load('frames/dragon_f_run_anim_r3.png').convert_alpha()]
dragon_f_run_left_img = [pygame.image.load('frames/dragon_f_run_anim_l0.png').convert_alpha(),
                         pygame.image.load('frames/dragon_f_run_anim_l1.png').convert_alpha(),
                         pygame.image.load('frames/dragon_f_run_anim_l2.png').convert_alpha(),
                         pygame.image.load('frames/dragon_f_run_anim_l3.png').convert_alpha()]
dragon_f_stat_img = [pygame.image.load('frames/dragon_f_stat_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/dragon_f_stat_anim_l0.png').convert_alpha()]
dragon_f_jump_img = [pygame.image.load('frames/dragon_f_hit_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/dragon_f_hit_anim_l0.png').convert_alpha()]

pumpkin_run_right_img = [pygame.image.load('frames/pumpkin_dude_run_anim_r0.png').convert_alpha(),
                         pygame.image.load('frames/pumpkin_dude_run_anim_r1.png').convert_alpha(),
                         pygame.image.load('frames/pumpkin_dude_run_anim_r2.png').convert_alpha(),
                         pygame.image.load('frames/pumpkin_dude_run_anim_r3.png').convert_alpha()]
pumpkin_run_left_img = [pygame.image.load('frames/pumpkin_dude_run_anim_l0.png').convert_alpha(),
                        pygame.image.load('frames/pumpkin_dude_run_anim_l1.png').convert_alpha(),
                        pygame.image.load('frames/pumpkin_dude_run_anim_l2.png').convert_alpha(),
                        pygame.image.load('frames/pumpkin_dude_run_anim_l3.png').convert_alpha()]
pumpkin_stat_img = [pygame.image.load('frames/pumpkin_dude_stat_anim_r0.png').convert_alpha(),
                    pygame.image.load('frames/pumpkin_dude_stat_anim_l0.png').convert_alpha()]
pumpkin_jump_img = [pygame.image.load('frames/pumpkin_dude_hit_anim_r0.png').convert_alpha(),
                    pygame.image.load('frames/pumpkin_dude_hit_anim_l0.png').convert_alpha()]

doc_run_right_img = [pygame.image.load('frames/doc_run_anim_r0.png').convert_alpha(),
                     pygame.image.load('frames/doc_run_anim_r1.png').convert_alpha(),
                     pygame.image.load('frames/doc_run_anim_r2.png').convert_alpha(),
                     pygame.image.load('frames/doc_run_anim_r3.png').convert_alpha()]
doc_run_left_img = [pygame.image.load('frames/doc_run_anim_l0.png').convert_alpha(),
                    pygame.image.load('frames/doc_run_anim_l1.png').convert_alpha(),
                    pygame.image.load('frames/doc_run_anim_l2.png').convert_alpha(),
                    pygame.image.load('frames/doc_run_anim_l3.png').convert_alpha()]
doc_stat_img = [pygame.image.load('frames/doc_stat_anim_r0.png').convert_alpha(),
                pygame.image.load('frames/doc_stat_anim_l0.png').convert_alpha()]
doc_jump_img = [pygame.image.load('frames/doc_hit_anim_r0.png').convert_alpha(),
                pygame.image.load('frames/doc_hit_anim_l0.png').convert_alpha()]
