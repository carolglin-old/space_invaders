from tkinter import *
from PIL import Image, ImageTk
import random
import math
import time
import pygame.mixer as mix
import pdb

class CanvasObjects():
	def __init__(self):
		self.screen_width = 800
		self.screen_height = 550

	def image_convert(self, imagepath, width, height):
		size = width, height
		graphic = Image.open(imagepath)
		graphic.thumbnail(size, Image.ANTIALIAS)
		resized = ImageTk.PhotoImage(graphic)
		return resized

	def draw(self, canvas, x, y, graphic, tag):
		canvas.create_image(x, y, image = graphic, anchor = SW, tag = tag)

	def play(self, music_file, volume = 0.8):
		mix.music.stop()
		mix.music.load(music_file)
		mix.music.play()

	def stop_music(self):
		mix.music.stop()

class GameObjects(CanvasObjects):
	def __init__(self, width, height, source):
		super().__init__()
		self.width = width
		self.height = height
		self.source = source

		self.create = EventHook()
		self.remove = EventHook()

		self.graphic = self.image_convert(self.source, self.width, self.height)

		self.flash = False

		mix.init()

		self.tag = "game_object"

	def wait_time(self, fire_time, wait_time):
		if time.clock() > fire_time + wait_time:
			return True

	def create_laser(self, x, y, dx, dy, hit_list, graphic):
		l = Laser(x, y, dx, dy, hit_list, graphic)
		self.create.fire(l)

	def animate(self):
		a = Animation(self.x, self.y, self.animation_width, self.animation_height, self.animation_graphic, self.num_sprites)
		self.create.fire(a)

class LevelManager(CanvasObjects):
	def __init__(self, canvas):
		self.levels = Levels()
		self.current = 0
		self.total_aliens = 0

		self.c = canvas

		self.a = AlienTypes()

		self.dude_load_list = []
		self.laser_load_list = []

		self.create = EventHook()
		self.clear = EventHook()

	def init_level(self, current_level):
		self.total_aliens = 0
		self.current_level = self.levels.data[self.current]
		self.load_level(self.current_level)

	def load_level(self, current_level):
		for i in current_level:
			if i["type"] == Dude:
				self.create_object(i["type"])
			if i["type"] == Alien:
				self.alien_load_list = []
				self.load_block(i, self.alien_load_list)
			if i["type"] == Barrier:
				self.barrier_load_list = []
				self.load_block(i, self.barrier_load_list)

	def load_block(self, raw, final_list):
		self.add_rows_columns(final_list, raw["rows"], raw["columns"], raw["xcorner"], raw["ycorner"], raw["xspacing"], raw["yspacing"])
		if raw["type"] == Alien:
			self.combine_movement(raw)
			self.add_alien_info(raw)

		self.create_block(raw["type"], final_list)

	def combine_movement(self, raw):
		for i in self.alien_load_list:
			i.append(self.movement_pattern(raw["movement"]))

	def add_alien_info(self, raw):
		for i in self.alien_load_list:
			if raw["id"] == "one":
				i.append(self.a.one)
			if raw["id"] == "two":
				i.append(self.a.two)
			if raw["id"] == "three":
				i.append(self.a.three)

	def movement_pattern(self, raw_movement_data):
		movement_list = []
		for i in raw_movement_data:
			j = 0
			while j < i[1]:
				movement_list.append(i[0])
				j += 1
		return movement_list

	def add_rows_columns(self, end_list, rows, columns, xcorner, ycorner, xspacing, yspacing):
		index = 1
		while index <= rows:
			y_val = (index - 1) * yspacing + ycorner
			for i in range(columns):
				x_val = i * xspacing + xcorner
				add = [x_val, y_val]
				end_list.append(add)
			index += 1 

	def create_block(self, object_type, create_list):
		if object_type is Alien:
			for i in create_list:
				a = Alien(i[0], i[1], i[2], i[3]) 
				self.total_aliens += 1
				a.remove += self.aliens_left
				self.create.fire(a)

		if object_type is Barrier:
			for i in create_list:
				b = Barrier(i[0], i[1])
				self.create.fire(b)

	def create_object(self, object_type):
		if object_type is Dude:
			d = Dude(self.c)
			self.create.fire(d)

	def aliens_left(self, obj):
		self.total_aliens -= 1
		if self.total_aliens == 0:
			self.clear.fire()

class Game(CanvasObjects):
	def __init__(self):
		super().__init__()

		self.sleepTime = 5
		self.lives = 3

		self.update_list = []

		self.isStopped = True

		self.load_screen()

	def load_screen(self):
		w = Tk()

		self.background = '/Users/carollin/Dev/space_invaders/graphics/background.png'
		size = self.screen_width, self.screen_height

		frame = Frame()

		self.canvas = Canvas(w, width = self.screen_width, height = self.screen_height)
		self.canvas.pack(expand = YES, fill = BOTH)

		self.canvas.focus_set()
		self.start_button = Button(self.canvas, text = "Start", command = self.start)
		self.start_button.pack()

		self.backgroundimage = self.image_convert(self.background, self.screen_width, self.screen_height)
		self.canvas.create_image(0, 0, image = self.backgroundimage, anchor = NW)

		self.level_manager = LevelManager(self.canvas)
		self.level_manager.create += self.add_to_update_list
		self.level_manager.clear += self.next_level

		self.create_start_button()

		w.mainloop()

	def create_start_button(self):
		self.canvas.focus_set()
		self.canvas.create_window(self.screen_width / 2, self.screen_height / 2, window = self.start_button, tags = "start")

	def start(self):
		self.isStopped = False
		self.reset_screen()
		self.level_manager.init_level(self.level_manager.current)
		self.mainloop()

	def reset_update_list(self):
		copy = self.update_list[:]
		for i in copy:
			if type(i) is Barrier:
				self.update_list.remove(i)

	def reset_screen(self):
		self.canvas.delete("text")
		self.canvas.delete("start")
		self.canvas.update()

	def add_to_update_list(self, obj):
		self.update_list.append(obj)
		obj.remove += self.remove_object
		# if hasattr(obj, "animate"):
		# 	obj.animate += self.animate
		if hasattr(obj, "create"):
			obj.create += self.add_to_update_list

	def remove_object(self, obj):
		if obj in self.update_list:
			self.update_list.remove(obj)
		self.check_lives(obj)

	def next_level(self):
		self.canvas.create_text(self.screen_width / 2, (self.screen_height / 2) - 100, fill = "yellow", text = "Next Level! Ready?", tags = "text")
		self.level_manager.current += 1
		self.reset_update_list()
		self.create_start_button()

	def check_lives(self, obj):
		if type(obj) is Dude:
			self.lives -= 1
			if self.lives > 0:
				self.level_manager.create_object(Dude)
			else:
				self.canvas.create_text(self.screen_width / 2, self.screen_height / 2, fill = "yellow", text = "YOU LOSE! Oh poo")

	def mainloop(self):
		while not self.isStopped:
			self.canvas.after(self.sleepTime)
			self.update_model()
			self.refresh_view()

	def refresh_view(self):
		self.canvas.delete("game_object")
		self.canvas.delete("dude")
		copy = self.update_list[:]
		for obj in copy:
			if obj.flash is True:
				pass 
			else:
				self.draw(self.canvas, obj.x, obj.y, obj.graphic, obj.tag)

		self.canvas.update()


	def update_model(self):
		copy = self.update_list[:]
		for obj in copy:
			# trying to improve runtime with below:
			if type(obj) is Laser:
				obj.update(copy)
			else:
				obj.update()

class Barrier(GameObjects):
	def __init__(self, x, y):
		super().__init__(30, 20, '/Users/carollin/Dev/space_invaders/graphics/barrier.jpg')
		self.x = x
		self.y = y

		self.animation_graphic = '/Users/carollin/Dev/space_invaders/graphics/barrierexplosion.png'
		self.animation_width = 250
		self.animation_height = 46
		self.num_sprites = 5

	def hit(self, laser):
		self.remove.fire(self)
		self.animate()

	def update(self):
		pass

class Dude(GameObjects):
	def __init__(self, canvas): 
		super().__init__(30, 30, '/Users/carollin/Dev/space_invaders/graphics/dude.png')

		self.x = self.screen_width / 2
		self.y = self.screen_height - 5
		self.dx = 0
		self.dy = 0
		self.tag = "dude"

		self.movement_speed = 5

		self.c = canvas

		self.c.focus_set()
		self.c.bind("a", self.left)
		self.c.bind("d", self.right)
		self.c.bind("<space>", self.shoot)
		self.c.bind("<KeyRelease-space>", self.stop_shoot)
		self.c.bind("<KeyRelease-a>", self.reset_movement)
		self.c.bind("<KeyRelease-d>", self.reset_movement)
		self.c.pack()

		self.laser_graphic = '/Users/carollin/Dev/space_invaders/graphics/redbeam.jpg'
		self.laser_dx = 0
		self.laser_dy = -6
		self.laser_sound = '/Users/carollin/Dev/space_invaders/sounds/dudelaser.ogg'
		self.laser_strength = 10

		self.animation_graphic = '/Users/carollin/Dev/space_invaders/graphics/dudeexplosion.png'
		self.animation_width = 1024
		self.animation_height = 128
		self.num_sprites = 20

		self.flash = True
		self.flash_iter = 1

		self.shot_wait = 0.45
		self.time_fired = 0
		self.shooting = False

		self.spawn_time = time.clock()

		self.hit_list = [Alien, Barrier]

	# movement functions	
	def left(self, event):
		self.dx = self.movement_speed * -1

	def right(self, event):
		self.dx = self.movement_speed

	def reset_movement(self, event):
		self.dx = 0

	def movement(self):
		self.infinite_sides()
		self.x += self.dx
		self.y += self.dy

	def infinite_sides(self):
		if self.x > self.screen_width:
			self.x = 5
		if self.x < 0:
			self.x = self.screen_width - 5

	def shoot(self, event):
		self.shooting = True
		if self.wait_time(self.time_fired, self.shot_wait) is True:
			mid_x = self.x + (self.width / 2)
			top_y = self.y - self.height
			self.create_laser(mid_x, top_y, self.laser_dx, self.laser_dy, self.hit_list, self.laser_graphic)
			self.play(self.laser_sound)
			self.time_fired = time.clock()

	def stop_shoot(self, event):
		self.shooting = False

	def hit(self, laser):
		if self.invincible() is False:
			self.remove.fire(self)
			self.animate()

	def check_flash(self):
		if self.invincible() == True:
			if self.flash_iter % 3 == 0:
				self.flash = True
			else: 
				self.flash = False
			self.flash_iter += 1

	def invincible(self):
		if (time.clock() - self.spawn_time) <= 3:
			return True
		else:
			return False

	def update(self):
		self.check_flash()
		self.movement()

class Alien(GameObjects):
	def __init__(self, x, y, movement_list, type_list):
		super().__init__(type_list[0], type_list[1], type_list[2])

		self.x = x
		self.y = y
		self.dx = 0
		self.dy = 0
		self.horizontal_jump = type_list[3]
		self.vertical_jump = type_list[4]

		self.laser_dx = type_list[5]
		self.laser_dy = type_list[6]
		self.laser_graphic = type_list[7]
		self.laser_sound = type_list[8]

		self.move_wait = type_list[9]
		self.shot_wait = type_list[10]
		self.time_moved = 0

		self.hit_points = type_list[11]

		self.movement_list = movement_list

		self.animation_graphic = '/Users/carollin/Dev/space_invaders/graphics/alienexplosion.png'
		self.animation_width = 320
		self.animation_height = 40
		self.num_sprites = 8

		self.hit_list = [Dude, Barrier]

	# movement functions

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

	# shooting functions

	def attempt_shot(self):
		if self.randomize() == "go":
			self.play(self.laser_sound)
			mid_x = self.x + (self.width / 2)
			self.create_laser(mid_x, self.y, self.laser_dx, self.laser_dy, self.hit_list, self.laser_graphic)

	def randomize(self):
		if random.randrange(self.shot_wait) == 1:
			return "go"

	def hit(self, laser):
		self.hit_points -= 10
		if self.hit_points <= 0:
			self.remove.fire(self)
			self.animate()

	def update(self):
		self.movement()
		self.attempt_shot()

class Laser(GameObjects):
	def __init__(self, x, y, dx, dy, hit_list, graphic):
		super().__init__(5, 15, '/Users/carollin/Dev/space_invaders/graphics/greenbeam.jpg')

		self.x = x
		self.y = y
		self.dx = dx
		self.dy = dy

		self.graphic = self.image_convert(graphic, self.width, self.height)

		self.hit_list = hit_list

	def move(self):
		self.x += self.dx
		self.y += self.dy

	def x_test(self, obj):
		if self.x + self.width >= obj.x and self.x <= obj.x + obj.width:
			return True

	def y_test(self, obj):
		# only the tip of the laser can be collided into
		if self.y + self.height >= obj.y and (self.y + self.height - 5) <= obj.y + obj.width: 
			return True

	def check_objects(self, master_list):
		for obj in master_list:
			self.check_type(obj)

	def check_type(self, obj):
		if type(obj) in self.hit_list:
			self.check_boundaries(obj)

	def check_boundaries(self, obj):
		if self.x_test(obj) is True and self.y_test(obj) is True:
			obj.hit(self)
			self.remove.fire(self)

	def check_if_active(self):
		if self.y > self.screen_height or self.y < 0:
			self.remove.fire(self)

	def update(self, master_list):
		self.move()
		self.check_if_active()
		self.check_objects(master_list)

class Animation(GameObjects):
	def __init__(self, x, y, width, height, source, num_sprites):
		super().__init__(width, height, source)

		self.source = source

		self.x = x
		self.y = y

		self.sprite_width = (width / num_sprites) - 1

		self.spritesheet = self.image_convert(self.source, width, height)
		self.num_sprites = num_sprites
		self.current_sprite = 0
		self.tag = "game_object"

		self.slide_image()

	def slide_image(self):
		i = self.current_sprite
		self.graphic = self.subimage(int(self.sprite_width * i), 0, int(self.sprite_width * (i + 1)), self.height)

	def subimage(self, l, t, r, b):
		dst = PhotoImage()
		dst.tk.call(dst, 'copy', self.spritesheet, '-from', l, t, r, b, '-to', 0, 0)
		return dst

	def update(self):
		self.current_sprite += 1
		if self.current_sprite == self.num_sprites:
			self.remove.fire(self)
		else:
			self.slide_image()

class AlienTypes:
	def __init__(self):

		# (width, height, graphic, horizontal_move, vertical_move, laser_dx, laser_dy, laser_graphic, shoot_sound, move_wait, shot_wait, hit_points)

		self.one = (35, 35, '/Users/carollin/Dev/space_invaders/graphics/alien1.png', 20, 20, 0, 6, '/Users/carollin/Dev/space_invaders/graphics/greenbeam.jpg', '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg', 0.5, 400, 10)
		self.two = (35, 35, '/Users/carollin/Dev/space_invaders/graphics/alien2.png', 20, 20, 0, 6, '/Users/carollin/Dev/space_invaders/graphics/greenbeam.jpg', '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg', 0.5, 300, 20)
		self.three = (30, 30, '/Users/carollin/Dev/space_invaders/graphics/alien3.png', 5, 5, 0, 10, '/Users/carollin/Dev/space_invaders/graphics/bluebeam.jpg', '/Users/carollin/Dev/space_invaders/sounds/alienlaser.ogg', 0, 30, 20)

class Levels:
	def __init__(self):
		self.data = [
			[ 
				{
					"type": Dude
				}, 
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

Game()

