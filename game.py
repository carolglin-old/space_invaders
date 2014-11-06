import pygame as pg
import time
import pdb

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

class LevelManager(CanvasObjects, pg.sprite.Sprite):
	def __init__(self):
		super().__init__()

class Game(CanvasObjects, pg.sprite.Sprite):
	def __init__(self):
		super().__init__()

		pg.init()

		self.size = (SCREEN_WIDTH, SCREEN_HEIGHT)
		self.screen = pg.display.set_mode(self.size)
		self.caption = '<(^.^<) Space Invaders! (>O.O)>'

		pg.display.set_caption(self.caption)

		self.isStopped = False

		self.clock = pg.time.Clock()
		self.sleepTime = 100

		self.bg_file = '/Users/carollin/Dev/space_invaders/graphics/background.png'

		self.background = self.open_resize_img(self.bg_file, SCREEN_WIDTH, SCREEN_HEIGHT)
		self.screen.blit(self.background, [0, 0])

		self.alien_list = pg.sprite.Group()	
		self.laser_list = pg.sprite.Group()
		self.barrier_list = pg.sprite.Group()

		self.update_list = pg.sprite.Group()

		self.start()

	def start(self):
		self.dude = Dude()
		self.update_list.add(self.dude)
		self.mainloop()

	def mainloop(self):
		while self.isStopped is False:

			self.keypress_listener()
			self.update_model()
			self.refresh_view()

			self.clock.tick(self.sleepTime)

	def keypress_listener(self):
		for event in pg.event.get():
			keys = pg.key.get_pressed()
			if keys[pg.K_a]:
				self.dude.left()
			if keys[pg.K_d]:
				self.dude.right()
			if event.type == pg.QUIT or keys[pg.K_ESCAPE]:
				self.isStopped = True

	def update_model(self): 
		for obj in self.update_list:
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

		self.shooting = False

	def left(self):
		self.dx = self.movement_speed * -1

	def right(self):
		self.dx = self.movement_speed

	def reset_movement(self, event):
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

	def update(self):
		self.movement()
		self.move_rect()

class Alien(GameObjects, pg.sprite.Sprite):
	def __init__(self, **kwargs):
		GameObjects.__init__(self, kwargs['width'], kwargs['height'], kwargs['graphic'])
		pg.sprite.Sprite.__init__(self)

		self.x = kwargs['x']
		self.y = kwargs['y']
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

	def update(self):
		self.movement()
		self.move_rect()

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


