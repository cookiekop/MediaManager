from xml.sax import handler
from jellyfin.jellyfin_client import ClientManager
from handler import ErrorHandler
from header import *
import time

handler = ErrorHandler()
class JellyfinManager:
    def __init__(self, db):
        self._client_manager = ClientManager()
        self._db = db
        
    def update(self):
        self._client_manager.cli_connect()
        jf_client = list(self._client_manager.clients.values())[0]
        media_folders = jf_client.jellyfin.get_media_folders()['Items']
        def update_jf_data(item, is_series=False):
            item_imdb_id = item.get('ProviderIds', {}).get('Imdb', None)
            if item_imdb_id is None: 
                handler.notify('No IMDb ID: {}'.format(item['Name']), critical=False)
                return
            if not is_series:
                self._db.insert(db_tb_name, db_cols, (item_imdb_id, None, 0, 0, None, None, item['Id'], None))
                self._db.update(db_tb_name, 'jf_id', item['Id'], 'imdb_id', item_imdb_id, None)
            else:
                serie_imdb_id = item_imdb_id
                seasons = jf_client.jellyfin.get_provider_info(parent_id=item['Id'])['Items']
                print(item['Name'])
                for season in seasons:
                    season_num = season['Name'].strip().split(' ')[-1]
                    if season_num == '1':
                        self._db.insert(db_tb_name, db_cols, (serie_imdb_id, None, 0, 1, None, None, season['Id'], None))
                        self._db.update(db_tb_name, 'jf_id', season['Id'], 'imdb_id', serie_imdb_id, None)
                    else:
                        episode_0 = jf_client.jellyfin.get_provider_info(parent_id=season['Id'])['Items'][0]
                        episode_imdb_id = episode_0.get('ProviderIds', {}).get('Imdb', None)
                        if episode_imdb_id is None:
                            handler.notify('No IMDb ID: {}'.format(episode_0['Name']), critical=False)
                            continue
                        self._db.insert(db_tb_name, db_cols, (episode_imdb_id, None, 0, 1, None, None, season['Id'], None))
                        self._db.update(db_tb_name, 'jf_id', season['Id'], 'imdb_id', episode_imdb_id, None)
                            
        for folder in media_folders:
            if folder['Name'] == 'Movies':
                ret = jf_client.jellyfin.get_provider_info(parent_id=folder['Id'], recursive=True)['Items']
                for item in ret:  update_jf_data(item)
            else: 
                ret = jf_client.jellyfin.get_provider_info(parent_id=folder['Id'])['Items']
                for item in ret: update_jf_data(item, is_series=True)
        self._client_manager.stop_all_clients()