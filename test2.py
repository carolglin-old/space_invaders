''' tk_pg_playmusic2.py
play a sound file with Tkinter using the module pygame
works with .wav .ogg .mid or .mp3 sound/music files
tested with Python27/Python33 and PyGame192
'''
import pygame as pg
from functools import partial
import tkinter as tk

def pg_play_music(music_file, volume=0.8):
    """
    stream music with mixer.music module in blocking manner
    this will stream the sound from disk while playing
    """
    # set up the mixer
    freq = 44100     # audio CD quality
    bitsize = -16    # unsigned 16 bit
    channels = 2     # 1 is mono, 2 is stereo
    buffer = 2048    # number of samples (experiment for good sound)
    pg.mixer.init(freq, bitsize, channels, buffer)
    pg.mixer.music.set_volume(volume)
    clock = pg.time.Clock()
    try:
        pg.mixer.music.load(music_file)
        print("Playing file %s" % music_file)
    except pg.error:
        print("File %s not found! (%s)" % \
            (music_file, pg.get_error()))
        return
    pg.mixer.music.play()
    # check if playback has finished
    while pg.mixer.music.get_busy():
        clock.tick(30)

root = tk.Tk()
# use width x height + x_offset + y_offset (no spaces!)
root.geometry("250x50+50+30")
root['bg'] = 'green'
# pick .wav .ogg .mid or .mp3 music/sound files you have in
# the working folder, otherwise give the full file path
#sound_file = "OhLaLa.mid"
sound_file = '/Users/carollin/Dev/space_invaders/sounds/barrierexplosion.ogg'
root.title(sound_file)
# set volume from 0 to 1.0
volume = 0.9
btn_text = "Play " + sound_file
cmd = partial(pg_play_music, sound_file, volume)
btn = tk.Button(root, text=btn_text, command=cmd)
btn.pack(padx=30, pady=5)
root.mainloop()