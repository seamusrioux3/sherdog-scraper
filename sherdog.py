from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from tqdm import tqdm
import numpy as np
import pickle
import os
import datetime

#Headers sent in request to google
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

#Add proxies if needed
proxies = {}

'''
    Function that searches fighters based on string uses google and 
    find first link that is on sherdog

    Returns sherdog link (str)
'''
def searchFighter(name):
    print(name)
    search = 'sherdog' + name
    url = 'https://www.google.com/search'

    headers = {
        'Accept' : '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
    }
    parameters = {'q': search}

    content = requests.get(url, headers = headers, params = parameters, proxies=proxies).text
    soup = BeautifulSoup(content, 'html.parser')
    print(soup)

    # search = soup.find(id = 'search')
    div = soup.select_one('.yuRUbf a')
    if(div is None):
        return ''
    first_link = soup.select_one('.yuRUbf a')['href']
    
    return first_link

'''
    Reads document into pandas df based on type

    Returns pandas df
'''
def readSheet(file: str) -> pd.DataFrame: 
    extension = file.split('.')[1]
    if(extension is 'csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)


'''
    Writes pandas df into the specified file
'''
def writeSheet(file: str, df: pd.DataFrame):
    extension = file.split('.')[1]
    if(extension is 'csv'):
        df.to_csv(file)
    else:
        df.to_excel(file)

'''
    Get links for all the fighters listed in the spreadsheet
    and then writes them back to the spreadsheet in a seperate column
'''
def getFighterLinks(fileName, searchField):
    links = []

    df = readSheet(fileName)

    if('Links' in df.columns):
        try:
            for _, row in tqdm(df.iterrows()):

                playerName = str(row[searchField]).split(' ')

                if(pd.isna(row['Links'])):
                    link = searchFighter(playerName)
                    links.append(link)
                    print(link)
                else:
                    links.append(row['Links'])
                    print('had' + str(row['Links']))
        except:
            df['Links'] =  links
            writeSheet(fileName, df)
    
    df['Links'] =  links
    writeSheet(fileName, df)



def getLastFightLink(link):
    s = requests.Session() 
    r = s.get(link, headers=headers, proxies=proxies)

    soup = BeautifulSoup(r.content, 'html.parser')
    tableSpan = soup.find('span', {'class': 'sub_line'})

    lastFight = "N/A"

    if(tableSpan):
        lastFight = tableSpan.contents[0]
        if(lastFight == 'N/A'):
            return 'N/A'
        # lastFight = datetime.datetime.strptime(lastFight, '%b / %d / %Y')
        # lastFight = lastFight.isoformat()

    return lastFight


def parseExcelSheet():
    dates = []
    df = pd.read_csv('ufcfighters.csv', index_col=0)
    
    for _, row in tqdm(df.iterrows()):
        try:
            link = row['Links']
            if(pd.isna(row['Last Fight'])):
                date = getLastFightLink(link)
                dates.append(date)
                print(link + " "+ date, end ='\n')
            elif(row['Last Fight'] == 'N/A'):
                print('filled ' + link)
                link = searchFighter(row['PLAYERNAME'])
                date = getLastFightLink(link)
                print(link + " "+ date, end ='\n')
                dates.append(date)
            else:
                print('filled ' + link)
                dates.append(row['Last Fight'])
        except KeyboardInterrupt:
            df['Last Fight'] =  dates + [np.nan] * (589 - len(dates))
            df.to_excel("ufc1.xlsx")
            return
        except requests.exceptions.SSLError:
            continue
        except requests.exceptions.ProxyError:
            continue


    df['Last Fight'] =  dates
    df.to_csv('ufcfighters.csv')



#getFighterLinks("ufc1.xlsx")

#print(getLastFightLink('https://www.sherdog.com/fighter/Charlie-Radtke-175669'))
parseExcelSheet()
#giveFighterLink()
        
#getFighterLinks('ufcfighters.csv')
