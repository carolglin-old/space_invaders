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

class CanvasObjects:
	def __init__(self):
		pg.mixer.init()

	def play(self, music_file, volume = 0.8):
		pg.mixer.music.load(music_file)
		pg.mixer.music.play()

	def stop_music(self):
		pg.mixer.music.stop()

	def open_resize_img(self, img_source, width, height):
		graphic = pg.image.load(img_source).convert()
		graphic = pg.transform.scale(graphic, (width, height))
		graphic.set_colorkey(BLACK)
		return graphic

class GameObjects(CanvasObjects):
	def __init__(self, width, height, x, y, img_source):
		super().__init__()

		self.width = width
		self.height = height
		self.x = x
		self.y = y

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

class LevelManager(CanvasObjects, pg.sprite.Sprite):
	def __init__(self):
		super().__init__()

		self.levels = Levels()
		self.current = 0

		self.a = AlienTypes()

		self.create = EventHook()
		self.clear = EventHook()

	def init_level(self, current_level):
		self.current_level = self.levels.data[self.current]
		self.load_level(self.current_level)

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

	def create_block(self, object_type, info_list):
		if object_type is Alien:
			for dictionary in info_list:
				a = Alien(**dictionary)
				self.create.fire(a)

		if object_type is Barrier:
			for dictionary in info_list:
				b = Barrier(**dictionary)
				self.create.fire(b)

class Game(CanvasObjects, pg.sprite.Sprite):
	def __init__(self):
		super().__init__()

		pg.init()

		self.isStopped = True

		self.lives = 3

		self.clock = pg.time.Clock()
		self.sleepTime = 100

		self.alien_group = pg.sprite.Group()	
		self.barrier_group = pg.sprite.Group()
		self.dude_group = pg.sprite.GroupSingle()
		self.alien_laser_group = pg.sprite.Group()
		self.dude_laser_group = pg.sprite.Group()
		self.update_list = pg.sprite.Group()

		self.level_manager = LevelManager()
		self.level_manager.create += self.add_to_list
		self.level_manager.clear += self.next_level

		self.total_aliens = 0

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

		self.create_dude()
		self.start()

	def start(self):
		self.isStopped = False
		self.level_manager.init_level(self.level_manager.current)
		self.mainloop()

	def create_dude(self):
		self.dude = Dude()
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
		if type(obj) is Barrier:
			self.barrier_group.add(obj)
		if type(obj) is Laser:
			if obj.origin == "dude":
				self.dude_laser_group.add(obj)
			if obj.origin == "alien":
				self.alien_laser_group.add(obj)

	def remove_object(self, obj):
		if type(obj) is Dude:
			self.check_lives()
		if type(obj) is Alien:
			self.check_aliens()

		obj.kill()

	def next_level(self):
		self.isStopped = True
		self.level_manager.current += 1
		self.reset_groups()
		self.start()

	def reset_groups(self):
		self.alien_group.empty()
		self.alien_laser_group.empty()
		self.barrier_group.empty()
		self.dude_laser_group.empty()

	def check_lives(self):
		self.lives -= 1
		if self.lives > 0:
			self.create_dude()
		else:
			self.isStopped = True

	def check_aliens(self):
		self.total_aliens -= 1
		if self.total_aliens == 0:
			self.next_level()

	def mainloop(self):
		while self.isStopped is False:

			self.key_events()
			self.update_model()
			self.refresh_view()

			self.clock.tick(self.sleepTime)

	def key_events(self):
		for event in pg.event.get():
			self.last_keys_pressed = self.keys
			self.keys = pg.key.get_pressed()
			if self.keys[pg.K_a]:
				self.dude.left()
			if self.keys[pg.K_d]:
				self.dude.right()
			if self.keys[pg.K_SPACE]:
				self.dude.shoot()
			if self.keyrelease_listener(pg.K_a) is True:
				self.dude.reset_movement()
			if self.keyrelease_listener(pg.K_d) is True:
				self.dude.reset_movement()
			if self.keyrelease_listener(pg.K_SPACE) is True:
				self.dude.shooting = False
			if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
				self.isStopped = True

	def keyrelease_listener(self, key_code):
		if self.last_keys_pressed[key_code] and not self.keys[key_code]:
			return True
		return False

	def update_model(self): 
		for obj in self.update_list:
			if type(obj) is Laser:
				obj.update(self.alien_group, self.barrier_group, self.dude_group)
			else:
				obj.update()

	def refresh_view(self):
		self.update_list.clear(self.screen, self.background)
		self.update_list.draw(self.screen)

		pg.display.update()

class Dude(GameObjects, pg.sprite.Sprite):
	def __init__(self):
		GameObjects.__init__(self, 30, 30, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 35, '/Users/carollin/Dev/space_invaders/graphics/dude.png')
		pg.sprite.Sprite.__init__(self)

		self.dx = 0
		self.dy = 0

		self.movement_speed = 5

		self.laser_graphic = '/Users/carollin/Dev/space_invaders/graphics/redlaser.png'
		self.laser_dx = 0
		self.laser_dy = -6
		self.laser_sound = '/Users/carollin/Dev/space_invaders/sounds/dudelaser.ogg'
		self.laser_strength = 10

		self.shooting = False
		self.time_fired = 0
		self.shot_wait = 0.45

		self.spawn_time = time.clock()

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
			mid_x = self.x + (self.width / 2)
			self.create_laser(mid_x, self.y, self.laser_dx, self.laser_dy, "dude", self.laser_graphic)
			self.time_fired = time.clock()

	def stop_shooting(self):
		self.shooting = False

	def hit(self):
		if self.invincible() is False:
			self.remove.fire(self)

	def invincible(self):
		if (time.clock() - self.spawn_time) <= 3:
			return True
		else:
			return False

	def update(self):
		self.movement()
		self.move_rect()
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

		self.hit_points = kwargs['hit_points']

		self.movement_list = kwargs['movement_list']

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
	    if self.wait_time(self.time_moved, self.move_wait) is True:
	    	self.determine_move()

	    	self.x += self.dx
	    	self.y += self.dy

	    	self.shift_moves()
	    	self.time_moved = time.clock()

	def shift_moves(self):
		self.movement_list.append(self.movement_list[0])
		self.movement_list.pop(0)

	def attempt_shot(self):
		if self.randomize() == "go":
			mid_x = self.x + (self.width / 2)
			self.create_laser(mid_x, self.y, self.laser_dx, self.laser_dy, "alien", self.laser_graphic)

	def randomize(self):
		if random.randrange(self.shot_wait) == 1:
			return "go"

	def update(self):
		self.attempt_shot()
		self.movement()
		self.move_rect()

class Laser(GameObjects, pg.sprite.Sprite):
	def __init__(self, x, y, dx, dy, origin, graphic = '/Users/carollin/Dev/space_invaders/graphics/greenlaser.png'):
		GameObjects.__init__(self, 3, 15, x, y, graphic)
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
				self.remove.fire(alien_hit[0])
				self.remove.fire(self)
			if len(barrier_hit) != 0:
				self.remove.fire(barrier_hit[0])
				self.remove.fire(self)

		if self.origin == "alien":
			barrier_hit = pg.sprite.spritecollide(self, barrier_group, False)
			dude_hit = pg.sprite.spritecollide(self, dude_group, False)

			if len(barrier_hit) != 0:
				self.remove.fire(barrier_hit[0])
				self.remove.fire(self)
			if len(dude_hit) != 0:
				dude_hit[0].hit()
				self.remove.fire(self)

	# def collision_detect_list(self, sprite_list):
	# 	for i in sprite_list:
	# 		if self.rect.colliderect(i.rect) is True:
	# 			self.remove.fire(i)

	# def collision_detect_object(self, obj):
	# 	if self.rect.colliderect(obj):
	# 		self.remove.fire(obj)

	# def create_rect_list(self, sprite_list):
	# 	rect_list = []
	# 	for i in sprite_list:
	# 		rect_list.append(i.rect)
	# 	return rect_list

	def update(self, alien_group, barrier_group, dude_group):
		self.movement()
		self.move_rect()
		self.check_objects(alien_group, barrier_group, dude_group)

class Barrier(GameObjects, pg.sprite.Sprite):
	def __init__(self, **kwargs):
		GameObjects.__init__(self, 30, 20, kwargs['x'], kwargs['y'], '/Users/carollin/Dev/space_invaders/graphics/barrier.jpg')
		pg.sprite.Sprite.__init__(self)

	def update(self):
		pass

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
            'laser_dx': 0, 
            'laser_dy': 6, 
            'laser_graphic': '/Users/carollin/Dev/space_invaders/graphics/greenlaser.png', 
            'laser_sound': '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg', 
            'move_wait': 0.5, 
            'shot_wait': 400, 
            'hit_points': 20
        }
        self.two = {
            'width': 25, 
            'height': 20, 
            'graphic': '/Users/carollin/Dev/space_invaders/graphics/alien2.png', 
            'h_move': 20, 
            'v_move': 20, 
            'laser_dx': 0, 
            'laser_dy': 6, 
            'laser_graphic': '/Users/carollin/Dev/space_invaders/graphics/greenlaser.png', 
            'laser_sound': '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg', 
            'move_wait': 0.5, 
            'shot_wait': 300, 
            'hit_points': 20
        }
        self.three = {
            'width': 25, 
            'height': 20, 
            'graphic': '/Users/carollin/Dev/space_invaders/graphics/alien3.png', 
            'h_move': 5, 
            'v_move': 5, 
            'laser_dx': 0, 
            'laser_dy': 10, 
            'laser_graphic': '/Users/carollin/Dev/space_invaders/graphics/greenlaser.png', 
            'laser_sound': '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg', 
            'move_wait': 0, 
            'shot_wait': 30, 
            'hit_points': 30
        }

class Levels:
    def __init__(self):
        self.data = [
            [  
                {
                    "type": Alien,
                    "id": "two",
                    "rows": 2,
                    "columns": 11,
                    "xcorner": 30,
                    "ycorner": 50,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 15),
                        ("down", 1),
                        ("left", 15),
                        ("down", 1)
                    ]
                }, {
                    "type": Alien,
                    "id": "one",
                    "rows": 3,
                    "columns": 11,
                    "xcorner": 30,
                    "ycorner": 130,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 15),
                        ("down", 1),
                        ("left", 15),
                        ("down", 1)
                    ]
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 100,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 340,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 580,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }
            ], [ 
                {
                    "type": Alien,
                    "id": "three",
                    "rows": 1,
                    "columns": 1,
                    "xcorner": 25,
                    "ycorner": 40,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 145),
                        ("left", 145),
                    ]
                }, {
                    "type": Alien,
                    "id": "three",
                    "rows": 1,
                    "columns": 1,
                    "xcorner": 735,
                    "ycorner": 70,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("left", 145),
                        ("right", 145),
                    ] 
                }, {
                    "type": Alien,
                    "id": "two",
                    "rows": 2,
                    "columns": 6,
                    "xcorner": 25,
                    "ycorner": 110,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 6),
                        ("down", 1),
                        ("left", 6),
                        ("down", 1) 
                    ]
                }, {
                    "type": Alien,
                    "id": "two",
                    "rows": 2,
                    "columns": 6,
                    "xcorner": 535,
                    "ycorner": 110,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("left", 6),
                        ("down", 1),
                        ("right", 6),
                        ("down", 1) 
                    ]
                }, {
                    "type": Alien,
                    "id": "one",
                    "rows": 2,
                    "columns": 6,
                    "xcorner": 25,
                    "ycorner": 190,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("right", 6),
                        ("down", 1),
                        ("left", 6),
                        ("down", 1) 
                    ]
                }, {
                    "type": Alien,
                    "id": "one",
                    "rows": 2,
                    "columns": 6,
                    "xcorner": 535,
                    "ycorner": 190,
                    "xspacing": 40,
                    "yspacing": 40,
                    "movement": [
                        ("left", 6),
                        ("down", 1),
                        ("right", 6),
                        ("down", 1) 
                    ]
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 100,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 340,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }, {
                    "type": Barrier,
                    "rows": 3,
                    "columns": 6,
                    "xcorner": 580,
                    "ycorner": 450,
                    "xspacing": 30,
                    "yspacing": 20
                }
            ]       
        ]


Game()


