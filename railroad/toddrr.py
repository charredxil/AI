from math import pi , acos , sin , cos
from collections import defaultdict
from tkinter import *
import time
def calcd(y1,x1, y2,x2):
   #
   # y1 = lat1, x1 = long1
   # y2 = lat2, x2 = long2
   # all assumed to be in decimal degrees

   # if (and only if) the input is strings
   # use the following conversions

   #y1  = float(y1)
   #x1  = float(x1)
   #y2  = float(y2)
   #x2  = float(x2)
   #R   = 3958.76 # miles 
   R = 6371 # km
   y1 *= pi/180.0
   x1 *= pi/180.0
   y2 *= pi/180.0
   x2 *= pi/180.0
   # approximate great circle distance with law of cosines
   return acos( sin(y1)*sin(y2) + cos(y1)*cos(y2)*cos(x2-x1) ) * R

start = time.time()
nodestxt = open("rnodes.txt", 'r')
edgestxt = open("redges.txt", 'r')
citytxt = open("rnames.txt", 'r')
summ = 0
nodes = [line.strip() for line in nodestxt]
edges = [line.strip() for line in edgestxt]
names = [line.strip() for line in citytxt]
nodedict = {}
edgedict = defaultdict(list)
costdict = {}
mGui = Tk()
canvas = Canvas(mGui,height=500,width=1000,bg="white")
for x in nodes:
	spl = x.split()
	nodedict[spl[0]] = (float(spl[1]), float(spl[2]))
for e in edges:
	sp = e.split()
	edgedict[sp[0]].append(sp[1])
	edgedict[sp[1]].append(sp[0])
	y1 = nodedict[sp[0]][0]
	x1 = nodedict[sp[0]][1]
	y2 = nodedict[sp[1]][0]
	x2 = nodedict[sp[1]][1]
	canvas.create_line((x1-20)*50,500-(y1-40)*50,(x2-20)*50,500-(y2-40)*50)
	costdict[(sp[0], sp[1])] = calcd(y1,x1,y2,x2)
	costdict[(sp[1], sp[0])] = calcd(y1,x1,y2,x2)
	summ = summ + calcd(y1,x1,y2,x2)
    
canvas.pack()
print(edgedict)
print("Distance is: " + str(summ) + " kilometers")
print("Time: " + str(time.time()-start) + " seconds")
mainloop()
	
	




