#!/usr/bin/env python3.10

import subprocess

import os

from PIL import Image

import re

import numpy as np

from datetime import datetime

from astropy.io import fits

import sys

import argparse



fitcropX=1.0

fitcropY=1.0

speedPara=1.0

downSample=2 ##default downSample=2

depthStar='11-20'

dt=datetime.now()



def solvCoord(myImage, mydepth, mydownsample):

    depthStar=mydepth

    dt=datetime.now()

    ##run solve-field again

    cmd = f'solve-field --no-plot --scale-low 0.1 --downsample {mydownsample} --depth {mydepth} --overwrite  {myImage}' #resized_img_filename

    output = subprocess.check_output(cmd, shell=True, universal_newlines=True)

    print(output)

    dt2=datetime.now()-dt

    print ("Platesolve time:", dt2)

    # Parse the output to get the RA and Dec coordinates

    ra = None

    dec = None

    for line in output.split('\n'):

   

        if line.startswith('simplexy:'):

            starno=line.split('simplexy: found ')[1].split(' sources.')

            print('simplyxy:',starno,' stars')

        if line.startswith('Field center: (RA,Dec) = ('):

           # ra, dec = re.findall(r"[-+]?(?:\d*\.*\d+)",(line.split(') = (')[1].split(',')))

            ra,dec=line.split(' (RA,Dec) = (')[1].split(',')

            #radd,decdd=line.split(' D:M:S) = (')[1].split(',')

            #radecnp =np.array( re.findall(r"[-+]?(?:\d*\.*\d+)",radec))

            print(ra,dec)

            ra = float(ra)

            dec = float(dec[:-6])

            #print (radd,decdd)

            #radd=radd

            #decdd=decdd[:-2]

        if line.startswith('Field size: '):

           fieldInfo = line.split('Field size: ')[1].split()

           print(fieldInfo)

           #fieldX=float(fieldInfo[0])

           #fieldY=float(fieldInfo[2])



           arcUnit=fieldInfo[3]

           #translate unit to degrees

           if arcUnit=='degrees':

              fieldX=float(fieldInfo[0])

              fieldY=float(fieldInfo[2])

           elif arcUnit[:7]=='arcminu':

              fieldX=float(fieldInfo[0])/60

              fieldY=float(fieldInfo[2])/60

           else:

              fieldX=float(fieldInfo[0])/3600

              fieldY=float(fieldInfo[2])/3600  

             

        if line.startswith('Field rotation angle: '):

           rotateA = line.split(' up is ')[1].split()

           #rotateA=float(rotateA)

           print('rot', rotateA) 

           break

    return (ra, dec, rotateA, fieldX, fieldY, starno)

    

def rawTotiff_resize(myImage, resizeRateX, resizeRateY):

    # Convert the raw image file to FITS format using dcraw

    dt=datetime.now()

    outfitfile=myImage[:-4]+'.fit'

    #os.system(f"rawtran -c R -o {outfitfile} {myImage}")

    os.system(f"dcraw -4 -T -h  {myImage}")

    print("dcraw img conv to tiff:",datetime.now()-dt)

    # Get the name of the FITS file that was created by dcraw

    #fits_image_file = os.path.splitext(myImage)[0] + '.fit'

    fits_image_file = os.path.splitext(myImage)[0] + '.tiff'

    print("t img:",datetime.now()-dt)

    image = Image.open(fits_image_file)

    width,height = image.size

    if (resizeRateX is not None or  resizeRateY is not None): 

      if float(resizeRateX) > 1.0 or float(resizeRateX)< 0.10 or  float(resizeRateY) > 1.0 or float(resizeRateY) < 0.10  :

         resizeRateX=1.0

         resizeRateY=1.0

    else:

      resizeRateX=0.25 ##default resizeset to 0.25

      resizeRateY=0.25     

    resized_img=image.resize((int(width*resizeRateX),int(height*resizeRateY)))

    resized_img_filename=os.path.splitext(myImage)[0] + '_q.jpg'

    resized_img.save(resized_img_filename)

    print("q img:",datetime.now()-dt,resized_img_filename)

    #resized_img3=img.resize((int(width/3),int(height/3)))

    #resized_img3_filename=os.path.splitext(myImage)[0] + '_s.jpg'

    #resized_img3.save(resized_img3_filename)

    outImage=resized_img_filename

    #image = fits.getdata(fits_image_file)

    return (outImage)

    

##for fits crop to reduce image size and solve-field speed.    

def fits_crop(myImage,cropX,cropY):

    ##directly fits translate and crop into 800x800 pixels

    image = fits.getdata(myImage)

  

    height, width = image.shape

    ##crop fits if crop <1.0

    if cropX is not None or cropY is not None:

     if float(cropX) >1.0 or float(cropY)<0.1:

        cropX=1.0

        cropY=1.0

    #default crop=0.5    

    else:

    	cropX=0.5

    	cropY=0.5     	

    # Calculate the coordinates of the center of the image

    center_x = width // 2

    center_y = height // 2

    fitcropXw=int(cropX*width)

    fitcropYh=int(cropY*height)

    # Calculate the coordinates of the top-left corner of the crop

    crop_x = center_x - fitcropXw // 2

    crop_y = center_y - fitcropYh // 2

    # Crop the image

    cropped_image = image[crop_y:crop_y+fitcropXw, crop_x:crop_x+fitcropYh] 

    # Save the cropped image to a new file

    fitcrop2_name = myImage[:-4]+'_crop'  +myImage[-4:]  ##'.tiff'

    print ('\n',datetime.now()-dt,'\t',fitcrop2_name ,'\t',fitcropXw,'x',fitcropYh, ' pixels fits image cropped')

    fits.writeto(fitcrop2_name, cropped_image,overwrite=True)

    outImage=fitcrop2_name

    return (outImage)    

    

#main arg parser for input parameters      

def solvefield_arg_parse():

    ##input args

    #if len(sys.argv)<2:

    #    print("Usage python3 solveLocal2.py <input image (fit/fits/cr2/nef/arw)> for plate-    solve")

    #    sys.exit(1)

    parser = argparse.ArgumentParser(description='input the image, crop ratio and speed parameter')

    #group = parser.add_mutually_exclusive_group()

    parser.add_argument('-c', '--crop', type=float, help='Resize(.raw)/Crop(.fits) factor 0.02(0.1)-1.0 to make sure pixels ~ 800 pixels for shorter solve-field time.(default=1.0)')

    parser.add_argument('-z', '--downsample', type=int, help='downsample parameter in solve-field (defualt=2)')

    parser.add_argument('-d', '--depth', type=str, help='depth sequence of stars in solve-field (default=11-20)')

    #group.add_argument('-s', '--speed', type=int, help='speed for solve-field **test only**')

    parser.add_argument('imagefile', type=str, help='input image filename cr2/nef/fit')

    args = parser.parse_args()

    if args.imagefile =='':

        print("Usage python3 solveLocal6.py -c 1.0 -z 2 <input image (fit/fits/cr2/nef/arw)> for plate-solve.")

        sys.exit(1)

    else:

       raw_image_file=args.imagefile    

    if args.crop is not None:

      if float(args.crop) <= 1.0 and float(args.crop)>=0.02:

        fitcropX=float(args.crop)  ##set the crop ration

        fitcropY=float(args.crop)

    else:  ##default crop=1.0

      fitcropX=1.0

      fitcropY=1.0        

    #elif args.downsample is not None :     

    if args.downsample is not None:

      if int(args.downsample)>1:

        downSample=int(args.downsample)

        print('downSample',downSample)

      else:

        downSample=1  

    else:

      downSample=2

      print(args.crop,args.downsample)      

   #elif args.speed > 1:

   #    speedPara=args.speed

    if args.depth is not None:

      depthStar=args.depth

    else:

      depthStar='11-20'

      ##default nu,ber is 11th to 20th bright stars	

    return(raw_image_file, downSample, fitcropX,fitcropY, depthStar)

        

        

def main():

    dt=datetime.now()

    #input arguments truncation loop

    raw_image_file, downSample, fitcropX, fitcropY, depthStar = solvefield_arg_parse()

 

    ##

    

    # Path to the raw image file

    #raw_image_file = args.imagefile

    verifyRaw=raw_image_file.lower()[-4:]





    print(verifyRaw, downSample, fitcropX, fitcropY, depthStar)

    if verifyRaw == '.cr2' or verifyRaw == '.nef' or verifyRaw=='.arw':

      ##dslr image resize routine it will slower 7-8sec than fits file for convertion.

      outImage=rawTotiff_resize(raw_image_file,fitcropX,fitcropY)



    else:

      ##fits image croped routine

      outImage=fits_crop(raw_image_file,fitcropX,fitcropY)

   

      

  

    dt1=datetime.now()-dt

    print ("image translate", dt1,outImage)

    #depthStar='11-20'

    ra, dec, rotateA, fieldX, fieldY, starno = solvCoord(outImage, depthStar, downSample)



     

    if ra is not None and dec is not None:

        print(f'RA: {ra}, Dec: {dec}')

        print('Field:', fieldX, 'x', fieldY,'degs')

        print('Rotation angle:', rotateA[0])

        #print(f'RA: {radd}, Dec: {decdd}')

    else:

        print('Plate-solving failed.')

    print('star in croped img:',starno[0])



    if starno in (10, 20) : ##smaller 20 star

        depthStar='2-11'

        ra, dec, rotateA, fieldX, fieldY, starno = solvCoord(outImage, depthStar, downSample)



    if ra is not None and dec is not None: 

        print(f'RA: {ra}, Dec: {dec}')

        print('Field:', fieldX, 'x', fieldY,'degs')

        print('Rotation angle:', rotateA[0])

        #print(f'RA: {radd}, Dec: {decdd}')

    else:

        print('Plate-solving failed.')

    print('star a croped img:',starno[0])

    ##printfinal proess time

    dt2=datetime.now()-dt

    print ("Platesolve time:", dt2)







if __name__ == "__main__":

    main()
