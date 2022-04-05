from header import *
from handler import ErrorHandler
import rarbg.api as api
from mysql_media import MediaSQL
import sys

handler = ErrorHandler()
def main():

    def fix_season_num(x):
        if x < 0 or x > 99: return ""
        if x < 10: return "0{}".format(x)
        else: return str(x)

    client = api.RarbgAPI()
    db = MediaSQL()
    movie_categories = [api.RarbgAPI.CATEGORY_MOVIE_X264, \
                        api.RarbgAPI.CATEGORY_MOVIE_X264_1080P, \
                        api.RarbgAPI.CATEGORY_MOVIE_X264_720P, \
                        api.RarbgAPI.CATEGORY_MOVIE_X265_1080P]
    series_categories = [api.RarbgAPI.CATEGORY_TV_EPISODES_HD]
    db_data = db.query(db_tb_name, "(rating=0 or rating=5) AND jf_id is NULL")
    db_data = sorted(db_data, key=lambda x: x[2])
    download_num = 0
    with open("movies.magnets", "w") as f_l_m, \
         open("series.magnets", "w") as f_l_s, \
         open("filenames", "w") as f_n:
        for data in db_data:
            f = f_l_s if data[3] == 1 else f_l_m
            fn_prefix = "series" if data[3] == 1 else "movie"
            if data[3] == 0: 
                api_ret = client.search(search_imdb=data[0], categories=movie_categories, sort='last')
            else:
                season_num = fix_season_num(data[4])
                api_ret = client.search(search_string=".S{}.".format(season_num), \
                                        search_imdb=data[5], \
                                        categories=series_categories, \
                                        sort='last')
            if len(api_ret) == 0: handler.notify("No torrent: {}".format(data[0]), critical=False)
            for torrent in api_ret:
                if torrent.leechers == 0 and torrent.seeders < 3: continue
                f_n.write(fn_prefix+"/"+torrent.filename+"\n")
                f.write(torrent.download+"\n")
                download_num += 1
                break
            if download_num == settings['max_downloads']: break
    
if __name__ == "__main__":
    main()