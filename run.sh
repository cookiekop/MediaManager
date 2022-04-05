#!/bin/bash -e
export PYTHONIOENCODING=utf-8

get_from_settings() {
    python3 -c "from header import *;print(settings[$1])"
}
DOWNLOAD_DIR=`get_from_settings \'download_dir\'`
TRANSMISSION_HOST=`get_from_settings \'transmission_host\'`
TRANSMISSION_AUTH=`get_from_settings \'transmission_auth\'`

python3 update_db.py
python3 get_magnet_url.py
while read line 
do 
    transmission-remote $TRANSMISSION_HOST --auth=$TRANSMISSION_AUTH --download_dir ${DOWNLOAD_DIR}/movie -a $line
done < movie.magnets

while read line 
do 
    transmission-remote $TRANSMISSION_HOST --auth=$TRANSMISSION_AUTH --download_dir ${DOWNLOAD_DIR}/series -a $line
done < series.magnets