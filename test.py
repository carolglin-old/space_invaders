from tkinter import *
from PIL import Image, ImageTk
import random
import math
import time
# import pdb

class Master():
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

class Level(Master):
	def __init__(self):
		super(Level, self).__init__()
		
	def load_level(self, level):
		if level == "one":
			self.level_one_aliens()
		if level == "two":
			self.level_two_aliens()

	def level_one_aliens(self):
		self.level_one_xy = []
		columns = 12
		rows = 5
		xborder = 25
		yborder = 50
		xspacing = self.screen_width / 20
		yspacing = xspacing

		self.add_rows_columns(self.level_one_xy, columns, rows, xborder, yborder, xspacing, yspacing)

	def level_two_aliens(self):
		self.level_two_xy_group1 = []
		columns = 6
		rows = 3
		xborder = 25
		yborder = 50
		xspacing = self.screen_width / 20
		yspacing = xspacing + 40

		self.add_rows_columns(self.level_two_xy_group1, columns, rows, xborder, yborder, xspacing, yspacing)

		self.level_two_xy_group2 = []
		columns = 6
		rows = 3
		xborder = self.screen_width - 25
		yborder = 50
		spacing = self.screen_width / 20

		self.add_rows_columns(self.level_two_xy_group2, columns, rows, xborder, yborder, xspacing, yspacing)

	def add_rows_columns(self, end_list, columns, rows, xborder, yborder, xspacing, yspacing):
		index = 1
		while index <= rows:
			y_val = (index - 1) * yspacing + yborder
			for i in range(columns - 1):
				x_val = i * xspacing + xborder
				add = x_val, y_val
				end_list.append(add)
			index += 1
		return end_list

class Game(Master):
	def __init__(self):
		super(Game, self).__init__()

		self.sleepTime = 5
		self.lives = 3

		self.update_list = []
		self.to_delete = []

		self.isStopped = True

		self.level = Level()
		self.current_level = "one"
		self.load_screen()

	def load_screen(self):
		w = Tk()

		self.background = '/Users/carollin/dev/space_invaders/graphics/background.png'
		size = self.screen_width, self.screen_height

		self.canvas = Canvas(w, width = self.screen_width, height = self.screen_height)
		self.canvas.pack(expand = YES, fill = BOTH)

		self.backgroundimage = self.image_convert(self.background, self.screen_width, self.screen_height)
		self.canvas.create_image(0, 0, image = self.backgroundimage, anchor = NW)

		self.start(self.current_level)

		w.mainloop()

	def start(self, current_level):
		self.isStopped = False
		self.create_dude()
		self.create_level(current_level)
		self.mainloop()

	def create_dude(self):
		self.dude = Dude(self.canvas)
		self.dude.shoot += self.create_lasers
		self.update_list.append(self.dude)

	def create_level(self, current_level):
		self.create_aliens(current_level)
		# self.create_barriers(self, current_level)

	def create_aliens(self, current_level):
		xy_list = self.level.load_level(current_level)
		for i in xy_list:
			x = i[0]
			y = i[1]
			a = AlienTypeOne(x, y)
			a.shoot += self.create_lasers
			self.update_list.append(a)

	def create_lasers(self, x, y, origin):
		l = Laser(x, y, origin)
		l.remove += self.remove_object
		l.hit += self.remove_object
		self.update_list.append(l)

	def remove_object(self, obj):
		self.update_list.remove(obj)

	def check_if_win(self):
		aliens_remaining = 0
		for obj in self.update_list:
			if type(obj) is AlienTypeOne:
				aliens_remaining += 1
		if aliens_remaining == 0:
			self.canvas.create_text(self.screen_width / 2, self.screen_height / 2, fill = "yellow", text = "YOU WIN! w00t!")

	def check_lives(self, obj2):
		if obj2.tag == "dude":
			self.lives -= 1
			if self.lives > 0:
				self.create_dude()
			else:
				self.canvas.create_text(self.screen_width / 2, self.screen_height / 2, fill = "yellow", text = "YOU LOSE! Oh poo")

	def mainloop(self):
		while not self.isStopped:
			self.canvas.after(self.sleepTime)
			self.update_model()
			self.refresh_view()

	def refresh_view(self):
		copy = self.update_list[:]
		for obj in copy:
			self.draw(self.canvas, obj.x, obj.y, obj.graphic, obj.tag)

		self.canvas.update()
		self.canvas.delete("dude")
		self.canvas.delete("alien")

	def update_model(self):
		copy = self.update_list[:]
		for obj in copy:
			obj.update(copy)

class Dude(Master):
	def __init__(self, canvas):
		super(Dude, self).__init__()

		self.height = 30
		self.width = 30
		self.x = self.screen_width / 2
		self.y = self.screen_height - 5
		self.dx = 0
		self.dy = 0
		self.source = '/Users/carollin/dev/space_invaders/graphics/dude.png'
		self.tag = "dude"
		self.movement_speed = 4

		self.c = canvas

		self.c.focus_set()
		self.graphic = self.image_convert(self.source, self.width, self.height)

		self.c.bind("a", self.left)
		self.c.bind("d", self.right)
		self.c.bind("<space>", self.shoot)
		self.c.bind("<KeyRelease-a>", self.reset_movement)
		self.c.bind("<KeyRelease-d>", self.reset_movement)
		self.c.pack()

		self.wait_time = 0.5
		self.time_fired = 0

		# event handlers
		self.shoot = EventHook()
		self.shoot_pause = EventHook()

	# movement functions	

	def left(self, event):
		self.dx = self.movement_speed * -1

	def right(self, event):
		self.dx = self.movement_speed

	def reset_movement(self, event):
		self.dx = 0

	def move(self):
		# infinite moving left and right
		if self.x > self.screen_width:
			self.x = 5
		if self.x < 0:
			self.x = self.screen_width - 5

		self.x += self.dx

	# shooting functions

	def shoot(self, event):
		if self.check_time() is True:
			mid_x = self.x + (self.width / 2)
			top_y = self.y - self.height
			self.shoot.fire(mid_x, top_y, "dude")
			self.time_fired = time.clock()

	def update(self, master_list):
		self.move()

	def check_time(self):
		if time.clock() > self.time_fired + self.wait_time:
			return True

class AlienTypeOne(Master):
	def __init__(self, x, y):
		super(AlienTypeOne, self).__init__()

		self.height = 35
		self.width = 35
		self.x = x
		self.y = y
		self.dx = 20
		self.dy = 40
		self.source = '/Users/carollin/dev/space_invaders/graphics/alien1.png'
		self.tag = "alien"
		self.horizontal_jump = 20
		self.vertical_jump = 20
		self.wait_time = 1

		self.movement_list = []

		self.create_movement_pattern()

		self.time_between_shots = 500

		self.graphic = self.image_convert(self.source, self.width, self.height)

		# event handlers
		self.shoot = EventHook()

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

	def create_movement_pattern(self):
		for i in range(17):
			self.movement_list.append("right")
		self.movement_list.append("down")
		for i in range(17):
			self.movement_list.append("left")
		self.movement_list.append("down")

	def determine_move(self):
		direction = self.movement_list[0]
		if direction == 'left':
			self.left()
		elif direction == 'right':
			self.right()
		elif direction == 'up':
			self.up()
		else: 
			self.down()

	def move(self):
		if self.check_wait_time() == "go":
			self.determine_move()

			self.x += self.dx
			self.y += self.dy

			self.shift_moves()
			self.wait_time = 0

	def shift_moves(self):
		self.movement_list.append(self.movement_list[0])
		self.movement_list.pop(0)

	def check_wait_time(self):
		self.wait_time += 1
		if self.wait_time == 20:
			return "go"

	# shooting functions

	def attempt_shot(self):
		if self.randomize() == "go":
			mid_x = self.x + (self.width / 2)
			self.shoot.fire(mid_x, self.y, "alien")

	def randomize(self):
		if random.randrange(self.time_between_shots) == 1:
			return "go"

	def update(self, master_list):
		self.move()
		self.attempt_shot()

class Laser(Master):
	def __init__(self, x, y, origin):
		super(Laser, self).__init__()

		self.height = 15
		self.width = 5
		self.x = x
		self.y = y
		self.dx = 0
		self.dy = 0
		self.movement_speed = 6
		self.aliensource = '/Users/carollin/dev/space_invaders/graphics/greenbeam.jpg'
		self.dudesource = '/Users/carollin/dev/space_invaders/graphics/redbeam.jpg'

		self.determine_type(origin)

		# event handlers
		self.remove = EventHook()
		self.hit = EventHook()
		
	def determine_type(self, origin):
		if origin == "dude":
			self.dy = self.movement_speed * -1
			self.graphic = self.image_convert(self.dudesource, self.width, self.height)
			self.tag = "dude"
		elif origin == "alien":
			self.dy = self.movement_speed * 1
			self.graphic = self.image_convert(self.aliensource, self.width, self.height)
			self.tag = "alien"

	def move(self):
		self.x += self.dx
		self.y += self.dy

	def x_test(self, obj):
		if self.x + self.width >= obj.x and self.x <= obj.x + obj.width:
			return True

	def y_test(self, obj):
		if self.y + self.height >= obj.y and self.y <= obj.y + obj.width:
			return True

	def check_objects(self, master_list):
		for obj in master_list:
			self.check_type(obj)

	def check_type(self, obj):
		if type(obj) is not Laser:
			self.check_boundaries(obj)

	def check_boundaries(self, obj):
		if self.tag != obj.tag:
			if self.x_test(obj) is True and self.y_test(obj) is True:
				self.hit.fire(self)
				self.hit.fire(obj)

	def check_if_active(self):
		if self.y > self.screen_height or self.y < 0:
			self.remove.fire(self)

	def update(self, master_list):
		self.move()
		self.check_if_active()
		self.check_objects(master_list)

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










