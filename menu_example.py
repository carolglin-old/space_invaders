class Animation(pg.sprite.Sprite):
    def __init__(self, screen, SpriteStripAnim, num_sprites):
        pg.sprite.Sprite.__init__(self)

        self.strip = SpriteStripAnim
        self.num = num_sprites
        self.rect = self.strip.rect
        self.screen = screen 

        self.remove = EventHook()

        self.strip.iter()
        self.image = self.strip.next()
        print(self.image)

    def update(self):
        self.num -= 1
        if self.num == 0:
            self.remove.fire(self)
        self.image = self.strip.next()

class SpriteStripAnim(object):
    def __init__(self, x, y, width, height, filename, rect, count, colorkey=None, loop=False, frames=1):
        self.filename = filename
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.ss = Spritesheet(filename, self.x, self.y, self.width, self.height)
        self.rect = rect
        self.num_sprites = count
        self.images = self.ss.load_strip(self.rect, self.num_sprites, colorkey)
        self.i = 0
        self.loop = loop
        self.frames = frames
        self.f = frames

    def iter(self):
        self.i = 0
        self.f = self.frames
        return self

    def next(self):
        if self.i < self.num_sprites:
        # if self.i >= len(self.images):
            # if not self.loop:
            #     raise StopIteration
            # else:
            #     self.i = 0
            image = self.images[self.i]
            self.f -= 1
            if self.f == 0:
                self.i += 1
                self.f = self.frames
            else:
                self.i += 1
            return image

    def __add__(self, ss):
        self.images.extend(ss.images)
        return self

class Spritesheet(CanvasObjects):
    def __init__(self, filename, x, y, width, height):
        CanvasObjects.__init__(self)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        try:
            self.sheet = self.open_resize_img(filename, self.width, self.height)
        except pg.error, message:
            print 'Unable to load spritesheet image:', filename
            raise SystemExit, message

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        "Loads image from x,y,x+offset,y+offset"
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), area = rect)

        # if colorkey is not None:
        #     if colorkey is -1:
        #         colorkey = image.get_at((0,0))
        #     image.set_colorkey(colorkey, pg.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)


        