import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import matplotlib.pyplot as plt
import sqlite3
import datetime
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from Definitions import doGet
import sys

def scrape_13f(date,url):
#     date = '2020-08-17'
#     url = 'https://www.sec.gov/Archives/edgar/data/1224962/000101297520000701/xslForm13F_X01/infotable.xml'
    #     html = open("13f/"+file).read()
    res = doGet(url)
    soup = BeautifulSoup(res.text, 'lxml')
    rows = soup.find_all('tr')[11:]
    positions = []          
    for row in rows:
        dic = {}
        position = row.find_all('td')
        dic["NAME_OF_ISSUER"] = position[0].text
        dic["TITLE_OF_CLASS"] = position[1].text
        dic["CUSIP"] = position[2].text
        dic["VALUE"] = int(position[3].text.replace(',', ''))*1000
        dic["SHARES"] = int(position[4].text.replace(',', ''))
        dic["DATE"] = date.strip(".html")
        positions.append(dic) 

    if len(rows) != 0:
        holdings_df = pd.DataFrame(positions)
        cusip_nums = holdings_df['CUSIP'].to_list()
        ticker_column = []
        for c in cusip_nums:
            url = "https://www.openfigi.com/search#!?simpleSearchString="+c
            driver = webdriver.Chrome(ChromeDriverManager(version='118').install())
            driver.get(url)
            ticker_elem = driver.find_element_by_css_selector('body > div.outer-wrapper > div.content-wrapper > div > div > div.col-sm-16.col-md-18 > figi-search-grid > div > div > table > tbody > tr:nth-child(1) > td:nth-child(3) > span')
            ticker_column.append(ticker_elem.text)        
        holdings_df["SYMBOL"] = ticker_column
        time.sleep(1)
        holdings_df = pd.DataFrame(positions)
        
        holdings_df['SHARES'] = holdings_df['SHARES'].fillna(0).astype(int)
        holdings_df['VALUE'] = holdings_df['VALUE'].fillna(0).astype(int)
        holdings_df = holdings_df.sort_values(by="VALUE", ascending=False)
        holdings_df['DATE'] = holdings_df['DATE'].astype('datetime64[ns]')
        holdings_df= holdings_df[['SYMBOL','NAME_OF_ISSUER','VALUE','SHARES','DATE','TITLE_OF_CLASS','CUSIP']]
        temp = 'temp_'+fund_table_name
        script = '''
                    INSERT OR IGNORE INTO '''+ fund_table_name+''' 
                    SELECT * FROM '''+ '''temp_'''+fund_table_name+''';
                    SELECT * FROM '''+fund_table_name+''' 
                    ORDER BY [DATE] DESC;
                            '''
        holdings_df.to_sql(temp, conn, if_exists='replace', index=False)
        cur.executescript(script)
        conn.commit()
        cur.close()

#VARIABLES TO INPUT
try:
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    fund_table_name = 'hf_bvf' #i.e. hf_orbimed
except sqlite3.Error as error:
    print("Failed to connect to the fund table", error)  
finally:
        if (conn):
            conn.close()

conn2 = sqlite3.connect('SEC scraper/Database.db')
cursor2 = conn2.cursor()
cursor2.execute('SELECT cik FROM CompanyInformation')
#CIKs = cursor2.fetchall()
conn2.close()
CIKs = ['0001633313','0001263508', '0001595855']#,'0001056807', '0001534261','0001055951','0001224962','0001603466','0001346824','0001037389','0001748240']
print(CIKs)

n=8 #number of 13f reports to pull
type = '13f'

#String for Creating the new hedge fund table
stringcreate='''CREATE TABLE IF NOT EXISTS '''+ fund_table_name +''' (
    SYMBOL TEXT,
    NAME_OF_ISSUER TEXT, 
    VALUE INTEGER, 
    SHARES INTEGER, 
    DATE DATE, 
    TITLE_OF_CLASS TEXT, 
    CUSIP TEXT)'''

#String for Creating the unique index for the table so rows do not get dupliated
stringindex = '''CREATE UNIQUE INDEX '''+ '''index_'''+ fund_table_name+ ''' ON '''+fund_table_name+''' (
    SYMBOL,
    NAME_OF_ISSUER,
    VALUE,
    SHARES,
    DATE,
    TITLE_OF_CLASS,
    CUSIP
);'''


#Creating the table
try:
    conn = sqlite3.connect("Database.db")
    cur = conn.cursor()
    cur.execute(stringcreate)
    cur.execute(stringindex)
    conn.commit()
    cur.close()
except sqlite3.Error as error:
    print("Failed to connect to create table", error)  


# Obtain HTML for search page
for cik in CIKs:
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&count=100&type={}"
    edgar_resp = doGet(base_url.format(cik,type))
#try:    
    edgar_str = edgar_resp.text

# Find the document link
    doc_link = ''
    soup = BeautifulSoup(edgar_str, 'html.parser')
    table_tag = soup.find('table', class_='tableFile2')
    rows = table_tag.find_all('tr')


#Table of all recent listings:
    table = soup.find_all('table')
    filings_df = pd.read_html(str(table))[2].head(10)
    filings_df['URL'] = ''
    for index,row in zip(filings_df.index.to_list(),rows[1:]):
        cells = row.find_all('td')
        s1 = cells[1].a['href']
        s2 = s1.rsplit('/', 1)[0]
        if len(cells) > 3:
            try:
                doc_link = 'https://www.sec.gov'+s2+'/xslForm13F_X01/infotable.xml'
                filings_df.loc[index,'URL'] = doc_link
                time.sleep(1)
            except:
                continue
# filings_df = filings_df.groupby('Filings').head(2).reset_index(drop=True)
# filings_df['URL'] = filings_df['URL'].apply(lambda x: '<a href="{0}" target="_blank">{0}</a>'.format(x))
    filings_df = filings_df[~filings_df.Description.str.contains("Amend")]
    filings_df['isAmmended'] = False
    filings_df = filings_df.head(n)
    filings_df = filings_df.reset_index(drop=True)
    ammended_filings_df = filings_df[filings_df.Description.str.contains("Amend")]
    ammended_filings_df['isAmmended'] = False
    ammended_filings_df = ammended_filings_df.head(n)
    ammended_filings_df = ammended_filings_df.reset_index(drop=True)
    for date, url in zip(filings_df['Filing Date'], filings_df.URL):
        scrape_13f(date,url)
    for date, url in zip(ammended_filings_df['Filing Date'], ammended_filings_df.URL):
        scrape_13f(date,url)
    # except AttributeError as error:
    #     print(error)
    #     print(cik)

