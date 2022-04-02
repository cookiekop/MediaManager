from header import *
from handler import ErrorHandler
import rarbg.api as api
from mysql_media import MediaSQL
import sys

handler = ErrorHandler()
def main():

    client = api.RarbgAPI(options={'retries': 1})
    db = MediaSQL()
    movie_categories = [api.RarbgAPI.CATEGORY_MOVIE_X264, \
                        api.RarbgAPI.CATEGORY_MOVIE_X264_1080P, \
                        api.RarbgAPI.CATEGORY_MOVIE_X264_720P, \
                        api.RarbgAPI.CATEGORY_MOVIE_X265_1080P]
    series_categories = [api.RarbgAPI.CATEGORY_TV_EPISODES_HD]
    db_data = db.query(db_tb_name, "(rating=0 OR rating=5) AND jf_id is NULL AND is_series=0")[:max_downloads]
    with open("magnets_movies.txt", "w") as f_l_m, \
         open("magnets_series.txt", "w") as f_l_s, \
         open("filenames.txt", "w") as f_n:
        for data in db_data:
            category = series_categories if data[2] == 1 else movie_categories
            f = f_l_s if data[2] == 1 else f_l_m
            fn_prefix = "series" if data[2] == 1 else "movies"
            for retry in range(retries):
                api_ret = client.search(search_imdb=data[0], categories=category, sort='last')
                if len(api_ret) > 0: 
                    f_n.write(fn_prefix+"/"+api_ret[0].filename+"\n")
                    f.write(api_ret[0].download+"\n")
                    break
                if (retry == retries - 1): handler.notify("RARBG Max Retries")
    print(download_dir)
    

if __name__ == "__main__":
    main()