#!/bin/bash -e
export PYTHONIOENCODING=utf-8

python update_db.py
download_dir=`python3 get_magnet_url.py`
aria2c -c -i magnets_movies.txt -d ${download_dir}/movie -l ariac.log --listen-port=16999 --dht-listen-port=16999 --seed-time=0 --max-overall-upload-limit=1K
aria2c -c -i magnets_series.txt -d ${download_dir}/series -l ariac.log --listen-port=16999 --dht-listen-port=16999 --seed-time=0 --max-overall-upload-limit=1K
python clean_up.py download_dir