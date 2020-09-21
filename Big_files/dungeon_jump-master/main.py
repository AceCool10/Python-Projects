import pygame
import random as rnd
import sys
import frames
import sounds

from pygame.locals import (
    K_ESCAPE,
    K_BACKSPACE,
    K_RETURN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_a,
    K_d,
    KEYDOWN)

screen_w = 512
screen_h = 704


def main():
    pygame.init()
    game = State()
    running = True
    while running:

        if game.showing_title:
            game.show_title()

        elif game.showing_selection:
            game.show_selection()

        elif game.showing_leaderboard:
            game.show_leaderboard()

        elif game.showing_options:
            game.show_options(None)

        elif game.showing_help:
            game.show_help(None)

        elif game.running:
            game.run_game()

        elif game.showing_death:
            game.show_death_screen()

        else:
            running = False

    pygame.display.quit()
    pygame.quit()
    sys.exit()


class State:

    def __init__(self):
        self.screen = pygame.display.set_mode((screen_w, screen_h))
        self.clock = pygame.time.Clock()
        self.lrg_font = pygame.font.Font(None, 50)
        self.med_font = pygame.font.Font(None, 37)
        self.sm_y_font = pygame.font.SysFont(None, 28)
        self.sm_font = pygame.font.SysFont(None, 24)
        self.fps = 60

        self.background1 = Background(screen_w//2)
        self.background2 = Background(screen_w//2-704)

        self.showing_title = True
        self.showing_leaderboard = False
        self.showing_selection = False
        self.running = False
        self.paused = False
        self.showing_death = False
        self.showing_options = False
        self.showing_help = False

        self.character = None
        self.difficulty = None

        self.leaderboard = get_leaderboard()
        self.highscore = False
        self.score = 0

    def run_game(self):

        dynamic_sprites = pygame.sprite.Group()
        dynamic_sprites.add([self.background1, self.background2])

        n_platforms = 15
        pos = [rnd.uniform(100, screen_w-100), screen_h-25]
        platforms = [Platform(pos)]
        for i in range(1, n_platforms):
            platforms.append(Platform(platforms[i-1].rect.center))
        dynamic_sprites.add(platforms)

        player = Player(platforms[3].rect.center[0], platforms[3].rect.top, self.character)

        origin = Origin(player.rect.center)
        dynamic_sprites.add(origin)

        static_sprites = pygame.sprite.Group()

        lives_marker = Powerup(screen_w-155, 30, 'lives')
        d_jump_marker = Powerup(screen_w-155, 60, 'double_jump')
        fireball_marker = Powerup(screen_w-155, 90, 'fireball')

        static_sprites.add([lives_marker, d_jump_marker, fireball_marker, player])

        if self.difficulty == 'medium':
            enemy_chance = 10
            projectile_chance = 100
            projectile_speed = 6
            powerup_chance = 10
            enemy_speed = 5

        elif self.difficulty == 'easy':
            enemy_chance = 20
            projectile_chance = 200
            projectile_speed = 4
            powerup_chance = 5
            enemy_speed = 3

        else:
            enemy_chance = 5
            projectile_chance = 50
            projectile_speed = 8
            powerup_chance = 20
            enemy_speed = 7

        self.score = 0

        while self.running:
            for event in pygame.event.get():

                if event.type == KEYDOWN:

                    if event.key == K_ESCAPE:
                        self.pause_game()
                        self.show_pause_screen()

                    if event.key == K_SPACE:

                        if player.on_platform:
                            player.is_jumping = True
                            player.on_platform = False
                            player.time = 0
                            pygame.mixer.Sound.play(sounds.jump_sound)

                        elif player.powerups['double_jump'] > 0:
                            player.powerups['double_jump'] -= 1
                            player.is_jumping = True
                            player.time = 0
                            pygame.mixer.Sound.play(sounds.jump_sound)

                if event.type == pygame.MOUSEBUTTONDOWN and player.powerups['fireball'] > 0 and player.projectile is None:
                    player.powerups['fireball'] -= 1
                    pos = pygame.mouse.get_pos()
                    player.create_projectile(pos, dynamic_sprites)

                if event.type == pygame.QUIT:
                    self.exit()

            pressed_keys = pygame.key.get_pressed()
            player.move(pressed_keys, dynamic_sprites)

            if player.projectile is not None:
                player.projectile.move()
                if player.projectile.hits_boundary():
                    player.remove_projectile()

            if platforms[0].rect.top > screen_h+50:
                platforms[0].remove_platform(platforms)
                platforms.append(Platform(platforms[-1].rect.center))
                dynamic_sprites.add(platforms[-1])
                if rnd.choice(range(enemy_chance)) == 0:
                    platforms[-1].create_enemy(dynamic_sprites, enemy_speed)
                if rnd.choice(range(powerup_chance)) == 0:
                    platforms[-1].create_powerup(dynamic_sprites)

            current_platform = True
            for platform in platforms:

                if current_platform:
                    if player.falls_off(platform):
                        current_platform = False
                    elif player.lands_on(platform, platform.lastYPos, dynamic_sprites):
                        pygame.mixer.Sound.play(sounds.step_sound)
                        current_platform = False
                platform.lastYPos = platform.rect.top

                if platform.powerup is not None and player.touches(platform.powerup):
                    player.consumes(platform.powerup)
                    platform.remove_powerup()

                if platform.enemy is not None:
                    platform.enemy.move()
                    if player.projectile is not None and player.projectile.hits(platform.enemy):
                        platform.remove_enemy()
                        self.score += 500
                    elif player.touches(platform.enemy):
                        self.go_to_death()

                if platform.projectile is not None:
                    platform.projectile.move()
                    if platform.projectile.hits(player):
                        if player.powerups['lives'] > 1:
                            player.powerups['lives'] -= 1
                            platform.remove_projectile()
                        else:
                            self.go_to_death()
                    elif platform.projectile.hits_boundary():
                        platform.remove_projectile()
                elif platform.enemy is not None and rnd.choice(range(projectile_chance)) == 0:
                    platform.create_projectile(projectile_speed, dynamic_sprites)

            if player.falls_below(platforms[0]):
                self.go_to_death()

            player.animate()

            self.background1.shift_background()
            self.background2.shift_background()

            if origin.rect.center[1]-player.rect.center[1] > self.score:
                self.score = origin.rect.center[1]-player.rect.center[1]

            scoreboard_surf, scoreboard_rect = render_text(self.sm_font, 'Score: {}'.format(self.score), left=20,
                                                           top=20)
            lives_surf, lives_rect = render_text(self.sm_font, 'Lives: {}'.format(player.powerups['lives']),
                                                 left=lives_marker.rect.right+10, top=lives_marker.rect.top+5)
            d_jump_surf, d_jump_rect = render_text(self.sm_font, 'Double Jump: {}'.format(player.powerups['double_jump']),
                                                   left=d_jump_marker.rect.right+10, top=d_jump_marker.rect.top+5)
            fireball_surf, fireball_rect = render_text(self.sm_font, 'Fireball: {}'.format(player.powerups['fireball']),
                                                       left=fireball_marker.rect.right+10, top=fireball_marker.rect.top+5)

            for entity in dynamic_sprites:
                self.screen.blit(entity.surf, entity.rect)
            for entity in static_sprites:
                self.screen.blit(entity.surf, entity.rect)
            self.screen.blit(scoreboard_surf, scoreboard_rect)
            self.screen.blit(lives_surf, lives_rect)
            self.screen.blit(d_jump_surf, d_jump_rect)
            self.screen.blit(fireball_surf, fireball_rect)

            pygame.display.flip()
            self.clock.tick(self.fps)

    def show_title(self):
        title_surf, title_rect = render_text(self.lrg_font, 'Dungeon Jump', x=screen_w//2, y=1.5*screen_h//5)
        play_game_surf_w, play_game_rect_w = render_text(self.sm_font, 'Play Game', x=screen_w//2, y=2.5*screen_h//5)
        play_game_surf_y, play_game_rect_y = render_text(self.sm_y_font, 'Play Game', x=screen_w//2, y=2.5*screen_h//5,
                                                         color=(255, 255, 0))
        leaderboard_surf_w, leaderboard_rect_w = render_text(self.sm_font, 'Leaderboards', x=screen_w//2,
                                                             y=3*screen_h//5)
        leaderboard_surf_y, leaderboard_rect_y = render_text(self.sm_y_font, 'Leaderboards', x=screen_w//2,
                                                             y=3*screen_h//5, color=(255, 255, 0))
        options_surf_w, options_rect_w = render_text(self.sm_font, 'Options', x=screen_w//2, y=3.5*screen_h//5)
        options_surf_y, options_rect_y = render_text(self.sm_y_font, 'Options', x=screen_w//2, y=3.5*screen_h//5,
                                                     color=(255, 255, 0))
        help_surf_w, help_rect_w = render_text(self.sm_font, 'Help', x=screen_w//2, y=4*screen_h//5)
        help_surf_y, help_rect_y = render_text(self.sm_y_font, 'Help', x=screen_w//2, y=4*screen_h//5,
                                               color=(255, 255, 0))

        while self.showing_title:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                if play_game_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_selection()

                if leaderboard_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_leaderboard()

                if options_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_options()

                if help_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_help()

            self.scrolling_background()
            self.screen.blit(title_surf, title_rect)

            if play_game_rect_w.collidepoint(mouse_pos):
                self.screen.blit(play_game_surf_y, play_game_rect_y)
            else:
                self.screen.blit(play_game_surf_w, play_game_rect_w)

            if leaderboard_rect_w.collidepoint(mouse_pos):
                self.screen.blit(leaderboard_surf_y, leaderboard_rect_y)
            else:
                self.screen.blit(leaderboard_surf_w, leaderboard_rect_w)

            if options_rect_w.collidepoint(mouse_pos):
                self.screen.blit(options_surf_y, options_rect_y)
            else:
                self.screen.blit(options_surf_w, options_rect_w)

            if help_rect_w.collidepoint(mouse_pos):
                self.screen.blit(help_surf_y, help_rect_y)
            else:
                self.screen.blit(help_surf_w, help_rect_w)

            pygame.display.flip()
            self.clock.tick(self.fps)

    def show_selection(self):
        difficulty_surf, difficulty_rect = render_text(self.med_font, 'Choose Your Difficulty', x=screen_w//2,
                                                       y=screen_h//6)
        easy_surf_w, easy_rect_w = render_text(self.sm_font, 'Easy', x=0.75*screen_w//3, y=1.5*screen_h//6)
        easy_surf_y, easy_rect_y = render_text(self.sm_y_font, 'Easy', x=0.75*screen_w//3, y=1.5*screen_h//6,
                                               color=(255, 255, 0))
        medium_surf_w, medium_rect_w = render_text(self.sm_font, 'Medium', x=1.5*screen_w//3, y=1.5*screen_h//6)
        medium_surf_y, medium_rect_y = render_text(self.sm_y_font, 'Medium', x=1.5*screen_w//3, y=1.5*screen_h//6,
                                                   color=(255, 255, 0))
        hard_surf_w, hard_rect_w = render_text(self.sm_font, 'Hard', x=2.25*screen_w//3, y=1.5*screen_h//6)
        hard_surf_y, hard_rect_y = render_text(self.sm_y_font, 'Hard', x=2.25*screen_w//3, y=1.5*screen_h//6,
                                               color=(255, 255, 0))

        character_surf, character_rect = render_text(self.med_font, 'Choose Your Character', x=screen_w//2,
                                                     y=2*screen_h//6)
        knight_m = Player(screen_w//5, 2.75*screen_h//6, 'knight_m')
        knight_m_surf_w, knight_m_rect_w = render_text(self.sm_font, 'Knight (m)', x=screen_w//5, y=2.9*screen_h//6)
        knight_m_surf_y, knight_m_rect_y = render_text(self.sm_y_font, 'Knight (m)', x=screen_w//5, y=2.9*screen_h//6,
                                                       color=(255, 255, 0))
        elf_m = Player(2*screen_w//5, 2.75*screen_h//6, 'elf_m')
        elf_m_surf_w, elf_m_rect_w = render_text(self.sm_font, 'Elf (m)', x=2*screen_w//5, y=2.9*screen_h//6)
        elf_m_surf_y, elf_m_rect_y = render_text(self.sm_y_font, 'Elf (m)', x=2*screen_w//5, y=2.9*screen_h//6,
                                                 color=(255, 255, 0))
        wizard_m = Player(3*screen_w//5, 2.75*screen_h//6, 'wizard_m')
        wizard_m_surf_w, wizard_m_rect_w = render_text(self.sm_font, 'Wizard (m)', x=3*screen_w//5,
                                                       y=2.9*screen_h//6)
        wizard_m_surf_y, wizard_m_rect_y = render_text(self.sm_y_font, 'Wizard (m)', x=3*screen_w//5,
                                                       y=2.9*screen_h//6, color=(255, 255, 0))
        dragon_m = Player(4*screen_w//5, 2.75*screen_h//6, 'dragon_m')
        dragon_m_surf_w, dragon_m_rect_w = render_text(self.sm_font, 'Dragon (m)', x=4*screen_w//5,
                                                       y=2.9*screen_h//6)
        dragon_m_surf_y, dragon_m_rect_y = render_text(self.sm_y_font, 'Dragon (m)', x=4*screen_w//5,
                                                       y=2.9*screen_h//6, color=(255, 255, 0))
        knight_f = Player(screen_w//5, 3.5*screen_h//6, 'knight_f')
        knight_f_surf_w, knight_f_rect_w = render_text(self.sm_font, 'Knight (f)', x=screen_w//5, y=3.65*screen_h//6)
        knight_f_surf_y, knight_f_rect_y = render_text(self.sm_y_font, 'Knight (f)', x=screen_w//5, y=3.65*screen_h//6,
                                                       color=(255, 255, 0))
        elf_f = Player(2*screen_w//5, 3.5*screen_h//6, 'elf_f')
        elf_f_surf_w, elf_f_rect_w = render_text(self.sm_font, 'Elf (f)', x=2*screen_w//5, y=3.65*screen_h//6)
        elf_f_surf_y, elf_f_rect_y = render_text(self.sm_y_font, 'Elf (f)', x=2*screen_w//5, y=3.65*screen_h//6,
                                                 color=(255, 255, 0))
        wizard_f = Player(3*screen_w//5, 3.5*screen_h//6, 'wizard_f')
        wizard_f_surf_w, wizard_f_rect_w = render_text(self.sm_font, 'Wizard (f)', x=3*screen_w//5,
                                                       y=3.65*screen_h//6)
        wizard_f_surf_y, wizard_f_rect_y = render_text(self.sm_y_font, 'Wizard (f)', x=3*screen_w//5,
                                                       y=3.65*screen_h//6, color=(255, 255, 0))
        dragon_f = Player(4*screen_w//5, 3.5*screen_h//6, 'dragon_f')
        dragon_f_surf_w, dragon_f_rect_w = render_text(self.sm_font, 'Dragon (f)', x=4*screen_w//5,
                                                       y=3.65*screen_h//6)
        dragon_f_surf_y, dragon_f_rect_y = render_text(self.sm_y_font, 'Dragon (f)', x=4*screen_w//5,
                                                       y=3.65*screen_h//6, color=(255, 255, 0))
        pumpkin = Player(1.5*screen_w//5, 4.25*screen_h//6, 'pumpkin')
        pumpkin_surf_w, pumpkin_rect_w = render_text(self.sm_font, 'Pumpkin', x=1.5*screen_w//5, y=4.4*screen_h//6)
        pumpkin_surf_y, pumpkin_rect_y = render_text(self.sm_y_font, 'Pumpkin', x=1.5*screen_w//5,
                                                     y=4.4*screen_h//6, color=(255, 255, 0))
        doc = Player(3.5*screen_w//5, 4.25*screen_h//6, 'doc')
        doc_surf_w, doc_rect_w = render_text(self.sm_font, 'Plague Doctor', x=3.5*screen_w//5, y=4.4*screen_h//6)
        doc_surf_y, doc_rect_y = render_text(self.sm_y_font, 'Plague Doctor', x=3.5*screen_w//5, y=4.4*screen_h//6,
                                             color=(255, 255, 0))

        sprites = pygame.sprite.Group()
        sprites.add([knight_m, elf_m, wizard_m, dragon_m, knight_f, elf_f, wizard_f, dragon_f, pumpkin, doc])

        play_game_surf_w, play_game_rect_w = render_text(self.sm_font, 'Play Game', x=screen_w//3, y=5*screen_h//6)
        play_game_surf_y, play_game_rect_y = render_text(self.sm_y_font, 'Play Game', x=screen_w//3, y=5*screen_h//6,
                                                         color=(255, 255, 0))
        back_surf_w, back_rect_w = render_text(self.sm_font, 'Main Menu', x=2*screen_w//3, y=5*screen_h//6)
        back_surf_y, back_rect_y = render_text(self.sm_y_font, 'Main Menu', x=2*screen_w//3, y=5*screen_h//6,
                                               color=(255, 255, 0))
        error_surf, error_rect = render_text(self.sm_y_font, 'Select Your Character/Difficulty', x=screen_w//2,
                                             y=5.5*screen_h//6, color=(255, 0, 0))
        error = False

        while self.showing_selection:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                if play_game_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.difficulty is not None and self.character is not None:
                            self.go_to_game()
                        else:
                            error = True

                if back_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_title()

                elif easy_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.difficulty != 'easy':
                            self.difficulty = 'easy'
                        else:
                            self.difficulty = None

                elif medium_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.difficulty != 'medium':
                            self.difficulty = 'medium'
                        else:
                            self.difficulty = None

                elif hard_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.difficulty != 'hard':
                            self.difficulty = 'hard'
                        else:
                            self.difficulty = None

                elif knight_m_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'knight_m':
                            self.character = 'knight_m'
                        else:
                            self.character = None

                elif elf_m_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'elf_m':
                            self.character = 'elf_m'
                        else:
                            self.character = None

                elif wizard_m_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'wizard_m':
                            self.character = 'wizard_m'
                        else:
                            self.character = None

                elif dragon_m_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'dragon_m':
                            self.character = 'dragon_m'
                        else:
                            self.character = None

                elif knight_f_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'knight_f':
                            self.character = 'knight_f'
                        else:
                            self.character = None

                elif elf_f_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'elf_f':
                            self.character = 'elf_f'
                        else:
                            self.character = None

                elif wizard_f_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'wizard_f':
                            self.character = 'wizard_f'
                        else:
                            self.character = None

                elif dragon_f_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'dragon_f':
                            self.character = 'dragon_f'
                        else:
                            self.character = None

                elif pumpkin_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'pumpkin':
                            self.character = 'pumpkin'
                        else:
                            self.character = None

                elif doc_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.character != 'doc':
                            self.character = 'doc'
                        else:
                            self.character = None

            self.scrolling_background()
            self.screen.blit(difficulty_surf, difficulty_rect)
            self.screen.blit(character_surf, character_rect)

            if self.difficulty == 'easy' or easy_rect_w.collidepoint(mouse_pos):
                self.screen.blit(easy_surf_y, easy_rect_y)
            else:
                self.screen.blit(easy_surf_w, easy_rect_w)

            if self.difficulty == 'medium' or medium_rect_w.collidepoint(mouse_pos):
                self.screen.blit(medium_surf_y, medium_rect_y)
            else:
                self.screen.blit(medium_surf_w, medium_rect_w)

            if self.difficulty == 'hard' or hard_rect_w.collidepoint(mouse_pos):
                self.screen.blit(hard_surf_y, hard_rect_y)
            else:
                self.screen.blit(hard_surf_w, hard_rect_w)

            if self.character == 'knight_m' or knight_m_rect_w.collidepoint(mouse_pos):
                self.screen.blit(knight_m_surf_y, knight_m_rect_y)
                knight_m.selection_animate()
            else:
                self.screen.blit(knight_m_surf_w, knight_m_rect_w)
                knight_m.surf = knight_m.stat_image[0]

            if self.character == 'elf_m' or elf_m_rect_w.collidepoint(mouse_pos):
                self.screen.blit(elf_m_surf_y, elf_m_rect_y)
                elf_m.selection_animate()
            else:
                self.screen.blit(elf_m_surf_w, elf_m_rect_w)
                elf_m.surf = elf_m.stat_image[0]

            if self.character == 'wizard_m' or wizard_m_rect_w.collidepoint(mouse_pos):
                self.screen.blit(wizard_m_surf_y, wizard_m_rect_y)
                wizard_m.selection_animate()
            else:
                self.screen.blit(wizard_m_surf_w, wizard_m_rect_w)
                wizard_m.surf = wizard_m.stat_image[0]

            if self.character == 'dragon_m' or dragon_m_rect_w.collidepoint(mouse_pos):
                self.screen.blit(dragon_m_surf_y, dragon_m_rect_y)
                dragon_m.selection_animate()
            else:
                self.screen.blit(dragon_m_surf_w, dragon_m_rect_w)
                dragon_m.surf = dragon_m.stat_image[0]

            if self.character == 'knight_f' or knight_f_rect_w.collidepoint(mouse_pos):
                self.screen.blit(knight_f_surf_y, knight_f_rect_y)
                knight_f.selection_animate()
            else:
                self.screen.blit(knight_f_surf_w, knight_f_rect_w)
                knight_f.surf = knight_f.stat_image[0]

            if self.character == 'elf_f' or elf_f_rect_w.collidepoint(mouse_pos):
                self.screen.blit(elf_f_surf_y, elf_f_rect_y)
                elf_f.selection_animate()
            else:
                self.screen.blit(elf_f_surf_w, elf_f_rect_w)
                elf_f.surf = elf_f.stat_image[0]

            if self.character == 'wizard_f' or wizard_f_rect_w.collidepoint(mouse_pos):
                self.screen.blit(wizard_f_surf_y, wizard_f_rect_y)
                wizard_f.selection_animate()
            else:
                self.screen.blit(wizard_f_surf_w, wizard_f_rect_w)
                wizard_f.surf = wizard_f.stat_image[0]

            if self.character == 'dragon_f' or dragon_f_rect_w.collidepoint(mouse_pos):
                self.screen.blit(dragon_f_surf_y, dragon_f_rect_y)
                dragon_f.selection_animate()
            else:
                self.screen.blit(dragon_f_surf_w, dragon_f_rect_w)
                dragon_f.surf = dragon_f.stat_image[0]

            if self.character == 'pumpkin' or pumpkin_rect_w.collidepoint(mouse_pos):
                self.screen.blit(pumpkin_surf_y, pumpkin_rect_y)
                pumpkin.selection_animate()
            else:
                self.screen.blit(pumpkin_surf_w, pumpkin_rect_w)
                pumpkin.surf = pumpkin.stat_image[0]

            if self.character == 'doc' or doc_rect_w.collidepoint(mouse_pos):
                self.screen.blit(doc_surf_y, doc_rect_y)
                doc.selection_animate()
            else:
                self.screen.blit(doc_surf_w, doc_rect_w)
                doc.surf = doc.stat_image[0]

            if play_game_rect_w.collidepoint(mouse_pos):
                self.screen.blit(play_game_surf_y, play_game_rect_y)
            else:
                self.screen.blit(play_game_surf_w, play_game_rect_w)

            if back_rect_w.collidepoint(mouse_pos):
                self.screen.blit(back_surf_y, back_rect_y)
            else:
                self.screen.blit(back_surf_w, back_rect_w)

            if error:
                self.screen.blit(error_surf, error_rect)

            for entity in sprites:
                self.screen.blit(entity.surf, entity.rect)

            pygame.display.flip()
            self.clock.tick(self.fps)

    def show_options(self, entities):
        title_surf, title_rect = render_text(self.med_font, 'Options', x=screen_w//2, y=2*screen_h//5)
        plus_volume_surf_w, plus_volume_rect_w = render_text(self.sm_font, '+', x=3.1*screen_w//5, y=2.5*screen_h//5)
        plus_volume_surf_y, plus_volume_rect_y = render_text(self.sm_y_font, '+', x=3.1*screen_w//5,
                                                             y=2.5*screen_h//5, color=(255, 255, 0))
        minus_volume_surf_w, minus_volume_rect_w = render_text(self.sm_font, '-', x=3.2*screen_w//5,
                                                               y=2.5*screen_h//5)
        minus_volume_surf_y, minus_volume_rect_y = render_text(self.sm_y_font, '-', x=3.2*screen_w//5,
                                                               y=2.5*screen_h//5, color=(255, 255, 0))
        back_surf_w, back_rect_w = render_text(self.sm_font, 'Back', x=screen_w//2, y=3*screen_h//5)
        back_surf_y, back_rect_y = render_text(self.sm_y_font, 'Back', x=screen_w//2, y=3*screen_h//5,
                                               color=(255, 255, 0))

        while self.showing_options:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                if back_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.running:
                            self.pause_game()
                        else:
                            self.go_to_title()

                elif plus_volume_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        current_sound = sounds.fireball_sound.get_volume()
                        if current_sound > 0.85:
                            sounds.adjust_volume(1)
                        else:
                            sounds.adjust_volume(current_sound+0.1)

                elif minus_volume_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        current_sound = sounds.fireball_sound.get_volume()
                        if current_sound < 0.15:
                            sounds.adjust_volume(0)
                        else:
                            sounds.adjust_volume(current_sound-0.1)

            if entities is None:
                self.scrolling_background()
            else:
                self.screen.blit(entities[0], entities[1])
            self.screen.blit(title_surf, title_rect)

            if back_rect_w.collidepoint(mouse_pos):
                self.screen.blit(back_surf_y, back_rect_y)
            else:
                self.screen.blit(back_surf_w, back_rect_w)

            if plus_volume_rect_w.collidepoint(mouse_pos):
                self.screen.blit(plus_volume_surf_y, plus_volume_rect_y)
            else:
                self.screen.blit(plus_volume_surf_w, plus_volume_rect_w)

            if minus_volume_rect_w.collidepoint(mouse_pos):
                self.screen.blit(minus_volume_surf_y, minus_volume_rect_y)
            else:
                self.screen.blit(minus_volume_surf_w, minus_volume_rect_w)

            volume_surf, volume_rect = render_text(self.sm_font, 'Volume: {:<3.0f}'.format(100*round(sounds.fireball_sound.get_volume(), 1)),
                                                   x=screen_w//2, y=2.5*screen_h//5)
            self.screen.blit(volume_surf, volume_rect)

            pygame.display.flip()
            self.clock.tick(self.fps)

    def show_help(self, entities):

        controls_surf, controls_rect = render_text(self.med_font, 'Controls', x=screen_w//2, y=screen_h//5)
        jump_surf, jump_rect = render_text(self.sm_font, '<ENTER> - Jump', x=screen_w//2, y=1.25*screen_h//5)
        move_right_surf, move_right_rect = render_text(self.sm_font, '<RIGHT ARROW or D Key> - Move Right',
                                                       x=screen_w//2, y=1.5*screen_h//5)
        move_left_surf, move_left_rect = render_text(self.sm_font, '<LEFT ARROW or A Key> - Move Left',
                                                     x=screen_w//2, y=1.75 * screen_h//5)
        shoot_surf, shoot_rect = render_text(self.sm_font, '<MOUSE CLICK> - Shoot Fireball', x=screen_w//2,
                                             y=2*screen_h//5)

        tips_surf, tips_rect = render_text(self.med_font, 'Help', x=screen_w//2, y=2.5*screen_h//5)

        lives_surf, lives_rect = render_text(self.sm_font, 'Collect          to gain extra lives when hit by an enemy fireball!',
                                             x=screen_w//2, y=2.75*screen_h//5)
        jumps_surf, jumps_rect = render_text(self.sm_font, 'Collect          to gain extra jumps to use in the air!',
                                             x=screen_w//2, y=3*screen_h//5)
        fireballs_surf, fireballs_rect = render_text(self.sm_font, 'Collect          to gain fireballs to shoot at enemies!',
                                                     x=screen_w//2, y=3.25*screen_h//5)
        sprite_surfs = [controls_surf, jump_surf, move_right_surf, move_left_surf, shoot_surf, tips_surf, lives_surf, jumps_surf, fireballs_surf]
        sprite_rects = [controls_rect, jump_rect, move_right_rect, move_left_rect, shoot_rect, tips_rect, lives_rect, jumps_rect, fireballs_rect]

        marker_sprites = pygame.sprite.Group()
        lives_marker = Powerup(screen_w//2-160, 2.75*screen_h//5+10, 'lives')
        d_jump_marker = Powerup(screen_w//2-110, 3*screen_h//5+10, 'double_jump')
        fireball_marker = Powerup(screen_w//2-110, 3.25*screen_h//5+10, 'fireball')
        marker_sprites.add([lives_marker, d_jump_marker, fireball_marker])

        back_surf_w, back_rect_w = render_text(self.sm_font, 'Back', x=screen_w//2, y=4*screen_h//5)
        back_surf_y, back_rect_y = render_text(self.sm_y_font, 'Back', x=screen_w//2, y=4*screen_h//5,
                                               color=(255, 255, 0))

        while self.showing_help:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                if back_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.running:
                            self.pause_game()
                        else:
                            self.go_to_title()

            if entities is None:
                self.scrolling_background()
            else:
                self.screen.blit(entities[0], entities[1])

            for surf, rect in zip(sprite_surfs, sprite_rects):
                self.screen.blit(surf, rect)

            for entity in marker_sprites:
                self.screen.blit(entity.surf, entity.rect)

            if back_rect_w.collidepoint(mouse_pos):
                self.screen.blit(back_surf_y, back_rect_y)
            else:
                self.screen.blit(back_surf_w, back_rect_w)

            pygame.display.flip()
            self.clock.tick(self.fps)

    def show_leaderboard(self):
        title_surf, title_rect = render_text(self.med_font, 'Leaderboards', x=screen_w//2, y=screen_h//4)
        leaderboards = []
        text_y = screen_h//4+35
        i = 0
        for entry in self.leaderboard[:10]:
            i += 1
            text_y += 25
            text = '{}.  '.format(i)+' '.join(map(str, entry))
            leaderboards.append(render_text(self.sm_font, text, x=screen_w//2, y=text_y))
        play_game_surf_w, play_game_rect_w = render_text(self.sm_font, 'Play Game', x=screen_w//3,
                                                         y=leaderboards[-1][1].bottom+50)
        play_game_surf_y, play_game_rect_y = render_text(self.sm_y_font, 'Play Game', x=screen_w//3,
                                                         y=leaderboards[-1][1].bottom+50, color=(255, 255, 0))
        back_surf_w, back_rect_w = render_text(self.sm_font, 'Main Menu', x=2*screen_w//3,
                                               y=leaderboards[-1][1].bottom+50)
        back_surf_y, back_rect_y = render_text(self.sm_y_font, 'Main Menu', x=2*screen_w//3,
                                               y=leaderboards[-1][1].bottom+50, color=(255, 255, 0))

        while self.showing_leaderboard:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                if play_game_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_selection()

                if back_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_title()

            self.scrolling_background()
            self.screen.blit(title_surf, title_rect)

            if play_game_rect_w.collidepoint(mouse_pos):
                self.screen.blit(play_game_surf_y, play_game_rect_y)
            else:
                self.screen.blit(play_game_surf_w, play_game_rect_w)

            if back_rect_w.collidepoint(mouse_pos):
                self.screen.blit(back_surf_y, back_rect_y)
            else:
                self.screen.blit(back_surf_w, back_rect_w)

            for entity in leaderboards:
                self.screen.blit(entity[0], entity[1])

            pygame.display.flip()
            self.clock.tick(self.fps)

    def show_pause_screen(self):
        title_surf, title_rect = render_text(self.med_font, 'Paused', x=screen_w//2, y=2*screen_w//5)
        resume_surf_w, resume_rect_w = render_text(self.sm_font, 'Resume', x=screen_w//2, y=2.5*screen_w//5)
        resume_surf_y, resume_rect_y = render_text(self.sm_y_font, 'Resume', x=screen_w//2, y=2.5*screen_w//5,
                                                   color=(255, 255, 0))
        options_surf_w, options_rect_w = render_text(self.sm_font, 'Options', x=screen_w//2, y=3*screen_w//5)
        options_surf_y, options_rect_y = render_text(self.sm_y_font, 'Options', x=screen_w//2, y=3*screen_w//5,
                                                     color=(255, 255, 0))
        help_surf_w, help_rect_w = render_text(self.sm_font, 'Help', x=screen_w//2, y=3.5*screen_w//5)
        help_surf_y, help_rect_y = render_text(self.sm_y_font, 'Help', x=screen_w//2, y=3.5*screen_w//5,
                                               color=(255, 255, 0))
        menu_surf_w, menu_rect_w = render_text(self.sm_font, 'Main Menu', x=screen_w//2, y=4*screen_w//5)
        menu_surf_y, menu_rect_y = render_text(self.sm_y_font, 'Main Menu', x=screen_w//2, y=4*screen_w//5,
                                               color=(255, 255, 0))
        box_surf = self.screen.subsurface((0, 0, screen_w, screen_h)).copy()
        box_rect = box_surf.get_rect()

        while self.paused:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.go_to_game()

                if event.type == pygame.QUIT:
                    self.exit()

                if resume_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_game()

                if options_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_options()
                        self.show_options([box_surf, box_rect])

                if help_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_help()
                        self.show_help([box_surf, box_rect])

                if menu_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_title()

            self.screen.blit(box_surf, box_rect)
            self.screen.blit(title_surf, title_rect)

            if resume_rect_w.collidepoint(mouse_pos):
                self.screen.blit(resume_surf_y, resume_rect_y)
            else:
                self.screen.blit(resume_surf_w, resume_rect_w)

            if options_rect_w.collidepoint(mouse_pos):
                self.screen.blit(options_surf_y, options_rect_y)
            else:
                self.screen.blit(options_surf_w, options_rect_w)

            if help_rect_w.collidepoint(mouse_pos):
                self.screen.blit(help_surf_y, help_rect_y)
            else:
                self.screen.blit(help_surf_w, help_rect_w)

            if menu_rect_w.collidepoint(mouse_pos):
                self.screen.blit(menu_surf_y, menu_rect_y)
            else:
                self.screen.blit(menu_surf_w, menu_rect_w)

            pygame.display.flip()
            self.clock.tick(self.fps)

    def show_death_screen(self):
        title_surf, title_rect = render_text(self.med_font, 'You Died!', x=screen_w//2, y=screen_h//5)
        restart_surf_w, restart_rect_w = render_text(self.sm_font, 'Restart', x=screen_w//2, y=2*screen_h//5)
        restart_surf_y, restart_rect_y = render_text(self.sm_y_font, 'Restart', x=screen_w//2, y=2*screen_h//5,
                                                     color=(255, 255, 0))
        selection_surf_w, selection_rect_w = render_text(self.sm_font, 'Change Character/Difficulty', x=screen_w//2,
                                                         y=2.5*screen_h//5)
        selection_surf_y, selection_rect_y = render_text(self.sm_y_font, 'Change Character/Difficulty', x=screen_w//2,
                                                         y=2.5*screen_h//5, color=(255, 255, 0))
        menu_surf_w, menu_rect_w = render_text(self.sm_font, 'Main Menu', x=screen_w//2, y=3*screen_h//5)
        menu_surf_y, menu_rect_y = render_text(self.sm_y_font, 'Main Menu', x=screen_w//2, y=3*screen_h//5,
                                               color=(255, 255, 0))

        highscore = self.new_highscore()
        name = ''
        if highscore:
            highscore_surf, highscore_rect = render_text(self.sm_font, 'New Highscore: {}'.format(self.score),
                                                         x=screen_w//2, y=3.5*screen_h//5)
            enter_surf, enter_rect = render_text(self.sm_font, 'Press ENTER to save player name', x=screen_w//2,
                                                 y=4*screen_h//5)
        else:
            highscore_surf = None
            highscore_rect = None
            enter_surf = None
            enter_rect = None

        while self.showing_death:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == KEYDOWN and highscore:
                    if event.key == K_BACKSPACE:
                        name = name[:-1]
                    elif event.key == K_RETURN:
                        self.update_leaderboard(name)
                        self.go_to_leaderboard()
                    else:
                        name += event.unicode

                if event.type == pygame.QUIT:
                    self.exit()

                if restart_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_game()

                if selection_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_selection()

                if menu_rect_w.collidepoint(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.go_to_title()

            self.scrolling_background()
            self.screen.blit(title_surf, title_rect)

            if restart_rect_w.collidepoint(mouse_pos):
                self.screen.blit(restart_surf_y, restart_rect_y)
            else:
                self.screen.blit(restart_surf_w, restart_rect_w)

            if selection_rect_w.collidepoint(mouse_pos):
                self.screen.blit(selection_surf_y, selection_rect_y)
            else:
                self.screen.blit(selection_surf_w, selection_rect_w)

            if menu_rect_w.collidepoint(mouse_pos):
                self.screen.blit(menu_surf_y, menu_rect_y)
            else:
                self.screen.blit(menu_surf_w, menu_rect_w)

            if highscore_surf is not None:
                name_surf, name_rect = render_text(self.sm_font, 'Enter Your Name: {}'.format(name), x=screen_w//2,
                                                   y=3.75*screen_h//5)
                self.screen.blit(highscore_surf, highscore_rect)
                self.screen.blit(name_surf, name_rect)
                self.screen.blit(enter_surf, enter_rect)

            pygame.display.flip()
            self.clock.tick(self.fps)
        self.highscore = False

    def go_to_title(self):
        self.showing_title = True
        self.showing_selection = False
        self.showing_leaderboard = False
        self.showing_options = False
        self.showing_help = False
        self.running = False
        self.paused = False
        self.showing_death = False

    def go_to_selection(self):
        self.showing_selection = True
        self.showing_title = False
        self.showing_leaderboard = False
        self.running = False
        self.showing_death = False

    def go_to_leaderboard(self):
        self.showing_leaderboard = True
        self.showing_title = False
        self.showing_death = False

    def go_to_options(self):
        self.showing_options = True
        self.showing_title = False
        self.paused = False

    def go_to_help(self):
        self.showing_help = True
        self.showing_title = False
        self.paused = False

    def go_to_game(self):
        self.running = True
        self.showing_title = False
        self.showing_selection = False
        self.paused = False
        self.showing_death = False

    def pause_game(self):
        self.paused = True
        self.showing_help = False
        self.showing_options = False

    def go_to_death(self):
        self.showing_death = True
        self.running = False

    def exit(self):
        self.showing_death = False
        self.running = False
        self.showing_title = False
        self.showing_selection = False
        self.showing_leaderboard = False
        self.showing_help = False
        self.paused = False
        self.showing_options = False
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def new_highscore(self):
        self.leaderboard.append(['temp', self.score])
        self.leaderboard = sorted(self.leaderboard, reverse=True, key=lambda x: x[1])
        return ['temp', self.score] in self.leaderboard[:10]

    def update_leaderboard(self, name):
        self.leaderboard[self.leaderboard.index(['temp', self.score])][0] = name
        entry_text = [' '.join(map(str, entry)) for entry in self.leaderboard[:10]]
        open('leaderboard.txt', 'w').write('\n'.join(entry_text))

    def scrolling_background(self):
        self.background1.rect.top += 1
        self.background2.rect.top += 1
        self.background1.shift_background()
        self.background2.shift_background()
        self.screen.blit(self.background1.surf, self.background1.rect)
        self.screen.blit(self.background2.surf, self.background2.rect)


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y, name):
        super().__init__()
        self.name = name
        self.v_x = 5
        self.v_y = 8.5
        self.g = 6
        self.time = 0
        self.dt = 0.135
        self.on_platform = True
        self.is_jumping = False
        self.is_falling = False
        self.face_right = True
        self.is_stationary = True
        self.powerups = {'lives': 1, 'double_jump': 0, 'fireball': 0}
        self.projectile = None
        self.frame = 0

        if name == 'knight_m':
            self.run_right = frames.knight_m_run_right_img
            self.run_left = frames.knight_m_run_left_img
            self.jump_image = frames.knight_m_jump_img
            self.stat_image = frames.knight_m_stat_img
        elif name == 'elf_m':
            self.run_right = frames.elf_m_run_right_img
            self.run_left = frames.elf_m_run_left_img
            self.jump_image = frames.elf_m_jump_img
            self.stat_image = frames.elf_m_stat_img
        elif name == 'wizard_m':
            self.run_right = frames.wizard_m_run_right_img
            self.run_left = frames.wizard_m_run_left_img
            self.jump_image = frames.wizard_m_jump_img
            self.stat_image = frames.wizard_m_stat_img
        elif name == 'dragon_m':
            self.run_right = frames.dragon_m_run_right_img
            self.run_left = frames.dragon_m_run_left_img
            self.jump_image = frames.dragon_m_jump_img
            self.stat_image = frames.dragon_m_stat_img
        elif name == 'knight_f':
            self.run_right = frames.knight_f_run_right_img
            self.run_left = frames.knight_f_run_left_img
            self.jump_image = frames.knight_f_jump_img
            self.stat_image = frames.knight_f_stat_img
        elif name == 'elf_f':
            self.run_right = frames.elf_f_run_right_img
            self.run_left = frames.elf_f_run_left_img
            self.jump_image = frames.elf_f_jump_img
            self.stat_image = frames.elf_f_stat_img
        elif name == 'wizard_f':
            self.run_right = frames.wizard_f_run_right_img
            self.run_left = frames.wizard_f_run_left_img
            self.jump_image = frames.wizard_f_jump_img
            self.stat_image = frames.wizard_f_stat_img
        elif name == 'dragon_f':
            self.run_right = frames.dragon_f_run_right_img
            self.run_left = frames.dragon_f_run_left_img
            self.jump_image = frames.dragon_f_jump_img
            self.stat_image = frames.dragon_f_stat_img
        elif name == 'pumpkin':
            self.run_right = frames.pumpkin_run_right_img
            self.run_left = frames.pumpkin_run_left_img
            self.jump_image = frames.pumpkin_jump_img
            self.stat_image = frames.pumpkin_stat_img
        elif name == 'doc':
            self.run_right = frames.doc_run_right_img
            self.run_left = frames.doc_run_left_img
            self.jump_image = frames.doc_jump_img
            self.stat_image = frames.doc_stat_img
        self.surf = self.stat_image[0]
        self.w, self.h = self.surf.get_size()
        self.rect = self.surf.get_rect()
        self.rect.center = (round(x), 0)
        self.rect.bottom = round(y)

    def move(self, pressed_keys, dynamic_sprites):
        if pressed_keys[K_LEFT] or pressed_keys[K_a]:
            self.rect.move_ip((-self.v_x, 0))
            self.face_right = False
            self.frame += 1
            self.is_stationary = False
            if self.rect.center[0] < 0:
                self.rect.right = screen_w+self.w//2
        elif pressed_keys[K_RIGHT] or pressed_keys[K_d]:
            self.rect.move_ip((self.v_x, 0))
            self.face_right = True
            self.frame += 1
            self.is_stationary = False
            if self.rect.center[0] > screen_w:
                self.rect.left = -self.w//2
        else:
            self.frame = 0
            self.is_stationary = True

        dy = 0
        if self.is_jumping:
            self.time += self.dt
            dy = round(self.v_y*self.time-0.5*self.g*self.time ** 2)
        elif self.is_falling:
            self.time += self.dt
            dy = round(-0.5*self.g*self.time ** 2)
        if dy < -1.6*self.v_y:
            dy = -14
        if dy != 0:
            for sprite in dynamic_sprites:
                sprite.rect.move_ip((0, dy))

    def touches(self, enemy):
        return self.rect.colliderect(enemy.rect)

    def falls_below(self, platform):
        if self.rect.top > platform.rect.bottom:
            self.rect.move_ip((0, 5))
            if self.rect.top >= screen_h:
                return True
        return False

    def lands_on(self, platform, last_top_pos, dynamic_sprites):
        if not self.on_platform and (self.rect.left <= platform.rect.right) and (self.rect.right >= platform.rect.left):
            if platform.rect.top <= self.rect.bottom <= last_top_pos:
                dy = round(platform.rect.top-self.rect.bottom)
                for sprite in dynamic_sprites:
                    sprite.rect.move_ip((0, -dy))
                self.on_platform = True
                self.is_jumping = False
                self.is_falling = False
                self.time = 0
                return True
        return False

    def falls_off(self, platform):
        if (self.rect.left > platform.rect.right) or (self.rect.right < platform.rect.left):
            if self.rect.bottom == platform.rect.top:
                self.on_platform = False
                self.is_falling = True
                return True
        return False

    def consumes(self, powerup):
        self.powerups[powerup.name] += 1

    def animate(self):
        if self.face_right:
            if self.is_jumping or self.is_falling:
                self.surf = self.jump_image[0]
            elif self.is_stationary:
                self.surf = self.stat_image[0]
            else:
                self.surf = self.run_right[self.frame//5 % 4]
        else:
            if self.is_jumping or self.is_falling:
                self.surf = self.jump_image[1]
            elif self.is_stationary:
                self.surf = self.stat_image[1]
            else:
                self.surf = self.run_left[self.frame//5 % 4]

    def selection_animate(self):
        self.surf = self.run_right[self.frame//5 % 4]
        self.frame += 1

    def create_projectile(self, pos, dynamic_sprites):
        v = pygame.math.Vector2()
        v.xy = (pos[0]-self.rect.center[0]) / 40, (pos[1]-self.rect.center[1]) / 40
        norm = v.length()
        if norm < 6:
            v = v*6 / norm
        self.projectile = Projectile(self.rect.center, round(v[0]), round(v[1]))
        dynamic_sprites.add(self.projectile)
        pygame.mixer.Sound.play(sounds.fireball_sound)

    def remove_projectile(self):
        self.projectile.kill()
        self.projectile = None


class Platform(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.lastYPos = 0
        self.enemy = None
        self.powerup = None
        self.projectile = None
        self.surf = frames.platform_img
        self.w, self.h = self.surf.get_size()
        self.rect = self.surf.get_rect()
        self.rect.center = self.create_platform(pos)

    def create_platform(self, pos):
        xi = pos[0]
        yi = pos[1]
        v_x = 5
        v_y = 8.5
        y_max = v_y ** 2  # 12*(v_y**2)/(2*G)
        x_max = 4*v_x*v_y  # 24*v_x*v_y/G

        x = xi+rnd.uniform(-x_max, x_max)
        y = yi-rnd.uniform(0.8*y_max, y_max)

        if x <= self.w:
            x = xi+rnd.uniform(0.5*x_max, x_max)
        elif x >= screen_w-self.w:
            x = xi-rnd.uniform(0.5*x_max, x_max)
        if (x-xi < 0.5*x_max) and (x-xi > 0):
            x = xi+rnd.uniform(0.5*x_max, x_max)
        if (x-xi > -0.5*x_max) and (x-xi < 0):
            x = xi-rnd.uniform(0.5*x_max, x_max)
        if x < self.w//2:
            x = self.w//2
        if x > screen_w-self.w//2:
            x = screen_w-self.w//2
        return round(x), round(y)

    def create_enemy(self, dynamic_sprites, speed):
        self.enemy = Enemy(self.rect.center[0], self.rect.top, speed)
        dynamic_sprites.add(self.enemy)

    def create_powerup(self, dynamic_sprites):
        num = rnd.randint(0, 6)
        if num == 0:
            self.powerup = Powerup(self.rect.center[0], self.rect.top, 'lives')
        elif num in [1, 2, 3]:
            self.powerup = Powerup(self.rect.center[0], self.rect.top, 'double_jump')
        elif num in [4, 5, 6]:
            self.powerup = Powerup(self.rect.center[0], self.rect.top, 'fireball')
        dynamic_sprites.add(self.powerup)

    def create_projectile(self, v_y, dynamic_sprites):
        self.projectile = Projectile(self.enemy.rect.center, 0, v_y)
        dynamic_sprites.add(self.projectile)
        pygame.mixer.Sound.play(sounds.fireball_sound)

    def remove_platform(self, platforms):
        platforms.pop(0)
        if self.enemy is not None:
            self.remove_enemy()
        if self.projectile is not None:
            self.remove_projectile()
        if self.powerup is not None:
            self.remove_powerup()
        self.kill()

    def remove_enemy(self):
        self.enemy.kill()
        self.enemy = None

    def remove_powerup(self):
        self.powerup.kill()
        self.powerup = None

    def remove_projectile(self):
        self.projectile.kill()
        self.projectile = None


class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y, v_x):
        super().__init__()
        self.v_x = v_x
        self.face_right = rnd.randint(0, 1)
        self.frame = 0
        self.run_right = frames.demon_run_right_img
        self.run_left = frames.demon_run_left_img
        if self.face_right:
            self.surf = self.run_right[0]
        else:
            self.surf = self.run_left[0]
        self.rect = self.surf.get_rect()
        self.rect.center = (x, 0)
        self.rect.bottom = y

    def move(self):
        if self.face_right:
            self.rect.move_ip((self.v_x, 0))
            self.frame += 1
            self.surf = self.run_right[self.frame//4 % 4]
            if self.rect.right > screen_w:
                self.face_right = False
        else:
            self.rect.move_ip((-self.v_x, 0))
            self.frame += 1
            self.surf = self.run_left[self.frame//4 % 4]
            if self.rect.left < 0:
                self.face_right = True


class Projectile(pygame.sprite.Sprite):

    def __init__(self, pos, v_x, v_y):
        super().__init__()
        self.v_x = v_x
        self.v_y = v_y
        self.surf = frames.fire_img
        self.rect = self.surf.get_rect()
        self.rect.center = (pos[0], pos[1])
        self.new_projectile = True

    def move(self):
        self.rect.move_ip((self.v_x, self.v_y))

    def hits(self, obj):
        if self.rect.colliderect(obj.rect):
            pygame.mixer.Sound.play(sounds.explosion_sound)
            return True
        return False

    def hits_boundary(self):
        if self.new_projectile and self.rect.bottom <= 0:
            return False
        else:
            self.new_projectile = False
        if self.rect.left >= screen_w or self.rect.right <= 0:
            return True
        if self.rect.top >= screen_h or self.rect.bottom <= 0:
            return True
        return False


class Powerup(pygame.sprite.Sprite):

    def __init__(self, x, y, name):
        super().__init__()
        self.name = name
        if self.name == 'lives':
            self.surf = frames.heart_img
        if self.name == 'double_jump':
            self.surf = frames.blue_flask_img
        if self.name == 'fireball':
            self.surf = frames.red_flask_img
        self.rect = self.surf.get_rect()
        self.rect.center = (round(x), 0)
        self.rect.bottom = round(y)


class Origin(pygame.sprite.Sprite):

    def __init__(self, pos):
        super().__init__()
        self.surf = pygame.Surface((1, 1))
        self.rect = self.surf.get_rect()
        self.rect.center = (pos[0], pos[1])


class Background(pygame.sprite.Sprite):

    def __init__(self, y):
        super().__init__()
        self.surf = frames.background_img
        self.rect = self.surf.get_rect()
        self.w, self.h = self.surf.get_size()
        self.rect.left = 0
        self.rect.top = y

    def shift_background(self):
        if self.rect.top > screen_h:
            self.rect.bottom = self.rect.top-self.h
        if self.rect.bottom < 0:
            self.rect.top = self.rect.bottom+self.h
            

def get_leaderboard():
    entries = []
    for entry in open('leaderboard.txt', 'r').readlines():
        name, score = entry.split()
        entries.append([name, int(score)])
    return entries


def render_text(font, text, **args):
    x = args.get('x', None)
    y = args.get('y', None)
    left = args.get('left', None)
    right = args.get('right', None)
    top = args.get('top', None)
    bottom = args.get('bottom', None)
    color = args.get('color', (255, 255, 255))

    _surf = font.render(text, True, color)
    _rect = _surf.get_rect()
    if x is not None:
        _rect.center = (round(x), round(y))
    else:
        if left is not None:
            _rect.left = round(left)
        else:
            _rect.right = round(right)
        if top is not None:
            _rect.top = round(top)
        else:
            _rect.bottom = round(bottom)
    return _surf, _rect


if __name__ == '__main__':
    main()
