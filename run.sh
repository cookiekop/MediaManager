#!/bin/bash -e
export PYTHONIOENCODING=utf-8

get_from_settings() {
    python3 -c "from header import *;print(settings[$1])"
}

python3 update_db.py
# python3 get_magnet_url.py
# python3 aria2_download.py