import requests 
import json
from bs4 import BeautifulSoup


def soup_as_list(soup):
    tags = []
    for tag in soup.strings:
        if tag != '\n':
            tags.append(tag)

    return tags;


iban_country_codes = requests.get('https://www.iban.com/country-codes')
page = BeautifulSoup(iban_country_codes.text, features='html.parser')
country_code_table = page.table
keys = soup_as_list(country_code_table.thead)
# print(keys)
        
country_data = []
for row in country_code_table.tbody.children:
    if row == None or row == '\n':
        continue
    
    column = 0
    country = {}
    data = soup_as_list(row)
    # print(data)

    assert len(data) == len(keys)

    while column % len(data) != 0 or column == 0:
        country[keys[column]] = data[column]
        column += 1

    country_data.append(country)

# print(json.dumps(country_data, indent=4))
# print(len(country_data))


