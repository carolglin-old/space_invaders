from tkinter import *
from PIL import Image, ImageTk

class CanvasObjects:
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

class GameObjects(CanvasObjects):
	def __init__(self, width, height, source):
		super().__init__()
		self.width = width
		self.height = height
		self.source = source

		self.create = EventHook()
		self.remove = EventHook()

		self.graphic = self.image_convert(self.source, self.width, self.height)

		self.tag = "game_object"

	def wait_time(self, fire_time, wait_time):
		if time.clock() > fire_time + wait_time:
			return True

	def hit(self, laser):
		self.remove.fire(self)

class Master(CanvasObjects):
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

		self.create_start_button()

		w.mainloop()

	def create_start_button(self):
		self.canvas.focus_set()
		self.canvas.create_window(self.screen_width / 2, self.screen_height / 2, window = self.start_button, tags = "start")

	def start(self):
		self.isStopped = False
		self.canvas.delete("start")
		self.dude = Dude(self.canvas)
		self.add_to_update_list(self.dude)
		self.mainloop()

	def add_to_update_list(self, obj):
		self.update_list.append(obj)
		obj.remove += self.remove_object
		if hasattr(obj, "create"):
			obj.create += self.add_to_update_list

	def remove_object(self, obj):
		if obj in self.update_list:
			self.update_list.remove(obj)

	def mainloop(self):
		while not self.isStopped:
			self.canvas.after(self.sleepTime)
			self.update_model()
			self.refresh_view()

	def update_model(self):
		for i in self.update_list:
			i.update()

	def refresh_view(self):
		self.canvas.delete("game_object")
		for obj in self.update_list:
			self.draw(self.canvas, obj.x, obj.y, obj.graphic, obj.tag)

		self.canvas.update()

	def updateimage(self, sprite):
		self.canvas.delete(self.last_img)
		self.last_img = self.canvas.create_image(self.size, 128, image=self.images[sprite])
		self.canvas.after(100, self.updateimage, (sprite+1) % self.num_sprites)

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

class Dude(GameObjects):
	def __init__(self, canvas): 
		super().__init__(30, 30, '/Users/carollin/Dev/space_invaders/graphics/dude.png')

		self.x = self.screen_width / 2
		self.y = self.screen_height - 5
		self.dx = 0
		self.dy = 0

		self.movement_speed = 5

		self.c = canvas

		self.c.focus_set()
		self.c.bind("a", self.left)
		self.c.bind("d", self.right)
		self.c.bind("<space>", self.animate)
		self.c.bind("<KeyRelease-a>", self.reset_movement)
		self.c.bind("<KeyRelease-d>", self.reset_movement)
		self.c.pack()

		self.animation_graphic = '/Users/carollin/Dev/space_invaders/graphics/explosion.png'
		self.animation_width = 1024
		self.animation_height = 128
		self.num_sprites = 20

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

	def animate(self, event):
		a = Animation(self.x, self.y, self.animation_width, self.animation_height, self.animation_graphic, self.num_sprites)
		self.create.fire(a)

	def update(self):
		self.movement()

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

M = Master()
