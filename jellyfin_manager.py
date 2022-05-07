from jellyfin.jellyfin_client import ClientManager
from subfinder import SubFinder
from handler import ErrorHandler
from header import *
import time
import os

handler = ErrorHandler()

class JellyfinManager:
    def __init__(self, db):
        self._client_manager = ClientManager()
        self._db = db
        self._sf = SubFinder()
        
    def update(self):
        ts = int(time.time())
        self._client_manager.cli_connect()
        jf_client = list(self._client_manager.clients.values())[0]
        media_folders = jf_client.jellyfin.get_media_folders()['Items']

        def update_jf_data(item, is_series=False):
            def update_sub(path, imdb_id, episodes=None):
                if not is_series:
                    parent, filename = os.path.split(path)
                    for file in os.listdir(parent):
                        if file.split('.')[-1] in self._sf.SUB_EXT: return
                    self._sf.get_sub(parent, imdb_id, name=filename[: filename.rfind('.')])
                else:
                    namemap = {}
                    for ep in episodes:
                        ep_path = ep['Path']
                        ep_num = ep['IndexNumber']
                        parent, ep_fname = os.path.split(ep_path)
                        for file in os.listdir(parent): 
                            if file.split('.')[-1] in self._sf.SUB_EXT: return
                        namemap[ep_num] = ep_fname[: ep_fname.rfind('.')]
                    self._sf.get_sub(path, imdb_id, name_map=namemap)

            item_imdb_id = item.get('ProviderIds', {}).get('Imdb', None)
            if item_imdb_id is None: 
                handler.notify('No IMDb ID: {}'.format(item['Name']), critical=False)
                return
            if not is_series:
                update_sub(item['Path'], item_imdb_id)
                self._db.insert(db_tb_name, db_cols, (item_imdb_id, None, 0, 0, None, None, item['Id'], ts))
                self._db.update(db_tb_name, 'jf_id', item['Id'], 'imdb_id', item_imdb_id, ts)
            else:
                seasons = jf_client.jellyfin.get_provider_info(parent_id=item['Id'])['Items']
                for season in seasons:
                    season_num = season['IndexNumber']
                    episodes = jf_client.jellyfin.get_provider_info(parent_id=season['Id'])['Items']
                    if season_num == 1:
                        serie_imdb_id = item_imdb_id
                    else:
                        serie_imdb_id = episodes[0].get('ProviderIds', {}).get('Imdb', None)
                        if serie_imdb_id is None:
                            handler.notify('No IMDb ID: {}'.format(episodes[0]['Name']), critical=False)
                            continue
                    update_sub(season['Path'], serie_imdb_id, episodes=episodes)
                    self._db.insert(db_tb_name, db_cols, (serie_imdb_id, None, 0, 1, None, None, season['Id'], ts))
                    self._db.update(db_tb_name, 'jf_id', season['Id'], 'imdb_id', serie_imdb_id, ts)
                            
        for folder in media_folders:
            if folder['Name'] == 'Movies':
                ret = jf_client.jellyfin.get_provider_info(parent_id=folder['Id'], recursive=True)['Items']
                for item in ret:  update_jf_data(item)
            else: 
                ret = jf_client.jellyfin.get_provider_info(parent_id=folder['Id'])['Items']
                for item in ret: update_jf_data(item, is_series=True)
        self._client_manager.stop_all_clients()