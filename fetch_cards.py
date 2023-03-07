import json
import logging
import requests
from bs4 import BeautifulSoup
import os.path
import genanki
import random

API_ENDPOINT = 'https://countryflagsapi.com/svg/'
IBAN_ENDPOINT = 'https://www.iban.com/country-codes'
FLAG_MODEL = genanki.Model(
    1121025992,
    'Flag Model',
    fields=[
        {'name': 'Country'},
        {'name': 'Alpha-2'},
        {'name': 'Alpha-3'},
        {'name': 'Numeric'},
        {'name': 'Image'},
    ],
    templates=[
        {
            'name': 'Country Name',
            'qfmt': '<img src={{Image}} />',
            'afmt': '{{FrontSide}}<hr id="answer"><p>Name: {{Country}}</p>'
        },
        {
            'name': 'Alpha-2 Code',
            'qfmt': '<img src={{Image}} />',
            'afmt': '{{FrontSide}}<hr id="answer"><p>Alpha-2 Code: {{Alpha-2}}</p>'
        },
        {
            'name': 'Alpha-3 Code',
            'qfmt': '<img src={{Image}} />',
            'afmt': '{{FrontSide}}<hr id="answer"><p>Alpha-3 Code: {{Alpha-3}}</p>'
        },
        {
            'name': 'ISO Numeric Code',
            'qfmt': '<img src={{Image}} />',
            'afmt': '{{FrontSide}}<hr id="answer"><p>ISO Numeric Code: {{Numeric}}</p>'
        },
    ])

logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def soup_as_list(soup):
    tags = []
    for tag in soup.strings:
        if tag != '\n':
            tags.append(tag)

    return tags


def get_country_data():
    iban_country_codes = requests.get(IBAN_ENDPOINT)
    page = BeautifulSoup(iban_country_codes.text, features='html.parser')
    country_code_table = page.table
    keys = soup_as_list(country_code_table.thead)

    logger.info(f'keys: {keys}')

    country_data = []
    for row in country_code_table.tbody.children:
        if row == None or row == '\n':
            continue

        column = 0
        country = {}
        data = soup_as_list(row)

        assert len(data) == len(keys)

        while column % len(data) != 0 or column == 0:
            logger.info(f'{data[column]} written to the dictionary')
            country[keys[column]] = data[column]
            column += 1

        country_data.append(country)
     
    return keys, country_data


def download_flag_svgs(country_data):
    for country in country_data:
        PATH = f'flags/{country[keys[0]]}.svg'
        if os.path.exists(f'flags/'):
            logger.warning(f'skipped {PATH}')
            continue

        flag_svg = requests.get(API_ENDPOINT + country[keys[3]])

        if not flag_svg.ok:
            logger.error(f'{country[keys[3]]} is invalid')
            continue

        f = open(PATH, 'w')
        f.write(flag_svg.text)
        logger.info(f'wrote {PATH}')
        f.close()


def write_countries_json(country_data):
    json_file = open('countries.json', 'w')
    json_file.write(json.dumps(country_data, indent=4))
    logger.info('wrote countries.json')
    

(keys, country_data) = get_country_data()
download_flag_svgs(country_data)
write_countries_json(country_data)

flag_deck = genanki.Deck(
    1775916622,
    'Country Flags')

for country in country_data:
    fields = list(country.values())
    fields.append(f'flags/{country[keys[0]]}.svg')
    logger.info(fields)
    country_card = genanki.Note(
        model=FLAG_MODEL,
        fields=fields,
        
    )
    flag_deck.add_note(country_card)

flag_pakage = genanki.Package(flag_deck)
for country in country_data:
    flag_pakage.media_files.append(f'flags/{country[keys[0]]}.svg')
  
flag_pakage.write_to_file('flag_cards.apkg')