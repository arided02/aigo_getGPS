# aigo_getGPS

It's the aigo get gps/time from smart phone via web. The usage is on raspberry pi with astrophotography configuration like AiGo, TinyAstro, AstroHub, AstroBerry, ....
Before install, user need to install 

1. kstars-bleeding: [https://indilib.org/get-indi/download-ubuntu.html](https://indilib.org/get-indi/download-ubuntu.html)
      by indilib.org. 
      
2. EQMODgui :
      [https://sourceforge.net/projects/eqmodgui/](https://sourceforge.net/projects/eqmodgui/) 
      choose *.armhf.deb (32bit OS) or *.arm64.deb (for 64bit OS) file.

**install**

Upload web sync files to /var/www/html

save the aigo_web-getgps.sh in /usr/local/bin

    - cd ~/Download
    - git clone https://github.com/arided02/aigo_getGPS.git
    - cd aigo_getGPS
    - sudo cp aigo_web-getgps.sh /usr/local/bin

    
After all ready, user can use mobile phone to connect astrophography Pi, here I use AiGO to connect

   -- [http://192.168.11.254](http://192.168.11.254)
  
   User can by-passed Chrome's alarm to connect the non-https internal webpage. There are 3 bottoms, one bottom is Sync Mobile phone GPS location.
  
