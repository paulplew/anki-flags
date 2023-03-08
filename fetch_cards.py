import json
import logging
import requests
from bs4 import BeautifulSoup
import os.path
import genanki
import random

API_ENDPOINT = 'https://countryflagsapi.com/svg/'
IBAN_ENDPOINT = 'https://www.iban.com/country-codes'

class FlagNote(genanki.Note):
  @property
  def guid(self):
    return genanki.guid_for(self.fields[0])

class ISONote(genanki.Note):
    @property
    def guid(self):
        return genanki.guid_for(self.fields[0], self.fields[1])

STYLE = """
.center {
  display: flex;
  align-items: center;
  justify-content: center;
}
"""
FLAG_MODEL = genanki.Model(
    1121025992,
    'Flag Model',
    fields=[
        {'name': 'Country'},
        {'name': 'Image_lg'},
        {'name': 'Image_sm'},
    ],
    templates=[
        {
            'name': 'Flag to Country Name',
            'qfmt': '<div class="center">{{Image_lg}}</div>',
            'afmt': '{{FrontSide}}<hr id="answer"><p>Name: {{Country}}</p>'
        },
        {
            'name': 'Country Name To Flag',
            'qfmt': '<div class="center">The flag for {{Country}}</div>',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="center">{{Image_sm}}</div>'
        },
    ],
    css=STYLE)

ISO_MODEL = genanki.Model(
1228079407,
    'ISO3166 Model',
    fields=[
        {'name': 'Country'},
        {'name': 'Alpha-2'},
        {'name': 'Alpha-3'},
        {'name': 'Numeric'},
    ],
    templates=[
        {
            'name': 'Country Name to Alpha 2',
            'qfmt': '<div class=center><p>What is the Alpha-2 code for {{Country}}?</p></div>',
            'afmt': '{{FrontSide}}<hr id="answer"><p>Alpha-2: {{Alpha-2}}</p>'
        },
        {
            'name': 'Country Name to Alpha 3',
            'qfmt': '<div class=center><p>What is the Alpha-3 code for {{Country}}?</p></div>',
            'afmt': '{{FrontSide}}<hr id="answer"><p>Alpha-3: {{Alpha-3}}</p>'
        },
        {
            'name': 'Country Name to Numeric',
            'qfmt': '<div class=center><p>What is the Numeric code for {{Country}}?</p></div>',
            'afmt': '{{FrontSide}}<hr id="answer"><p>{{Numeric}}</p>'
        },
        {
            'name': 'Alpha 2 to Country Name',
            'qfmt': '<div class=center><p>What country does the alpha-2 code <b>{{Alpha-2}}</b> represent?</p></div>',
            'afmt': '{{FrontSide}}<hr id="answer"><p>Country: {{Country}}</p>'
        },
        {
            'name': 'Alpha 3 to Country Name',
            'qfmt': '<div class=center><p>What country does the alpha-3 code <b>{{Alpha-3}}</b> represent?</p></div>',
            'afmt': '{{FrontSide}}<hr id="answer"><p>{{Country}}</p>'
        },
        {
            'name': 'Numeric to Country Name',
            'qfmt': '<div class=center><p>What country does the numeric code <b>{{Numeric}}</b> represent?</p></div>',
            'afmt': '{{FrontSide}}<hr id="answer"><p>{{Country}}</p>'
        },
    ],
    css=STYLE)

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

# Generate the Flag Deck
flag_deck = genanki.Deck(
    1775916622,
    'Country Flags')

for country in country_data:
    fields = [country['Country']]
    fields.append(f'<img src="{country[keys[0]]}.svg" height="450px">')
    fields.append(f'<img src="{country[keys[0]]}.svg" height="225px">')
    logger.info(fields)
    country_card = FlagNote(
        model=FLAG_MODEL,
        fields=fields,
        
    )
    flag_deck.add_note(country_card)

flag_pakage = genanki.Package(flag_deck)
for country in country_data:
    flag_pakage.media_files.append(f'./flags/{country[keys[0]]}.svg')
  
flag_pakage.write_to_file('flag_cards.apkg')

# generate the ISO 3166 Deck
iso_deck = genanki.Deck(
    1963129519,
    'ISO3166')
for country in country_data:
    fields = list(country.values())
    logger.info(fields)
    iso_note = ISONote(
        model=ISO_MODEL,
        fields=fields,
    )
    iso_deck.add_note(iso_note)

iso_package = genanki.Package(iso_deck)
iso_package.write_to_file('iso3166.apkg')