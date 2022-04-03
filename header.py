db_host = "localhost"
db_name = "media"
db_user = "root"
db_passwd = ""
db_tb_name = "media_status"
db_cols = (    "imdb_id",     "douban_id",   "rating",   "is_series", "season_num", "serie_imdb_id", "jf_id",        "update_time")
db_col_ds = (  "VARCHAR(20)", "VARCHAR(20)", "INT",      "INT",       "INT",        "VARCHAR(20)",   "VARCHAR(100)", "INT")
db_col_type = ("PRIMARY KEY", "UNIQUE",      "NOT NULL", "NOT NULL",  "",           "",              "NOT NULL",     "NOT NULL")
retries = 100
max_downloads = 1
download_dir = ""
media_ext = ["mp4", "mkv"]

proxies = {}