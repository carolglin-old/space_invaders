from tkinter import *
from PIL import Image, ImageTk, ImageDraw

class Test:
	def __init__(self):
		w = Tk()

		self.source = '/Users/carollin/Dev/space_invaders/graphics/alien1.png'

		self.width = 800
		self.height = 550
		frame = Frame()

		self.canvas = Canvas(w, width = self.width, height = self.height, background = "black")
		self.canvas.pack(expand = YES, fill = BOTH)

		self.graphic = self.image_convert(self.source, self.width, self.height)

		self.canvas.create_image(0, 0, image = self.graphic, anchor = NW)

		w.mainloop()

	def image_convert(self, imagepath, width, height):
		size = width, height
		graphic = Image.open(imagepath)
		graphic.thumbnail(size, Image.ANTIALIAS)
		resized = ImageTk.PhotoImage(graphic)
		return resized


		# def main(self):
		# 	# Open the original image
		# 	main = Image.open("/Users/carollin/Dev/space_invaders/graphics/dude.png")

		# 	# Create a new image for the watermark with an alpha layer (RGBA)
		# 	#  the same size as the original image
		# 	watermark = Image.new("RGBA", main.size)
		# 	# Get an ImageDraw object so we can draw on the image
		# 	waterdraw = ImageDraw.ImageDraw(watermark, "RGBA")
		# 	# Place the text at (10, 10) in the upper left corner. Text will be white.
		# 	waterdraw.text((10, 10), "The Image Project")

		# 	# Get the watermark image as grayscale and fade the image
		# 	# See <http://www.pythonware.com/library/pil/handbook/image.htm#Image.point>
		# 	#  for information on the point() function
		# 	# Note that the second parameter we give to the min function determines
		# 	#  how faded the image will be. That number is in the range [0, 256],
		# 	#  where 0 is black and 256 is white. A good value for fading our white
		# 	#  text is in the range [100, 200].
		# 	watermask = watermark.convert("L").point(lambda x: min(x, 100))
		# 	# Apply this mask to the watermark image, using the alpha filter to 
		# 	#  make it transparent
		# 	watermark.putalpha(watermask)

		# 	# Paste the watermark (with alpha layer) onto the original image and save it
		# 	main.paste(watermark, None, watermark)
			

Test()



