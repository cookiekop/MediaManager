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
    transmission-remote $TRANSMISSION_HOST --auth=$TRANSMISSION_AUTH --download-dir ${DOWNLOAD_DIR}/movie --dht --port 16999 -a $line
done < movies.magnets

while read line 
do 
    transmission-remote $TRANSMISSION_HOST --auth=$TRANSMISSION_AUTH --download-dir ${DOWNLOAD_DIR}/series --dht --port 16999 -a $line
done < series.magnets