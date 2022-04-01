#!/bin/bash -e

python3 update_db.py
download_dir=`python3 get_magnet_url.py`
aria2c -i magnets.txt -d $download_dir -l ariac.log
python3 clean_up.py