#!/bin/bash -e
export PYTHONIOENCODING=utf-8

get_download_dir() {
    python3 -c "from header import *;print(settings['download_dir'])"
}
DOWNLOAD_DIR=`get_download_dir`

python update_db.py
python get_magnet_url.py
aria2c -c -i magnets_movies.txt -d ${DOWNLOAD_DIR}/movie -l ariac.log --listen-port=16999 --dht-listen-port=16999 --seed-time=0 --max-overall-upload-limit=1K
aria2c -c -i magnets_series.txt -d ${DOWNLOAD_DIR}/series -l ariac.log --listen-port=16999 --dht-listen-port=16999 --seed-time=0 --max-overall-upload-limit=1K
python clean_up.py download_dir