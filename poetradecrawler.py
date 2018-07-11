from bs4 import BeautifulSoup
from time import sleep
import requests
import os
from datetime import date
from Helpers import helper_mean
from Helpers import helper_median

class PoETradeCrawler(object):
    base_url = 'http://poe.trade/search'
    currency_url = 'http://currency.poe.trade/search'
    # Only keeping the relevant currencies for now to reduce load on poe.trade
    currency_helper_dict = {
#        'alteration' : '1',
        'fusing' : '2',
#        'alchemy': '3',
#        'gcp': '5',
        'exalted': '6',
#        'chrome': '7',
#        'jeweller': '8',
#        'chance': '9',
#        'chisel': '10',
#        'scouring': '11',
#        'blessed': '12',
#        'regret': '13',
#        'regal': '14',
        'divine': '15',
#        'vaal': '16',
    }
    base_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'DNT': '1',
        'Host': 'poe.trade',
        'Origin': 'http://poe.trade',
        'Referer': 'http://poe.trade/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116'
    }
    div_always_save = [
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
    div_always_uber = [
        "House of Mirrors",
        "The Immortal",
        "The Doctor",
        "The Fiend"
    ]
    div_always_shit = [
        "The Scholar",
        "The Gambler",
        "The Gemcutter",
        "The Catalyst",
        "Loyalty",
        "The Survivalist",
        "Three Faces in the Dark",
        "The Carrion Crow",
        "Destined to Crumble",
        "Dying Anguish",
        "The Endurance",
        "The Flora's Gift",
        "The Fox",
        "Gift of the Gemling Queen",
        "Her Mask",
        "The Hermit",
        "Grave Knowledge",
        "The Inoculated",
        "The Jester",
        "The King's Blade",
        "Lantador's Lost Love",
        "The Lord in Black",
        "Merciless Armament",
        "The Metalsmith's Gift",
        "Prosperity",
        "The Rabid Rhoa",
        "The Road to Power",
        "Shard of Fate",
        "The Sigil",
        "The Spoiled Prince",
        "The Summoner",
        "The Surgeon",
        "The Twins",
        "The Tyrant",
        "Volatile Power",
        "The Warden",
        "The Web"
    ]
    div_shit_list = [
    ]
    div_epic_list = [
    ]
    div_shit_cutoff = 45
    div_uber_cutoff = 50
    unique_price_cutoff = 60
    delay_between_queries = 2
    # TODO Make this populate dynamically somehow? List of league uniques + boss uniques from wiki?
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
        "The Surrender"
    ]
    currency_ratio = {
        'chaos': 1,
        'gcp': 0.904156,
        'fusing': 0.400236,
        'exalted': 62.140000,
        'chance': 0.147604,
        'divine': 14,
        'blessed': 0.330106,
        'vaal': 1.269048,
        'chrome': 0.070571,
        'regret': 1.162857,
        'scouring': 0.578042,
        'regal': 0.635425,
        'jewellers': 0.096933,
        'alteration': 0.052711,
        'chisel': 0.320704,
        'alchemy': 0.255218
    }
    bad_names_dict = {
        "Rigwald's Charge": "Rigvald's Charge",
        "Victario's Flight": "Ondar's Flight",
        "Jack, the Axe": "Jack, The Axe",
        "Fortified Legion": "Bulwark Legion",
        "Veruso's Battering Rams": "Veruso’s Battering Rams"
    }

    # type: 0 = unique non-corrupt, 1 = div card
    def construct_payload(self, item_name, league, type):
        if type == 0:
            payload = "league=" + requests.utils.quote(league) + "&type=&base=&name=" + requests.utils.quote(item_name)\
                      +"&dmg_min=&dmg_max=&aps_min=&aps_max=&crit_min=&crit_max=&dps_min=&dps_max=&edps_min=&" \
                       "edps_max=&pdps_min=&pdps_max=&armour_min=&armour_max=&evasion_min=&evasion_max=&shield_min=&" \
                       "shield_max=&block_min=&block_max=&sockets_min=&sockets_max=&link_min=&link_max=&sockets_r=&" \
                       "sockets_g=&sockets_b=&sockets_w=&linked_r=&linked_g=&linked_b=&linked_w=&rlevel_min=&" \
                       "rlevel_max=&rstr_min=&rstr_max=&rdex_min=&rdex_max=&rint_min=&rint_max=&mod_name=&mod_min=&" \
                       "mod_max=&group_type=And&group_min=&group_max=&group_count=1&q_min=&q_max=&level_min=&" \
                       "level_max=&ilvl_min=&ilvl_max=&rarity=unique&seller=&thread=&identified=&corrupted=0&" \
                       "online=x&has_buyout=1&altart=&capquality=&buyout_min=&buyout_max=&buyout_currency=&crafted=&enchanted="
        elif type == 1:
            payload = "league=" + requests.utils.quote(league) + "&type=" + requests.utils.quote('Divination Card') + "&base=&name=" + requests.utils.quote(item_name)\
                      + "&dmg_min=&dmg_max=&aps_min=&aps_max=&crit_min=&crit_max=&dps_min=&dps_max=&edps_min=&" \
                        "edps_max=&pdps_min=&pdps_max=&armour_min=&armour_max=&evasion_min=&evasion_max=&shield_min=&" \
                        "shield_max=&block_min=&block_max=&sockets_min=&sockets_max=&link_min=&link_max=&sockets_r=&" \
                        "sockets_g=&sockets_b=&sockets_w=&linked_r=&linked_g=&linked_b=&linked_w=&rlevel_min=&" \
                        "rlevel_max=&rstr_min=&rstr_max=&rdex_min=&rdex_max=&rint_min=&rint_max=&mod_name=&mod_min=&" \
                        "mod_max=&group_type=And&group_min=&group_max=&group_count=1&q_min=&q_max=&level_min=&" \
                        "level_max=&ilvl_min=&ilvl_max=&rarity=&seller=&thread=&identified=&corrupted=&" \
                        "online=x&has_buyout=1&altart=&capquality=&buyout_min=&buyout_max=&buyout_currency=&crafted=&enchanted="
        else:
            payload = "wtf_this_isnt_happenging"

        return payload

    # Try to calculate a reasonable estimate of price, base on a list of all prices
    # Will try to remove the bottom offers to try and minimize scammers effect on price
    def calculate_a_price(self, list_of_prices):
        if len(list_of_prices) == 0:
            return 99999
        elif len(list_of_prices) < 4:
            return list_of_prices[0]
        elif len(list_of_prices) < 10:
            temp_list = list_of_prices[1:int(len(list_of_prices) * 1/2)]
            return helper_mean(temp_list)
        elif len(list_of_prices) < 20:
            temp_list = list_of_prices[2:int(len(list_of_prices) * 1/2)]
            return helper_mean(temp_list)
        else:
            temp_list = list_of_prices[3:int(len(list_of_prices) * 1/3)]
            return helper_mean(temp_list)

    # Will get a response type for given item and league name. Will return 0 if failed. Type: 0 = unique, 1 = divcard
    def get_a_page(self, item_name, league_name, type):
        payload = self.construct_payload(item_name, league_name, type)
        full_headers = self.base_headers
        full_headers['Content-Length'] = str(len(payload))
        full_headers['Cookie'] = "league=" + league_name
        failed_attempts = 0
        while failed_attempts < 10:
            r = requests.post(self.base_url, data=payload, headers=full_headers)
            # cases when we will retry
            if r.text.find('Request unsuccessful.') >= 0:
                print("This seems like a failed attempt")
                failed_attempts += failed_attempts
            elif r.status_code in [400, 401, 402, 403, 404, 405, 406, 408, 409, 410, 411, 412]:
                print("This seems like a failed attempt with a code of %d" % r.status_code)
                failed_attempts += failed_attempts
            # cases when we will abort trying
            # other cases = we win
            else:
                return r
            print("Sleeping %d seconds" % self.delay_between_queries)
            sleep(self.delay_between_queries)
        # seems like 10 attempts has gone through and we still returned nothing
        return 0

    # Will clear outliers out of a price list.
    # Less than half of the median and more than 3 times than median is an outlier
    def remove_outliers(self, some_list):
        temp_list1 = []
        for item in some_list:
            if item < 50 * self.currency_ratio['exalted']:
                temp_list1.append(item)
        median = helper_median(temp_list1)
        temp_list = []
        for item in temp_list1:
            if (item >= median/2) and (item <= median * 3):
                temp_list.append(item)
        return temp_list

    # Will take a string in the format 'x currency' and return a float of how many chaos that is.
    # Will return 0 if the currency not in the dictionary
    def convert_to_chaos_cents(self, price):
        number = float(price[:price.find(' ')])
        currency = price[price.find(' ')+1:]
        if currency in self.currency_ratio:
            temp = float(number * self.currency_ratio[currency])
            return int(temp * 100)
        else:
            return 0

    # Process div cards according to cut-offs
    def process_div_cards(self):
        print("Processing div cards now.")
        for item in self.div_prices_dict:
            # First we check if divination card is in predefined list and process accordingly. Otherwise resort to price check
            print("Now processing ", item)
            if item in self.div_always_uber:
                self.div_uber_list.append(item)
                print("Found ", item, " in always uber list. Appending to uber list")
                continue
            if item in self.div_always_shit:
                self.div_shit_list.append(item)
                print("Found ", item, " in always shit list. Appending to shit list")
                continue
            if item in self.div_always_save:
                print("Found ", item, " in save list. Appending nowhere")
                continue
            if self.div_prices_dict[item] <= self.div_shit_cutoff:
                print(item, " costs lower than shit cutoff, appending to shit list")
                self.div_shit_list.append(item)
            elif self.div_prices_dict[item] >= self.div_uber_cutoff:
                print(item, " costs more than uber cutoff, appending to uber list")
                self.div_uber_list.append(item)

    # Will take a requests result and parse all prices out of it as a list.
    def parse_item_prices(self, response):
        prices_list = []
        s1 = 'data-buyout="'
        text = response.text
        while text.find(s1) > 0:
            text = text[text.find(s1)+len(s1):]
            price = text[:text.find('"')]
            prices_list.append(float(self.convert_to_chaos_cents(price)/100))
        return self.remove_outliers(sorted(prices_list))

    # This outputs files with resulting filters and stuff into corresponding directories. Make sure current input
    # Blank files are provided
    def produce_result_files(self):
        # make a folder
        if not os.path.exists('/output/'):
            os.makedirs('/output/')
        today = date.today().isoformat()
        current_path = 'output/' + today + '/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        league_path = current_path + self.league_name + '/'
        if not os.path.exists(league_path):
            os.makedirs(league_path)
        # Now to individual files
        # Making a uniques to save line and uniques to trashline
        uniques_to_save_line = ""
        uniques_to_trash_line = ""
        unique_savelist = []
        for item in self.prices_dict:
            # This is for bad names, which differ in memory and client. Seems obsolete after 05-01-2017
            fix_item = item
            # if item in self.bad_names_dict:
            #   fix_item = self.bad_names_dict[item]
            if self.prices_dict[item] <= self.unique_price_cutoff:
                # trash this one
                if len(uniques_to_trash_line) == 0:
                    # first item in line
                    uniques_to_trash_line = 'item.IsUnique and (item.FullName == \\"' + fix_item + '\\"'
                else:
                    # rest items
                    uniques_to_trash_line = uniques_to_trash_line + ' or item.FullName == \\"' + fix_item + '\\"'
            else:
                # stash this one
                unique_savelist.append(fix_item)
                if len(uniques_to_save_line) == 0:
                    uniques_to_save_line = 'item.IsUnique and (item.FullName == \\"' + fix_item + '\\"'
                else:
                    uniques_to_save_line = uniques_to_save_line + ' or item.FullName == \\"' + fix_item + '\\"'
        uniques_to_trash_line += ')'
        uniques_to_save_line += ')'
        # NOW ONTO divination cards
        div_cards_save_line = ""
        div_cards_trash_line = "item.IsDivinationCard"
        for item in self.div_shit_list:
            div_cards_trash_line = div_cards_trash_line + ' and not item.FullName == \\"' + item + '\\"'
        for item in self.div_uber_list:
            div_cards_save_line = div_cards_save_line + '    {\n      "IsEnabled": true,\n' \
                                                        '      "Type": 8,\n' \
                                                        '      "ItemName": "' + item + '",\n' \
                                                                                       '      "TabName": "3"\n    },\n'
        # Ok, now let's do proper files. First let's load the 'blank'
        print('Now writing files to: %s' % league_path)
        with open(league_path + 'CustomFilter' + self.league_name + ".json", 'w', encoding='utf-8') as output_file:
            with open('CustomFilterBlank.json', 'r') as input_file:
                for line in input_file:
                    final_line = line.replace('###GOOD UNIQUES LINE###', uniques_to_save_line)
                    final_line = final_line.replace('###BAD UNIQUES LINE###', uniques_to_trash_line)
                    final_line = final_line.replace('###BAD DIV CARDS LINE###', div_cards_trash_line)
                    output_file.write(final_line)
        with open(league_path + 'AdvancedItemFilter.json', 'w', encoding='utf-8') as output_file:
            with open('AdvancedItemFilter.json', 'r') as input_file:
                for line in input_file:
                    final_line = line.replace("###LEAGUE HERE###", self.league_name)
                    final_line = final_line.replace('### GOOD DIV CARDS LINE HERE ###', div_cards_save_line)
                    output_file.write(final_line)
        # Let's do a separate file for currency tab owner bots
        with open(league_path + 'curtabAdvancedItemFilter.json', 'w', encoding='utf-8') as output_file:
            with open('curtabAdvancedItemFilter.json', 'r') as input_file:
                for line in input_file:
                    final_line = line.replace("###LEAGUE HERE###", self.league_name)
                    final_line = final_line.replace('### GOOD DIV CARDS LINE HERE ###', div_cards_save_line)
                    output_file.write(final_line)
        # And another file for cur tab + 5th tab
        with open(league_path + 'curtab5AdvancedItemFilter.json', 'w', encoding='utf-8') as output_file:
            with open('curtab5AdvancedItemFilter.json', 'r') as input_file:
                for line in input_file:
                    final_line = line.replace("###LEAGUE HERE###", self.league_name)
                    final_line = final_line.replace('### GOOD DIV CARDS LINE HERE ###', div_cards_save_line)
                    output_file.write(final_line)
        # This is for chancing suggestions
        with open(league_path + "Chancing suggestions.txt", 'w', encoding='utf-8') as output_file:
            output_file.write("Top 10 items to chance in %s: \n" % self.league_name)
            index = 0
            for w in sorted(self.prices_dict, key=self.prices_dict.get, reverse=True):
                if self.prices_dict[w] == 99999:
                    continue
                if w in self.unchanced_uniques:
                    continue
                output_file.write("%s = %d ex\n" % (w, int(self.prices_dict[w] / self.currency_ratio['exalted'])))
                index += 1
                if index >= 10:
                    break
        # This is to write raw data
        with open(league_path + "Raw_data.txt", 'w', encoding='utf-8') as output_file:
            output_file.write('Uniques to save:\n')
            for item in unique_savelist:
                output_file.write(item + '\n')
            output_file.write('Div cards to save:\n')
            for item in self.div_prices_dict:
                if (item not in self.div_shit_list) and item not in self.div_uber_list:
                    output_file.write(item + '\n')
            output_file.write('Uber div cards:\n')
            for item in self.div_uber_list:
                output_file.write(item + '\n')

    # method to populate currency conversion ratios from poe.trade
    def populate_currency_ratios(self):
        headers = self.base_headers
        headers['Host'] = 'currency.poe.trade'
        headers['DNT'] = '1'
        headers['Upgrade-Insecure-Requests'] = '1'
        for item in self.currency_helper_dict:
            payload = {'online': 'x', 'want': '4', 'league': self.league_name, 'have': self.currency_helper_dict[item]}
            r = requests.get(self.currency_url, headers=self.base_headers, params=payload)
            soup = BeautifulSoup(r.text, 'html.parser')
            rows = soup.find_all('div', {'class': 'displayoffer'})
            temp_prices = []
            # Let's only do first 15 elements and do mean from that.
            for row in rows[0:15]:
                price = float(row['data-sellvalue']) / float(row['data-buyvalue'])
                temp_prices.append(price)
            final_price = helper_mean(temp_prices)
            self.currency_ratio[item] = final_price
            print("Updated %s price to %f" % (item, final_price))
            print("Going to sleep %d seconds before next request" % self.delay_between_queries)
            sleep(self.delay_between_queries)

    # Massive parsing inc. type: 0 = unique, 1 = div card
    def parse_a_list_of_names(self, list_of_items, type):
        result = {}
        count_of_no_price_items = 0
        for index, item in enumerate(list_of_items):
            print("Getting item %s on %s (%d out of %d)" % (item, self.league_name, index+1, len(list_of_items)))
            request_result = self.get_a_page(item, self.league_name, type)
            price = self.parse_item_prices(request_result)
            result[item] = self.calculate_a_price(price)
            if result[item] == 99999:
                count_of_no_price_items += 1
        print("========================================================================================")
        print("Finished with a set of items. I couldn't find prices for %d items out of %d"
              % (count_of_no_price_items, len(list_of_items)))
        print("========================================================================================")
        return result

    def parse_all(self, wikicrawler):
        self.prices_dict = self.parse_a_list_of_names(wikicrawler.unique_items, 0)
        self.div_prices_dict = self.parse_a_list_of_names(wikicrawler.div_card_names, 1)
        self.process_div_cards()
        self.produce_result_files()

    def __init__(self, league_name):
        self.league_name = league_name
        self.div_uber_list = []
        self.div_shit_list = []
        self.div_prices_dict = {}
        self.prices_dict = {}
        # For some reason doesn't work with populating currencies, keeping it off fow now.
        # TODO Figure out WTF is wrong.
        # self.populate_currency_ratios()
