from tkinter import Frame, Tk, Label, Button
from PIL import Image, ImageTk, ImageFilter

class Application(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		master.wm_title("Image examples")
		self.pack()
		self.createWidgets()

	def createWidgets(self):
		self.img = Image.open('/Users/carollin/Dev/space_invaders/graphics/dude.png')
		self.photo1 = ImageTk.PhotoImage(self.img.convert("RGB"))
		self.label1 = Label(self, image=self.photo1)
		self.label1.grid(row=0, column=0)

		self.photo2 = ImageTk.PhotoImage(self.img.convert("RGB"))
		self.label2 = Label(self, image=self.photo2)
		self.label2.grid(row=0, column=1)

		button = Button(self, text="Brighten", command=self.brighten)
		button.grid(row=0, column=2)

	def brighten(self):
		img2 = self.img.point(lambda p: p * 0.3)
		# img2.show()
		self.photo2 = ImageTk.PhotoImage(img2)
		self.label2 = Label(self, image=self.photo2)
		self.label2.grid(row=0, column=1)

root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()