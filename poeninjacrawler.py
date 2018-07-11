from bs4 import BeautifulSoup
from time import sleep
import requests
import os
import json
from datetime import date
from Helpers import generate_good_or_line

class PoENinjaCrawler(object):
    base_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-GB,en;q=0.8,en-US;q=0.6,ru;q=0.4',
        'Host': 'cdn.poe.ninja',
        'Origin': 'http://poe.ninja',
        'Referer': 'http://poe.ninja/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116'
    }
    unique_urls = ['http://cdn.poe.ninja/api/Data/GetUniqueAccessoryOverview?league=',
                   'http://cdn.poe.ninja/api/Data/GetUniqueArmourOverview?league=',
                   'http://cdn.poe.ninja/api/Data/GetUniqueWeaponOverview?league=',
                   'http://cdn.poe.ninja/api/Data/GetUniqueFlaskOverview?league=',
                   'http://cdn.poe.ninja/api/Data/GetUniqueJewelOverview?league=',
                   'http://cdn.poe.ninja/api/Data/GetUniqueMapOverview?league=']
    unchanced_uniques = [
        "Song of the Sirens",
        "Headhunter",
        "Shavronne's Revelation",
        "Atziri's Acuity",
        "The Harvest",
        "The Taming",
        "Berek's Respite",
        "Demigod's Dominance",
        "Atziri's Disfavour",
        "Starforge",
        "Emperor's Wit",
        "Faminebind",
        "Voll's Devotion",
        "The Perandus Manor",
        "Ylfeban's Trickery",
        "Null and Void",
        "The Gull",
        "The Retch",
        "Rigwald's Quills",
        "Rigwald's Command",
        "Dying Sun",
        "Emperor's Mastery",
        "Feastbind",
        "The Red Nightmare",
        "Reach of the Council",
        "Rigwald's Savagery",
        "United in Dream",
        "The Red Dream",
        "The Green Dream",
        "The Blue Dream",
        "The Green Nightmare",
        "The Blue Nightmare",
        "Emperor's Cunning",
        "Presence of Chayula",
        "The Anima Stone",
        "Primordial Might",
        "The Surrender",
        "Demigod's Bounty",
        "Eyes of the Greatwolf",
        "Emperor's Might",
        "Demigod's Presence",
        "Demigod's Stride",
        "Demigod's Triumph",
        "Demigod's Touch",
        "Demigod's Eye",
        "Talisman of the Victor",
        "Angler's Plait",
        "Natural Hierarchy"
    ]
    protect_currency_cards = True
    protected_cards = [
        "Abandoned Wealth",
        "The Cartographer",
        "Chaotic Disposition",
        "Coveted Possession",
        "Emperor's Luck",
        "The Hoarder",
        "The Inventor",
        "Lucky Connections",
        "The Union",
        "The Saint's Treasure",
        "Vinia's Token",
        "The Wrath",
        "Lucky Deck",
        "The Wretched",
        "The Risk",
        "The Sephirot"
    ]
    protect_prophecies = True
    protected_prophecies = [
        "Trash to Treasure",
        "Fated Connections"
    ]
    league = ""
    divination_threshold = 0
    prophecy_threshold = 0
    unique_threshold = 0
    unique_item_prices = {}

    def __init__(self, league_name, div_thr, prop_thr, uni_thr):
        self.league = league_name
        self.divination_threshold = div_thr
        self.prophecy_threshold = prop_thr
        self.unique_threshold = uni_thr

    def currency_prices(self):
        r = requests.get('http://api.poe.ninja/api/Data/GetCurrencyOverview?league='+self.league, headers=self.base_headers)
        parsed_json = json.loads(r.text)
        temp_dict = {}
        for line in parsed_json['lines']:
            temp_dict[line["currencyTypeName"]] = line["chaosEquivalent"]
        return temp_dict

    def divination_prices(self):
        r = requests.get('http://api.poe.ninja/api/Data/GetDivinationCardsOverview?league='+self.league, headers=self.base_headers)
        parsed_json = json.loads(r.text)
        temp_dict = {}
        for line in parsed_json['lines']:
            if line["chaosValue"] > self.divination_threshold:
                temp_dict[line["name"]] = line["chaosValue"]
        return temp_dict

    def prophecy_prices(self):
        r = requests.get('http://api.poe.ninja/api/Data/GetProphecyOverview?league=' + self.league, headers=self.base_headers)
        parsed_json = json.loads(r.text)
        temp_dict = {}
        for line in parsed_json['lines']:
            if line["chaosValue"] > self.prophecy_threshold:
                temp_dict[line["name"]] = line["chaosValue"]
        return temp_dict

    def unique_prices(self):
        temp_dict = {'Relics': {},
                     'Uniques': {}}
        for url in self.unique_urls:
            r = requests.get(url + self.league, headers=self.base_headers)
            parsed_json = json.loads(r.text)
            # itemClass = 9 for Legacy league, with relics and shit
            # links to discard 5-6l stuff after update
            for line in parsed_json['lines']:
                if line["chaosValue"] > self.unique_threshold:
                    if line["links"] == 5 or line["links"] == 6:
                        continue
                    if line["itemClass"] == 9:
                        temp_dict['Relics'][line["name"]] = line["chaosValue"]
                    else:
                        temp_dict['Uniques'][line["name"]] = line["chaosValue"]
        self.unique_item_prices = temp_dict['Uniques']
        return temp_dict

    def good_uniques(self):
        return generate_good_or_line(self.unique_prices()['Uniques'].keys())

    def good_cards(self):
        temp_list = []
        if self.protect_currency_cards:
            temp_list.extend(self.protected_cards)
        temp_list.extend(self.divination_prices().keys())
        temp_list = list(set(temp_list))
        return generate_good_or_line(temp_list)

    def good_prophecies(self):
        temp_list = []
        if self.protect_prophecies:
            temp_list.extend(self.protected_prophecies)
        temp_list.extend(self.prophecy_prices().keys())
        temp_list = list(set(temp_list))
        return generate_good_or_line(temp_list)

    # This outputs files with resulting filters and stuff into corresponding directories. Make sure current input
    # Blank files are provided
    def produce_result_files(self):
        # make a folder
        good_uniques_line = self.good_uniques()
        good_divcards_line = self.good_cards()
        good_prophecies_line = self.good_prophecies()
        if not os.path.exists('/output/'):
            os.makedirs('/output/')
        today = date.today().isoformat()
        current_path = 'output/' + today + '/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        league_path = current_path + self.league + '/'
        if not os.path.exists(league_path):
            os.makedirs(league_path)
        # Now to individual files
        # Ok, now let's do proper files. First let's load the 'blank'
        print('Now writing files to: %s' % league_path)
        with open(league_path + 'CustomFilter' + self.league + ".json", 'w', encoding='utf-8') as output_file:
            with open('CustomFilterBlank.json', 'r') as input_file:
                for line in input_file:
                    final_line = line.replace('### GOOD PROPHECIES NAMES (FullName OR) ###', good_prophecies_line)
                    final_line = final_line.replace('###GOOD UNIQUES LINE (Fullname OR) ###', good_uniques_line)
                    final_line = final_line.replace('###Good DIV CARDS LINE (FullName OR) ###', good_divcards_line)
                    output_file.write(final_line)
        # This is for chancing suggestions
        with open(league_path + "Chancing suggestions.txt", 'w', encoding='utf-8') as output_file:
            output_file.write("Top 10 items to chance in %s: \n" % self.league)
            index = 0
            for item in sorted(self.unique_item_prices, key=self.unique_item_prices.get, reverse=True):
                if item in self.unchanced_uniques:
                    continue
                output_file.write("%s = %d c\n" % (item, int(self.unique_item_prices[item])))
                index += 1
                if index >= 10:
                    break