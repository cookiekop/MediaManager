db_name = "media"
db_passwd = 
db_tb_name = "media_status"
db_cols = ("imdb_id", "rating", "is_series", "jf_id", "update_time")
db_col_ds = ("VARCHAR(20)", "INT", "INT", "VARCHAR(100)", "INT")
db_col_type = ("PRIMARY KEY", "NOT NULL", "NOT NULL", "", "NOT NULL")
retries = 100
max_downloads = 1
download_dir = 
media_ext = ["mp4", "mkv"]

proxies = {'http': '',
           'https': ''}