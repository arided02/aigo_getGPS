#!/bin/bash
KSTARSCFGDIR=/home/aigo/.config/
EQMODCFGDIR=/home/aigo/.config/eqmodgui
SKYCHARTCFGDIR=/home/aigo/.skychart

LON=$1
LAT=$2
ALT=$3
TS=$4
TZ=`date +%:::z`

GPSFILE=/home/aigo/gps.txt
echo "lon="$LON > $GPSFILE
echo "lat="$LAT >> $GPSFILE
echo "alt="$ALT >> $GPSFILE
echo "tm="$TS   >> $GPSFILE
echo "tz="$TZ   >> $GPSFILE

chown aigo.aigo $GPSFILE
chmod 644 $GPSFILE
## update kstarsrc by tls 211030 ###
#backup
cp $KSTARSCFGDIR/kstarsrc $KSTARSCFGDIR/kstarsrc.aigobak
KSLAT=`awk '/Latitude=/{print $1}' $KSTARSCFGDIR/kstarsrc`
KSLON=`awk '/Longitude=/{print $1}' $KSTARSCFGDIR/kstarsrc`
KSALT=`awk '/Elevation=/{print $1}' $KSTARSCFGDIR/kstarsrc`
KSTZ=`awk '/TimeZone=/{print $1}' $KSTARSCFGDIR/kstarsrc`
#echo $KSLAT, $KSLON, $KSALT, $KSTZ
#sed 's/$KSLAT
KSLARPL=$KSLAT
KSLORPL=$KSLON
KSALRPL=$KSALT
KSTZRPL=$KSTZ
#echo $KSLARPL
printf -v KSLARPL "s/%s/Latitude=%s/1" $KSLAT $2
printf -v KSLORPL "s/%s/Longitude=%s/1" $KSLON $1
printf -v KSALRPL "s/%s/Elevation=%s/1" $KSALT $3
printf -v KSTZRPL "s/%s/TimeZone=%s/1" $KSTZ $TZ
echo $KSLARPL ,$KSLORPL,$KSTZRPL,$KSALRPL
sed -i $KSLARPL $KSTARSCFGDIR/kstarsrc
sed -i $KSLORPL $KSTARSCFGDIR/kstarsrc
sed -i $KSALRPL $KSTARSCFGDIR/kstarsrc
sed -i $KSTZRPL $KSTARSCFGDIR/kstarsrc #temperal rls...211031...

#### eqmod cfg ####
#backup cfg file
cp $EQMODCFGDIR/eqmodgui.cfg $EQMODCFGDIR/eqmodgui.cfg.aigobak
SYNCLOC=`awk '/<Site1 /{print $1}' $EQMODCFGDIR/eqmodgui.cfg`
EQLAT=`awk '/Latitude=/{print $2}' $EQMODCFGDIR/eqmodgui.cfg`
EQLON=`awk '/Longitude=/{print $5}' $EQMODCFGDIR/eqmodgui.cfg`
EQALT=`awk '/Elevation=/{print $4}' $EQMODCFGDIR/eqmodgui.cfg`
echo $SYNCLOC, $EQLAT, $EQLON, $EQALT
printf -v EQLATRPL "s|%s|Latitude=\"%s\"|1" $EQLAT $2
printf -v EQLONRPL "s|%s|Longitude=\"%s\"|1" $EQLON $1   ##update sed separator from / to | in html format cfg file.
printf -v EQALTRPL "s|%s|Elevation=\"%s\"|1" $EQALT $3
echo $EQLATRPL, $EQLONRPL, $EQALTRPL
sed -i $EQLATRPL $EQMODCFGDIR/eqmodgui.cfg
sed -i $EQLONRPL $EQMODCFGDIR/eqmodgui.cfg
sed -i $EQALTRPL $EQMODCFGDIR/eqmodgui.cfg

### skychart location cfg ###
#backup ini file
cp $SKYCHARTCFGDIR/skychart.ini $SKYCHARTCFGDIR/skychart.ini.aigobak
SKLAT=`awk '/ObsLatitude=/{print $1}' $SKYCHARTCFGDIR/skychart.ini`
SKLON=`awk '/ObsLongitude=/{print $1}' $SKYCHARTCFGDIR/skychart.ini`
SKALT=`awk '/ObsAltitude=/{print $1}' $SKYCHARTCFGDIR/skychart.ini`
echo $SKLAT, $SKLON, $SKALT
SKLONNEG=$(echo "-1.0 * $1" | bc) ##change to neg sign in E is negative in carte du ciel skychart
#SKLONNEG=`expr -1.0 \* $1 |bc`
echo "skycharti negative longitude", $SKLONNEG
printf -v SKLATRPL "s|%s|ObsLatitude=%s|1" $SKLAT $2
printf -v SKLONRPL "s|%s|ObsLongitude=%s|1" $SKLON $SKLONNEG
printf -v SKALTRPL "s|%s|ObsAltitude=%s|1" $SKALT $3
echo $SKLATRPL, $SKLONRPL, $SKALTRPL
sed -i $SKLATRPL $SKYCHARTCFGDIR/skychart.ini
sed -i $SKLONRPL $SKYCHARTCFGDIR/skychart.ini
sed -i $SKALTRPL $SKYCHARTCFGDIR/skychart.ini

