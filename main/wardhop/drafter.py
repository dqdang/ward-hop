import os
from riotwatcher import LolWatcher, ApiError
import main.settings as settings
from wardhop import analysis

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

    def get_all_champ_images(self):
        images = {}
        for champ in self.static_champ_list['data']:
            image = self.static_champ_list['data'][champ]['image']
            if champ == "MonkeyKing":
                image['full'] = "Wukong." + image['full'].split(".")[1]
            images[champ] = image
        return images

    def get_all_champ_names(self):
        names = []
        for champ in self.static_champ_list['data']:
            if champ == "MonkeyKing":
                champ = "Wukong"
            names.append(champ)
        return names

    def get_champ_image(self, key):
        key = ''.join(e for e in key if e.isalpha())
        for champ in self.static_champ_list['data']:
            champ_lower_case = champ.lower()
            if champ_lower_case == "monkeyking":
                champ_lower_case = "wukong"
            if champ_lower_case.startswith(key):
                image = self.static_champ_list['data'][champ]['image']
                if champ_lower_case == "wukong":
                    image['full'] = "Wukong." + image['full'].split(".")[1]
                return image
        return None

    def search(self, key):
        key = ''.join(e.lower() for e in key if e.isalpha())
        if key == "":
            return None
        champions = self.get_all_champ_names()
        for champ in champions:
            champ = champ.lower()
            if champ.startswith(key):
                return champ
        return None

    def get_all_champ_analysis(self):
        analysis_dict = {}
        for champ in self.static_champ_list['data']:
            if champ == "MonkeyKing":
                champ = "Wukong"
            analysis_dict[champ] = analysis.analyze(champ)
        return analysis_dict

    def get_single_champ_analysis(self, champ):
        if champ == "MonkeyKing":
            champ = "Wukong"
        return analysis.analyze(champ)

    def get_multiple_champ_analysis(self, champs):
        analysis_dict = {}
        for champ in champs:
            if champ == "MonkeyKing":
                champ = "Wukong"
            analysis_dict[champ] = analysis.analyze(champ)
        return analysis_dict
