#
# run this script to build server on Orange Pi Zero Plus(2)
#
# hankso
# email: 3080863354@qq.com
# page: https://github.com/hankso
#


if (( $EUID != 0  )); then
    echo "run as root please"
    exit
fi


#
# config apache2
#
# Apache2 is used to host server and load python bottle programs to generate
# dynamic html for clients(user's web browser)
#

# sites conf
SITE=/etc/apache2/sites-available/000-default.conf
mv $SITE $SITE.$(date +"%Y%m%d")
cp 0-sites.conf $SITE

# server files
mkdir -p /var/www/pyemg
cp src/* /var/www/pyemg/

# other configs
a2enmod macro
service apache2 restart



#
# config interface
#
# service networking interface set wlan0 static ip 
INTF=/etc/network/interfaces
mv $INTF $INTF.$(date +"%Y%m%d")
cp 1-interfaces $INTF
service networking restart
# ifdown wlan0 && ifup wlan0



#
# config hostapd
#
# Hostapd will turn WiFi chip into AP(Access Point) mode, thus you can
# find this available hotspot on your PC/mobile devices.
#

# hostapd.conf
HOSTAPD=/etc/hostapd.conf
mv $HOSTAPD $HOSTAPD.$(date +"%Y%m%d")
cp 2-hostapd.conf $HOSTAPD
# echo 'DAEMON_CONF="/etc/hostapd.conf"' > /etc/default/hostapd
service hostapd restart



#
# config dnsmasq
#
# Dnsmasq provide DHCP and FTP service, DHCP can automatically select 
# and distribute an IP address to devices that connect to this WiFi 
# hotspot, unless they are set to a static IP manually
#
DNS=/etc/dnsmasq.conf
mv $DNS $DNS.$(date +"%Y%m%d")
cp 5-dnsmasq.conf $DNS
# echo 'DNSMASQ_OPTS="--conf-file=/etc/dnsmasq.conf"' >> /etc/default/dnsmasq
service dnsmasq restart



echo "All configuration done!"
