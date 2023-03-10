import numpy as np
import sys

aoa = 0.
xcol = 0
ycol = 1
try:
    aoa = float(input("Please specify angle of attack (degrees): "))
except:
    print(f"Could not read angle of attack. Falling back to default ({aoa}).")
    
upper = [[], [], []]#x, y, cf
lower = [[], [], []]#x, y, cf

tg = np.tan(-aoa*np.pi/180.)

if(len(sys.argv)>1):
    filename = sys.argv[1]
else:
    filename = input("Please specify file to be sorted:\n")

try:
    xcol = int(input("Please specify x column index: "))
except:
    print(f"Could not read angle of attack. Falling back to default ({xcol}).")
    
try:
    ycol = int(input("Please specify y column index: "))
except:
    print(f"Could not read angle of attack. Falling back to default ({ycol}).")

file = open(filename, "r")
header = []
upperfile = open(".".join(filename.split(".")[:-1])+"_upper."+filename.split(".")[-1], "w")
lowerfile = open(".".join(filename.split(".")[:-1])+"_lower."+filename.split(".")[-1], "w")
for line in file:
    ll = line.split(" ")
    try:
        x = float(ll[xcol])
    except:
        for i in range(len(ll)):
            upperfile.write(ll[i])
            lowerfile.write(ll[i])
            if(i<len(ll)-1):
                upperfile.write(" ")
                lowerfile.write(" ")
        continue
    y = float(ll[ycol])
    if(y<x*tg):
        for i in range(len(ll)):
            lowerfile.write(ll[i])
            if(i<len(ll)-1):
                lowerfile.write(" ")
    else:
        for i in range(len(ll)):
            upperfile.write(ll[i])
            if(i<len(ll)-1):
                upperfile.write(" ")
upperfile.close()
lowerfile.close()
    