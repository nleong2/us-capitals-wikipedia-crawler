import os
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup       # parse HTML and XML
import urllib.request               # Open urls

verbose = True

def main():
    # wikipedia homepage url
    wiki_home_url = "https://en.wikipedia.org"
    # crawler wiki page url
    us_capitals_url = "https://en.wikipedia.org/wiki/List_of_capitals_in_the_United_States"

    # open crawler wiki page
    page = urllib.request.urlopen(us_capitals_url)
    soup = BeautifulSoup(page, "lxml") # (html.parser) used to parse cml and html

    # find table containing US capitals
    table = soup.find('table', class_='wikitable sortable')

    # Make a list of urls to the US capitals
    # Save list of wiki extensions to the capitals
    capitals = []
    for row in table.findAll('tr'):
        row_data = row.findAll('td')
        if len(row_data) > 4:
            capitals.append(row_data[3].find('a').get('href'))

    # Create list populated by wiki homepage
    us_capitals_links = [wiki_home_url] * len(capitals)

    # Concatenate the wiki home page and wiki extensions
    for i in range(len(capitals)):
        us_capitals_links[i] += capitals[i]

    # Initialize wanted table headers for scraping
    headers = ['Country', 'State', 'Founded', 'Mayor', 'Elevation', 'Population', 'Demonym(s)']

    # initalize structure for the capital cities' data
    capitals_data = []

    # Scrape urls and add to data structure
    for link in us_capitals_links:
        capitals_data.append(scrape_city(link, headers))

    # Add header for 'City'. This would have disrupted the scraping if 
    # initalized sooner, so make sure this is done right before creating 
    # the pandas dataframe
    headers.insert(0, 'City')

    # Create pandas dataframe
    df = pd.DataFrame(capitals_data, columns=headers)

    # Save data to csv
    curr_dir = os.getcwd()
    csv_file = curr_dir + '/us_capitals_crawler_data.csv'
    #csv_file = '/us_capitals_crawler_data.csv'
    df.to_csv(csv_file, index=False)


# Scraping function
def scrape_city(city_link, headers):
    # Open link to city wiki page
    city_url = city_link
    page = urllib.request.urlopen(city_url)
    
    # Set up bs for city wiki page
    soup = BeautifulSoup(page, "lxml") # (html.parser) used to parse cml and html
    
    # Initalize empty array for data
    data = [None] * len(headers)
    
    table = soup.find('table', class_='infobox geography vcard')

    # SCRAPE the heck out of the city wiki
    for row in table.findAll('tr'):
        header = row.find('th')
        if header:
            header = header.text.replace('•', '').lstrip()       
            if header in headers:
                td = row.find('td')
                if td:
                    data[headers.index(header)] = td.text  
            elif 'Population' in header:
                pop = row.findNext('tr')
                td = pop.find('td')
                if td:
                    data[headers.index('Population')] = td.text
    
    # Add city name to the data            
    city_name = soup.title.string.split(',', 1)
    data.insert(0, city_name[0])
    
    # Verify data
    if verbose:
        print(data)
    
    # return list
    return data


if __name__ == "__main__":
    main()

