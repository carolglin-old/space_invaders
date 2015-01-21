import pygame as pg
import time
import pdb
import random
import math

'''
Global constants
'''

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 550

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)



class CanvasObjects:
	def __init__(self):
		pg.mixer.init()
		self.channel_background_music = pg.mixer.Channel(0)
		self.channel_game_sound = pg.mixer.Channel(1)

	def play(self, type, music_file, volume = 0.8):
		sound = pg.mixer.Sound(music_file)
		if type == "game_sound":
			self.channel_game_sound.play(sound)
		elif type == "background_music":
			self.channel_background_music.play(sound, loops = 1)

	def stop_music(self):
		pg.mixer.music.stop()

	def open_resize_img(self, img_source, width, height):
		graphic = pg.image.load(img_source).convert_alpha()
		graphic = pg.transform.scale(graphic, (width, height))
		graphic.set_colorkey(BLACK)
		return graphic

	def blit_alpha(self, target, source, location, opacity):
		x = location[0]
		y = location[1]
		temp = pg.Surface((source.get_width(), source.get_height())).convert()
		temp.blit(target, (-x, -y))
		temp.blit(source, (0, 0))
		temp.set_alpha(opacity)
		target.blit(temp, location)

class GameObjects(CanvasObjects, pg.sprite.Sprite):
	def __init__(self, width, height, x, y, img_source):
		CanvasObjects.__init__(self)
		pg.sprite.Sprite.__init__(self)

		self.width = width
		self.height = height
		self.x = x
		self.y = y

		self.state = "full_health"
		self.flash = False

		self.image_file = img_source
		self.image = self.open_resize_img(self.image_file, self.width, self.height)
		self.rect = self.image.get_rect()

		self.create = EventHook()
		self.remove = EventHook()

		self.move_rect()

	def move_rect(self):
		self.rect.move(self.x, self.y)
		self.rect.topleft = (self.x, self.y)
		self.rect.bottomright = (self.x + self.width, self.y + self.height)

	def wait_time(self, fire_time, wait_time):
		if time.clock() > fire_time + wait_time:
			return True

	def create_laser(self, x, y, dx, dy, origin, graphic):
		l = Laser(x, y, dx, dy, origin, graphic)
		self.create.fire(l)

	def death_animation(self):
		death_strip = Animation(self.x, self.y, self.death_sprite_width, self.death_sprite_height, self.death_sprite_source, self.death_num_sprites)
		self.create.fire(death_strip)

class LevelManager(CanvasObjects):
	def __init__(self):
		CanvasObjects.__init__(self)

		self.levels = Levels()
		self.current = 0
		self.total_levels = 3

		self.level_one_music = "/Users/carollin/Dev/space_invaders/sounds/level_one.ogg"
		self.level_two_music = "/Users/carollin/Dev/space_invaders/sounds/level_two.ogg"
		self.level_three_music = "/Users/carollin/Dev/space_invaders/sounds/boss.ogg"

		self.a = AlienTypes()

		self.create = EventHook()

	def win_screen(self):
		self.init_level(3)

	def play_level_music(self):
		if self.current == 0:
			self.play("background_music", self.level_one_music)
		if self.current == 1:
			self.play("background_music", self.level_two_music)
		if self.current == 2:
			self.play("background_music", self.level_three_music)

	def init_level(self, current_level):
		self.play_level_music()
		self.load_level(self.levels.data[self.current])

	def load_level(self, current_level):
		for i in current_level:
			if i["type"] == Alien:
				self.alien_info_list = []
				self.load_block(i, self.alien_info_list)
			if i["type"] == Barrier:
				self.barrier_info_list = []
				self.load_block(i, self.barrier_info_list)

	def load_block(self, raw, info_list):
		# take raw layout data into a list of dictionaries for each item
		self.add_rows_columns(info_list, raw["rows"], raw["columns"], raw["xcorner"], raw["ycorner"], raw["xspacing"], raw["yspacing"])
		if raw["type"] == Alien:
			self.combine_movement(raw)
			self.add_alien_info(raw)

		self.create_block(raw["type"], info_list)

	def combine_movement(self, raw):
		for i in self.alien_info_list:
			i['movement_list'] = self.movement_pattern(raw["movement"])

	def add_rows_columns(self, info_list, rows, columns, xcorner, ycorner, xspacing, yspacing):
		index = 1
		while index <= rows:
			y_val = (index - 1) * yspacing + ycorner
			for i in range(columns):
				x_val = i * xspacing + xcorner
				# creates a list of individual dictionaries for each block
				new_dict = {'x': x_val, 'y': y_val}
				info_list.append(new_dict)
			index += 1

	def movement_pattern(self, raw_movement_data):
		# add alien movement pattern to each dictionary
		movement_list = []
		for i in raw_movement_data:
			j = 0
			while j < i[1]:
				movement_list.append(i[0])
				j += 1
		return movement_list

	def add_alien_info(self, raw):
		# adding additional alien information to the dictionary depending on what type it is
		for i in self.alien_info_list:
			if raw["id"] == "one":
				i.update(self.a.one)
			if raw["id"] == "two":
				i.update(self.a.two)
			if raw["id"] == "three":
				i.update(self.a.three)
			if raw["id"] == "four":
				i.update(self.a.four)
			if raw["id"] == "five":
				i.update(self.a.five)

	def create_block(self, object_type, info_list):
		if object_type is Alien:
			for dictionary in info_list:
				a = Alien(**dictionary)
				self.create.fire(a)

		if object_type is Barrier:
			for dictionary in info_list:
				b = Barrier(**dictionary)
				self.create.fire(b)

class Menu:
	def __init__(self, text, font_size, pos, screen, font = None):
		self.hovered = False
		self.text = text
		self.pos = pos
		self.font = pg.font.Font(font, font_size)
		self.screen = screen
		self.set_rect()
		self.draw()

	def draw(self):
		self.set_rend()
		self.screen.blit(self.rend, self.rect)

	def set_rend(self):
		self.rend = self.font.render(self.text, True, self.get_color())

	def get_color(self):
		if self.hovered:
			return WHITE
		else:
			return GRAY

	def set_rect(self):
		self.set_rend()
		self.rect = self.rend.get_rect()
		self.rect.topleft = self.pos

class ScreenText:
	def __init__(self, text, pos, screen, font = None, font_size = 20, font_color = WHITE):
		self.text = text
		self.pos = pos
		self.font = pg.font.Font(font, font_size)
		self.font_color = font_color
		self.screen = screen
		self.set_rect()
		self.draw()

	def draw(self):
		self.set_rend()
		self.screen.blit(self.rend, self.rect)

	def set_rend(self):
		self.rend = self.font.render(self.text, True, self.font_color)

	def set_rect(self):
		self.set_rend()
		self.rect = self.rend.get_rect()
		self.rect.topleft = self.pos

class Game(CanvasObjects, pg.sprite.Sprite):
	def __init__(self):
		CanvasObjects.__init__(self)
		pg.sprite.Sprite.__init__(self)

		pg.init()

		self.isStopped = True
		self.prestart = True

		self.lives = 3
		self.score = 0

		self.clock = pg.time.Clock()
		self.sleepTime = 100

		self.alien_group = pg.sprite.Group()	
		self.barrier_group = pg.sprite.Group()
		self.dude_group = pg.sprite.GroupSingle()
		# self.alien_laser_group = pg.sprite.Group()
		# self.dude_laser_group = pg.sprite.Group()
		self.update_list = pg.sprite.Group()

		self.start_message = "CLICK TO START"
		# self.next_level_message = "READY FOR NEXT LEVEL? CLICK!"
		self.game_over_message = "RUH ROH, GAME OVER. RESTART?"
		self.win_message = "YOU DID IT. EARTH IS SAVED...FOR NOW."

		self.selection_sound = '/Users/carollin/Dev/space_invaders/sounds/start.ogg'
		self.win_sound = "/Users/carollin/Dev/space_invaders/sounds/win.ogg"

		self.level_manager = LevelManager()
		self.level_manager.create += self.add_to_list

		self.total_aliens = 0
		self.power_up_count = 0

		self.keys = pg.key.get_pressed()
		self.last_keys_pressed = self.keys

		self.load_screen()

	def load_screen(self):
		self.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
		self.screen = pg.display.set_mode(self.size)
		self.caption = '<(^.^<) Space Invaders! (>O.O)>'

		pg.display.set_caption(self.caption)

		self.bg_file = '/Users/carollin/Dev/space_invaders/graphics/background.png'

		self.background = self.open_resize_img(self.bg_file, SCREEN_WIDTH, SCREEN_HEIGHT)
		self.screen.blit(self.background, [0, 0])
		pg.display.update()

		self.create_dude()

		self.screen_text_list = []

		self.load_score()
		self.load_lives_left()
		self.load_menu(self.start_message, 30, (300, 250), self.screen)

	def load_menu(self, text, font_size, pos, screen):
		self.buttons = [Menu(text, font_size, pos, screen)]

		# changing color while hovering over menu
		while self.prestart is True:
			pg.event.pump()
			for button in self.buttons:
				if button.rect.collidepoint(pg.mouse.get_pos()):
					button.hovered = True
				else:
					button.hovered = False
				button.draw()

			self.check_mouse_click(text)
			pg.display.update()

	def load_score(self):
		self.screen_score = ScreenText("SCORE = " + str(self.score), (5, 5), self.screen)

	def load_lives_left(self):
		self.screen_lives = ScreenText("LIVES LEFT = " + str(self.lives), (690, 5), self.screen)

	def check_mouse_click(self, text):
		for event in pg.event.get():
			if event.type == pg.MOUSEBUTTONDOWN:
				current_pos = pg.mouse.get_pos()
				if self.buttons[0].rect.collidepoint(current_pos):
					self.play("game_sound", self.selection_sound)
					pg.display.update()
					self.prestart = False
					self.clear_screen()
					self.check_message(text)

	def check_message(self, text):
		if text == self.start_message:
			self.start()
		if text == self.game_over_message:
			self.game_over()
		# if text == self.win_message:
		# 	self.level_manager.win_screen()

	def start(self):
		self.isStopped = False
		self.win()
		self.mainloop()

	def create_dude(self):
		self.dude = Dude(self.screen)
		self.add_to_list(self.dude)

	def add_to_list(self, obj):
		self.update_list.add(obj)
		obj.remove += self.remove_object
		if hasattr(obj, "create"):
			obj.create += self.add_to_list
		if type(obj) is Dude:
			self.dude_group.add(obj)
		if type(obj) is Alien:
			self.total_aliens += 1
			self.alien_group.add(obj)
			obj.game_over += self.game_over
		if type(obj) is Barrier:
			self.barrier_group.add(obj)
		# if type(obj) is Laser:
		# 	if obj.origin == "dude":
		# 		self.dude_laser_group.add(obj)
		# 	if obj.origin == "alien":
		# 		self.alien_laser_group.add(obj)

	def remove_object(self, obj):
		obj.kill()

		if type(obj) is Dude:
			self.check_lives()
		if type(obj) is Alien:
			self.check_aliens()
			self.add_points(obj)

	def next_level(self):
		self.level_manager.current += 1
		if self.level_manager.current == self.level_manager.total_levels:
			self.win()			
		else:
			self.clear_groups()
			self.start()

	def win(self):
		self.play("background_music", self.win_sound)
		self.dude.invincible == True
		self.level_manager.win_screen()

	def win_text(self):
		self.win_screen_text = ScreenText(self.win_text, (300, 50), self.screen, font_size = 25)

	def clear_screen(self):
		self.screen.blit(self.background, [0, 0])
		self.load_score()
		self.load_lives_left()

	def clear_groups(self):
		self.alien_group.empty()
		self.barrier_group.empty()
		self.update_list.empty()
		self.update_list.add(self.dude)

	def clear_score_lives(self):
		self.score = 0
		self.lives = 3

	def create_game_over_screen(self):
		self.allow_animations()
		self.prestart = True
		self.load_menu(self.game_over_message, 30, (250, 250), self.screen)

	def allow_animations(self):
		for obj in self.update_list:
			if type(obj) is Animation:
				frames_left = obj.num_sprites - obj.current_sprite
				i = 0
				while i < frames_left:
					self.update_model()
					self.refresh_view()
					i += 1

	def game_over(self):
		self.create_dude()
		self.level_manager.current = 0
		self.clear_groups()
		self.clear_score_lives()
		self.clear_screen()
		self.total_aliens = 0
		self.start()

	def check_lives(self):
		self.lives -= 1
		if self.lives == 0:
			self.create_game_over_screen()
		else:
			self.create_dude()

	def add_points(self, obj):
		self.score += obj.total_points
		self.clear_screen()

	def check_aliens(self):
		self.total_aliens -= 1
		if self.total_aliens == 0:
			self.allow_animations()
			self.next_level()

	def key_events(self):
		for event in pg.event.get():
			self.last_keys_pressed = self.keys
			self.keys = pg.key.get_pressed()
			if self.keys[pg.K_LEFT]:
				self.dude.left()
			if self.keys[pg.K_RIGHT]:
				self.dude.right()
			if self.keys[pg.K_SPACE]:
				self.dude.shoot()
			if self.keyrelease_listener(pg.K_LEFT) is True:
				self.dude.reset_movement()
			if self.keyrelease_listener(pg.K_RIGHT) is True:
				self.dude.reset_movement()
			if self.keyrelease_listener(pg.K_SPACE) is True:
				self.dude.shooting = False
			if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
				self.isStopped = True

	def keyrelease_listener(self, key_code):
		if self.last_keys_pressed[key_code] and not self.keys[key_code]:
			return True
		return False

	def randomize_power_up(self, randomrange):
		if random.randrange(randomrange) == 1:
			self.power_up = PowerUp()
			self.power_up_count = 1
			self.add_to_list(self.power_up)

	def mainloop(self):
		while self.isStopped is False:

			self.special_objects()
			self.key_events()
			self.update_model()
			self.refresh_view()

			self.clock.tick(self.sleepTime)

	def special_objects(self):
		if self.level_manager.current == 1:
			if self.power_up_count == 0:
				self.randomize_power_up(100)
		if self.level_manager.current == 2:
			if self.power_up_count < 2:
				self.randomize_power_up(300)

	def update_model(self): 
		for obj in self.update_list:
			if type(obj) is Laser:
				obj.update(self.alien_group, self.barrier_group, self.dude_group)
			elif type(obj) is PowerUp:
				obj.update(self.dude_group)
			else:
				obj.update()

	def refresh_view(self):
		self.screen.blit(self.background, (0,0))
		# self.update_list.clear(self.screen, self.background)
		for sprite in self.update_list:
			if sprite.state == "full_health":
				self.screen.blit(sprite.image, (sprite.x, sprite.y))
			elif sprite.state == "damaged" or "invincible":
				self.blit_alpha(self.screen, sprite.image, (sprite.x, sprite.y), sprite.alpha)
				
		self.load_score()
		self.load_lives_left()

		if self.level_manager.current == 3:
			self.win_text()

		pg.display.update()

class PowerUp(GameObjects, pg.sprite.Sprite):
	def __init__(self):
		GameObjects.__init__(self, 40, 40, random.randrange(SCREEN_WIDTH), 0, '/Users/carollin/Dev/space_invaders/graphics/speed_powerup.png')
		pg.sprite.Sprite.__init__(self)

		self.dx = 0
		self.dy = 2

		self.death_sprite_width = 320
		self.death_sprite_height = 32
		self.death_sprite_source = '/Users/carollin/Dev/space_invaders/graphics/powerup_splash.png'
		self.death_num_sprites = 10

	def movement(self):
		self.x += self.dx
		self.y += self.dy

	# def change_direction(self):
	# 	self.dx = self.dx * -1
	# 	self.dy = self.dy * -1

	# def check_borders(self):
	# 	if self.x < 0: 
	# 		self. dx = self.dx * -1
	# 	if self.x > (SCREEN_WIDTH - self.width):
	# 		self.dx = self.dx * -1
	# 	if self.y < 0:
	# 		self.dy = self.dy * -1
	# 	if self.dy > (SCREEN_HEIGHT - self.height):
	# 		self.dy = self.dy * -1

	def check_collision(self, dude_group):
		dude_hit = pg.sprite.spritecollide(self, dude_group, False)

		if len(dude_hit) != 0:
			self.remove.fire(self)
			self.death_animation()
			dude_hit[0].speed_up()
			dude_hit[0].shot_wait = 0.25

	def update(self, dude_group):
		# self.check_borders()
		self.check_collision(dude_group)
		self.movement()
		self.move_rect()

class Dude(GameObjects, pg.sprite.Sprite):
	def __init__(self, screen):
		GameObjects.__init__(self, 30, 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 35, '/Users/carollin/Dev/space_invaders/graphics/dude.png')
		pg.sprite.Sprite.__init__(self)

		self.dx = 0
		self.dy = 0

		self.screen = screen

		self.movement_speed = 5

		self.laser_graphic = '/Users/carollin/Dev/space_invaders/graphics/redlaser.png'
		self.laser_dx = 0
		self.laser_dy = -6
		self.laser_sound = '/Users/carollin/Dev/space_invaders/sounds/dudelaser.ogg'
		self.laser_strength = 10

		self.death_sprite_source = '/Users/carollin/Dev/space_invaders/graphics/dudeexplosion.png'
		self.death_num_sprites = 20
		self.death_sprite_width = 512
		self.death_sprite_height = 64

		self.shooting = False
		self.time_fired = 0
		self.shot_wait = 0.45

		self.flash_iter = 1
		self.alpha = 50

		self.spawn_time = time.clock()

	def speed_up(self):
		self.movement_speed = 10

	def left(self):
		self.dx = self.movement_speed * -1

	def right(self):
		self.dx = self.movement_speed

	def reset_movement(self):
		self.dx = 0

	def movement(self):
		self.infinite_sides()
		self.x += self.dx
		self.y += self.dy

	def infinite_sides(self):
		if self.x > SCREEN_WIDTH:
			self.x = 5
		if self.x < 0:
			self.x = SCREEN_WIDTH - 5

	def shoot(self):
		self.shooting = True
		if self.wait_time(self.time_fired, self.shot_wait) is True:
			# self.play(self.laser_sound)
			mid_x = self.x + (self.width / 2)
			self.create_laser(mid_x, self.y, self.laser_dx, self.laser_dy, "dude", self.laser_graphic)
			self.time_fired = time.clock()

	def stop_shooting(self):
		self.shooting = False

	def hit(self):
		if self.invincible() is False:
			self.death_animation()
			self.remove.fire(self)

	def invincible(self):
		if (time.clock() - self.spawn_time) <= 3:
			return True
		else:
			return False

	def check_flash(self):
		if self.invincible() == True:
			if self.flash_iter % 5 == 0:
				self.state = "invincible"
			else:
				self.state = "full_health"
			self.flash_iter += 1
		else:
			self.state = "full_health"

	def update(self):
		self.movement()
		self.move_rect()
		self.check_flash()
		if self.shooting is True:
			self.shoot()

class Alien(GameObjects, pg.sprite.Sprite):
	def __init__(self, **kwargs):
		GameObjects.__init__(self, kwargs['width'], kwargs['height'], kwargs['x'], kwargs['y'], kwargs['graphic'])
		pg.sprite.Sprite.__init__(self)

		self.dx = 0
		self.dy = 0
		self.horizontal_jump = kwargs['h_move']
		self.vertical_jump = kwargs['v_move']

		self.laser_dx = kwargs['laser_dx']
		self.laser_dy = kwargs['laser_dy']
		self.laser_graphic = kwargs['laser_graphic']
		self.laser_sound = kwargs['laser_sound']

		self.move_wait = kwargs['move_wait']
		self.shot_wait = kwargs['shot_wait']
		self.time_moved = 0

		self.hit_points_left = kwargs['hit_points']
		self.total_points = kwargs['hit_points']

		self.movement_list = kwargs['movement_list']
		self.alpha = 255
		self.alpha_decrease_amount = self.set_alpha_decreases()

		self.death_sprite_source = kwargs['death_sprite']
		self.death_sprite_width = kwargs['death_sprite_width']
		self.death_sprite_height = kwargs['death_sprite_height']
		self.death_num_sprites = kwargs['death_num_sprites']

		self.index = 0
		self.move_indicies = int(kwargs['move_wait'])

		self.game_over = EventHook()

	def left(self):
		self.dx = self.horizontal_jump * -1
		self.dy = 0

	def right(self):
		self.dx = self.horizontal_jump
		self.dy = 0

	def up(self):
		self.dx = 0
		self.dy = self.vertical_jump * -1

	def down(self):
		self.dx = 0
		self.dy = self.vertical_jump

	def determine_move(self):
			direction = self.movement_list[0]
			if direction == "left":
				self.left()
			elif direction == "right":
				self.right()
			elif direction == "up":
				self.up()
			elif direction == "down": 
				self.down()

	def movement(self):
		if len(self.movement_list) > 0:
			self.index += 1
			
			if self.index == self.move_indicies:
				self.determine_move()

				self.x += self.dx
				self.y += self.dy

				self.shift_moves()
				self.index = 0
		else:
			pass

	def shift_moves(self):
		self.movement_list.append(self.movement_list[0])
		self.movement_list.pop(0)

	def attempt_shot(self):
		if self.randomize() == "go":
			self.play("game_sound", self.laser_sound)
			mid_x = self.x + (self.width / 2)
			self.create_laser(mid_x, self.y, self.laser_dx, self.laser_dy, "alien", self.laser_graphic)

	def randomize(self):
		if random.randrange(self.shot_wait) == 1:
			return "go"

	def hit(self):
		self.hit_points_left -= 5
		if self.hit_points_left > 0:
			self.alpha -= self.alpha_decrease_amount
			self.state = "damaged" 
		if self.hit_points_left == 0:
			self.death_animation()
			self.remove.fire(self)

	def set_alpha_decreases(self):
		num_alpha_decreases = self.total_points / 5
		alpha_decrease_amount = 255 / num_alpha_decreases
		return int(alpha_decrease_amount)

	def check_touchdown(self):
		if self.y > 530:
			self.game_over.fire()

	def update(self):
		self.attempt_shot()
		self.check_touchdown()
		self.movement()
		self.move_rect()

class Laser(GameObjects, pg.sprite.Sprite):
	def __init__(self, x, y, dx, dy, origin, graphic = '/Users/carollin/Dev/space_invaders/graphics/greenlaser.png'):
		GameObjects.__init__(self, 5, 15, x, y, graphic)
		pg.sprite.Sprite.__init__(self)

		self.dx = dx
		self.dy = dy

		self.origin = origin

	def movement(self):
		self.x += self.dx
		self.y += self.dy

	def check_if_active(self):
		if self.y > SCREEN_HEIGHT or self.y < 0:
			self.remove.fire(self)

	def check_objects(self, alien_group, barrier_group, dude_group):
		if self.origin == "dude":
			alien_hit = pg.sprite.spritecollide(self, alien_group, False)
			barrier_hit = pg.sprite.spritecollide(self, barrier_group, False)

			if len(alien_hit) != 0:
				alien_hit[0].hit()
				self.remove.fire(self)
			if len(barrier_hit) != 0:
				barrier_hit[0].hit()
				self.remove.fire(self)

		if self.origin == "alien":
			barrier_hit = pg.sprite.spritecollide(self, barrier_group, False)
			dude_hit = pg.sprite.spritecollide(self, dude_group, False)

			if len(barrier_hit) != 0:
				barrier_hit[0].hit()
				self.remove.fire(self)
			if len(dude_hit) != 0:
				dude_hit[0].hit()
				self.remove.fire(self)

	def update(self, alien_group, barrier_group, dude_group):
		self.movement()
		self.move_rect()
		self.check_objects(alien_group, barrier_group, dude_group)

class Barrier(GameObjects, pg.sprite.Sprite):
	def __init__(self, **kwargs):
		GameObjects.__init__(self, 30, 20, kwargs['x'], kwargs['y'], '/Users/carollin/Dev/space_invaders/graphics/barrier.jpg')
		pg.sprite.Sprite.__init__(self)

		self.death_sprite_source = '/Users/carollin/Dev/space_invaders/graphics/barrierexplosion.png'
		self.death_sprite_width = 163
		self.death_sprite_height = 30
		self.death_num_sprites = 5

	def hit(self):
		self.death_animation()
		self.remove.fire(self)

	def update(self):
		pass

class Animation(GameObjects, pg.sprite.Sprite):
	def __init__(self, x, y, width, height, source, num_sprites):
		GameObjects.__init__(self, width, height, x, y, source)
		pg.sprite.Sprite.__init__(self)

		self.source = source
		self.x = x
		self.y = y
		self.num_sprites = num_sprites
		self.spritesheet = self.open_resize_img(self.source, width, height)
		self.sprite_width = (width / self.num_sprites)
		self.rect = (0, 0, self.sprite_width, self.height)

		self.current_sprite = 0
		self.image_list = self.create_image_list()
		self.image = self.image_list[self.current_sprite]

	def update(self):
		self.determine_current()

	def determine_current(self):
		self.current_sprite += 1
		if self.current_sprite >= self.num_sprites:
			self.end_animation()
		else:
			self.image = self.image_list[self.current_sprite]


	def end_animation(self):
		self.remove.fire(self)

	def slide_image(self):
		i = self.current_sprite
		self.image = self.image_list[i]

	def create_image_list(self):
		r = self.rect
		rectangles = [(r[0] + r[2] * i, r[1], r[2], r[3]) for i in range(self.num_sprites)]
		return self.create_partial(rectangles)

	def create_partial(self, rectangles):
		return [self.load_image(rect) for rect in rectangles]

	def load_image(self, rectangle):
		r = pg.Rect(rectangle)
		image = pg.Surface(r.size).convert()
		image.blit(self.spritesheet, (0, 0), r)
		return image


class EventHook(object):
    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)

    def clearObjectHandlers(self, inObject):
        for theHandler in self.__handlers:
            if theHandler.im_self == inObject:
                self -= theHandler

class AlienTypes:
    def __init__(self):
        self.one = {
            'width': 25, 
            'height': 20, 
            'graphic': '/Users/carollin/Dev/space_invaders/graphics/alien1.png', 
            'h_move': 20, 
            'v_move': 20, 
            'move_wait': 15,
            'laser_dx': 0, 
            'laser_dy': 6, 
            'laser_graphic': '/Users/carollin/Dev/space_invaders/graphics/greenlaser.png', 
            'laser_sound': '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg', 
            'shot_wait': 300, 
            'hit_points': 5,
            'death_sprite': '/Users/carollin/Dev/space_invaders/graphics/alienexplosion.png',
            'death_sprite_width': 240,
            'death_sprite_height': 30,
            'death_num_sprites': 8
        }
        self.two = {
            'width': 25, 
            'height': 20, 
            'graphic': '/Users/carollin/Dev/space_invaders/graphics/alien2.png', 
            'h_move': 20, 
            'v_move': 20,
            'move_wait': 15, 
            'laser_dx': 0, 
            'laser_dy': 6, 
            'laser_graphic': '/Users/carollin/Dev/space_invaders/graphics/greenlaser.png', 
            'laser_sound': '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg', 
            'shot_wait': 200, 
            'hit_points': 10,
            'death_sprite': '/Users/carollin/Dev/space_invaders/graphics/alienexplosion.png',
            'death_sprite_width': 240,
            'death_sprite_height': 30,
            'death_num_sprites': 8
        }
        self.three = {
            'width': 25, 
            'height': 20, 
            'graphic': '/Users/carollin/Dev/space_invaders/graphics/alien3.png', 
            'h_move': 5, 
            'v_move': 5, 
            'move_wait': 1,
            'laser_dx': 0, 
            'laser_dy': 10, 
            'laser_graphic': '/Users/carollin/Dev/space_invaders/graphics/purplelaser.png', 
            'laser_sound': '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg',
            'shot_wait': 30, 
            'hit_points': 15,
            'death_sprite': '/Users/carollin/Dev/space_invaders/graphics/alienexplosion.png',
            'death_sprite_width': 240,
            'death_sprite_height': 30,
            'death_num_sprites': 8
        }
        self.four = {
        	'width': 25, 
            'height': 20, 
            'graphic': '/Users/carollin/Dev/space_invaders/graphics/alien3.png', 
            'h_move': 20, 
            'v_move': 20, 
            'move_wait': 15,
            'laser_dx': 0, 
            'laser_dy': 10, 
            'laser_graphic': '/Users/carollin/Dev/space_invaders/graphics/purplelaser.png', 
            'laser_sound': '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg',
            'shot_wait': 30, 
            'hit_points': 15,
            'death_sprite': '/Users/carollin/Dev/space_invaders/graphics/alienexplosion.png',
            'death_sprite_width': 240,
            'death_sprite_height': 30,
            'death_num_sprites': 8
        }
        self.five = {
        	'width': 15, 
            'height': 15, 
            'graphic': '/Users/carollin/Dev/space_invaders/graphics/alien4.png', 
            'h_move': 5, 
            'v_move': 5, 
            'move_wait': 5,
            'laser_dx': 0, 
            'laser_dy': 0, 
            'laser_graphic': '/Users/carollin/Dev/space_invaders/graphics/purplelaser.png', 
            'laser_sound': '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg',
            'shot_wait': 300000, 
            'hit_points': 15,
            'death_sprite': '/Users/carollin/Dev/space_invaders/graphics/alienexplosion.png',
            'death_sprite_width': 240,
            'death_sprite_height': 30,
            'death_num_sprites': 8
        }

class Levels:
    def __init__(self):
        self.data = [
            [ 
            #     {
            #         "type": Alien,
            #         "id": "two",
            #         "rows": 2,
            #         "columns": 11,
            #         "xcorner": 30,
            #         "ycorner": 50,
            #         "xspacing": 40,
            #         "yspacing": 40,
            #         "movement": [
            #             ("right", 15),
            #             ("down", 1),
            #             ("left", 15),
            #             ("down", 1)
            #         ]
            #     }, {
            #         "type": Alien,
            #         "id": "one",
            #         "rows": 3,
            #         "columns": 11,
            #         "xcorner": 30,
            #         "ycorner": 130,
            #         "xspacing": 40,
            #         "yspacing": 40,
            #         "movement": [
            #             ("right", 15),
            #             ("down", 1),
            #             ("left", 15),
            #             ("down", 1)
            #         ]
            #     }, {
            #         "type": Barrier,
            #         "rows": 3,
            #         "columns": 6,
            #         "xcorner": 100,
            #         "ycorner": 450,
            #         "xspacing": 30,
            #         "yspacing": 20
            #     }, {
            #         "type": Barrier,
            #         "rows": 3,
            #         "columns": 6,
            #         "xcorner": 340,
            #         "ycorner": 450,
            #         "xspacing": 30,
            #         "yspacing": 20
            #     }, {
            #         "type": Barrier,
            #         "rows": 3,
            #         "columns": 6,
            #         "xcorner": 580,
            #         "ycorner": 450,
            #         "xspacing": 30,
            #         "yspacing": 20
            #     }
            # ], [ 
            #     {
            #         "type": Alien,
            #         "id": "three",
            #         "rows": 1,
            #         "columns": 1,
            #         "xcorner": 25,
            #         "ycorner": 40,
            #         "xspacing": 40,
            #         "yspacing": 40,
            #         "movement": [
            #             ("right", 145),
            #             ("left", 145),
            #         ]
            #     }, {
            #         "type": Alien,
            #         "id": "three",
            #         "rows": 1,
            #         "columns": 1,
            #         "xcorner": 735,
            #         "ycorner": 70,
            #         "xspacing": 40,
            #         "yspacing": 40,
            #         "movement": [
            #             ("left", 145),
            #             ("right", 145),
            #         ] 
            #     }, {
            #         "type": Alien,
            #         "id": "two",
            #         "rows": 2,
            #         "columns": 6,
            #         "xcorner": 25,
            #         "ycorner": 110,
            #         "xspacing": 40,
            #         "yspacing": 40,
            #         "movement": [
            #             ("right", 6),
            #             ("down", 1),
            #             ("left", 6),
            #             ("down", 1) 
            #         ]
            #     }, {
            #         "type": Alien,
            #         "id": "two",
            #         "rows": 2,
            #         "columns": 6,
            #         "xcorner": 535,
            #         "ycorner": 110,
            #         "xspacing": 40,
            #         "yspacing": 40,
            #         "movement": [
            #             ("left", 6),
            #             ("down", 1),
            #             ("right", 6),
            #             ("down", 1) 
            #         ]
            #     }, {
            #         "type": Alien,
            #         "id": "one",
            #         "rows": 2,
            #         "columns": 6,
            #         "xcorner": 25,
            #         "ycorner": 190,
            #         "xspacing": 40,
            #         "yspacing": 40,
            #         "movement": [
            #             ("right", 6),
            #             ("down", 1),
            #             ("left", 6),
            #             ("down", 1) 
            #         ]
            #     }, {
            #         "type": Alien,
            #         "id": "one",
            #         "rows": 2,
            #         "columns": 6,
            #         "xcorner": 535,
            #         "ycorner": 190,
            #         "xspacing": 40,
            #         "yspacing": 40,
            #         "movement": [
            #             ("left", 6),
            #             ("down", 1),
            #             ("right", 6),
            #             ("down", 1) 
            #         ]
            #     }, {
            #         "type": Barrier,
            #         "rows": 3,
            #         "columns": 6,
            #         "xcorner": 100,
            #         "ycorner": 450,
            #         "xspacing": 30,
            #         "yspacing": 20
            #     }, {
            #         "type": Barrier,
            #         "rows": 3,
            #         "columns": 6,
            #         "xcorner": 340,
            #         "ycorner": 450,
            #         "xspacing": 30,
            #         "yspacing": 20
            #     }, {
            #         "type": Barrier,
            #         "rows": 3,
            #         "columns": 6,
            #         "xcorner": 580,
            #         "ycorner": 450,
            #         "xspacing": 30,
            #         "yspacing": 20
            #     }
            # ], 
            # [
            # 	{
	           #  	"type": Alien,
	           #  	"id": "four",
	           #  	"rows": 1,
	           #  	"columns": 2,
	           #  	"xcorner": 200,
	           #  	"ycorner": 100,
	           #  	"xspacing": 200,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	]
            # 	}, {
            # 		"type": Alien,
	           #  	"id": "four",
	           #  	"rows": 1,
	           #  	"columns": 2,
	           #  	"xcorner": 240,
	           #  	"ycorner": 140,
	           #  	"xspacing": 120,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	]
            # 	}, {
            # 		"type": Alien,
	           #  	"id": "two",
	           #  	"rows": 1,
	           #  	"columns": 6,
	           #  	"xcorner": 200,
	           #  	"ycorner": 180,
	           #  	"xspacing": 40,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	]
            # 	}, {
            # 		"type": Alien,
	           #  	"id": "four",
	           #  	"rows": 1,
	           #  	"columns": 3,
	           #  	"xcorner": 120,
	           #  	"ycorner": 220,
	           #  	"xspacing": 40,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	]	
            # 	}, {
            # 		"type": Alien,
	           #  	"id": "two",
	           #  	"rows": 1,
	           #  	"columns": 2,
	           #  	"xcorner": 280,
	           #  	"ycorner": 220,
	           #  	"xspacing": 40,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	]            		
            # 	}, {
            # 	    "type": Alien,
	           #  	"id": "four",
	           #  	"rows": 1,
	           #  	"columns": 3,
	           #  	"xcorner": 400,
	           #  	"ycorner": 220,
	           #  	"xspacing": 40,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	] 
            # 	}, {
            # 	    "type": Alien,
	           #  	"id": "two",
	           #  	"rows": 1,
	           #  	"columns": 12,
	           #  	"xcorner": 80,
	           #  	"ycorner": 260,
	           #  	"xspacing": 40,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	] 
            # 	}, {
            # 		"type": Alien,
            # 		"id": "one",
            # 		"rows": 1,
	           #  	"columns": 2,
	           #  	"xcorner": 80,
	           #  	"ycorner": 300,
	           #  	"xspacing": 440,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	] 
            # 	}, {
            # 		"type": Alien,
            # 		"id": "two",
            # 		"rows": 1,
	           #  	"columns": 8,
	           #  	"xcorner": 160,
	           #  	"ycorner": 300,
	           #  	"xspacing": 40,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	] 
            # 	}, {
            # 		"type": Alien,
            # 		"id": "one",
            # 		"rows": 1,
	           #  	"columns": 2,
	           #  	"xcorner": 80,
	           #  	"ycorner": 340,
	           #  	"xspacing": 440,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	] 
            # 	}, {
            # 		"type": Alien,
            # 		"id": "one",
            # 		"rows": 1,
	           #  	"columns": 2,
	           #  	"xcorner": 160,
	           #  	"ycorner": 340,
	           #  	"xspacing": 280,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	] 
            # 	}, {
            # 		"type": Alien,
            # 		"id": "one",
            # 		"rows": 1,
	           #  	"columns": 2,
	           #  	"xcorner": 200,
	           #  	"ycorner": 400,
	           #  	"xspacing": 40,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	] 
            # 	}, {
            # 		"type": Alien,
            # 		"id": "one",
            # 		"rows": 1,
	           #  	"columns": 2,
	           #  	"xcorner": 360,
	           #  	"ycorner": 400,
	           #  	"xspacing": 40,
	           #  	"yspacing": 0,
	           #  	"movement": [
	           #  		("up", 3),
	           #  		("right", 8),
	           #  		("down", 3),
	           #  		("left", 8)
	           #  	] 
            # 	}, {
            #         "type": Barrier,
            #         "rows": 1,
            #         "columns": 6,
            #         "xcorner": 100,
            #         "ycorner": 450,
            #         "xspacing": 30,
            #         "yspacing": 20
            #     }, {
            #         "type": Barrier,
            #         "rows": 1,
            #         "columns": 6,
            #         "xcorner": 340,
            #         "ycorner": 450,
            #         "xspacing": 30,
            #         "yspacing": 20
            #     }, {
            #         "type": Barrier,
            #         "rows": 1,
            #         "columns": 6,
            #         "xcorner": 580,
            #         "ycorner": 450,
            #         "xspacing": 30,
            #         "yspacing": 20
            #     }
            # ], [
            	{
            		"type": Alien,
            		"id": "five",
            		"rows": 1,
	            	"columns": 1,
	            	"xcorner": 130,
	            	"ycorner": 200,
	            	"xspacing": 20,
	            	"yspacing": 0,
	            	"movement": []	
            	}, {
            	    "type": Alien,
            		"id": "five",
            		"rows": 2,
	            	"columns": 2,
	            	"xcorner": 120,
	            	"ycorner": 220,
	            	"xspacing": 20,
	            	"yspacing": 20,
	            	"movement": []	
            	}, {
            		"type": Alien,
            		"id": "five",
            		"rows": 1,
	            	"columns": 2,
	            	"xcorner": 100,
	            	"ycorner": 230,
	            	"xspacing": 20,
	            	"yspacing": 20,
	            	"movement": []
            	}, {
            		"type": Alien,
            		"id": "five",
            		"rows": 1,
	            	"columns": 1,
	            	"xcorner": 130,
	            	"ycorner": 260,
	            	"xspacing": 20,
	            	"yspacing": 20,
	            	"movement": []
            	}, {
            		"type": Alien,
            		"id": "five",
            		"rows": 3,
	            	"columns": 3,
	            	"xcorner": 110,
	            	"ycorner": 280,
	            	"xspacing": 20,
	            	"yspacing": 20,
	            	"movement": []
            	}, {
            		"type": Alien,
            		"id": "five",
            		"rows": 2,
	            	"columns": 3,
	            	"xcorner": 90,
	            	"ycorner": 340,
	            	"xspacing": 20,
	            	"yspacing": 20,
	            	"movement": [
	            		("right", 8),
	            		("left", 8)
	            	]
            	}, {
            		"type": Alien,
            		"id": "five",
            		"rows": 1,
	            	"columns": 3,
	            	"xcorner": 110,
	            	"ycorner": 380,
	            	"xspacing": 20,
	            	"yspacing": 20,
	            	"movement": []
            	}, {
            		"type": Alien,
            		"id": "five",
            		"rows": 1,
	            	"columns": 2,
	            	"xcorner": 100,
	            	"ycorner": 400,
	            	"xspacing": 60,
	            	"yspacing": 20,
	            	"movement": []
            	}, {
            		"type": Alien,
            		"id": "five",
            		"rows": 1,
	            	"columns": 2,
	            	"xcorner": 60,
	            	"ycorner": 420,
	            	"xspacing": 20,
	            	"yspacing": 20,
	            	"movement": [
	            		("left", 8),
	            		("right", 8)
	            	]
            	}, {
            		"type": Alien,
            		"id": "five",
            		"rows": 1,
	            	"columns": 2,
	            	"xcorner": 140,
	            	"ycorner": 420,
	            	"xspacing": 20,
	            	"yspacing": 20,
	            	"movement": [
	            		("left", 8),
	            		("right", 8)
	            	]
				}
			]     
		]

Game()


