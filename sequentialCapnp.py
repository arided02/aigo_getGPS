#!/usr/bin/python3.7
import sys
import time
from tzlocal import get_localzone
#from datetime import time
import picamera
from PIL import Image, ImageOps, ImageFont, ImageDraw
from fractions import Fraction
from time import sleep
import pytz
import array
from wand import image as wi   ##use imagemagick to composite
import numpy as np
import math

dark=36.69623   ##1.004 for picam v1.3 iso800, 1s, 24C   ##36.69623 ##for picam v2.1 noir iso1600, 2.51s, 25C
gpsheight=34.5 #will use gps.txt height
gamma=0.877            #gamma correction V1=AVo**Gamma
normg=math.pow(255,1-gamma) #gamma correction factor A
bortle2=20.0   #for borttle 2 grade magnitude is 20.0
font=ImageFont.truetype("/usr/share/font/truetype/dejavu/DejaVuSans.ttf",32)
picWidth=2440 ##2820
picHeight=2260  ##2464

frames=15
imgTemp=[]

myPicTimeStamp="2"+time.strftime("%Y%m%d_%H%M%S", time.localtime())
def imgFilenames():
    frame=0
    while frame < frames:
        yield myPicTimeStamp+'%02d.jpg' % frame
        imgTemp.append(myPicTimeStamp +'%02d.jpg' % frame)
        frame += 1
#gamma correction function
def gmCo(vi):
    return(float(math.pow(1/normg*vi,1/gamma)))

#saveStackimg=Image.new('RGB', (width+1*frames,height))
with picamera.PiCamera(resolution=(picWidth, picHeight), framerate=Fraction(2,5)) as ncamera:
    ncamera.shutter_speed=2510000
    ncamera.iso=1600
    ncamera.exposure_mode='night'
    ncamera.start_preview()

    time.sleep(0.125)
    start=time.time()
    ncamera.capture_sequence(imgFilenames(), use_video_port=False)
    finish = time.time()
print('Captured %d frames at %.4ffps' %(frames, frames/(finish-start)))
#print ('Total %.3fs',%(finish-start))
#print (imgFilenames)
##start stacking image
print (imgTemp)
images=[Image.open(x) for x in imgFilenames()]
widths, heights= zip(*(i.size for i in images))
#print (i.size)
widthMax=max(widths) ##+1*frames need same width and height
heightMax=max(heights)
print(widthMax, heightMax)
new_image=Image.new('RGB' , (widthMax,heightMax))
ni2=Image.new('RGB', (widthMax, heightMax),0)
mask =[ Image.new("L",(widthMax, heightMax) , 256-(int(255/(m+1))+1)) for m in range(0,frames+1)] ##all black mask use diff waiting
x_offset=0
new_image=images[0]

for im in range(1, frames):  ##images:
    new_image=Image.composite(new_image, images[im], mask[im])
    #print(im)
    ##ni2=new_image.copy()
    #new_image.composite_channel('all_channels',im, 'plus')
    x_offset +=1
newimgFile=myPicTimeStamp+'st.jpg'
new_image.save(newimgFile,quality=100)
mask[frames-1].save(myPicTimeStamp+'mask.jpg',quality=98)

##numpy merge method
'''
imarr=np.array(images) ## # of frames images array....
print (imarr.size)
'''
imgnp=np.array(Image.open(newimgFile))
print ('array shapre',imgnp.shape,'size=',imgnp.nbytes)
k=np.mean(imgnp[int(picWidth/2-128):int(picWidth/2+128),int(picHeight/2-128):int(picHeight/2+128),:])
ks=np.std(imgnp[int(picWidth/2-128):int(picWidth/2+128),int(picHeight/2-128):int(picHeight/2+128),:])
allk=np.mean(imgnp)
gamak=gmCo(k)
gamadark=gmCo(dark)
print (k,ks,allk,gamak,gamadark)
if (gamak < gamadark):
    gamak=gamadark+0.00001

iSQM=bortle2-math.log10(gamak-gamadark)/math.log10(2.512)-1.7  ## -1.7 for picam v1.3 to 2.1 iso from 800 to 1600, exposure time from 1s to 2.51s cal value.
print ("The zenith effectve SQM is %.2f" %iSQM)
iSQMtxt="Zenith iSQM is %.2f" %iSQM
##draw the text of SQM
imgTxt=Image.open(newimgFile)
draw=ImageDraw.Draw(imgTxt)
draw.text((25,picHeight-85),iSQMtxt, (202,234,30), font=font)
imgTxt.save(newimgFile) ##writeback
