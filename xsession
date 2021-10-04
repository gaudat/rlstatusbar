xset s off
xset -dpms
xrandr --newmode "1920x264_60.00"   39.75  1920 1976 2160 2400  264 267 277 280 -hsync +vsync
xrandr --addmode HDMI-1 "1920x264_60.00"
xrandr --output HDMI-1 --mode "1920x264_60.00" --scale 1x0.5
#exec lxterminal --geometry=999x999 -e /home/pi/toilet.sh
#exec lxterminal --geometry=999x999 -e tmux
exec lxsession
unclutter -display :0 -noevents -grab &
#exec chromium-browser --window-position=0,0 --window-size=9999,9999 --kiosk /srv/rlstatusbar/lightning/index.html 
