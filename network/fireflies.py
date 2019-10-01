from tkinter import *
import random
import time
import math
from collections import namedtuple

Firefly = namedtuple("Firefly", "x y glow")
Veloc   = namedtuple("Veloc", "x y")

WIDTH = 1000
HEIGHT = 800
FLIES = 200
R = 4
THRESHOLD = 0.92
BUMP = 0.001
DELTA = 0.05
TAU = 0.7

root = Tk()
canvas = Canvas(root, width=WIDTH, height=HEIGHT, bg='black')
canvas.pack()

flies = []
veloc = []
for f in range(FLIES):
    x = random.uniform(R, WIDTH-R)
    y = random.uniform(R, HEIGHT-R)
    glow = random.random()
    hex_value = hex(int(16*glow))[2]
    color = "#" + hex_value*4 + "33"
    canvas.create_oval(x-R, y-R, x+R, y+R, fill=color)
    f = Firefly(x, y, glow)
    flies.append(f)
    speed = random.random()
    direction = random.uniform(0, 2*math.pi)
    veloc.append(Veloc(speed*math.cos(direction), speed*math.sin(direction)))

root.update()
while True:
    bumps = 0
    for e, f in enumerate(flies):
        x, y, glow = f.x, f.y, f.glow
        v = veloc[e]

        speed = random.random()
        direction = random.uniform(0, 2*math.pi)
        vx = v.x + speed*math.cos(direction)
        vy = v.y + speed*math.sin(direction)
        x += vx
        y += vy
        if x <= R: x, vx = R, 0.8*abs(vx)
        if x >= WIDTH-R: x, vx = WIDTH-R, -0.8*abs(vx)
        if y <= R: y, vy = R, 0.8*abs(vy)
        if y >= HEIGHT-R: y, vy = HEIGHT-R, -0.8*abs(vy)
        veloc[e] = Veloc(vx*0.9, vy*0.9)

        glow +=  DELTA * (1-glow)/TAU
        if glow > THRESHOLD: bumps += 1
        flies[e] = Firefly(x, y, glow)
    while bumps > 0:
        past_bumps, bumps = bumps, 0
        for e, f in enumerate(flies):
            glow = f.glow
            if glow > THRESHOLD:
                glow = 0.01
            else:
                glow += BUMP*past_bumps
                if glow > THRESHOLD: bumps += 1
            flies[e] = Firefly(f.x, f.y, glow)
    canvas.delete("all")
    for f in flies:
        hex_value = hex(int(16*f.glow))[2]
        color = "#" + hex_value*4 + "33"
        canvas.create_oval(f.x-R, f.y-R, f.x+R, f.y+R, fill=color)
    root.update()
    time.sleep(DELTA)


root.mainloop()
