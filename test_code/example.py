import pygame as pg

class Test:
	def __init__(self):
		pg.init()
		self.img = '/Users/carollin/Dev/space_invaders/graphics/alien1.png'

		self.isStopped = False

		self.size = (800, 550)
		self.screen = pg.display.set_mode(self.size)
		self.caption = '<(^.^<) Space Invaders! (>O.O)>'

		pg.display.set_caption(self.caption)

		self.bg_file = '/Users/carollin/Dev/space_invaders/graphics/background.png'

		self.background = self.open_resize_img(self.bg_file, 800, 550)
		self.screen.blit(self.background, [0, 0])
		pg.display.update()

		self.normal = self.open_resize_img(self.img, 30, 30)

		self.mainloop()

	def mainloop(self):
		while self.isStopped is False:
			self.screen.blit(self.background, [0, 0])
			self.screen.blit(self.normal, [10, 10])
			self.blit_alpha(self.screen, self.normal, (50, 10), 100)
			pg.display.update()

	def open_resize_img(self, img_source, width, height):
		graphic = pg.image.load(img_source).convert_alpha()
		graphic = pg.transform.scale(graphic, (width, height))
		return graphic

	def blit_alpha(self, target, source, location, opacity):
		x = location[0]
		y = location[1]
		temp = pg.Surface((source.get_width(), source.get_height())).convert()
		temp.blit(target, (-x, -y))
		temp.blit(source, (0, 0))
		temp.set_alpha(opacity)
		target.blit(temp, location)

Test()


