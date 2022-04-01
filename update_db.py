from header import *

from douban.api import DoubanData
from mysql_media import MediaSQL
from jellyfin_manager import JellyfinManager

from handler import ErrorHandler
handler = ErrorHandler()
def main():
    db = MediaSQL(db_name=db_name, passwd=db_passwd)
    db.create_tb(db_tb_name, db_cols, db_col_ds, db_col_type)
    db_data = db.query(db_tb_name, 'True ORDER BY update_time ASC')
    last_update_time = 0
    if len(db_data) != 0: last_update_time = db_data[0][-1]

    jellyfin_manager = JellyfinManager(db)
    jellyfin_manager.update()

    douban_data = DoubanData(db, "175139954")
    douban_data.update(last_update_time)
    

if __name__ == "__main__":
    main()