import requests
from bs4 import BeautifulSoup
from time import sleep
from Helpers import remove_extra_spaces_from_string

class WikiCrawler(object):
    unique_items = []
    div_card_names = []
    div_card_currency_names = []
    delay_between_queries = 0
    list_of_urls = [
        'http://pathofexile.gamepedia.com/List_of_unique_accessories',
        'http://pathofexile.gamepedia.com/List_of_unique_armour',
        'http://pathofexile.gamepedia.com/List_of_unique_weapons',
        'http://pathofexile.gamepedia.com/List_of_unique_flasks',
        'http://pathofexile.gamepedia.com/List_of_unique_jewels',
        'http://pathofexile.gamepedia.com/List_of_unique_maps'
    ]
    div_card_url = 'http://pathofexile.gamepedia.com/Divination_card'
    div_card_url_list = [
        'http://pathofexile.gamepedia.com/List_of_divination_cards_granting_currency',
        'http://pathofexile.gamepedia.com/List_of_divination_cards_granting_maps',
        'http://pathofexile.gamepedia.com/List_of_divination_cards_granting_other_items',
        'http://pathofexile.gamepedia.com/List_of_divination_cards_granting_skill_gems',
        'http://pathofexile.gamepedia.com/List_of_divination_cards_granting_unique_items'
    ]
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'pathofexile.gamepedia.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116'
    }

    def populate_card_list(self):
        first_run = 1
        # First attempt to populate from the single URL. If it fails, populate from separate links
        if first_run == 0:
            sleep(self.delay_between_queries)
        else:
            first_run = 0
        r = requests.get(self.div_card_url, headers=self.headers)
        soup = BeautifulSoup(r.content.decode('utf-8'), 'html.parser')
        table = soup.find('table', {'class': 'wikitable sortable'})
        if table is not None:
            rows = table.find_all('tr')
            for element in rows:
                columns = element.find_all('td')
                if len(columns) > 0:
                    card_name = columns[0].text
                    if (card_name not in self.div_card_names) and (card_name != ''):
                        self.div_card_names.append(remove_extra_spaces_from_string(card_name))
                        # if item == self.div_card_url_list[0]:
                        #    self.div_card_currency_names.append(remove_extra_spaces_from_string(card_name))
        # If the list is empty, we failed
        if len(self.div_card_names) < 10:
            print("Failed to get card list from mono url, getting them from separate links then.")
            first_run = 1
            for item in self.div_card_url_list:
                if first_run == 0:
                    sleep(self.delay_between_queries)
                else:
                    first_run = 0
                r = requests.get(item, headers=self.headers)
                soup = BeautifulSoup(r.content.decode('utf-8'), 'html.parser')
                table = soup.find('table', {'class': 'wikitable sortable'})
                rows = table.find_all('tr')
                for element in rows:
                    columns = element.find_all('td')
                    if len(columns) > 0:
                        card_name = columns[0].text
                        if (card_name not in self.div_card_names) and (card_name != ''):
                            self.div_card_names.append(remove_extra_spaces_from_string(card_name))
                            # if item == self.div_card_url_list[0]:
                            #    self.div_card_currency_names.append(remove_extra_spaces_from_string(card_name))
        self.div_card_names.sort()
        print('I have found %d divination cards' % len(self.div_card_names))

    def populate_unique_item_list(self):
        first_run = 1
        for item in self.list_of_urls:
            if first_run == 0:
                sleep(self.delay_between_queries)
            else:
                first_run = 0
            # we need to run this url, parse it and add all items to the list.
            r = requests.get(item, headers=self.headers)
            soup = BeautifulSoup(r.content.decode('utf-8'), 'html.parser')
            table = soup.find_all('span', {'class': 'inline-infobox-container'})
            for line in table:
                name = line.a.get_text()
                if (name not in self.unique_items) and (name != ''):
                    self.unique_items.append(name)
        print('I have found %d unique items' % len(self.unique_items))
        self.unique_items.sort()

    def __init__(self):
        self.populate_unique_item_list()
        self.populate_card_list()
