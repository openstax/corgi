#!/bin/bash

export GEOMETRY="$SCREEN_WIDTH""x""$SCREEN_HEIGHT""x""$SCREEN_DEPTH"

if [ -n "$VNC_NO_PASSWORD" ]; then
    echo "starting VNC server without password authentication"
    X11VNC_OPTS=
else
    X11VNC_OPTS=-usepw
fi

xvfb-run --server-args="-screen 0 ""$GEOMETRY"" -ac +extension RANDR" \
   fluxbox -display "$DISPLAY" &
   
rm -f /tmp/.X*lock

for i in $(seq 1 10)
do
  if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
    break
  fi
  echo Waiting xvfb...
  sleep 0.5
done

x11vnc $X11VNC_OPTS -forever -shared -rfbport 5900 -display "$DISPLAY" &

NODE_PID=$!

if [ -z "$@" ]; then
  wait $NODE_PID
else
  exec "$@"
fi
