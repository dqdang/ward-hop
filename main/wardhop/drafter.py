import os
from riotwatcher import LolWatcher, ApiError
import main.settings as settings


try:
    API_KEY = os.environ["API_KEY"]
except KeyError:
    API_KEY = settings.API_KEY

watcher = LolWatcher(API_KEY)
region = 'na1'


class ChampionDatabase():
    latest = {}
    static_champ_list = {}
    champ_dict = {}

    def __init__(self):
        self.latest = watcher.data_dragon.versions_for_region(region)[
            'n']['champion']
        self.static_champ_list = watcher.data_dragon.champions(
            self.latest, False, 'en_US')
        self.champ_dict = {}
        for key in self.static_champ_list['data']:
            row = self.static_champ_list['data'][key]
            if row['id'] == "MonkeyKing":
                row['id'] = "Wukong"
            self.champ_dict[row['key']] = row['id']

    def get_all_champ_data(self):
        return self.static_champ_list['data']

    def get_all_champ_names(self):
        names = []
        for key in self.static_champ_list['data']:
            names.append(key)
        return names

    def get_champ_images(self):
        images = {}
        for key in self.static_champ_list['data']:
            images[self.static_champ_list['data'][key]
                   ] = self.static_champ_list['data'][key]['image']
        return images

    def search(self, key):
        found = []
        champions = self.get_all_champ_names()
        for champ in champions:
            champ = champ.lower()
            key = ''.join(e for e in key if e.isalpha())
            if champ.startswith(key):
                found.append(champ)
        return found
