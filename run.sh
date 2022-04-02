#!/bin/bash -e
export PYTHONIOENCODING=utf-8

python update_db.py
download_dir=`python3 get_magnet_url.py`
aria2c -c -i magnets.txt -d $download_dir -l ariac.log --listen-port=6881 --dht-listen-port=6881
python clean_up.py