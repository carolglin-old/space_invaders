import pygame,sys
from pygame.locals import *


pygame.init()

done = True

screen = pygame.display.set_mode((200, 200))

def sprite_sheet(size,file,pos=(0,0)):

    #Initial Values
    len_sprt_x,len_sprt_y = size #sprite size
    sprt_rect_x,sprt_rect_y = pos #where to find first sprite on sheet

    sheet = pygame.image.load(file).convert_alpha() #Load the sheet
    sheet_rect = sheet.get_rect()
    sprites = []
    print sheet_rect.height, sheet_rect.width
    for i in range(0,sheet_rect.height-len_sprt_y,size[1]):#rows
        print "row"
        for i in range(0,sheet_rect.width-len_sprt_x,size[0]):#columns
            print "column"
            sheet.set_clip(pygame.Rect(sprt_rect_x, sprt_rect_y, len_sprt_x, len_sprt_y)) #find sprite you want
            sprite = sheet.subsurface(sheet.get_clip()) #grab the sprite you want
            sprites.append(sprite)
            sprt_rect_x += len_sprt_x

        sprt_rect_y += len_sprt_y
        sprt_rect_x = 0
    print sprites
    return sprites

sprite_source = '/Users/carollin/Dev/space_invaders/graphics/dudeexplosion.png'
sprite_list = sprite_sheet((51, 128), sprite_source)
print(sprite_list)

# index = 0

# while done is True:
#     screen.blit(sprite_list[index])
#     pygame.display.update()
#     index += 1
#     if index < 20:
#         index = 0