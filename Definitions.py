import pandas as pd
from yahooquery import Ticker
import sqlite3
from bs4 import BeautifulSoup
import datetime
from datetime import date
import matplotlib.pyplot as plt 
import textwrap
import numpy as np
import requests
import sys
from IPython.display import HTML
import contextlib
import pandas.io.formats.format as pf
import time
sqlite3.register_adapter(np.int64, lambda val: int(val))
from dateutil.relativedelta import relativedelta
import math

#returns the string of a number with B for billion, M for million, K for thousand
# def format_number(n):
#     if n is None:
#         return n
    
#     else:
#         sign = -1 if n<0 else 1
#         if abs(n) >= 1e9:
#             return '{}{}B'.format('-' if sign == -1 else '', abs(n) // 1e9)
#         elif abs(n) >= 1e6:
#             return '{}{}M'.format('-' if sign == -1 else '', abs(n) // 1e6)
#         elif abs(n) >= 1e3:
#             return '{}{}K'.format('-' if sign == -1 else '', abs(n) // 1e3)
#         else:
#             return '{}{}'.format('-' if sign == -1 else '', abs(n))


def format_number(n):
    if n is None:
        return n
    else:
        sign = -1 if n < 0 else 1
        if abs(n) >= 1e9:
            num = abs(n) / 1e9
            if num.is_integer():
                return '{}{}B'.format('-' if sign == -1 else '', int(num))
            else:
                return '{}{:.1f}B'.format('-' if sign == -1 else '', round(num, 1))
        elif abs(n) >= 1e6:
            num = abs(n) / 1e6
            if num.is_integer():
                return '{}{}M'.format('-' if sign == -1 else '', int(num))
            else:
                return '{}{:.1f}M'.format('-' if sign == -1 else '', round(num, 1))
        elif abs(n) >= 1e3:
            num = abs(n) / 1e3
            if num.is_integer():
                return '{}{}K'.format('-' if sign == -1 else '', int(num))
            else:
                return '{}{:.1f}K'.format('-' if sign == -1 else '', round(num, 1))
        else:
            num = abs(n)
            if num.is_integer():
                return '{}{}'.format('-' if sign == -1 else '', int(num))
            else:
                return '{}{:.1f}'.format('-' if sign == -1 else '', round(num, 1))


def get_date_two_weeks_ago():
    # Get today's date
    today = datetime.date.today()

    # Subtract 15 days from today
    fifteen_days_ago = today - datetime.timedelta(days=15)

    # Adjust the date to the preceding weekday if it falls on a Saturday or Sunday
    while fifteen_days_ago.weekday() >= 5:  # Saturday or Sunday
        fifteen_days_ago -= datetime.timedelta(days=1)

    # Get the string representation of the date
    date_string = fifteen_days_ago.strftime("%Y-%m-%d")

    return date_string

def get_date_two_months_ago():
    # Get today's date
    today = datetime.date.today()

    # Subtract 15 days from today
    fifteen_days_ago = today - datetime.timedelta(days=62)

    # Adjust the date to the preceding weekday if it falls on a Saturday or Sunday
    while fifteen_days_ago.weekday() >= 5:  # Saturday or Sunday
        fifteen_days_ago -= datetime.timedelta(days=1)

    # Get the string representation of the date
    date_string = fifteen_days_ago.strftime("%Y-%m-%d")

    return date_string


def get_date_one_year_ago():

    # Get today's date
    today = datetime.date.today()

    # Subtract 15 days from today
    one_year_ago = today - relativedelta(years=1)- datetime.timedelta(days=1)

    # Adjust the date to the preceding weekday if it falls on a Saturday or Sunday
    while one_year_ago.weekday() >= 5:  # Saturday or Sunday
        one_year_ago -= datetime.timedelta(days=1)

    # Get the string representation of the date
    date_string = one_year_ago.strftime("%Y-%m-%d")

    return date_string



def make_clickable(val):
    # target _blank to open new window
    return '<a target="_blank" href="{}">{}</a>'.format(val, val)
    
# class _IntArrayFormatter(pd.io.formats.format.GenericArrayFormatter):

#     def _format_strings(self):
#         formatter = self.formatter or (lambda x: ' {:,}'.format(x))
#         fmt_values = [formatter(x) for x in self.values]
#         return fmt_values
# #-------------------------------------------

#This script allows to display integers with commas if the following is used:         
# with custom_formatting():
#            display(df)
@contextlib.contextmanager
def custom_formatting():
    orig_float_format = pd.options.display.float_format
    orig_int_format = pf.IntArrayFormatter

    pd.options.display.float_format = '{:0,.2f}'.format
    class IntArrayFormatter(pf.GenericArrayFormatter):
        def _format_strings(self):
            formatter = self.formatter or '{:,d}'.format
            fmt_values = [formatter(x) for x in self.values]
            return fmt_values
    pf.IntArrayFormatter = IntArrayFormatter
    yield
    pd.options.display.float_format = orig_float_format
    pf.IntArrayFormatter = orig_int_format





def tickerhelp():
    print('''
    Stock's Company related:
    summary(''): Company summary 
    web(''): Company website
    sp(''), sps('') (for short version):  Summary profile
    salaries(''): Executive Salaries
    news(''): Recent news (yahoo)
    links(''): Helpful links
    
    Stock related:
    exchange(''):Stock exchange, along with date it started trading
    trend(''): Stock trend
    pctchange(''): Stock % change
    pc(''), pcs('') (for short version): Stock price
    ks(''), kss_new('') kss_old('') (for short version): Key statistics
    validate(''): Validate a ticker

    
    Stock Financials:
    bs('') , bss('') (for short version): Balance sheet
    fs('') , fss('') (for short version): Financial statement
    cf(''), cfs('') (for short version): Cash flows
    cash(''): time to 0$ cash based on cash burn
    dilution(''): Dilution SEC filings

    Stock Ownership:
    mhs(''): Major holders (from Yahoo)
    insiders(''): Insider activity (Buyers/sellers for the past 12 months)
    biotech_hf(''): Biotech hedge funds positionning (Perceptive, Baker Brothers...) from the latest 13F SEC filings
    institutions(''): Institutional Ownnership
    
    Drug related:
    pipeline (''): pulls the drug pipeline of a particular stock
    catalyst(''): pulls the drug catalysts of a particular stock
    search():asks for a word to look up in all the pipeline data
    catalystsall(): generates the whole dataframe of catalysts from the CSV file
    catalysts_update():updates the whole dataframe of catalysts and saves it to the CSV file
    pipeline_update():updates the pipeline of drugs of all companies with their news links, phase of study, and status
    clinical_trials('drug'): looks up a drug in clinicaltrials.gov and results a dataframe of all studies
    
    Database:
    database(): calls in df_bio, my main database
    add('symbol'): adds symbol to database along with report data
    clean(): cleans database from invalid tickers
    remove(''): removes a particular ticker from the database
    update(): update all tickers 
    add_list(): adds the items in symbol (separated by ',') to database
    add_new_from_list(): compares database list to symbol list and only adds itmes not in database
    add_later():adds tickers not yet on the market (IPO...) to add_later_list.pkl
    add_add_later_list():Calls the add_later_list and checks if its tickers are already in the database, if not it tries to add them then updates the list named add_later_list.pkl accordingly
    summary_search(): asks for a word to look up in all the database summaries
    ct_search(): searches for a word in the ClinicalTrials.Gov database
    
    Insider activity in the database:
    insiders_buy(): displays the most recent insider buyin activity of stocks in the database
    insiders_all(): displays the most recent insider activity of stocks in the database     
    
    Feeds:
    news(): News feed
    journals(): new publications in medical journals
    ''')   







def doGet(url):
    s = requests.Session()
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Sec-CH-UA': 'Examplary Browser',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': "Windows",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "authority": "www.sec.gov",
        "method": "GET",
        "path": "/Archives/edgar/data/59478/000120919121046268/0001209191-21-046268-index.htm",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip deflate br",
        "accept-language": "en-US,en;q=0.9,ar-LB;q=0.8,ar;q=0.7",
        "cache-control": "max-age=0"}


    r = None
    proxies = {
        'http': 'socks5://127.0.0.1:9050',
        'https': 'socks5://127.0.0.1:9050'
    }
    try:
        r = s.get(url, headers=headers)

        if r.status_code == 403:
            i = 1
            while r.status_code == 403 and i <= 10:
                print("Status code: " + str(r.status_code) + "  for : " + url)
                time.sleep(1)
                r = s.get(url, headers=headers, proxies = proxies)
                i += 1
        # print("Status code: " + str(r.status_code) + "  for : " + url)
        # r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("Http Error: " + errh + " for url: " + url)
        if r.get_status_code == 403:
            i = 1
            while r.status_code == 403 and i <= 10:
                time.sleep(i)
                r = s.get(url, headers=headers)
                i += 1
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting: " + str(errc) + "  for : " + url)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error: " + str(errt) + "  for : " + url)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else" + str(err) + "  for : " + url)

    return r

def earnings_df(symbol):
    from dateutil import parser
    import requests
    from bs4 import BeautifulSoup
    import requests
    import pandas as pd
    import sqlite3
    import datetime

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }

    # Make a request to the Yahoo Finance website
    url = f'https://finance.yahoo.com/calendar/earnings?symbol={symbol}'
    response = requests.get(url, headers=headers)

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the earnings data table in the HTML
    table = soup.find('table', {'class': 'W(100%)'})

    # If the table element was not found, print a message and exit
    if table is None:
        print(f"Earnings data for {symbol} not found or the class attribute for the table element might have changed.")
        exit()
        
    # Extract the rows from the table
    rows = table.find_all('tr')

    # Create an empty list to store the data
    data = []

    # Iterate through the rows and store the earnings data in a list
    for row in rows:
        cells = row.find_all('td')
        if len(cells)>0:
            symbol = cells[0].text.strip()
            company = cells[1].text.strip()
            earnings_date = cells[2].text.strip()
            EPS_estimate = cells[3].text.strip()
            reported_EPS = cells[4].text.strip()
            surprise= cells[5].text.strip()
            data.append([symbol,company, earnings_date, EPS_estimate, reported_EPS,surprise])

    # Create a dataframe from the list
    df = pd.DataFrame(data, columns=['symbol','Company','Earnings Date','EPS_estimate','Reported EPS', 'Surprise(%)'])
    df["Earnings Date"] = df["Earnings Date"].str.replace(r"([A-Z]{2})([A-Z]+)", r"\1 \2", regex=True)
    df["Earnings Date"] = df["Earnings Date"].apply(lambda x: parser.parse(x))
    df["EPS_estimate"] = pd.to_numeric(df["EPS_estimate"], errors='coerce')
    # earnings_date = df.loc[df['EPS_estimate'].notnull(), 'Earnings Date'].iloc[0]
    # if earnings_date.date() < datetime.date.today():
    #     earnings_date = 'NA'
    # else:
    #     earnings_date = str(earnings_date.date())
    return df


def earnings_estimates(symbol):
    from yahooquery import Ticker
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)

    df_estimates = pd.DataFrame
    df_estimates

    list_et = ticker.earnings_trend.get(symbol).get('trend')
    list_et
    df_et = pd.concat([pd.DataFrame(l) for l in list_et],axis=1).T
    df_et

    df1 = pd.DataFrame(list_et[0].get('earningsEstimate').items(), columns = [symbol,list_et[0]['endDate']+'_Estimate'])
    df1[symbol] = 'EPS_' + df1[symbol].astype(str)
    df1 = df1.set_index(symbol)
    df1

    df2 = pd.DataFrame(list_et[0].get('revenueEstimate').items(), columns = [symbol,list_et[0]['endDate']+'_Estimate'])
    df2[symbol] = 'Revenue_' + df2[symbol].astype(str)
    df2 = df2.set_index(symbol)
    df2.loc['Revenue_avg'] = df2.loc['Revenue_avg'].apply(np.float64)
    df2.loc['Revenue_high'] = df2.loc['Revenue_high'].apply(np.float64)
    df2.loc['Revenue_low'] = df2.loc['Revenue_low'].apply(np.float64)
    df2

    df3 = pd.DataFrame(list_et[0].get('epsTrend').items(), columns = [symbol,list_et[0]['endDate']+'_Estimate'])
    df3[symbol] = 'EPS_' + df3[symbol].astype(str)
    df3 = df3.set_index(symbol)
    df4 = pd.DataFrame(list_et[0].get('epsRevisions').items(), columns = [symbol,list_et[0]['endDate']+'_Estimate'])
    df4[symbol] = 'EPS_Revision_' + df4[symbol].astype(str)
    df4 = df4.set_index(symbol)
    df5 = pd.concat([df1,df2,df3,df4])
    df5


    df11 = pd.DataFrame(list_et[1].get('earningsEstimate').items(), columns = [symbol,list_et[1]['endDate']+'_Estimate'])
    df11[symbol] = 'EPS_' + df11[symbol].astype(str)
    df11 = df11.set_index(symbol)
    df11

    df22 = pd.DataFrame(list_et[1].get('revenueEstimate').items(), columns = [symbol,list_et[1]['endDate']+'_Estimate'])
    df22[symbol] = 'Revenue_' + df22[symbol].astype(str)
    df22 = df22.set_index(symbol)
    df22.loc['Revenue_avg'] = df22.loc['Revenue_avg'].apply(np.float64)
    df22.loc['Revenue_high'] = df22.loc['Revenue_high'].apply(np.float64)
    df22.loc['Revenue_low'] = df22.loc['Revenue_low'].apply(np.float64)
    df22

    df33 = pd.DataFrame(list_et[1].get('epsTrend').items(), columns = [symbol,list_et[1]['endDate']+'_Estimate'])
    df33[symbol] = 'EPS_' + df33[symbol].astype(str)
    df33 = df33.set_index(symbol)
    df44 = pd.DataFrame(list_et[1].get('epsRevisions').items(), columns = [symbol,list_et[1]['endDate']+'_Estimate'])
    df44[symbol] = 'EPS_Revision_' + df44[symbol].astype(str)
    df44 = df44.set_index(symbol)
    df55 = pd.concat([df11,df22,df33,df44])
    df55

    dfall = pd.merge(left=df5, right=df55, how='left', left_on=symbol, right_on=symbol)
    return dfall

def last_dilution(symbol):
    import requests
    from Definitions import doGet
    from bs4 import BeautifulSoup

    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={symbol}&type=424b&owner=exclude&count=100"


    response = doGet(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the table of filings
    table = soup.find('table', class_='tableFile2')
    rows = table.find_all('tr')

    # Find the latest 424b filing
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 0:
            filing_type = cells[0].text.strip()
            if filing_type.startswith('424B'):
                filing_date = cells[3].text.strip()
                # Print the filing date
                print(f"Last 424b on {filing_date}")
                link = 'http://sec.gov'+cells[1].a['href']
                print(f'link: {link}')
                break
            else:
                print('')

def earnings_date(symbol):
    from dateutil import parser
    import requests
    from bs4 import BeautifulSoup
    import requests
    import pandas as pd
    import sqlite3
    import datetime
    from datetime import  timedelta

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
    }

    # Make a request to the Yahoo Finance website
    url = f'https://finance.yahoo.com/calendar/earnings?symbol={symbol}'
    response = requests.get(url, headers=headers)

    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the earnings data table in the HTML
    table = soup.find('table', {'class': 'W(100%)'})

    # If the table element was not found, print a message and exit
    if table is None:
        print(f"Earnings data for {symbol} not found or the class attribute for the table element might have changed.")
        exit()
        
    # Extract the rows from the table
    rows = table.find_all('tr')

    # Create an empty list to store the data
    data = []

    # Iterate through the rows and store the earnings data in a list
    for row in rows:
        cells = row.find_all('td')
        if len(cells)>0:
            symbol = cells[0].text.strip()
            company = cells[1].text.strip()
            earnings_date = cells[2].text.strip()
            EPS_estimate = cells[3].text.strip()
            reported_EPS = cells[4].text.strip()
            surprise= cells[5].text.strip()
            data.append([symbol,company, earnings_date, EPS_estimate, reported_EPS,surprise])

    # Create a dataframe from the list
    df = pd.DataFrame(data, columns=['symbol','Company','Earnings Date','EPS_estimate','Reported EPS', 'Surprise(%)'])
    df["Earnings Date"] = df["Earnings Date"].str.replace(r"([A-Z]{2})([A-Z]+)", r"\1 \2", regex=True)
    df["Earnings Date"] = df["Earnings Date"].apply(lambda x: parser.parse(x))
    df["EPS_estimate"] = pd.to_numeric(df["EPS_estimate"], errors='coerce')

    dates = df["Earnings Date"].to_list()
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

    filtered_timestamps = [timestamp for timestamp in dates if timestamp.date() >= today.date()]

    closest_date = min(filtered_timestamps, key=lambda date: date.date() - datetime.date.today() )
    earnings_date = str(closest_date.date())
    return earnings_date

def auto_note(symbol):
    symbol = symbol.upper()
    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")  
        sql_query = f"""
            SELECT *
            FROM Auto_note WHERE symbol = '{symbol}'
    ;"""
        auto_note_df = pd.read_sql_query(sql_query, conn)

    except Exception as e:
        print(f'Failed to get {symbol}',e)
        pass

    finally:
        if (conn):
            conn.close()
    if  auto_note_df.empty:
        auto_note1 = str(f'{symbol} not in the biotech database. ')
        funds =1
        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")  
            sql_query = f"""
                SELECT *
                FROM catalysts_bfc WHERE symbol = '{symbol}'
        ;"""
            auto_note_df = pd.read_sql_query(sql_query, conn)
        except Exception as e:
            print(f'Failed to get {symbol}',e)
            pass
        finally:
            if (conn):
                conn.close()

        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")  
            sql_query = f"""
                SELECT *
                FROM HF_current_holdings WHERE symbol = '{symbol}'
        ;"""
            funds_df = pd.read_sql_query(sql_query, conn)
        except Exception as e:
            print(f'Failed to get {symbol}',e)
            pass
        finally:
            if (conn):
                conn.close()


    else:
        funds = 0
        m_c = format_number(auto_note_df['Mkt. Cap'][0])
        try:
            float = format_number(auto_note_df['Float'][0])
        except:
            float = 'NA'
            pass
        cash = format_number(auto_note_df['Cash/Short Term Inv.'][0])
        ev = format_number(auto_note_df['EV'][0])
        try:
            months_to_0 = format_number(auto_note_df['Months to 0$'][0])
        except:
            months_to_0 = 'NA'
            pass            
        ev = format_number(auto_note_df['EV'][0])
        try:
            insider_3m = format_number(auto_note_df['Net Activity (3M)'][0])
        except:
            insider_3m = 'NA'
            pass
        try:
            insider_12m = format_number(auto_note_df['Net Activity (12M)'][0])
        except:
            insider_12m = 'NA'
            pass
        auto_note1 = str(f"${m_c} MC, {float} float, ${ev} EV, ${cash} cash, {months_to_0} Mo to 0$. \
Insiders {insider_3m} (3Mo), {insider_12m} (12Mo).")
    try:
        stage = auto_note_df['Stage'][0]
        date = auto_note_df['Catalyst Date'][0]
        drug = auto_note_df['Drug'][0]
        indication = auto_note_df['Indication'][0]
        catalyst = str(f'{date} - {symbol} {stage} for {drug} in {indication}')
        if not date:
            catalyst = f'No Catalyst for {symbol}'
    except:
        catalyst = f'No Catalyst for {symbol}'
        pass


    if funds ==1:
        try:
            funds = (', ').join(funds_df['FUND'].unique().tolist())
            if not funds:
                funds = 'None'
        except:
            funds = 'None'
            pass
    else:
        try:
            funds = (', ').join(auto_note_df['FUND'].unique().tolist())
        except:
            funds = 'None'
            pass

    auto_note2= str(f"{catalyst}. Funds: {funds}. ")

    def earnings_date(symbol):
        from dateutil import parser
        import requests
        from bs4 import BeautifulSoup
        import requests
        import pandas as pd
        import sqlite3

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
        }

        # Make a request to the Yahoo Finance website
        url = f'https://finance.yahoo.com/calendar/earnings?symbol={symbol}'
        response = requests.get(url, headers=headers)

        # Parse the HTML response using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the earnings data table in the HTML
        table = soup.find('table', {'class': 'W(100%)'})

        # If the table element was not found, print a message and exit
        if table is None:
            print(f"Earnings data for {symbol} not found or the class attribute for the table element might have changed.")
            exit()
            
        # Extract the rows from the table
        rows = table.find_all('tr')

        # Create an empty list to store the data
        data = []

        # Iterate through the rows and store the earnings data in a list
        for row in rows:
            cells = row.find_all('td')
            if len(cells)>0:
                symbol = cells[0].text.strip()
                company = cells[1].text.strip()
                earnings_date = cells[2].text.strip()
                EPS_estimate = cells[3].text.strip()
                reported_EPS = cells[4].text.strip()
                surprise= cells[5].text.strip()
                data.append([symbol,company, earnings_date, EPS_estimate, reported_EPS,surprise])

        # Create a dataframe from the list
        df = pd.DataFrame(data, columns=['symbol','Company','Earnings Date','EPS_estimate','Reported EPS', 'Surprise(%)'])
        df["Earnings Date"] = df["Earnings Date"].str.replace(r"([A-Z]{2})([A-Z]+)", r"\1 \2", regex=True)
        df["Earnings Date"] = df["Earnings Date"].apply(lambda x: parser.parse(x))
        df["EPS_estimate"] = pd.to_numeric(df["EPS_estimate"], errors='coerce')
        earnings_date = df.loc[df['EPS_estimate'].notnull(), 'Earnings Date'].iloc[0]
        if earnings_date.date() < datetime.date.today():
            earnings_date = 'NA'
        else:
            earnings_date = str(earnings_date.date())
        return earnings_date
        
    try:    
        earnings_date_str = earnings_date(symbol)
        earnings_date_str = earnings_date(symbol)
        if  len(earnings_date_str) == 0:
            auto_note3 = ""
        else:
            auto_note3 = str(f' ER {earnings_date_str}.')
    except:
        auto_note3 = ""
        pass

    def last_dilution(symbol):
        import requests
        from Definitions import doGet
        from bs4 import BeautifulSoup

        url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={symbol}&type=424b&owner=exclude&count=100"


        response = doGet(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table of filings
        table = soup.find('table', class_='tableFile2')
        rows = table.find_all('tr')

        # Find the latest 424b filing
        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 0:
                filing_type = cells[0].text.strip()
                if filing_type.startswith('424B'):
                    filing_date = cells[3].text.strip()
                    # Print the filing date
                    link = 'http://sec.gov'+cells[1].a['href']
                    break
        return filing_date,link

    try:    
        filing_date,link = last_dilution(symbol)
        if  len(filing_date) == 0:
            auto_note4 = ""
        else:
            auto_note4 = str(f' Dilution {filing_date}. Link: {link}')
    except:
        auto_note4 = ""
        pass

    auto_note = auto_note2+auto_note1+auto_note3+auto_note4
    return print(auto_note)
    
#-------------------------------------------
def trend(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 3, 1)
    ax1.set_title('1 Month Chart')
    ax2 = fig.add_subplot(1, 3, 2)
    ax2.set_title('3 Month Chart')
    ax3 = fig.add_subplot(1, 3, 3)
    ax3.set_title('1 Year Chart')

    df_1m = ticker.history(period='1mo')
    df_3m = ticker.history(period='3mo')
    df_1y = ticker.history(period='1y')


    df_1m = df_1m.reset_index(level=['date'])
    df_3m = df_3m.reset_index(level=['date'])
    df_1y = df_1y.reset_index(level=['date'])
    # # print(plt.plot(df_1m['adjclose']))
    # # print(plt.plot(df_3m['adjclose']))
    # # print(plt.plot(df_1y['adjclose']))

    ax1.plot(df_1m['date'],df_1m['close'])
    ax2.plot(df_3m['date'],df_3m['close'])
    ax3.plot(df_1y['date'],df_1y['close'])
    # fig = plt.gcf()
    fig.set_size_inches(13, 2)
    fig.autofmt_xdate()
    return(plt.show())

#-------------------------------------------

def pctchange(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_pc1 = pd.DataFrame.from_dict(ticker.price, orient='index')
    try:

        df_1m = ticker.history(period='1mo')
        df_3m = ticker.history(period='3mo')
        df_1y = ticker.history(period='1y')

        Close1Mo = float(df_1m.head(1)['close'].iloc[0])
        Close3Mo = float(df_3m.head(1)['close'].iloc[0])
        Close1Y = float(df_1y.head(1)['close'].iloc[0])
        PriceToday = float(df_pc1['regularMarketPrice'].iloc[0])

        close = [{'PriceToday':PriceToday,'Close1Mo':Close1Mo, 'Close3Mo':Close3Mo,'Close1Y':Close1Y}]
        df_close =pd.DataFrame(close, index = symbols)
        df_close['1 Month Percentage Change'] = (df_close['PriceToday']- df_close['Close1Mo'])/df_close['Close1Mo']
        df_close['3 Month Percentage Change'] = (df_close['PriceToday']- df_close['Close3Mo'])/df_close['Close3Mo']
        df_close['1 Year Percentage Change'] = (df_close['PriceToday']- df_close['Close1Y'])/df_close['Close1Y']
        
        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,df_close['1 Month Percentage Change'][0],df_close['3 Month Percentage Change'][0],df_close['1 Year Percentage Change'][0])
            cur.execute('''
            INSERT INTO biotech (symbol,[1 Month Percentage Change],[3 Month Percentage Change],[1 Year Percentage Change]) 
            VALUES(?,?,?,?)
            ON CONFLICT(symbol) DO UPDATE SET 
            ([1 Month Percentage Change],[3 Month Percentage Change],[1 Year Percentage Change])=
            (excluded.`1 Month Percentage Change`,excluded.`3 Month Percentage Change`,excluded.`1 Year Percentage Change`)''',
            values
            )
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add pctchange", error)                                
        finally:
            if (conn):
                conn.close()

        df_close['1 Month Percentage Change'] = df_close['1 Month Percentage Change'].apply('{:.2%}'.format)
        df_close['3 Month Percentage Change'] = df_close['3 Month Percentage Change'].apply('{:.2%}'.format)
        df_close['1 Year Percentage Change'] = df_close['1 Year Percentage Change'].apply('{:.2%}'.format)
        df_pct = df_close.drop(columns= ['PriceToday','Close1Mo','Close3Mo','Close1Y'])
        return (df_pct)

    except Exception as e: 
        print(e)
        pass

#--------------------------------------------

def web(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_sp1 = pd.DataFrame.from_dict(ticker.summary_profile, orient='index')
    df_sp2 = df_sp1.add_suffix('_sp')
    try:
        df_web1 = df_sp2['website_sp']
        df_web2= df_web1.iloc[0]

        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,df_web2)
            # cur.execute("UPDATE biotech SET Web = ? WHERE symbol = ?", values )
            # cur.execute("update biotech set Web=? where symbol=?", values)
            cur.execute("""
            INSERT INTO biotech(symbol,Web) 
            VALUES(?,?)
            ON CONFLICT(symbol) DO UPDATE SET Web=excluded.Web""",
            values 
            )
            
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add pctchange", error)                                
        finally:
            if (conn):
                conn.close()              
        print(df_web2)
        
    except Exception as e: 
        print(e)
        pass
    
def web2(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_sp1 = pd.DataFrame.from_dict(ticker.summary_profile, orient='index')
    df_sp2 = df_sp1.add_suffix('_sp')
    try:
        df_web1 = df_sp2['website_sp']
        df_web2= df_web1.iloc[0]

        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,df_web2)
            # cur.execute("UPDATE biotech SET Web = ? WHERE symbol = ?", values )
            # cur.execute("update biotech set Web=? where symbol=?", values)
            cur.execute("""
            INSERT INTO biotech(symbol,Web) 
            VALUES(?,?)
            ON CONFLICT(symbol) DO UPDATE SET Web=excluded.Web""",
            values 
            )
            
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add pctchange", error)    
        finally:
            if (conn):
                conn.close()                             
        return(df_web2)   
        
    except Exception as e: 
        print(e)
        pass
    
#--------------------------------------------
def sp(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_sp1 = pd.DataFrame.from_dict(ticker.summary_profile, orient='index')
    df_sp2 = df_sp1.add_suffix('_sp')
    try:
        return (df_sp2)
    except Exception as e: 
        print(e)
        pass
#--------------------------------------------
def summary(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_sp1 = pd.DataFrame.from_dict(ticker.summary_profile, orient='index')
    df_sp2 = df_sp1.add_suffix('_sp')
    try:
        df_sum1 = df_sp2['longBusinessSummary_sp']
        df_sum2 = df_sum1.iloc[0]
        sum = str(df_sum2)
        print(textwrap.fill(sum, width=70))
        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,sum)
            cur.execute("""
            INSERT INTO biotech(symbol,Summary) 
            VALUES(?,?)
            ON CONFLICT(symbol) DO UPDATE SET Summary=excluded.Summary""",
            values 
            )
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add summary", error)                                
        finally:
            if (conn):
                conn.close()

    except Exception as e: 
        print(e)
        pass

#--------------------------------------------

def summary2(symbol):#Code identical to summary except for I removed the print command so I get no output
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_sp1 = pd.DataFrame.from_dict(ticker.summary_profile, orient='index')
    df_sp2 = df_sp1.add_suffix('_sp')
    try:
        df_sum1 = df_sp2['longBusinessSummary_sp']
        df_sum2 = df_sum1.iloc[0]
        sum = str(df_sum2)

        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,sum)
            cur.execute("""
            INSERT INTO biotech(symbol,Summary) 
            VALUES(?,?)
            ON CONFLICT(symbol) DO UPDATE SET Summary=excluded.Summary""",
            values 
            )
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add summary", error)    
        finally:
            if (conn):
                conn.close()

    except Exception as e: 
        print(e)
        pass

#--------------------------------------------   
def exchange(symbol):
    from datetime import datetime

    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        df_exchange = pd.DataFrame.from_dict(ticker.quote_type, orient='index')
        df_exchange = df_exchange[['exchange','firstTradeDateEpochUtc']]
        df_exchange = df_exchange.rename(columns={"exchange": "Exchange", "firstTradeDateEpochUtc": "First Traded"})
        try:
            df_exchange['First Traded'][0] = datetime.strptime(df_exchange['First Traded'][0], '%Y-%m-%d %H:%M:%S')
            df_exchange['First Traded'][0] = df_exchange['First Traded'][0].date()  
        except Exception as e: 
            print(e)
            pass
        df_pc1 = pd.DataFrame.from_dict(ticker.price, orient='index')
        df_pc1 = df_pc1.rename(columns={"exchangeName": "Exchange Name"})
        df_pc2 = df_pc1[['Exchange Name']] 
        df_exchange = df_pc2.join(df_exchange)
        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,df_exchange.loc[symbol,'Exchange Name'],df_exchange.loc[symbol,'First Traded'])
            cur.execute("""
            INSERT INTO biotech(symbol,Exchange,[First Traded]) 
            VALUES(?,?,?)
            ON CONFLICT(symbol) DO UPDATE SET Exchange=excluded.Exchange, [First Traded]=excluded.`First Traded`""",
            values 
            )
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add exchange", error)    
        finally:
            if (conn):
                conn.close()      
        
        return(df_exchange) 
    except Exception as e: 
        print(e)
        pass

#--------------------------------------------

def sps(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_sp1 = pd.DataFrame.from_dict(ticker.summary_profile, orient='index')
    df_sp2 = df_sp1.add_suffix('_sp')
    try: 
        df_sps=df_sp2[['industry_sp','sector_sp','phone_sp']]
        df_sps.columns = [['Industry','Sector','Phone']]

        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,df_sps.loc[symbol,'Industry'][0],df_sps.loc[symbol,'Sector'][0],df_sps.loc[symbol,'Phone'][0])
            cur.execute("""
            INSERT INTO biotech(symbol,Industry,Sector,Phone) 
            VALUES(?,?,?,?)
            ON CONFLICT(symbol) DO UPDATE SET Industry=excluded.Industry, Sector=excluded.Sector,Phone=excluded.Phone""",
            values 
            )
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add sps", error)    
        finally:
            if (conn):
                conn.close()

        return (df_sps)
    except Exception as e: 
        print(e)
        pass
#-------------------------------------------------------


def pc(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_pc1 = pd.DataFrame.from_dict(ticker.price, orient='index')
    df_pc2 = df_pc1.add_suffix('_pc')
    return (df_pc2)

def pcs(symbol):
    import numpy as np
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        df_pc1 = pd.DataFrame.from_dict(ticker.price, orient='index')
        df_pc2 = df_pc1.add_suffix('_pc')
        pc_columns=['shortName_pc','marketCap_pc','regularMarketPrice_pc','regularMarketChangePercent_pc', 'regularMarketVolume_pc' ]
        df_pcs = df_pc2[df_pc2.columns.intersection(pc_columns)]
        df_pcs = df_pcs.rename(columns={'shortName_pc':'Company', 'marketCap_pc':'Mkt. Cap','regularMarketPrice_pc': 'Price','regularMarketChangePercent_pc':'Percent Change', 'regularMarketVolume_pc':'Volume' })
        cols=[i for i in df_pcs.columns if i not in ["Company"]]
        df_pcs[cols] = df_pcs[cols].apply(pd.to_numeric, errors='ignore', downcast='float')
        
        df_pcs = df_pcs[['Company', 'Mkt. Cap', 'Price', 'Percent Change', 'Volume']]   
        if df_pcs['Price'][0] <1:
            df_pcs['Price'] = df_pcs['Price'].apply(lambda x: round(x, 3))
        elif df_pcs['Price'][0] >1:
            df_pcs['Price'] = df_pcs['Price'].apply(lambda x: round(x, 2))

        df_pcs['Mkt. Cap'] = df_pcs['Mkt. Cap'].apply(lambda x: pd.to_numeric(x))
        df_pcs['Volume'] = df_pcs['Volume'].astype(np.float64)
        df_pcs['Percent Change'] = df_pcs['Percent Change'].apply(pd.to_numeric,  errors='ignore', downcast='float')
        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,df_pcs.loc[symbol,'Company'],df_pcs.loc[symbol,'Price'],df_pcs.loc[symbol,'Mkt. Cap'],df_pcs.loc[symbol,'Volume'],df_pcs.loc[symbol,'Percent Change'])
            cur.execute("""
            INSERT INTO biotech(symbol,'Company',Price,[Mkt. Cap],Volume,[Percent Change]) 
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(symbol) DO UPDATE SET Company=excluded.Company, Price=excluded.Price,[Mkt. Cap]=excluded.`Mkt. Cap`,Volume=excluded.Volume,[Percent Change]=excluded.`Percent Change`""",
            values 
            )
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add pcs", error)    
        finally:
            if (conn):
                conn.close()
        df_pcs['Percent Change'] = df_pcs['Percent Change'].apply('{:.2%}'.format)
        return(df_pcs)
    except Exception as e: 
        print(e)
        pass

#-------------------------------------------------------

def quick(symbol):
    from datetime import datetime

    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_price = pd.DataFrame(ticker.price)

    filtered_index_price = ['marketCap','enterpriseValue','sharesOutstanding','floatShares','insidersPercentHeld','institutionsCount','institutionsFloatPercentHeld','institutionsPercentHeld','regularMarketPrice','preMarketPrice','postMarketPrice','DateFirstTraded','DateOfLastReport','Cash/Short Term Inv.','Months to 0$']
    df_price = df_price.reindex(index = filtered_index_price)
    df_price.loc['marketCap'] = df_price.loc['marketCap'].apply(np.float64)
    df_price.loc['regularMarketPrice'] = df_price.loc['regularMarketPrice'].apply(lambda x: round(x, 2))
    df_price.loc['preMarketPrice'] = df_price.loc['preMarketPrice'].apply(lambda x: round(x, 2))
    df_price.loc['postMarketPrice'] = df_price.loc['postMarketPrice'].apply(lambda x: round(x, 2))


    df_mh = pd.DataFrame(ticker.major_holders)
    filtered_index_mh = ['insidersPercentHeld','institutionsCount','institutionsFloatPercentHeld','institutionsPercentHeld']
    df_mh = df_mh.reindex(index = filtered_index_mh)
    df_mh.loc['insidersPercentHeld'] = df_mh.loc['insidersPercentHeld'].apply('{:.2%}'.format)
    df_mh.loc['institutionsFloatPercentHeld'] = df_mh.loc['institutionsFloatPercentHeld'].apply('{:.2%}'.format)
    df_mh.loc['institutionsPercentHeld'] = df_mh.loc['institutionsPercentHeld'].apply('{:.2%}'.format)

    df_ks= pd.DataFrame(ticker.key_stats)
    filtered_index_ks = ['sharesOutstanding','floatShares','enterpriseValue','regularMarketPrice','preMarketPrice','postMarketPrice']
    df_ks = df_ks.reindex(index = filtered_index_ks)
    df_ks.loc['floatShares'] = df_ks.loc['floatShares'].apply(np.float64)
    df_ks.loc['sharesOutstanding'] = df_ks.loc['sharesOutstanding'].apply(np.float64)
    df_ks.loc['enterpriseValue'] = df_ks.loc['enterpriseValue'].apply(np.float64)

    df_exchange = pd.DataFrame.from_dict(ticker.quote_type, orient='index')

    df_price.loc['floatShares'] = df_ks.loc['floatShares']
    df_price.loc['enterpriseValue'] = df_ks.loc['enterpriseValue']
    df_price.loc['sharesOutstanding'] = df_ks.loc['sharesOutstanding']
    df_price.loc['insidersPercentHeld'] = df_mh.loc['insidersPercentHeld']
    df_price.loc['insidersPercentHeld'] = df_price.loc['insidersPercentHeld']
    df_price.loc['institutionsCount'] = df_mh.loc['institutionsCount']
    df_price.loc['institutionsFloatPercentHeld'] = df_mh.loc['institutionsFloatPercentHeld']
    df_price.loc['institutionsPercentHeld'] = df_mh.loc['institutionsPercentHeld']


    global df_bio
    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")
        df_bio = pd.read_sql_query("select * from biotech ORDER BY symbol ASC;", conn)
        df_symbol = df_bio.loc[df_bio['symbol'] == symbol]
    except sqlite3.Error as error:
        print("Failed to select from biotech", error)  
    finally:
        if (conn):
            conn.close()

    df_price.loc['DateFirstTraded'] = datetime.strptime(df_exchange.iloc[0]['firstTradeDateEpochUtc'], '%Y-%m-%d %H:%M:%S').date()
    df_price.loc['Cash/Short Term Inv.'] = df_symbol.iloc[0]['Cash/Short Term Inv.']
    df_price.loc['totalCashPerShare'] = ticker.financial_data[symbol]['totalCashPerShare']
    df_price.loc['Months to 0$'] = df_symbol.iloc[0]['Months to 0$']
    df_price.loc['DateOfLastReport'] = df_symbol.iloc[0]['Date_BS']
    
    return df_price

#-------------------------------------------------------

def bs(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_bs1 = ticker.balance_sheet("q")
    df_bs2 = df_bs1[df_bs1.periodType != 'TTM']
    df_bs3 = df_bs2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
    df_bs4 = df_bs3.add_suffix('_bs')
    return (df_bs4)

def bs1(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_bs1 = ticker.balance_sheet("q")
    df_bs2 = df_bs1[df_bs1.periodType != 'TTM']
    df_bs3 = df_bs2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
    df_bs4 = df_bs3.add_suffix('_bs')
    df_bs1 = df_bs4.groupby('symbol').first()
    return (df_bs1) 

def bss(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        df_bs1 = ticker.balance_sheet("q")
        if str(df_bs1) == str("Balance Sheet data unavailable for " + symbol):
            print ("Balance Sheet data unavailable for " + symbol)
        else:
            df_bs2 = df_bs1[df_bs1.periodType != 'TTM']
            if str(df_bs2['asOfDate'].count()) == '0':
                print('Only TTM Balance Sheet Statement available for '+symbol+', with last report as of '+ str(df_bs1['asOfDate'][0]))
            else:
                df_bs3 = df_bs2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
                df_bs4 = df_bs3.add_suffix('_bs')
                df_bss = df_bs4[['asOfDate_bs','CashCashEquivalentsAndShortTermInvestments_bs','TotalAssets_bs','TotalLiabilitiesNetMinorityInterest_bs','TotalEquityGrossMinorityInterest_bs']]
                df_bss.columns = ['Date','Cash/Short Term Inv.','Tot.Assets','Tot.Liabilities','Tot.Equity']

                try:
                    conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
                    cur = conn.cursor()
                    values = (symbol,df_bss.loc[symbol,'Date'][0].date(),df_bss.loc[symbol,'Cash/Short Term Inv.'][0],df_bss.loc[symbol,'Tot.Assets'][0],df_bss.loc[symbol,'Tot.Liabilities'][0],df_bss.loc[symbol,'Tot.Equity'][0])
                    cur.execute("""
                    INSERT INTO biotech(symbol,'Date_BS',[Cash/Short Term Inv.],[Tot.Assets],[Tot.Liabilities],[Tot.Equity]) 
                    VALUES(?,?,?,?,?,?)
                    ON CONFLICT(symbol) DO UPDATE SET [Date_BS]=excluded.Date_BS, [Cash/Short Term Inv.]=excluded.`Cash/Short Term Inv.`,[Tot.Assets]=excluded.`Tot.Assets`,[Tot.Liabilities]=excluded.`Tot.Liabilities`,[Tot.Equity]=excluded.`Tot.Equity`""",
                    values 
                    )
                    conn.commit()
                    cur.close()
                except sqlite3.Error as error:
                    print("Failed to add bss", error)    
                finally:
                    if (conn):
                        conn.close()

                return(df_bss)
    except Exception as e: 
        print(e)
        pass

def bss1(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_bs1 = ticker.balance_sheet("q")
    df_bs2 = df_bs1[df_bs1.periodType != 'TTM']
    df_bs3 = df_bs2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
    df_bs4 = df_bs3.add_suffix('_bs')
    df_bs1 = df_bs4.groupby('symbol').first()
    df_bss1 = df_bs1[['asOfDate_bs','CashCashEquivalentsAndShortTermInvestments_bs','TotalAssets_bs','TotalLiabilitiesNetMinorityInterest_bs','TotalEquityGrossMinorityInterest_bs']]
    df_bss1.columns = ['Date','Cash/Short Term Inv.','Tot.Assets','Tot.Liabilities','Tot.Equity']    
    return (df_bss1)

#-------------------------------------------------------


def fs(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_is1 = ticker.income_statement("q")
    df_is2 = df_is1[df_is1.periodType != 'TTM']
    df_is3 = df_is2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
    df_is4 = df_is3.add_suffix('_is')
    return(df_is4)

def fs1(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_is1 = ticker.income_statement("q")
    df_is2 = df_is1[df_is1.periodType != 'TTM']
    df_is3 = df_is2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
    df_is4 = df_is3.add_suffix('_is')
    df_is1 = df_is4.groupby('symbol').first()
    return (df_is1)

def fss(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        df_is1 = ticker.income_statement("q")
        if str(df_is1) == str("Income Statement data unavailable for " + symbol):
            print ("Income Statement data unavailable for " + symbol)
        else:
            df_is2 = df_is1[df_is1.periodType != 'TTM']
            if str(df_is2['asOfDate'].count()) == '0':
                print('Only TTM Income Statement available for '+symbol+', with last report as of '+ str(df_is1['asOfDate'][0]))
            else:
                df_is3 = df_is2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
                df_is4 = df_is3.add_suffix('_is')
                df_iss=df_is4[['asOfDate_is','TotalRevenue_is','NetIncome_is']]
                df_iss.columns = ['Date','Tot.Revenue','Net Income']

                try:
                    conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
                    cur = conn.cursor()
                    values = (symbol,df_iss.loc[symbol,'Date'][0].date(),df_iss.loc[symbol,'Tot.Revenue'][0],df_iss.loc[symbol,'Net Income'][0])
                    cur.execute("""
                    INSERT INTO biotech(symbol,'Date_FS',[Tot.Revenue],[Net Income]) 
                    VALUES(?,?,?,?)
                    ON CONFLICT(symbol) DO UPDATE SET [Date_FS]=excluded.Date_FS,[Tot.Revenue]=excluded.`Tot.Revenue`,[Net Income]=excluded.`Net Income`""",
                    values 
                    )
                    conn.commit()
                    cur.close()
                except sqlite3.Error as error:
                    print("Failed to add fss", error)    
                finally:
                    if (conn):
                        conn.close()
                return(df_iss)

    except Exception as e: 
        print(e)
        pass

def fss1(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_is1 = ticker.income_statement("q")
    df_is2 = df_is1[df_is1.periodType != 'TTM']
    df_is3 = df_is2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
    df_is4 = df_is3.add_suffix('_is')
    df_is1 = df_is4.groupby('symbol').first()
    df_iss1=df_is1[['asOfDate_is','TotalRevenue_is','NetIncome_is']]
    df_iss1.columns = ['Date','Tot.Revenue','Net Income']
    return (df_iss1)

#-------------------------------------------------------



def cf(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_cf1 = ticker.cash_flow("q")
    df_cf2 = df_cf1[df_cf1.periodType != 'TTM']
    df_cf3 = df_cf2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
    df_cf4 = df_cf3.add_suffix('_cf')
    return (df_cf4)

def cf1(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_cf1 = ticker.cash_flow("q")
    df_cf2 = df_cf1[df_cf1.periodType != 'TTM']
    df_cf3 = df_cf2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
    df_cf4 = df_cf3.add_suffix('_cf')
    df_cf1 = df_cf4.groupby('symbol').first()
    return (df_cf1)

def cfs(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        df_cf1 = ticker.cash_flow("q")
        if str(df_cf1) == str("Cash Flow data unavailable for " + symbol):
            print ("Cash Flow data unavailable for " + symbol)
        else:
            df_cf2 = df_cf1[df_cf1.periodType != 'TTM']
            if str(df_cf2['asOfDate'].count()) == '0':
                print('Only TTM Cash Flow available for '+symbol+', with last report as of '+ str(df_cf1['asOfDate'][0]))
            else:
                df_cf3 = df_cf2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
                df_cf4 = df_cf3.add_suffix('_cf')
                df_cfs=df_cf4[['asOfDate_cf','FreeCashFlow_cf']]
                df_cfs.columns = ['Date','Free Cash Flow']

                try:
                    conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
                    cur = conn.cursor()
                    values = (symbol,df_cfs.loc[symbol,'Date'][0].date(),df_cfs.loc[symbol,'Free Cash Flow'][0])
                    cur.execute("""
                    INSERT INTO biotech(symbol,'Date_CF',[Free Cash Flow]) 
                    VALUES(?,?,?)
                    ON CONFLICT(symbol) DO UPDATE SET [Date_CF]=excluded.Date_CF,[Free Cash Flow]=excluded.`Free Cash Flow`""",
                    values 
                    )
                    conn.commit()
                    cur.close()
                except sqlite3.Error as error:
                    print("Failed to add cfs", error)    
                finally:
                    if (conn):
                        conn.close()
                return(df_cfs)
    except Exception as e: 
        print(e)
        pass

def cfs1(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_cf1 = ticker.cash_flow("q")
    df_cf2 = df_cf1[df_cf1.periodType != 'TTM']
    df_cf3 = df_cf2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
    df_cf4 = df_cf3.add_suffix('_cf')
    df_cf1 = df_cf4.groupby('symbol').first()
    df_cfs1=df_cf1[['asOfDate_cf','FreeCashFlow_cf']]
    df_cfs1.columns = ['Date','Free Cash Flow']
    return (df_cfs1)

#-------------------------------------------------------
def cash(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    pd.options.mode.chained_assignment = None
    try:
        df_bs1 = ticker.balance_sheet("q")
        if str(df_bs1) == str("Balance Sheet data unavailable for " + symbol):
            print ("Cash Burn can not be calculated for " + symbol)
        else:
            df_bs2 = df_bs1[df_bs1.periodType != 'TTM']
            if str(df_bs2['asOfDate'].count()) == '0':
                print("Cash Burn can not be calculated for " + symbol)
            else:
                df_bs3 = df_bs2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
                df_bs4 = df_bs3.add_suffix('_bs')
                df_bs1 = df_bs4.groupby('symbol').first()
                df_bss1 = df_bs1[['asOfDate_bs','CashCashEquivalentsAndShortTermInvestments_bs','TotalAssets_bs','TotalLiabilitiesNetMinorityInterest_bs','TotalEquityGrossMinorityInterest_bs']]
                df_bss1.columns = ['Date','Cash/Short Term Inv.','Tot.Assets','Tot.Liabilities','Tot.Equity']
                
                df_cf1 = ticker.cash_flow("q")
                if str(df_cf1) == str("Cash Flow data unavailable for " + symbol):
                    print ("Cash Burn can not be calculated for " + symbol)
                else:
                    df_cf2 = df_cf1[df_cf1.periodType != 'TTM']
                    if str(df_cf2['asOfDate'].count()) == '0':
                        print("Cash Burn can not be calculated for " + symbol)
                    else:
                        df_cf3 = df_cf2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
                        df_cf4 = df_cf3.add_suffix('_cf')
                        df_cf1 = df_cf4.groupby('symbol').first()
                        df_cfs1=df_cf1[['asOfDate_cf','FreeCashFlow_cf']]
                        df_cfs1.columns = ['Date','Free Cash Flow']

                        df_is1 = ticker.income_statement("q")
                        if str(df_is1) == str("Income Statement data unavailable for " + symbol):
                            print ("Cash Burn can not be calculated for " + symbol)
                        else:
                            df_is2 = df_is1[df_is1.periodType != 'TTM']
                            if str(df_is2['asOfDate'].count()) == '0':
                                print("Cash Burn can not be calculated for " + symbol)
                            else:
                                df_is3 = df_is2.sort_values(by=['symbol','asOfDate'], ascending=[True ,False])
                                df_is4 = df_is3.add_suffix('_is')
                                df_is1 = df_is4.groupby('symbol').first()
                                df_iss1=df_is1[['asOfDate_is','TotalRevenue_is','NetIncome_is']]
                                df_iss1.columns = ['Date','Tot.Revenue','Net Income']


                                if df_bss1.iloc[0]['Date'] == df_iss1.iloc[0]['Date']== df_cfs1.iloc[0]['Date']:
                                    df_all1 = df_bss1.merge(df_iss1, left_index=True, right_index=True).merge(df_cfs1, left_index=True, right_index=True)
                                    df_all1=df_all1.sort_index()
                                    df_cash_burn1 = df_all1[['Date','Free Cash Flow','Cash/Short Term Inv.']]
                                    date1 = date.today()
                                    date2= pd.to_datetime(df_cash_burn1['Date'].iloc[0])
                                    date2 = date2.date()
                                    days_since_last_quarter = (date1-date2).days


                                    df_cash_burn1 = df_all1[['Date','Free Cash Flow','Cash/Short Term Inv.']]
                                    df_cash_burn1['CashBurnPerDay']= (df_cash_burn1['Free Cash Flow']/91).apply(pd.to_numeric, errors='coerce').round(1)
                                    df_cash_burn1 ['CashLeftToday'] = df_cash_burn1['Cash/Short Term Inv.']+ df_cash_burn1 ['CashBurnPerDay'] * days_since_last_quarter
                                    decimals=1
                                    df_cash_burn1 ['CashLeftToday'] = df_cash_burn1 ['CashLeftToday'].apply(lambda x: round(x, decimals))
                                    df_cash_burn1 ['Months to 0$'] = (df_cash_burn1['CashLeftToday']/(-df_cash_burn1['CashBurnPerDay']*30.42)).round(1)
                                    df_cash_burn1 

                                    try:
                                        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
                                        cur = conn.cursor()
                                        values = (symbol,df_cash_burn1.loc[symbol,'Date'].date(),df_cash_burn1.loc[symbol,'CashBurnPerDay'],df_cash_burn1.loc[symbol,'CashLeftToday'],df_cash_burn1.loc[symbol,'Months to 0$'])
                                        cur.execute("""
                                        INSERT INTO biotech(symbol,'Date_CB',CashBurnPerDay,CashLeftToday,[Months to 0$]) 
                                        VALUES(?,?,?,?,?)
                                        ON CONFLICT(symbol) DO UPDATE SET [Date_CB]=excluded.Date_CB,CashBurnPerDay=excluded.CashBurnPerDay,CashLeftToday=excluded.CashLeftToday,[Months to 0$]=excluded.`Months to 0$`""",
                                        values 
                                        )
                                        conn.commit()
                                        cur.close()
                                    except sqlite3.Error as error:
                                        print("Failed to add cash", error)    
                                    finally:
                                        if (conn):
                                            conn.close()

                                    return(df_cash_burn1)

                                else:
                                    print('Dates for Balance Sheet, Financial Statement and Cash Flow are not identical to calculate cash burn')
    except Exception as e: 
        print(e)
        pass


#-------------------------------------------------------

def mh(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_mh1 = pd.DataFrame.from_dict(ticker.major_holders, orient='index')
    df_mh2 = df_mh1.add_suffix('_mh')
    return (df_mh2)

def mhs(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        df_mh1 = pd.DataFrame.from_dict(ticker.major_holders, orient='index')
        df_mh2 = df_mh1.add_suffix('_mh')
        mh_columns=['insidersPercentHeld_mh','institutionsPercentHeld_mh','institutionsFloatPercentHeld_mh','institutionsCount_mh']
        df_mhs = df_mh2[df_mh2.columns.intersection(mh_columns)]
        for col in mh_columns:
            if col not in df_mhs.columns:
                df_mhs[col] = np.nan
        df_mhs = df_mhs.rename(columns={'insidersPercentHeld_mh':'Insiders % Held','institutionsPercentHeld_mh':'Institutions % Held','institutionsFloatPercentHeld_mh':'Institutions Float % Held','institutionsCount_mh':'Institutions Count'})
        cols2=[i for i in df_mhs.columns]
        df_mhs[cols2] = df_mhs[cols2].apply(pd.to_numeric,  errors='ignore', downcast='float')
        df_mhs['Institutions Count'] = df_mhs['Institutions Count'].astype(np.float64)
        
        df_mhs["Insiders % Held"] = df_mhs["Insiders % Held"].apply(pd.to_numeric,  errors='ignore', downcast='float')
        df_mhs["Institutions % Held"] = df_mhs["Institutions % Held"].apply(pd.to_numeric,  errors='ignore', downcast='float')
        df_mhs["Institutions Float % Held"] = df_mhs["Institutions Float % Held"].apply(pd.to_numeric,  errors='ignore', downcast='float')

        try:
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,df_mhs.loc[symbol,'Insiders % Held'],df_mhs.loc[symbol,'Institutions % Held'],df_mhs.loc[symbol,'Institutions Float % Held'],df_mhs.loc[symbol,'Institutions Count'])
            cur.execute("""
            INSERT INTO biotech(symbol,[Insiders % Held],[Institutions % Held],[Institutions Float % Held],[Institutions Count]) 
            VALUES(?,?,?,?,?)
            ON CONFLICT(symbol) DO UPDATE SET [Insiders % Held]=excluded.`Insiders % Held`,[Institutions % Held]=excluded.`Institutions % Held`,[Institutions Float % Held]=excluded.`Institutions Float % Held`,[Institutions Count]=excluded.`Institutions Count`""",
            values 
            )
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add mhs", error)    
        finally:
            if (conn):
                conn.close()
                
        df_mhs["Insiders % Held"] = df_mhs["Insiders % Held"].apply('{:.2%}'.format)
        df_mhs["Institutions % Held"] = df_mhs["Institutions % Held"].apply('{:.2%}'.format)
        df_mhs["Institutions Float % Held"] = df_mhs["Institutions Float % Held"].apply('{:.2%}'.format)
        df_mhs.style.format({'Insiders % Held': "{:.2%}", 'Institutions % Held': '{:.2%}', 'Institutions Float % Held': '{:.2%}', 'Institutions Count':'{:.0f}'})
        return(df_mhs)
    except Exception as e: 
        print(e)
        pass

#-------------------------------------------------------

def ks(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    df_ks1 = pd.DataFrame.from_dict(ticker.key_stats, orient='index')
    df_ks2 = df_ks1.add_suffix('_ks')
    return (df_ks2)

def kss_new(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        df_ks1 = pd.DataFrame.from_dict(ticker.key_stats, orient='index')
        df_ks2 = df_ks1.add_suffix('_ks')
        ks_columns=['enterpriseValue_ks','sharesOutstanding_ks','floatShares_ks','dateShortInterest_ks','sharesShort_ks','shortRatio_ks','shortPercentOfFloat_ks','sharesShortPreviousMonthDate_ks','sharesShortPriorMonth_ks']
        df_kss = df_ks2[df_ks2.columns.intersection(ks_columns)].copy()
        for col in ks_columns:
            if col not in df_kss.columns:
                df_kss[col] = np.nan
        df_kss = df_kss.rename(columns={'enterpriseValue_ks':'EV','sharesOutstanding_ks':'Shares Outst.','floatShares_ks':'Float','dateShortInterest_ks':'Date of Short Report','sharesShort_ks':'Shares Short','shortRatio_ks':'Short Ratio','shortPercentOfFloat_ks':'Short % of Float','sharesShortPreviousMonthDate_ks':'Previous Date of Report','sharesShortPriorMonth_ks':'Prior Shares Short' })


        df_kss_new=df_kss[['Date of Short Report','EV','Shares Outst.','Float','Shares Short','Short % of Float','Short Ratio']].copy()


        df_kss_new.loc[symbol,'EV'] = df_kss_new.loc[symbol,'EV'].astype(np.float64)
        df_kss_new.loc[symbol,'Shares Outst.'] = df_kss_new.loc[symbol,'Shares Outst.'].astype(np.float64)
        df_kss_new.loc[symbol,'Float'] = df_kss_new.loc[symbol,'Float'].astype(np.float64)
        df_kss_new.loc[symbol,'Shares Short'] = df_kss_new.loc[symbol,'Shares Short'].astype(np.float64)

        if df_kss_new['Date of Short Report'].isnull().values.any() == True:           
            try:
                conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
                cur = conn.cursor()
                values = (symbol,df_kss_new.loc[symbol,'Date of Short Report'], df_kss_new.loc[symbol,'EV'], df_kss_new.loc[symbol,'Shares Outst.'], df_kss_new.loc[symbol,'Float'], df_kss_new.loc[symbol,'Shares Short'], df_kss_new.loc[symbol,'Short % of Float'], df_kss_new.loc[symbol,'Short Ratio'])
                cur.execute("""
                INSERT INTO biotech(symbol,[Date of Short Report],EV,[Shares Outst.],Float,[Shares Short],[Short % of Float],[Short Ratio]) 
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(symbol) DO UPDATE SET [Date of Short Report]=excluded.`Date of Short Report`,EV=excluded.EV, [Shares Outst.]=excluded.`Shares Outst.`,Float=excluded.Float,[Shares Short]=excluded.`Shares Short`,[Short % of Float]=excluded.`Short % of Float`,[Short Ratio]=excluded.`Short Ratio`""",
                values 
                )
                conn.commit()
                cur.close()
            except sqlite3.Error as error:
                print("Failed to add kss_new", error)    
            finally:
                if (conn):
                    conn.close()
            df_kss.loc[:,'Short % of Float'] = df_kss.loc[:,'Short % of Float'].apply('{:.2%}'.format)
            return(df_kss_new)

        else:
            df_kss_new.loc[:,'Date of Short Report']=pd.to_datetime(df_kss_new.loc[:, 'Date of Short Report'])
            try:
                conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
                cur = conn.cursor()
                values = (symbol,df_kss_new.loc[symbol,'Date of Short Report'].date(), df_kss_new.loc[symbol,'EV'], df_kss_new.loc[symbol,'Shares Outst.'], df_kss_new.loc[symbol,'Float'], df_kss_new.loc[symbol,'Shares Short'], df_kss_new.loc[symbol,'Short % of Float'], df_kss_new.loc[symbol,'Short Ratio'])
                cur.execute("""
                INSERT INTO biotech(symbol,[Date of Short Report],EV,[Shares Outst.],Float,[Shares Short],[Short % of Float],[Short Ratio]) 
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(symbol) DO UPDATE SET [Date of Short Report]=excluded.`Date of Short Report`,EV=excluded.EV, [Shares Outst.]=excluded.`Shares Outst.`,Float=excluded.Float,[Shares Short]=excluded.`Shares Short`,[Short % of Float]=excluded.`Short % of Float`,[Short Ratio]=excluded.`Short Ratio`""",
                values 
                )
                conn.commit()
                cur.close()
            except sqlite3.Error as error:
                print("Failed to add kss_new", error)    
            finally:
                if (conn):
                    conn.close()
            df_kss.loc[:,'Short % of Float'] = df_kss.loc[:,'Short % of Float'].apply('{:.2%}'.format)
            return(df_kss_new)

    except Exception as e: 
        print(e)
        pass

def kss_old(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        df_ks1 = pd.DataFrame.from_dict(ticker.key_stats, orient='index')
        df_ks2 = df_ks1.add_suffix('_ks')
        ks_columns=['enterpriseValue_ks','sharesOutstanding_ks','floatShares_ks','dateShortInterest_ks','sharesShort_ks','shortRatio_ks','shortPercentOfFloat_ks','sharesShortPreviousMonthDate_ks','sharesShortPriorMonth_ks']
        df_kss = df_ks2[df_ks2.columns.intersection(ks_columns)].copy()
        for col in ks_columns:
            if col not in df_kss.columns:
                df_kss[col] = np.nan
        df_kss = df_kss.rename(columns={'enterpriseValue_ks':'EV','sharesOutstanding_ks':'Shares Outst.','floatShares_ks':'Float','dateShortInterest_ks':'Date of Short Report','sharesShort_ks':'Shares Short','shortRatio_ks':'Short Ratio','shortPercentOfFloat_ks':'Short % of Float','sharesShortPreviousMonthDate_ks':'Previous Date of Report','sharesShortPriorMonth_ks':'Prior Shares Short' })
        df_kss['Short % of Float'] = df_kss['Short % of Float'].apply('{:.2%}'.format)

        df_kss_old=df_kss[['Previous Date of Report','Prior Shares Short']].copy()
        df_kss_old.loc[symbol,'Prior Shares Short'] = df_kss_old.loc[symbol,'Prior Shares Short'].astype(np.float64)

        if df_kss_old['Previous Date of Report'].isnull().values.any() == True:         
            try:
                conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
                cur = conn.cursor()
                values = (symbol,df_kss_old.loc[symbol,'Previous Date of Report'],df_kss_old.loc[symbol,'Prior Shares Short'])
                cur.execute("""
                INSERT INTO biotech(symbol,[Previous Date of Report],[Prior Shares Short]) 
                VALUES(?,?,?)
                ON CONFLICT(symbol) DO UPDATE SET [Previous Date of Report]=excluded.`Previous Date of Report`,[Prior Shares Short]=excluded.`Prior Shares Short` """,
                values 
                )
                conn.commit()
                cur.close()
            except sqlite3.Error as error:
                print("Failed to add kss_old", error)    
            finally:
                if (conn):
                    conn.close()
            return(df_kss_old)
        else:
            df_kss_old.loc[:,'Previous Date of Report'] = pd.to_datetime(df_kss_old.loc[:,'Previous Date of Report'])
            try:
                conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
                cur = conn.cursor()
                values = (symbol,df_kss_old.loc[symbol,'Previous Date of Report'].date(),df_kss_old.loc[symbol,'Prior Shares Short'])
                cur.execute("""
                INSERT INTO biotech(symbol,[Previous Date of Report],[Prior Shares Short]) 
                VALUES(?,?,?)
                ON CONFLICT(symbol) DO UPDATE SET [Previous Date of Report]=excluded.`Previous Date of Report`,[Prior Shares Short]=excluded.`Prior Shares Short` """,
                values 
                )
                conn.commit()
                cur.close()
            except sqlite3.Error as error:
                print("Failed to add kss_old", error)    
            finally:
                if (conn):
                    conn.close()
            return(df_kss_old)

    except Exception as e: 
        print(e)
        pass


#-------------------------------------------------------
def institutions(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        df_inst = ticker.institution_ownership   
        if df_inst.empty:
            print('No Institutional Holdings data available for '+ symbol)
        else:
            df_inst = df_inst.reset_index(level='row', drop = True)
            df_inst['position'] = df_inst['position'].apply('{:,}'.format)
            df_inst['value'] = df_inst['value'].apply('{:,}'.format)
            df_inst['pctHeld'] = df_inst['pctHeld'].apply('{:.2%}'.format)
            return(df_inst)
    except Exception as e: 
        print(e)
        pass 


#-------------------------------------------------------
def salaries(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        asset_profiles = ticker.asset_profile
        df_pay = pd.DataFrame(asset_profiles[symbol]['companyOfficers'])
        df_pay['symbol'] = symbol

        df_pay = df_pay.drop(['maxAge'], axis = 1)
        df_pay = df_pay.set_index('symbol')
        df_pay['totalPay'] = df_pay['totalPay'].apply('{:,}'.format)
        df_pay['fiscalYear'] = df_pay['fiscalYear'].fillna(0).astype(int)
        df_pay['unexercisedValue'] = df_pay['unexercisedValue'].apply('{:,}'.format)
        df_pay['exercisedValue'] = df_pay['exercisedValue'].apply('{:,}'.format)
        return(df_pay)
    except Exception as e: 
        print(e)
        pass
    
#-------------------------------------------------------
def implied_move(symbol):
    symbol = symbol.upper()
    ticker = Ticker(symbol, asynchronous=True)
    ticker.price
    price = ticker.price[symbol]['regularMarketPrice']
    print(price)
    df_options = ticker.option_chain
    df_options = df_options.sort_values(by=['expiration','strike'], ascending=[True,False])

    if isinstance(df_options, pd.DataFrame):
        #  df_options = df_options[df_options['strike'] <= price].sort_values(by=['expiration','strike'], ascending=[True,False])
        for expiration, expiration_df in df_options.groupby(level=1):
            options_list = expiration_df['strike'].tolist()
            #Selecting In the money option value
            itm_option = min(options_list, key=lambda x:abs(x-price))
            # #Selecting In the money option chains
            expiration_df = expiration_df[expiration_df['strike'] == itm_option].sort_values(by=['expiration','strike'], ascending=[True,False])
            display(expiration_df)
            if (len(expiration_df.index)) ==2:
                implied_move = round(0.85 * expiration_df['lastPrice'].sum()/price,3)
                print('Implied move: '+ str(implied_move))
            elif (len(expiration_df.index)) ==1:
                print('Implied move can not be computed (only one option type available)')
    elif isinstance(df_options, str):
        print('No option chain data found')

        
#-------------------------------------------------------
def sec(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')

    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")
        cur = conn.cursor()
        sql_select_query = "select CIK from biotech where symbol = ?"
        cur.execute(sql_select_query,(symbol,))
        cik = str(cur.fetchone()[0])
        conn.commit()
        cur.close()

        if cik == 'None':
            ticker = Ticker(symbols, asynchronous=True)
            df_secfilings = ticker.sec_filings
            if type(df_secfilings) is dict:
                print('No SEC Filings data available')
            else:
                df_secfilings = df_secfilings.drop(['maxAge', 'epochDate'], axis = 1)
                df_secfilings = df_secfilings.reset_index(level='row', drop = True)
                df_secfilings['edgarUrl'] = df_secfilings['edgarUrl'].apply(lambda x: '<a href="{0}" target="_blank">{0}</a>'.format(x))
                # display(HTML(df_secfilings.to_html(escape=False)))

        else:
            # Obtain HTML for search page
            base_url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&count=100" #&type={}&dateb={}"
            # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            edgar_resp = doGet(base_url.format(cik))
            edgar_str = edgar_resp.text


            # Find the document link
            doc_link = ''
            soup = BeautifulSoup(edgar_str, 'html.parser')
            table_tag = soup.find('table', class_='tableFile2')
            rows = table_tag.find_all('tr')

            #Table of all recent listings
            table = soup.find_all('table')
            filings_df = pd.read_html(str(table))[2]
            filings_df['URL']=''

            for index,row in zip(filings_df.index.to_list(),rows[1:]):

                cells = row.find_all('td')
                if len(cells) > 3:
            # #         if '2020' in cells[3].text:

                    try:
                        doc_link = 'https://www.sec.gov' + cells[1].a['href']
                        filings_df.loc[index,'URL']=doc_link
                    except:
                        continue
            filings_df = filings_df.groupby('Filings').head(2).reset_index(drop=True)
            filings_df['URL'] = filings_df['URL'].apply(lambda x: '<a href="{0}" target="_blank">{0}</a>'.format(x))
            display(HTML(filings_df.to_html(escape=False)))
    except sqlite3.Error as error:
         print("Failed to select symbol from biotech", error)



#-------------------------------------------------------
def corporate_events(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    try:
        corp_events_df = ticker.corporate_events
        corp_events_df = corp_events_df.reset_index(level = 'date')
        corp_events_df = corp_events_df.sort_values('date', ascending=False)
        corp_events_df = corp_events_df.drop(['significance'], axis = 1)
        return(corp_events_df)
    except Exception as e: 
        print(e)
        pass

#-------------------------------------------------------
def news(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    ticker = Ticker(symbols, asynchronous=True)
    dict = ticker.news (12)
    news_list=list(dict.values())
    if news_list[0] == 'No data found':
        print("No news found for " +symbol)
    else:
        news_list=list(dict.values())
        flattened_news_list = [val for sublist in news_list for val in sublist]
        try:
            for sub in flattened_news_list:
                print(sub['title'])
                #print(sub['summary'])
                print (sub['provider_name'])
                print (sub['url'])
                print()
        except Exception as e: 
            print(e)
            pass


#-------------------------------------------------------
def dilution(symbol):

    symbol = symbol.upper()

    import json

    url = "https://api.filingspro.com/sec?ticker="+symbol
    resp = requests.get(url)
    text = resp.text

    d = json.loads(text)
    if not d['shelfs']:
        print('No dilution data available')
    else:
        # rows list initialization 
        dil_rows = [] 

        # appending rows 
        for data in d["shelfs"]: 
            data_row = data['filings'] 
            time = data['effective'] 

            for row in data_row: 
                row['effective']= time 
                dil_rows.append(row) 
                
#         dil_columns = set().union(*(d.keys() for d in dil_rows))
#         while "explanatoryNote" in dil_columns: dil_columns.remove("explanatoryNote")
           
        for d in dil_rows:
            dil_columns = list(d.keys())

        dil_columns
        while "explanatoryNote" in dil_columns: dil_columns.remove("explanatoryNote")
        while "resaleTable" in dil_columns: dil_columns.remove("resaleTable")
        dil_columns.append(dil_columns.pop(dil_columns.index('documentUrl')))
        dil_columns.append(dil_columns.pop(dil_columns.index('fileID')))
        dil_columns.append(dil_columns.pop(dil_columns.index('fileUrl')))

        # using data frame 
        dil_df = pd.DataFrame(dil_rows)


        dil_df.columns = pd.CategoricalIndex(dil_df.columns, categories=dil_columns, ordered=True)
        dil_df = dil_df.sort_values(by=['date'], ascending = False)
        dil_df = dil_df.sort_index(axis=1)
        dil_df = dil_df.reset_index(drop=True)
    #     dil_df = df[df.columns.intersection(dil_columns)]
        dil_df = dil_df[dil_columns]
        dil_df['date'] = dil_df['date'].astype('datetime64[ns]') 
        dil_df['effective'] = dil_df['effective'].astype('datetime64[ns]')
        # df['effective'] = df['effective'].dt.date
        dil_df = dil_df.loc[:, ~(dil_df.astype(str) == 'False').all()]
        dil_df = dil_df.loc[:, ~(dil_df.astype(str) == '').all()]

        
    #     get a list of names
        fileID_list =dil_df['fileID'].unique()
        for i in fileID_list:
            sub_df = dil_df.loc[dil_df.fileID == i]
            sub_df = sub_df.loc[:, ~(sub_df.astype(str) == 'False').all()]
            sub_df = sub_df.loc[:, ~(sub_df.astype(str) == '').all()]
            try:
                sub_df = sub_df.sort_values(by=['date'], ascending = False)
            except Exception as e: 
                pass
            sub_df = sub_df.reset_index(drop=True)
            sub_df['fileUrl'] = sub_df['fileUrl'].apply(lambda x: '<a href="{0}" target="_blank">{0}</a>'.format(x))
            sub_df['documentUrl'] = sub_df['documentUrl'].apply(lambda x: '<a href="{0}" target="_blank">{0}</a>'.format(x))
            # with custom_formatting():
            display(HTML(sub_df.to_html(escape=False)))

#-------------------------------------------------------
def links(symbol):
    print('USEFUL LINKS')
    print('')
    symbols = symbol.split(',')
    #ticker = Ticker(symbols, asynchronous=True)
    for b in symbols:
        print("Company Website")
        web(symbol)
        print("Insider trading:")
        url1 = 'https://www.marketwatch.com/investing/stock/'+str(b)+'/insideractions'
        print(url1)
        url2= 'https://www.nasdaq.com/market-activity/stocks/'+str(b)+'/insider-activity'
        print(url2) 
        print("Reports:")
        url3="https://www.sec.gov/cgi-bin/browse-edgar?CIK="+str(b)+"&owner=exclude&action=getcompany&Find=Search"
        print(url3)
        print("Catalysts:")
        url4="https://www.biopharmcatalyst.com/company/"+str(b)
        print(url4)
        print("Transcripts:")
        url5="https://seekingalpha.com/symbol/"+str(b)+"/earnings/transcripts"
        print(url5)
#-------------------------------------------------------
def stock_info(symbol):
        print('')
        string = "Stock Report"
        new_string = (symbol+" - "+string).center(70)
        print(new_string)
        print('')
        print(web(symbol))
        print('')
        summary(symbol)
        print('')
        print ('STOCK INFO:')
        trend(symbol)
        print(pctchange(symbol))
        print(pcs(symbol))
        print(sps(symbol))
        print('-'*60)
        print('-'*60)
        print('')
        print ('EV AND SHARES SHORT:')
        print(kss_new(symbol))
        print(kss_old(symbol))
    
    
def finances(symbol):
    print('-'*60)
    print('-'*60)
    print('')
    print ('DILUTION:')
    dilution(symbol)
    print('-'*60)
    print('-'*60)
    print('')
    print ('BALANCE SHEET:')
    print(bss(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('FINANCIAL STATEMENT:')
    print(fss(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('CASH FLOWS:')
    print(cfs(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('CASH BURN:')
    print(cash(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('SALARIES:')
    print(salaries(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('MAJOR HOLDERS:')
    try:
        print(mhs(symbol))  
    except Exception as e: 
        print(e)
        pass
    
           
#-------------------------------------------------------

# df_all = df_bss.join(df_iss, on="Date", how='right')

# def all_s1():
#     df_all_s1 = df_bss1.merge(df_iss1, left_index=True, right_index=True).merge(df_cfs1, left_index=True, right_index=True).merge(df_kss, left_index=True, right_index=True).merge(df_mhs, left_index=True, right_index=True)
#     df_all_s1=df_all_s1.sort_index()
#     return (df_all_s1)



#Gets the list of new ORphan Drug Designations from the FDA
def ODD():
    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")
        df_ODD = pd.read_sql_query("select * from [*ODD_sorted] ORDER BY [Designation Date] DESC;", conn)

    except sqlite3.Error as error:
        print("Failed to select from biotech", error)  
    finally:
        if (conn):
            conn.close() 
    return df_ODD.head(10)

def nasdaq(symbol):
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    import time
    from time import sleep
    from bs4 import BeautifulSoup
    import pandas as pd

    options = webdriver.ChromeOptions() 
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options, executable_path='/Users/ralph/Biotech/chromedriver')
    driver.minimize_window()


    try:
        driver.get("https://www.nasdaq.com/market-activity/stocks/"+symbol+"/insider-activity")
        sleep(4)
        try:
            driver.find_element_by_id("_evidon-decline-button").click();
        except Exception as e: 
            pass
        try:   
            driver.find_element_by_xpath("/html/body/div[2]/div/main/div[2]/div[4]/div[3]/div/div[1]/div/div[1]/div[3]/div[2]/div[2]/div/table/thead/tr/th[3]/button/span[1]").click()
            sleep(1)
        except Exception as e: 
            pass
        try:   
            driver.find_element_by_xpath("/html/body/div[2]/div/main/div[2]/div[4]/div[3]/div/div[1]/div/div[1]/div[3]/div[2]/div[2]/div/table/thead/tr/th[3]/button/span[1]").click()
            sleep(1)
        except Exception as e: 
            pass

        # WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1.h1")))
        soup = BeautifulSoup(driver.page_source, 'lxml')
        #Always quit at the end of scrapin

        table = soup.find_all('table')


        trades_df = pd.read_html(str(table))[0] 
        volume_df = pd.read_html(str(table))[1] 
        transactions_df = pd.read_html(str(table))[2] 
        volume_df = pd.read_html(str(table))[1] 

        # display(trades_df)
        # display(volume_df)
        # display(transactions_df)

        volume_df['12 MONTHS'] = volume_df['12 MONTHS'].replace( '[)]','', regex=True )
        volume_df['12 MONTHS'] = volume_df['12 MONTHS'].replace('[(]','-',   regex=True )
        volume_df['12 MONTHS'] = volume_df['12 MONTHS'].replace('[,]','',   regex=True )
        volume_df['3 MONTHS'] = volume_df['3 MONTHS'].replace( '[)]','', regex=True )
        volume_df['3 MONTHS'] = volume_df['3 MONTHS'].replace('[(]','-',   regex=True )
        volume_df['3 MONTHS'] = volume_df['3 MONTHS'].replace('[,]','',   regex=True )

        try:    
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,int(trades_df.loc[0,'3 MONTHS']),int(trades_df.loc[0,'12 MONTHS']),int(trades_df.loc[1,'3 MONTHS']),int(trades_df.loc[1,'12 MONTHS']),
                        int(volume_df.loc[0,'3 MONTHS']),int(volume_df.loc[0,'12 MONTHS']),int(volume_df.loc[1,'3 MONTHS']),int(volume_df.loc[1,'12 MONTHS']),
                        int(volume_df.loc[3,'3 MONTHS']),int(volume_df.loc[3,'12 MONTHS'])
                        )
            cur.execute("""
            INSERT INTO biotech(symbol,[Buy (3M)],[Buy (12M)],[Sell (3M)],[Sell (12M)],[Shares Bought (3M)],[Shares Bought (12M)],[Shares Sold (3M)],[Shares Sold (12M)],[Net Activity (3M)],[Net Activity (12M)])
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(symbol) DO UPDATE SET [Buy (3M)]=excluded.`Buy (3M)`,[Buy (12M)]=excluded.`Buy (12M)`,[Sell (3M)]=excluded.`Sell (3M)`,[Sell (12M)]=excluded.`Sell (12M)`,[Shares Bought (3M)]=excluded.`Shares Bought (3M)`,[Shares Bought (12M)]=excluded.`Shares Bought (12M)`,[Shares Sold (3M)]=excluded.`Shares Sold (3M)`,[Shares Sold (12M)]=excluded.`Shares Sold (12M)`,[Net Activity (3M)]=excluded.`Net Activity (3M)`,[Net Activity (12M)]=excluded.`Net Activity (12M)`""",
            values)
            print(symbol+' added')
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add insiders", error)                                
        finally:
            if (conn):
                conn.close()


    except Exception as e: 
        print(symbol+' No insider transactions found')
        try:    
            conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")   
            cur = conn.cursor()
            values = (symbol,None,None,None,None,None,None,None,None,None,None)
            cur.execute("""
            INSERT INTO biotech(symbol,[Buy (3M)],[Buy (12M)],[Sell (3M)],[Sell (12M)],[Shares Bought (3M)],[Shares Bought (12M)],[Shares Sold (3M)],[Shares Sold (12M)],[Net Activity (3M)],[Net Activity (12M)])
            VALUES(?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(symbol) DO UPDATE SET [Buy (3M)]=excluded.`Buy (3M)`,[Buy (12M)]=excluded.`Buy (12M)`,[Sell (3M)]=excluded.`Sell (3M)`,[Sell (12M)]=excluded.`Sell (12M)`,[Shares Bought (3M)]=excluded.`Shares Bought (3M)`,[Shares Bought (12M)]=excluded.`Shares Bought (12M)`,[Shares Sold (3M)]=excluded.`Shares Sold (3M)`,[Shares Sold (12M)]=excluded.`Shares Sold (12M)`,[Net Activity (3M)]=excluded.`Net Activity (3M)`,[Net Activity (12M)]=excluded.`Net Activity (12M)`""",
            values)
            print(symbol+' Null values added')
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Failed to add insiders", error)                                
        finally:
            if (conn):
                conn.close()

    driver.quit()

def report_hf(hf):
    from datetime import datetime

    import sqlite3
    import pandas as pd
    
    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")
        query_string = "select * from hf_"+hf+";"
        hf_df = pd.read_sql_query(query_string, conn)
        hf_df
    except sqlite3.Error as error:
        print("Failed to access the BiotechDatabase file", error)  
    finally:
        if (conn):
            conn.close() 


    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")
        query_string = "select * from biotech;"
        biotech_df = pd.read_sql_query(query_string, conn)
    except sqlite3.Error as error:
        print("Failed to access the BiotechDatabase file", error)  
    finally:
        if (conn):
            conn.close() 
    
    biotech_df = biotech_df[['symbol','Price','Mkt. Cap','Float','3 Month Percentage Change','First Traded','Cash/Short Term Inv.','Months to 0$']]
    biotech_df['3 Month Percentage Change'] = biotech_df['3 Month Percentage Change'].astype(float, errors = 'raise')
    try:
        biotech_df['3 Month Percentage Change'] = biotech_df['3 Month Percentage Change'].apply('{:.2%}'.format)
    except:
        pass



    biotech_df = biotech_df.rename(columns={'symbol':'SYMBOL'})

    hf_df['DATE'] = hf_df['DATE'].astype('datetime64[ns]')
    hf_df.sort_values(by=['DATE'], inplace=True, ascending=False)
    #Select the most recent 2 dates in the hedge fund table (i.e most recent 2 quarters reported)        
    top_dates = list(hf_df['DATE'].unique()[0:2])
    new_date = top_dates[0]
    old_date = top_dates[1]

    #Select the last 2 quarters holdings
    hf_df = hf_df[hf_df['DATE'].isin(top_dates)]
    hf_df = hf_df.merge(biotech_df, on='SYMBOL', how='left')
    hf_df

    holdings_df = hf_df[hf_df['DATE']== new_date]

    hf_df_new_list = hf_df['CUSIP'][hf_df['DATE']== new_date].to_list()
    hf_df_old_list = hf_df['CUSIP'][hf_df['DATE']== old_date].to_list()


    diff = list(set(hf_df_new_list) - set(hf_df_old_list))
    diff

    hf_new_positions_df = hf_df[(hf_df['DATE'] == new_date) & (hf_df['CUSIP'].isin(diff)) ]
    hf_new_positions_df = hf_new_positions_df.sort_values('VALUE', ascending=False)
    hf_new_positions_df = hf_new_positions_df.reset_index(drop=True)
    hf_new_positions_df = hf_new_positions_df.drop(['TITLE_OF_CLASS','CUSIP'], axis=1)
    hf_new_positions_df


    diff2 = list(set(hf_df_old_list) - set(hf_df_new_list))
    diff2

    hf_closed_positions_df = hf_df[(hf_df['DATE'] == old_date) & (hf_df['CUSIP'].isin(diff2)) ]
    hf_closed_positions_df = hf_closed_positions_df.sort_values('VALUE', ascending=False)
    hf_closed_positions_df = hf_closed_positions_df.reset_index(drop=True)
    hf_closed_positions_df = hf_closed_positions_df.drop(['TITLE_OF_CLASS','CUSIP'], axis=1)
    hf_closed_positions_df

    common = list(set(hf_df_new_list).intersection(hf_df_old_list))
    common

    increased_list = []
    for cusip in common:
        df = hf_df[hf_df['CUSIP']== cusip]
    #     increased_list = []
        try:
            if (df['SHARES'][df['DATE']== new_date].values.sum() > df['SHARES'][df['DATE']== old_date].values.sum())==True:
                increased_list.append(cusip)
            else:
                  pass
        except Exception as e: 
            print(e)
            pass

    hf_increased_positions_df = hf_df[(hf_df['DATE'].isin(top_dates)) & (hf_df['CUSIP'].isin(increased_list)) ]
    hf_increased_positions_df1 = hf_increased_positions_df[(hf_increased_positions_df['DATE'] == new_date )]
    hf_increased_positions_df2 = hf_increased_positions_df[(hf_increased_positions_df['DATE'] == old_date )]

    for symbol in hf_increased_positions_df1['SYMBOL'].to_list():
        try:
            new_shares = hf_increased_positions_df1.loc[hf_increased_positions_df1['SYMBOL'] == symbol, 'SHARES'].values
            old_shares = hf_increased_positions_df2.loc[hf_increased_positions_df2['SYMBOL'] == symbol, 'SHARES'].values
            pct_change = (new_shares-old_shares)/old_shares
            hf_increased_positions_df1 = hf_increased_positions_df1.copy()
            hf_increased_positions_df1.loc[hf_increased_positions_df1['SYMBOL'] == symbol,'PCT_CHANGE']= pct_change
        except Exception as e: 
            print(e)
            pass

    hf_increased_positions_df1 = hf_increased_positions_df1.copy()
    hf_increased_positions_df1 = hf_increased_positions_df1.reset_index(drop = True)
    try:
        hf_increased_positions_df1['PCT_CHANGE'] = hf_increased_positions_df1['PCT_CHANGE'].apply('{:.2%}'.format)
    except Exception as e: 
        print(e)
        pass        
    hf_increased_positions_df1 = hf_increased_positions_df1.sort_values('VALUE', ascending=False)
    hf_increased_positions_df1 = hf_increased_positions_df1.reset_index(drop=True)
    hf_increased_positions_df1 = hf_increased_positions_df1.drop(['TITLE_OF_CLASS','CUSIP'], axis=1)
    hf_increased_positions_df1

    decreased_list = []
    for cusip in common:
        df = hf_df[hf_df['CUSIP']== cusip]
    #     decreased_list = []
        try:
            if (df['SHARES'][df['DATE']== new_date].values.sum() < df['SHARES'][df['DATE']== old_date].values.sum())==True:
                decreased_list.append(cusip)
            else:
                  pass
        except Exception as e: 
            print(e)
            pass

    hf_decreased_positions_df = hf_df[(hf_df['DATE'].isin(top_dates)) & (hf_df['CUSIP'].isin(decreased_list)) ]
    hf_decreased_positions_df1 = hf_decreased_positions_df[(hf_decreased_positions_df['DATE'] == new_date )]
    hf_decreased_positions_df2 = hf_decreased_positions_df[(hf_decreased_positions_df['DATE'] == old_date )]

        
    for symbol in hf_decreased_positions_df1['SYMBOL'].to_list():
        try:
                
            new_shares = hf_decreased_positions_df1.loc[hf_decreased_positions_df1['SYMBOL'] == symbol, 'SHARES'].values
            old_shares = hf_decreased_positions_df2.loc[hf_decreased_positions_df2['SYMBOL'] == symbol, 'SHARES'].values
            pct_change = (new_shares - old_shares)/old_shares
            hf_decreased_positions_df1 = hf_decreased_positions_df1.copy()
            hf_decreased_positions_df1.loc[hf_decreased_positions_df1['SYMBOL'] == symbol,'PCT_CHANGE']= pct_change
        except Exception as e: 
            print(e)
            pass
        
    hf_decreased_positions_df1 = hf_decreased_positions_df1.copy()
    hf_decreased_positions_df1 = hf_decreased_positions_df1.reset_index(drop = True)
    try:
        hf_decreased_positions_df1['PCT_CHANGE'] = hf_decreased_positions_df1['PCT_CHANGE'].apply('{:.2%}'.format)
    except Exception as e: 
        print(e)
        pass      
    hf_decreased_positions_df1 = hf_decreased_positions_df1.sort_values('VALUE', ascending=False)
    hf_decreased_positions_df1 = hf_decreased_positions_df1.reset_index(drop=True)
    hf_decreased_positions_df1 = hf_decreased_positions_df1.drop(['TITLE_OF_CLASS','CUSIP'], axis=1)
    hf_decreased_positions_df1


    unchanged_list = []
    for cusip in common:
        df = hf_df[hf_df['CUSIP']== cusip]
    #     decreased_list = []
        try:
            if (df['SHARES'][df['DATE']== new_date].values.sum() == df['SHARES'][df['DATE']== old_date].values.sum())==True:
                unchanged_list.append(cusip)
            else:
                  pass
        except Exception as e: 
            print(e)
            pass

    hf_unchanged_positions_df = hf_df[(hf_df['DATE'] == new_date) & (hf_df['CUSIP'].isin(unchanged_list)) ]
    hf_unchanged_positions_df = hf_unchanged_positions_df.sort_values('VALUE', ascending=False)
    hf_unchanged_positions_df = hf_unchanged_positions_df.reset_index(drop=True)
    hf_unchanged_positions_df = hf_unchanged_positions_df.drop(['TITLE_OF_CLASS','CUSIP'], axis=1)
    hf_unchanged_positions_df


    hf_df_new_list = hf_df['CUSIP'][hf_df['DATE']== new_date].to_list()
    hf_df_old_list = hf_df['CUSIP'][hf_df['DATE']== old_date].to_list()


    hf_new_positions_list=sorted(hf_new_positions_df['SYMBOL'].to_list())
    hf_new_positions_list  = list(filter(None, hf_new_positions_list))
    hf_new_positions_list_tweet = ', $'.join(hf_new_positions_list)
    hf_new_positions_list_tweet = "$"+hf_new_positions_list_tweet
    

    hf_closed_positions_list=sorted(hf_closed_positions_df['SYMBOL'].to_list())
    hf_closed_positions_list  = list(filter(None, hf_closed_positions_list))
    hf_closed_positions_list_tweet = ', $'.join(hf_closed_positions_list)
    hf_closed_positions_list_tweet = "$"+hf_closed_positions_list_tweet
    

    hf_increased_positions_list=sorted(hf_increased_positions_df1['SYMBOL'].to_list())
    hf_increased_positions_list  = list(filter(None, hf_increased_positions_list))
    hf_increased_positions_list_tweet = ', $'.join(hf_increased_positions_list)
    hf_increased_positions_list_tweet = "$"+hf_increased_positions_list_tweet
    

    hf_decreased_positions_list=sorted(hf_decreased_positions_df1['SYMBOL'].to_list())
    hf_decreased_positions_list  = list(filter(None, hf_decreased_positions_list))
    hf_decreased_positions_list_tweet = ', $'.join(hf_decreased_positions_list)
    hf_decreased_positions_list_tweet = "$"+hf_decreased_positions_list_tweet
    
    hf_unchanged_positions_list=sorted(hf_unchanged_positions_df['SYMBOL'].to_list())
    hf_unchanged_positions_list  = list(filter(None, hf_unchanged_positions_list))
    hf_unchanged_positions_list_tweet = ', $'.join(hf_unchanged_positions_list)
    hf_unchanged_positions_list_tweet = "$"+hf_unchanged_positions_list_tweet


    try:
        conn = sqlite3.connect("BiotechDatabase.db")
        # pd.read_sql_query("select * from biotech where symbol='MYOV';", conn)
        catalysts_df = pd.read_sql_query("select * from catalysts_bfc;", conn)
        catalysts_df = catalysts_df. rename(columns = {'symbol':'SYMBOL'}) 
        catalysts_df = catalysts_df.drop(columns = {'Catalyst Last Updated','Last Updated'})
        catalysts_df['Catalyst Rank'] = catalysts_df.index
    except sqlite3.Error as error:
        print("Failed to access the BiotechDatabase file", error)  
    finally:
        if (conn):
            conn.close()

    hf_new_positions_df = hf_new_positions_df.assign(Position = 'New')
    hf_closed_positions_df = hf_closed_positions_df.assign(Position = 'Closed')      
    hf_increased_positions_df1 = hf_increased_positions_df1.assign(Position = 'Increased')
    new_increased_positions_df = pd.concat([hf_new_positions_df, hf_increased_positions_df1], ignore_index=True,axis=0)
    hf_new_increased_positions_with_catalysts_df = pd.merge(catalysts_df,new_increased_positions_df,
                    on='SYMBOL', 
                    how='inner').sort_values(by = 'Catalyst Rank', ascending = True).reset_index(drop=True) 

    hf_new_increased_positions_with_catalysts_df = hf_new_increased_positions_with_catalysts_df.loc[hf_new_increased_positions_with_catalysts_df['SYMBOL']!= 'XBI'].reset_index(drop=True)  
    if hf_new_increased_positions_with_catalysts_df.empty == False:                   
        hf_new_increased_positions_with_catalysts_df = hf_new_increased_positions_with_catalysts_df[['SYMBOL','Catalyst Date','Stage','Drug','Indication','NAME_OF_ISSUER',	'VALUE', 'SHARES','PERCENT','Price','Mkt. Cap','Float','3 Month Percentage Change','First Traded','Cash/Short Term Inv.','Months to 0$','Position','PCT_CHANGE']]
    
    
    hf_decreased_positions_df1 = hf_decreased_positions_df1.assign(Position = 'Decreased')
    closed_decreased_positions_df = pd.concat([hf_closed_positions_df, hf_decreased_positions_df1], ignore_index=True,axis=0)
    hf_closed_decreased_positions_with_catalysts_df = pd.merge(catalysts_df,closed_decreased_positions_df,
                    on='SYMBOL', 
                    how='inner').sort_values(by = 'Catalyst Rank', ascending = True).reset_index(drop=True) 
    hf_closed_decreased_positions_with_catalysts_df = hf_closed_decreased_positions_with_catalysts_df.loc[hf_closed_decreased_positions_with_catalysts_df['SYMBOL']!= 'XBI'].reset_index(drop=True)     
    if hf_closed_decreased_positions_with_catalysts_df.empty == False:     
        hf_closed_decreased_positions_with_catalysts_df = hf_closed_decreased_positions_with_catalysts_df[['SYMBOL','Catalyst Date','Stage','Drug','Indication','NAME_OF_ISSUER',	'VALUE', 'SHARES','PERCENT','Price','Mkt. Cap','Float','3 Month Percentage Change','First Traded','Cash/Short Term Inv.','Months to 0$','Position','PCT_CHANGE']]
    


    hf_new_increased_positions_with_catalysts_list=sorted(list(set(hf_new_increased_positions_with_catalysts_df['SYMBOL'].to_list())))
    hf_new_increased_positions_with_catalysts_list  = list(filter(None, hf_new_increased_positions_with_catalysts_list))
    hf_new_increased_positions_with_catalysts_list_tweet = ', $'.join(hf_new_increased_positions_with_catalysts_list)
    hf_new_increased_positions_with_catalysts_list_tweet = "$"+hf_new_increased_positions_with_catalysts_list_tweet


    hf_closed_decreased_positions_with_catalysts_list=sorted(list(set(hf_closed_decreased_positions_with_catalysts_df['SYMBOL'].to_list())))
    hf_closed_decreased_positions_with_catalysts_list  = list(filter(None, hf_closed_decreased_positions_with_catalysts_list))
    hf_closed_decreased_positions_with_catalysts_list_tweet = ', $'.join(hf_closed_decreased_positions_with_catalysts_list)
    hf_closed_decreased_positions_with_catalysts_list_tweet = "$"+hf_closed_decreased_positions_with_catalysts_list_tweet





    
    print('')
    string = " Report"
    new_string = (hf.capitalize()+string).center(70)
    print(new_string)
    print('')  
    top_40 = holdings_df.sort_values(by="VALUE", ascending=False)[["SYMBOL", "VALUE"]][:40]
    top_10_df = holdings_df.sort_values(by="VALUE", ascending=False)
    top_10_df = top_10_df.head(10)
    top_10_df = top_10_df.reset_index(drop=True)
    top_10_df  = top_10_df.drop(['TITLE_OF_CLASS','CUSIP'], axis=1)
    a = top_40.SYMBOL
    b = top_40.VALUE
    c = range(len(b))

    fig = plt.figure(figsize=(15,5))
    ax = fig.add_subplot(111)
    ax.bar(c, b)

    plt.xticks(c, a, rotation=90)
    plt.title('Top 40 Stock Holdings by Value')
    plt.xlabel('Stock Ticker')
    plt.ylabel('USD')
    plt.show()


    print(hf.capitalize()+' Top 10 Stock Holdings by Value')
    display(top_10_df)
    print('')
    print(hf.capitalize()+" New Positions")
    display(hf_new_positions_df)
    
    print('-'*60)
    print('-'*60)
    print('')
    print(hf.capitalize()+" Increased Positions")
    display(hf_increased_positions_df1)
    
    print('-'*60)
    print('-'*60)
    print('')
    print(hf.capitalize()+" Closed Positions")
    display(hf_closed_positions_df)
    print('-'*60)
    print('-'*60)
    print('')
    print(hf.capitalize()+" Decreased Positions")
    display(hf_decreased_positions_df1)
    print('-'*60)
    print('-'*60)
    print('')
    print(hf.capitalize()+" Unchanged Positions")
    display(hf_unchanged_positions_df)
    print('-'*60)
    print('-'*60)
    print(hf.capitalize()+" New or Increased Positions with Nearby Catalysts")
    display(hf_new_increased_positions_with_catalysts_df)
    print('-'*60)
    print('-'*60)
    print(hf.capitalize()+" Closed or Decreased Positions with Nearby Catalysts")
    display(hf_closed_decreased_positions_with_catalysts_df)
    print('-'*60)
    print('-'*60)
    print('')
    
    
    print(hf.capitalize()+' 13F positions: ')
    print('New: '+ hf_new_positions_list_tweet)
    print('Increased: '+ hf_increased_positions_list_tweet)
    print('Closed: '+ hf_closed_positions_list_tweet)
    print('Decreased: '+ hf_decreased_positions_list_tweet)
    print('Unchanged: '+ hf_unchanged_positions_list_tweet)
    print('New or Increased, with an upcoming catalyst: '+ hf_new_increased_positions_with_catalysts_list_tweet)
    print('Closed or Decreased, with an upcoming catalyst: '+ hf_closed_decreased_positions_with_catalysts_list_tweet)

def report_hf_all():
    import sqlite3
    import pandas as pd
    global hf_df

    conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db") 
    # pd.read_sql_query("select * from biotech where symbol='MYOV';", conn)
    df = pd.read_sql_query("select * from HF_cumulative_holdings ORDER BY DATE DESC,symbol ASC;", conn)

    df['DATE']= pd.to_datetime(df['DATE'])
    df['YEAR'] = pd. DatetimeIndex(df['DATE']).year
    df['MONTH'] = pd. DatetimeIndex(df['DATE']).month
    dates = df['MONTH']
    # b = pd.IntervalIndex.from_tuples([(1, 3), (4, 6), (7, 9), (10,12)])
    b = [1,4,7,10,12]
    l = ['Q4','Q1', 'Q2','Q3']
    df['QUARTER'] = pd.cut(dates, bins=b, labels=l, right=False)
    df.loc[df.QUARTER.isin(['Q4']), 'YEAR'] = df['YEAR']-1 
    df.drop('DATE',inplace=True, axis=1)
    df


    df.loc[df.QUARTER.isin(['Q1']), 'MONTH'] = 3
    df.loc[df.QUARTER.isin(['Q2']), 'MONTH'] = 6
    df.loc[df.QUARTER.isin(['Q3']), 'MONTH'] = 9
    df.loc[df.QUARTER.isin(['Q4']), 'MONTH'] = 12

    df.loc[df.QUARTER.isin(['Q1']), 'DAY'] = 31
    df.loc[df.QUARTER.isin(['Q2']), 'DAY'] = 30
    df.loc[df.QUARTER.isin(['Q3']), 'DAY'] = 30
    df.loc[df.QUARTER.isin(['Q4']), 'DAY'] = 31

    df['DATE']= pd.to_datetime(df[['YEAR', 'MONTH', 'DAY']])
    df['FUND_LIST']=df['FUND']
    df = df.rename(columns={'FUND': 'FUND_COUNT'})

    d = {'Company':['first'],'Price':['first'],'Mkt. Cap':['first'],'3 Month Percentage Change':['first'],'Float':['first'],'First Traded':['first'],'VALUE': ['sum'], 'SHARES': ['sum'],'FUND_COUNT': ['count'],'FUND_LIST':'-'.join}

    hf_df = df.groupby(['SYMBOL','DATE']).agg(d).reset_index()
    hf_df .columns = hf_df .columns.droplevel(1)
    hf_df['3 Month Percentage Change'] = hf_df['3 Month Percentage Change'].astype(float, errors = 'raise')
    try:
        hf_df['3 Month Percentage Change'] = hf_df['3 Month Percentage Change'].apply('{:.2%}'.format)
    except:
        pass

    hf_df['DATE'] = hf_df['DATE'].astype('datetime64[ns]')
    hf_df.sort_values(by=['DATE'], inplace=True, ascending=False)
    #Select the most recent 2 dates in the hedge fund table (i.e most recent 2 quarters reported)        
    top_dates = list(hf_df['DATE'].unique()[0:2])
    new_date = top_dates[0]
    old_date = top_dates[1]

    #Select the last 2 quarters holdings
    
    hf_df = hf_df[hf_df['DATE'].isin(top_dates)]
    hf_df

    holdings_df = hf_df[hf_df['DATE']== new_date]

    hf_df_new_list = hf_df['SYMBOL'][hf_df['DATE']== new_date].to_list()
    hf_df_old_list = hf_df['SYMBOL'][hf_df['DATE']== old_date].to_list()


    diff = list(set(hf_df_new_list) - set(hf_df_old_list))
    diff

    hf_new_positions_df = hf_df[(hf_df['DATE'] == new_date) & (hf_df['SYMBOL'].isin(diff)) ]
    hf_new_positions_df = hf_new_positions_df.sort_values('VALUE', ascending=False)
    hf_new_positions_df = hf_new_positions_df.reset_index(drop=True)
    hf_new_positions_df

    hf_new_positions_by_fund_count_df = hf_new_positions_df.sort_values(by="FUND_COUNT", ascending = False) 
    hf_new_positions_by_fund_count_df = hf_new_positions_by_fund_count_df.reset_index(drop=True)
    hf_new_positions_by_fund_count_df

    diff2 = list(set(hf_df_old_list) - set(hf_df_new_list))
    diff2

    hf_closed_positions_df = hf_df[(hf_df['DATE'] == old_date) & (hf_df['SYMBOL'].isin(diff2)) ]
    hf_closed_positions_df = hf_closed_positions_df.sort_values('VALUE', ascending=False)
    hf_closed_positions_df = hf_closed_positions_df.reset_index(drop=True)
    hf_closed_positions_df

    common = list(set(hf_df_new_list).intersection(hf_df_old_list))
    common

    increased_list = []
    for symbol in common:
        df = hf_df[hf_df['SYMBOL']== symbol]
    #     increased_list = []
        try:
            if (df['SHARES'][df['DATE']== new_date].values.sum() > df['SHARES'][df['DATE']== old_date].values.sum())==True:
                increased_list.append(symbol)
            else:
                pass
        except Exception as e: 
            print(e)
            pass

    hf_increased_positions_df = hf_df[(hf_df['DATE'].isin(top_dates)) & (hf_df['SYMBOL'].isin(increased_list)) ]
    hf_increased_positions_df1 = hf_increased_positions_df[(hf_increased_positions_df['DATE'] == new_date )]
    hf_increased_positions_df2 = hf_increased_positions_df[(hf_increased_positions_df['DATE'] == old_date )]

    for symbol in hf_increased_positions_df1['SYMBOL'].to_list():
        try:
            new_shares = hf_increased_positions_df1.loc[hf_increased_positions_df1['SYMBOL'] == symbol, 'SHARES'].values
            old_shares = hf_increased_positions_df2.loc[hf_increased_positions_df2['SYMBOL'] == symbol, 'SHARES'].values
            pct_change = (new_shares-old_shares)/old_shares
            hf_increased_positions_df1 = hf_increased_positions_df1.copy()
            hf_increased_positions_df1.loc[hf_increased_positions_df1['SYMBOL'] == symbol,'PCT_CHANGE']= pct_change
        except Exception as e: 
            print(e)
            pass

    hf_increased_positions_df1 = hf_increased_positions_df1.copy()
    hf_increased_positions_df1 = hf_increased_positions_df1.reset_index(drop = True)
    # hf_increased_positions_df1['PCT_CHANGE'] = round(hf_increased_positions_df1['PCT_CHANGE']*100,3)

    
    hf_increased_positions_df1 = hf_increased_positions_df1.sort_values('VALUE', ascending=False)
    hf_increased_positions_df1 = hf_increased_positions_df1.reset_index(drop=True)
    hf_increased_positions_df1

    hf_increased_percent_df1 = hf_increased_positions_df1.sort_values('PCT_CHANGE', ascending=False)
    hf_increased_percent_df1 = hf_increased_percent_df1.reset_index(drop=True)
    hf_increased_percent_df1


    hf_increased_funds_df1 = hf_increased_positions_df1.sort_values('FUND_COUNT', ascending=False)
    hf_increased_funds_df1 = hf_increased_funds_df1.reset_index(drop=True)
    hf_increased_funds_df1


    try:
        hf_increased_positions_df1['PCT_CHANGE'] = hf_increased_positions_df1['PCT_CHANGE'].apply('{:.2%}'.format)    
    except Exception as e: 
        print(e)
        pass   

    try:
        hf_increased_percent_df1['PCT_CHANGE'] = hf_increased_percent_df1['PCT_CHANGE'].apply('{:.2%}'.format)    
    except Exception as e: 
        print(e)
        pass   

    try:
        hf_increased_funds_df1['PCT_CHANGE'] = hf_increased_funds_df1['PCT_CHANGE'].apply('{:.2%}'.format)    
    except Exception as e: 
        print(e)
        pass   


    decreased_list = []
    for symbol in common:
        df = hf_df[hf_df['SYMBOL']== symbol]
    #     decreased_list = []
        try:
            if (df['SHARES'][df['DATE']== new_date].values.sum() < df['SHARES'][df['DATE']== old_date].values.sum())==True:
                decreased_list.append(symbol)
            else:
                pass
        except Exception as e: 
            print(e)
            pass

    hf_decreased_positions_df = hf_df[(hf_df['DATE'].isin(top_dates)) & (hf_df['SYMBOL'].isin(decreased_list)) ]
    hf_decreased_positions_df1 = hf_decreased_positions_df[(hf_decreased_positions_df['DATE'] == new_date )]
    hf_decreased_positions_df2 = hf_decreased_positions_df[(hf_decreased_positions_df['DATE'] == old_date )]


    for symbol in hf_decreased_positions_df1['SYMBOL'].to_list():
        try:
            new_shares = hf_decreased_positions_df1.loc[hf_decreased_positions_df1['SYMBOL'] == symbol, 'SHARES'].values
            old_shares = hf_decreased_positions_df2.loc[hf_decreased_positions_df2['SYMBOL'] == symbol, 'SHARES'].values
            pct_change = (new_shares - old_shares)/old_shares
            hf_decreased_positions_df1 = hf_decreased_positions_df1.copy()
            hf_decreased_positions_df1.loc[hf_decreased_positions_df1['SYMBOL'] == symbol,'PCT_CHANGE']= pct_change
        except Exception as e: 
            print(e)
            pass

    hf_decreased_positions_df1 = hf_decreased_positions_df1.copy()
    hf_decreased_positions_df1 = hf_decreased_positions_df1.reset_index(drop = True)
    # hf_decreased_positions_df1['PCT_CHANGE'] = round(hf_decreased_positions_df1['PCT_CHANGE']*100,3)   

    hf_decreased_positions_df1 = hf_decreased_positions_df1.sort_values('VALUE', ascending=False)
    hf_decreased_positions_df1 = hf_decreased_positions_df1.reset_index(drop=True)
    hf_decreased_positions_df1

    hf_decreased_percent_df1 = hf_decreased_positions_df1.sort_values('PCT_CHANGE', ascending=True)
    hf_decreased_percent_df1 = hf_decreased_percent_df1.reset_index(drop=True)
    hf_decreased_percent_df1

    hf_decreased_funds_df1 = hf_decreased_positions_df1.sort_values('FUND_COUNT', ascending=False)
    hf_decreased_funds_df1 = hf_decreased_funds_df1.reset_index(drop=True)
    hf_decreased_funds_df1



    try:
        hf_decreased_positions_df1['PCT_CHANGE'] = hf_decreased_positions_df1['PCT_CHANGE'].apply('{:.2%}'.format)
    except Exception as e: 
        print(e)
        pass   

    try:
        hf_decreased_percent_df1['PCT_CHANGE'] = hf_decreased_percent_df1['PCT_CHANGE'].apply('{:.2%}'.format)
    except Exception as e: 
        print(e)
        pass   

    try:
        hf_decreased_funds_df1['PCT_CHANGE'] = hf_decreased_funds_df1['PCT_CHANGE'].apply('{:.2%}'.format)
    except Exception as e: 
        print(e)
        pass   

    unchanged_list = []
    for symbol in common:
        df = hf_df[hf_df['SYMBOL']== symbol]
    #     decreased_list = []
        try:
            if (df['SHARES'][df['DATE']== new_date].values.sum() == df['SHARES'][df['DATE']== old_date].values.sum())==True:
                unchanged_list.append(symbol)
            else:
                pass
        except Exception as e: 
            print(e)
            pass

    hf_unchanged_positions_df = hf_df[(hf_df['DATE'] == new_date) & (hf_df['SYMBOL'].isin(unchanged_list)) ]
    hf_unchanged_positions_df = hf_unchanged_positions_df.sort_values('VALUE', ascending=False)
    hf_unchanged_positions_df = hf_unchanged_positions_df.reset_index(drop=True)
    hf_unchanged_positions_df


    hf_df_new_list = hf_df['SYMBOL'][hf_df['DATE']== new_date].to_list()
    hf_df_old_list = hf_df['SYMBOL'][hf_df['DATE']== old_date].to_list()


    hf_new_positions_list=sorted(hf_new_positions_df['SYMBOL'].to_list())
    hf_new_positions_list  = list(filter(None, hf_new_positions_list))
    hf_new_positions_list_tweet = ','.join(hf_new_positions_list)
    # hf_new_positions_list_tweet = ', $'.join(hf_new_positions_list)
    # hf_new_positions_list_tweet = "$"+hf_new_positions_list_tweet


    hf_closed_positions_list=sorted(hf_closed_positions_df['SYMBOL'].to_list())
    hf_closed_positions_list  = list(filter(None, hf_closed_positions_list))
    hf_closed_positions_list_tweet = ','.join(hf_closed_positions_list)
    # hf_closed_positions_list_tweet = ', $'.join(hf_closed_positions_list)
    # hf_closed_positions_list_tweet = "$"+hf_closed_positions_list_tweet


    hf_increased_positions_list=sorted(hf_increased_positions_df1['SYMBOL'].to_list())
    hf_increased_positions_list  = list(filter(None, hf_increased_positions_list))
    hf_increased_positions_list_tweet = ','.join(hf_increased_positions_list)
    # hf_increased_positions_list_tweet = ', $'.join(hf_increased_positions_list)
    # hf_increased_positions_list_tweet = "$"+hf_increased_positions_list_tweet


    hf_decreased_positions_list=sorted(hf_decreased_positions_df1['SYMBOL'].to_list())
    hf_decreased_positions_list  = list(filter(None, hf_decreased_positions_list))
    hf_decreased_positions_list_tweet = ','.join(hf_decreased_positions_list)
    # hf_decreased_positions_list_tweet = ', $'.join(hf_decreased_positions_list)
    # hf_decreased_positions_list_tweet = "$"+hf_decreased_positions_list_tweet

    hf_unchanged_positions_list=sorted(hf_unchanged_positions_df['SYMBOL'].to_list())
    hf_unchanged_positions_list  = list(filter(None, hf_unchanged_positions_list))
    hf_unchanged_positions_list_tweet = ','.join(hf_unchanged_positions_list)
    # hf_unchanged_positions_list_tweet = ', $'.join(hf_unchanged_positions_list)
    # hf_unchanged_positions_list_tweet = "$"+hf_unchanged_positions_list_tweet


    try:
        conn = sqlite3.connect("BiotechDatabase.db")
        # pd.read_sql_query("select * from biotech where symbol='MYOV';", conn)
        catalysts_df = pd.read_sql_query("select * from catalysts_bfc;", conn)
        catalysts_df = catalysts_df. rename(columns = {'symbol':'SYMBOL'}) 
        try:
            catalysts_df = catalysts_df.drop(columns = {'Catalyst Last Updated','Last Updated','Price'})
        except:
            pass
        catalysts_df['Catalyst Rank'] = catalysts_df.index
    except sqlite3.Error as error:
        print("Failed to access the BiotechDatabase file", error)  
    finally:
        if (conn):
            conn.close()

    hf_new_positions_df = hf_new_positions_df.assign(Position = 'New')
    hf_closed_positions_df = hf_closed_positions_df.assign(Position = 'Closed')      
    hf_increased_positions_df1 = hf_increased_positions_df1.assign(Position = 'Increased')
    new_increased_positions_df = pd.concat([hf_new_positions_df, hf_increased_positions_df1], ignore_index=True,axis=0)
    hf_new_increased_positions_with_catalysts_df = pd.merge(catalysts_df,new_increased_positions_df,
                    on='SYMBOL', 
                    how='inner').sort_values(by = 'Catalyst Rank', ascending = True).reset_index(drop=True) 

    hf_new_increased_positions_with_catalysts_df = hf_new_increased_positions_with_catalysts_df.loc[hf_new_increased_positions_with_catalysts_df['SYMBOL']!= 'XBI'].reset_index(drop=True)                
    # hf_new_increased_positions_with_catalysts_df = hf_new_increased_positions_with_catalysts_df[['SYMBOL','Catalyst Date','Stage','Drug','Indication','NAME_OF_ISSUER',	'VALUE', 'SHARES','PERCENT','Price','Mkt. Cap','Float','3 Month Percentage Change','First Traded','Cash/Short Term Inv.','Months to 0$','Position','PCT_CHANGE']]
    
    
    hf_decreased_positions_df1 = hf_decreased_positions_df1.assign(Position = 'Decreased')
    closed_decreased_positions_df = pd.concat([hf_closed_positions_df, hf_decreased_positions_df1], ignore_index=True,axis=0)
    hf_closed_decreased_positions_with_catalysts_df = pd.merge(catalysts_df,closed_decreased_positions_df,
                    on='SYMBOL', 
                    how='inner').sort_values(by = 'Catalyst Rank', ascending = True).reset_index(drop=True) 
    hf_closed_decreased_positions_with_catalysts_df = hf_closed_decreased_positions_with_catalysts_df.loc[hf_closed_decreased_positions_with_catalysts_df['SYMBOL']!= 'XBI'].reset_index(drop=True)     
    # hf_closed_decreased_positions_with_catalysts_df = hf_closed_decreased_positions_with_catalysts_df[['SYMBOL','Catalyst Date','Stage','Drug','Indication','NAME_OF_ISSUER',	'VALUE', 'SHARES','PERCENT','Price','Mkt. Cap','Float','3 Month Percentage Change','First Traded','Cash/Short Term Inv.','Months to 0$','Position','PCT_CHANGE']]
    


    hf_new_increased_positions_with_catalysts_list=sorted(list(set(hf_new_increased_positions_with_catalysts_df['SYMBOL'].to_list())))
    hf_new_increased_positions_with_catalysts_list  = list(filter(None, hf_new_increased_positions_with_catalysts_list))
    hf_new_increased_positions_with_catalysts_list_tweet = ', $'.join(hf_new_increased_positions_with_catalysts_list)
    hf_new_increased_positions_with_catalysts_list_tweet = "$"+hf_new_increased_positions_with_catalysts_list_tweet


    hf_closed_decreased_positions_with_catalysts_list=sorted(list(set(hf_closed_decreased_positions_with_catalysts_df['SYMBOL'].to_list())))
    hf_closed_decreased_positions_with_catalysts_list  = list(filter(None, hf_closed_decreased_positions_with_catalysts_list))
    hf_closed_decreased_positions_with_catalysts_list_tweet = ', $'.join(hf_closed_decreased_positions_with_catalysts_list)
    hf_closed_decreased_positions_with_catalysts_list_tweet = "$"+hf_closed_decreased_positions_with_catalysts_list_tweet

    print('')
    string = " Report for Combined Biotech 13F Filings"
    string2 = '''(Avoro, Baker Brothers, Boxer, BVF, Casdin, Cormorant, Deep Track, EcoR1, Logos, Opaleye, Orbimed, Perceptive, RA Capital, Tang)'''
    new_string = (string).center(70)
    new_string2 = (string2).center(70)
    print(new_string)
    print(new_string2)
    print('')  
    top_40 = holdings_df.sort_values(by="VALUE", ascending=False)[["SYMBOL", "VALUE"]][:40]
    top_40_df = holdings_df.sort_values(by="VALUE", ascending=False)
    top_40_df = top_40_df.head(40)
    top_40_df = top_40_df.reset_index(drop=True)
    a = top_40.SYMBOL
    b = top_40.VALUE
    c = range(len(b))

    fig = plt.figure(figsize=(15,5))
    ax = fig.add_subplot(111)
    ax.bar(c, b)

    plt.xticks(c, a, rotation=90)
    plt.title('Top 40 Stock Holdings by Value')
    plt.xlabel('Stock Ticker')
    plt.ylabel('USD')
    plt.show()


    print('Top 40 Stock Holdings by Value')
    display(top_40_df)
    print('')
    print("New Positions (Not previously in any of the funds) Sorted by Value")
    display(hf_new_positions_df)
    print('-'*60)
    print('-'*60)
    print('')
    print("New Positions (Not previously in any of the funds) Sorted by Number of Funds initiating the new position")
    display(hf_new_positions_by_fund_count_df)
    print('-'*60)
    print('-'*60)
    print('')
    print("Increased Positions (when all funds shares were added together) Sorted by Value")
    display(hf_increased_positions_df1)
    print('-'*60)
    print('-'*60)
    print('')
    print("Increased Positions (when all funds shares were added together) Sorted by Increase in Share %")
    display(hf_increased_percent_df1.head(20))
    print('-'*60)
    print('-'*60)
    print('')
    print("Increased Positions (when all funds shares were added together) Sorted by the Highest Fund Number")
    display(hf_increased_funds_df1.head(20))
    print('-'*60)
    print('-'*60)
    print('')
    print("Closed Positions (No longer in any in any of the funds) Sorted by Value")
    display(hf_closed_positions_df)
    print('-'*60)
    print('-'*60)
    print('')
    print("Decreased Positions (when all funds shares were added together) Sorted by Value")
    display(hf_decreased_positions_df1)
    print('-'*60)
    print('-'*60)
    print('')
    print("Decreased Positions (when all funds shares were added together) Sorted by Decrease in Share %")
    display(hf_decreased_percent_df1.head(20))
    print('-'*60)
    print('-'*60)
    print('')
    print("Decreased Positions (when all funds shares were added together) with the Highest Fund Number")
    display(hf_decreased_funds_df1.head(20))
    print('-'*60)
    print('-'*60)
    print('')
    print("Unchanged Positions (when all funds shares were added together) Sorted by Value")
    display(hf_unchanged_positions_df)
    print('-'*60)
    print('-'*60)
    print('')
    print("New or Increased Positions with Nearby Catalysts")
    display(hf_new_increased_positions_with_catalysts_df)
    print('-'*60)
    print('-'*60)
    print("Closed or Decreased Positions with Nearby Catalysts")
    display(hf_closed_decreased_positions_with_catalysts_df)
    print('-'*60)
    print('-'*60)
    print('')

    print('13F positions: ')
    print('New: '+ hf_new_positions_list_tweet)
    print('Increased: '+ hf_increased_positions_list_tweet)
    print('Closed: '+ hf_closed_positions_list_tweet)
    print('Decreased: '+ hf_decreased_positions_list_tweet)
    print('Unchanged: '+ hf_unchanged_positions_list_tweet)

def biotech_hf(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    # ticker = Ticker(symbols, asynchronous=True)
    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db") 
        cur = conn.cursor()
        sql_select_query = "select SYMBOL,DATE,SHARES,VALUE,FUND,RANK,PERCENT from HF_cumulative_holdings where symbol = ?"
        cur.execute(sql_select_query,(symbol,))
    #     db = pd.read_sql_query(sql_select_query, conn)
        rows = cur.fetchall()
        num_fields = len(cur.description)
        field_names = [i[0] for i in cur.description]
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print("Failed to select symbol from HF_cumulative_holdings", error)
    finally:
        if (conn):
            conn.close()   

    if not rows:
        print(symbol+ " is not in the HF_cumulative_holdings database")
    else:
        try:
            df = pd.DataFrame (rows,columns=field_names)
            df['DATE'] = df['DATE'].astype('datetime64[ns]')
            funds=df['FUND'].unique().tolist()

            for fund in funds:
                df_fund = df.loc[df.FUND== fund].copy()
                df_fund = df_fund.reset_index(drop=True)
                display(df_fund)
        except Exception as e: 
            print(e)
            pass

def biotech_current_hf(symbol):
    symbol = symbol.upper()
    symbols = symbol.split(',')
    # ticker = Ticker(symbols, asynchronous=True)
    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db") 
        cur = conn.cursor()
        sql_select_query = f"select * from HF_current_holdings where SYMBOL = '{symbol}'"
        
        df = pd.read_sql_query(sql_select_query, conn)
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print("Failed to select symbol from HF_current_holdings", error)
    finally:
        if (conn):
            conn.close()   

    if df.empty:
        print(symbol+ " is not in the HF_current_holdings database")
    else:
        return df
    
#-------------------------------------------------------
def ratios(symbols):
    symbol_list =  symbols.split(",")

    from datetime import datetime
    import pandas as pd
    from yahooquery import Ticker
    import numpy as np
    import datetime
    import math
    df_ratios_list = []
    
    for symbol in symbol_list:
        symbol = symbol.upper()
        ticker = Ticker(symbol, asynchronous=True)

        #Most Recent Quarter Date
        try:
            mostRecentQuarter_str = ticker.key_stats[symbol]['mostRecentQuarter']
            mostRecentQuarter = datetime.datetime.strptime(mostRecentQuarter_str, '%Y-%m-%d')
            mostRecentQuarter = mostRecentQuarter.date()  

            year = mostRecentQuarter.year
            month = mostRecentQuarter.month
            quarter = (month - 1) // 3 + 1
            quarter_string = "Q"+str(quarter)+ " "+str(year)
            quarter_string
        except Exception as e: 
            quarter_string = np.nan
            print(symbol +  " quarter_string error: " + str(e))
            pass


        #Price Items
        try:    
            marketCap = ticker.price[symbol]['marketCap']
        except Exception as e: 
            marketCap = np.nan
            print(symbol +  " marketCap error: " + str(e))
            pass

        try:
            price = ticker.price[symbol]['regularMarketPrice']
        except Exception as e: 
            price = np.nan
            print(symbol +  " price error: " + str(e))
            pass
        # price_AH = ticker.price[symbol]['postMarketPrice']

        #Financial statement TTM items
        try:
            fs_TTM_df = ticker.income_statement("q")[ticker.income_statement("q")['periodType'] == 'TTM'].tail(1)
        except Exception as e: 
            fs_TTM_df = pd.DataFrame()
            print(symbol +  " fs_TTM_df error: " + str(e))
            pass

        if fs_TTM_df.empty ==True:
            EBITDA = EBIT = TotalRevenue = CostOfRevenue = GrossProfit = InterestExpense = OperatingIncome = NetIncome = 'Missing'
        else:
            try:
                EBITDA = fs_TTM_df['EBITDA'].iloc[0]
                
            except Exception as e: 
                EBITDA = np.nan
                print(symbol +   " EBITDA error: " + str(e))
                pass

            try:
                EBIT = fs_TTM_df['EBIT'].iloc[0]          
            except Exception as e: 
                EBIT = np.nan
                print(symbol +  " EBIT error: " + str(e))
                pass

            try:
                TotalRevenue = fs_TTM_df['TotalRevenue'].iloc[0]
            except Exception as e: 
                TotalRevenue = np.nan
                print(symbol +  " TotalRevenue error: " + str(e))
                pass

            try:
                CostOfRevenue = fs_TTM_df['CostOfRevenue'].iloc[0]
            except Exception as e: 
                CostOfRevenue = np.nan
                print(symbol +  " CostOfRevenue error: " + str(e))
                pass

            try:
                GrossProfit	= fs_TTM_df['GrossProfit'].iloc[0]
            except Exception as e: 
                GrossProfit = np.nan
                print(symbol +  " GrossProfit error: " + str(e))
                pass

            try:    
                InterestExpense = fs_TTM_df['InterestExpense'].iloc[0]
            except Exception as e: 
                InterestExpense = np.nan
                print(symbol +  " InterestExpense error: " + str(e))
                pass

            try:
                OperatingIncome = fs_TTM_df['OperatingIncome'].iloc[0]
            except Exception as e: 
                OperatingIncome = np.nan
                print(symbol +  " OperatingIncome error: " + str(e))
                pass

            try:
                NetIncome = fs_TTM_df['NetIncome'].iloc[0]
            except Exception as e: 
                NetIncome = np.nan
                print(symbol +  " NetIncome error: " + str(e))
            pass

        #Financial statement Last Quarter items
        try:
            fs_q_df = ticker.income_statement("q")[ticker.income_statement("q")['periodType'] != 'TTM'].tail(1)
            revenue_growth_pct = ticker.income_statement("q")[ticker.income_statement("q")['periodType'] != 'TTM']
        except Exception as e: 
            fs_q_df = pd.DataFrame()
            revenue_growth_pct = pd.DataFrame()
            print(symbol +  " fs_q_df error: " + str(e))
            pass

        try:
            revenue_growth_pct_annual = ticker.income_statement("a")[ticker.income_statement("a")['periodType'] != 'TTM']
        except Exception as e: 
            revenue_growth_pct_annual= pd.DataFrame()
            print(symbol +   "revenue_growth_pct_annual error: " + str(e))
            pass 

        if revenue_growth_pct.empty ==True:
            revenue_growth_pct_currentQ = 'Missing'
            revenue_growth_pct_previousQ = 'Missing'   
        else:
            try:
                revenue_growth_pct['TotalRevenueGrowthPercent']=round(revenue_growth_pct['TotalRevenue'].pct_change(),2)
                revenue_growth_pct_currentQ = revenue_growth_pct['TotalRevenueGrowthPercent'].iloc[-1]
            except Exception as e: 
                revenue_growth_pct_currentQ = np.nan
                print(symbol +  " revenue_growth_pct_currentQ error: " + str(e))
                pass 

            try:
                revenue_growth_pct['TotalRevenueGrowthPercent']=round(revenue_growth_pct['TotalRevenue'].pct_change(),2)
                revenue_growth_pct_previousQ = revenue_growth_pct['TotalRevenueGrowthPercent'].iloc[-2]
            except Exception as e: 
                revenue_growth_pct_previousQ = np.nan
                print(symbol +  " revenue_growth_pct_previousQ error: " + str(e))
                pass 

        if revenue_growth_pct_annual.empty ==True:
            revenue_growth_pct_currentY = 'Missing'
        else:
            try:
                revenue_growth_pct_annual['TotalRevenueGrowthPercent']=round(revenue_growth_pct_annual['TotalRevenue'].pct_change(),2)
                revenue_growth_pct_currentY = revenue_growth_pct_annual['TotalRevenueGrowthPercent'].iloc[-1]
            except Exception as e: 
                revenue_growth_pct_currentY = np.nan
                print(symbol +  " revenue_growth_pct_currentY error: " + str(e))
                pass 

        if fs_q_df.empty ==True:
            TotalRevenue_q = CostOfRevenue_q= GrossProfit_q=OperatingIncome_q=NetIncome_q='Missing'
        else:
            try:
                TotalRevenue_q = fs_q_df['TotalRevenue'].iloc[0] 
            except Exception as e: 
                TotalRevenue_q = np.nan
                print(symbol +  " TotalRevenue_q error: " + str(e))
                pass 

            try:
                CostOfRevenue_q = fs_q_df['CostOfRevenue'].iloc[0]
            except Exception as e: 
                CostOfRevenue_q = np.nan
                print(symbol +  " CostOfRevenue_q error: " + str(e))
                pass

            try:
                GrossProfit_q	= fs_q_df['GrossProfit'].iloc[0]
            except Exception as e: 
                GrossProfit_q = np.nan
                print(symbol +  " GrossProfit_q error: " + str(e))
                pass

            try:
                OperatingIncome_q = fs_q_df['OperatingIncome'].iloc[0]
            except Exception as e: 
                OperatingIncome_q = np.nan
                print(symbol +  " OperatingIncome_q error: " + str(e))
                pass

            try:
                NetIncome_q = fs_q_df['NetIncome'].iloc[0]
            except Exception as e: 
                NetIncome_q = np.nan
                print(symbol +  " NetIncome_q error: " + str(e))
                pass

        #Balance sheet items
        try:
            bs_df = ticker.balance_sheet("q").tail(1)
        except Exception as e: 
            bs_df= pd.DataFrame()
            print(symbol +  " bs_df error: " + str(e))
            pass
        
        if bs_df.empty ==True:
            TotalAssets = TotalLiabilitiesNetMinorityInterest=CurrentAssets=CurrentLiabilities=Inventory=CashCashEquivalentsAndShortTermInvestments=ShareIssued=TotalDebt=StockholdersEquity=TangibleBookValue=RetainedEarnings=Payables='Missing'
        else:

            try:
                TotalAssets = bs_df['TotalAssets'].iloc[0]
            except Exception as e: 
                TotalAssets = np.nan
                print(symbol +  " TotalAssets error: " + str(e))
                pass

            try:
                TotalLiabilitiesNetMinorityInterest = bs_df['TotalLiabilitiesNetMinorityInterest'].iloc[0]
            except Exception as e: 
                TotalLiabilitiesNetMinorityInterest = np.nan
                print(symbol +  " TotalLiabilitiesNetMinorityInterest error: " + str(e))
                pass

            try:
                CurrentAssets = bs_df['CurrentAssets'].iloc[0]
            except Exception as e: 
                CurrentAssets = np.nan
                print(symbol +  " CurrentAssets error: " + str(e))
                pass     

            try:
                CurrentLiabilities = bs_df['CurrentLiabilities'].iloc[0]
            except Exception as e: 
                CurrentLiabilities = np.nan
                print(symbol +  " CurrentLiabilities error: " + str(e))
                pass

            try:
                Inventory = bs_df['Inventory'].iloc[0]
            except Exception as e: 
                Inventory = np.nan
                print(symbol +  " Inventory error: " + str(e))
                pass

            try:
                CashCashEquivalentsAndShortTermInvestments = bs_df['CashCashEquivalentsAndShortTermInvestments'].iloc[0]
            except Exception as e: 
                CashCashEquivalentsAndShortTermInvestments = np.nan
                print(symbol +  " CashCashEquivalentsAndShortTermInvestments error: " + str(e))
                pass        

            try:
                ShareIssued = bs_df['ShareIssued'].iloc[0]
            except Exception as e: 
                ShareIssued = np.nan
                print(symbol +  " ShareIssued error: " + str(e))
                pass        

            try:
                TotalDebt = bs_df['TotalDebt'].iloc[0]
            except Exception as e: 
                TotalDebt = np.nan
                print(symbol +  " TotalDebt error: " + str(e))
                pass   

            try:
                StockholdersEquity = bs_df['StockholdersEquity'].iloc[0]
            except Exception as e: 
                StockholdersEquity = np.nan
                print(symbol +  " StockholdersEquity error: " + str(e))
                pass        

            try:
                TangibleBookValue = bs_df['TangibleBookValue'].iloc[0]
            except Exception as e: 
                TangibleBookValue = np.nan
                print(symbol +  " TangibleBookValue error: " + str(e))
                pass        

            try:
                RetainedEarnings = bs_df['RetainedEarnings'].iloc[0]
            except Exception as e: 
                RetainedEarnings = np.nan
                print(symbol +  " RetainedEarnings error: " + str(e))
                pass

            try:
                Payables = bs_df['Payables'].iloc[0]
            except Exception as e: 
                Payables = np.nan
                print(symbol +  " Payables error: " + str(e))
                pass        

        #Balance Sheet items from previous quarter:
        try:
            bs_df_old = ticker.balance_sheet("q").tail(2).head(1)
        except Exception as e: 
            bs_df_old = pd.DataFrame()
            print(symbol +  " bs_df_old error: " + str(e))
            pass
        
        if bs_df_old.empty==True:
            Inventory_old = 'Missing'
        else:
            try:
                Inventory_old = bs_df_old['Inventory'].iloc[0]
            except Exception as e: 
                Inventory_old = np.nan
                print(symbol +  " Inventory_old error: " + str(e))
                pass

        #Cash Flow Statement Items
        try:
            cf_TTM_df = ticker.cash_flow("q")[ticker.cash_flow("q")['periodType'] == 'TTM']
        except Exception as e: 
            cf_TTM_df = pd.DataFrame()
            print(symbol +  " cf_TTM_df error: " + str(e))
            pass 

        if cf_TTM_df.empty==True:
            FreeCashFlow = CashFlowFromContinuingOperatingActivities = 'Missing'
        else:
            try:
                FreeCashFlow = cf_TTM_df['FreeCashFlow'].iloc[0]
            except Exception as e: 
                FreeCashFlow = np.nan
                print(symbol +  " FreeCashFlow error: " + str(e))
                pass       

            try:
                CashFlowFromContinuingOperatingActivities = cf_TTM_df['CashFlowFromContinuingOperatingActivities'].iloc[0]
            except Exception as e: 
                CashFlowFromContinuingOperatingActivities = np.nan
                print(symbol +  " CashFlowFromContinuingOperatingActivities error: " + str(e))
                pass

        #Key Stat Items
        try:
            ev = ticker.key_stats[symbol]['enterpriseValue']
        except Exception as e: 
            ev = np.nan
            print(symbol +  " ev error: " + str(e))
            pass
        # totalCashPerShare = ticker.financial_data[symbol]['totalCashPerShare']
        try:
            eps = ticker.key_stats[symbol]['trailingEps']
        except Exception as e: 
            eps = np.nan
            print(symbol +  " eps error: " + str(e))
            pass

        try:
            peg =  ticker.key_stats[symbol]['pegRatio']
        except Exception as e: 
            peg = np.nan
            print(symbol +  " peg error: " + str(e))
            pass

        ##RATIO CALCULATIONS##
        price = price
        # price_AH = price_AH


        #Profitability TTM
        if GrossProfit == 'Missing' or TotalRevenue == 'Missing' or OperatingIncome == 'Missing' or NetIncome == 'Missing':
            GrossMargin = 'Missing'
            OperatingMargin= 'Missing'
            NetMargin= 'Missing'

        elif TotalRevenue ==0:
            GrossMargin = np.nan
            OperatingMargin= np.nan
            NetMargin= np.nan
            
        else:
            GrossMargin = round(GrossProfit/TotalRevenue,2)
            OperatingMargin = round(OperatingIncome/TotalRevenue,2)
            NetMargin = round(NetIncome/TotalRevenue,2)

        #Profitability Last Quarter
        if GrossProfit_q == 'Missing' or TotalRevenue_q == 'Missing' or OperatingIncome_q == 'Missing' or NetIncome_q == 'Missing':
            GrossMargin_q  = 'Missing'
            OperatingMargin_q= 'Missing'
            NetMargin_q= 'Missing'

        elif TotalRevenue_q ==0:
            GrossMargin_q  = np.nan
            OperatingMargin_q= np.nan
            NetMargin_q= np.nan   
        else:
            GrossMargin_q = round(GrossProfit_q/TotalRevenue_q,2)
            OperatingMargin_q = round(OperatingIncome_q/TotalRevenue_q,2)
            NetMargin_q = round(NetIncome_q/TotalRevenue_q,2)

        #Per Share Ratios
        if CashCashEquivalentsAndShortTermInvestments == 'Missing' or ShareIssued == 'Missing':
            TotalCashPerShare = 'Missing'
        else:
            TotalCashPerShare =  round(CashCashEquivalentsAndShortTermInvestments/ShareIssued,2)
        eps = eps
        if StockholdersEquity == 'Missing' or ShareIssued == 'Missing':
            bvpershare = 'Missing'   
        else:
            bvpershare = round(StockholdersEquity/ShareIssued,2)
        if CashCashEquivalentsAndShortTermInvestments == 'Missing' or ShareIssued == 'Missing' or TotalDebt == 'Missing' :
            NetCashPerShare = 'Missing'
        else:
            NetCashPerShare = round((CashCashEquivalentsAndShortTermInvestments - TotalDebt)/ShareIssued,2)

        #Price Ratios
        try:
            peratio = round(price / eps,2)
        except Exception as e: 
            peratio = np.nan
            print(symbol +  " peratio error: " + str(e))
            pass          

        try:
            forwardPE = round(ticker.key_stats[symbol]['forwardPE'],2)
        except Exception as e: 
            forwardPE = np.nan
            print(symbol +  " forwardPE error: " + str(e))
            pass  

        # peratio_AH = round(price_AH / eps,2)
        peg = peg

        if marketCap == 'Missing' or TotalRevenue == 'Missing':
            priceToSales ='Missing'   
        elif TotalRevenue ==0:
            priceToSales  = np.nan    
        else:
            priceToSales = round(marketCap/TotalRevenue,2)

        if marketCap == 'Missing' or FreeCashFlow == 'Missing':
            pricetoFCF ='Missing'  
        elif FreeCashFlow ==0:
            pricetoFCF  = np.nan 
        else: 
            pricetoFCF = round(marketCap/FreeCashFlow,2)

        if marketCap == 'Missing' or TangibleBookValue == 'Missing':
            priceToTangibleBook = 'Missing'  
        elif TangibleBookValue ==0:
            priceToTangibleBook  = np.nan    
        else:
            priceToTangibleBook = round(marketCap/TangibleBookValue,2)

        #EV Ratios
        if EBITDA == 'Missing' or ev =='Missing':
            EVToEBITDA = 'Missing'
        elif EBITDA ==0:
            EVToEBITDA  = np.nan 
        else:
            try:
                EVToEBITDA =round(ev/EBITDA,2)
            except Exception as e: 
                EVToEBITDA = np.nan
                print(symbol +  " EVToEBITDA error: " + str(e))
                pass  

        if EBIT == 'Missing' or ev =='Missing':
            EVToEBIT = 'Missing'
        elif EBIT ==0:
            EVToEBITD  = np.nan 
        else:
            try:
                EVToEBIT= round(ev/EBIT,2)
            except Exception as e: 
                EVToEBIT = np.nan
                print(symbol +  " EVToEBIT error: " + str(e))
                pass  

        if TotalRevenue == 'Missing' or ev =='Missing':
            EVToTotalRevenue = 'Missing'
        elif TotalRevenue ==0:
            EVToTotalRevenue  = np.nan 
        else:
            try:
                EVToTotalRevenue = round(ev/TotalRevenue,2)
            except Exception as e: 
                EVToTotalRevenue = np.nan
                print(symbol +  "EVToTotalRevenue error: " + str(e))
                pass  

        #Performance
        if NetIncome == 'Missing' or StockholdersEquity == 'Missing':
            returnOnEquity = 'Missing'
        else:
            try:
                returnOnEquity = round(NetIncome/StockholdersEquity,2)
            except Exception as e: 
                returnOnEquity = np.nan
                print(symbol +  " returnOnEquity error: " + str(e))
                pass      

        if TotalAssets == 'Missing' or NetIncome == 'Missing':
            returnOnAssets  = 'Missing'
        elif TotalAssets == 0:
            returnOnAssets  = np.nan
        else:
            try:
                returnOnAssets = round(NetIncome/TotalAssets,2)
            except Exception as e: 
                returnOnAssets = np.nan
                print(symbol +  " returnOnAssets error: " + str(e))
                pass  


        #Liquidity Ratios
        if CurrentAssets == 'Missing' or CurrentLiabilities == 'Missing':
            currentRatio = 'Missing'
        else:
            currentRatio = round(CurrentAssets/CurrentLiabilities,2)
        if CurrentAssets == 'Missing' or CurrentLiabilities == 'Missing' or Inventory == 'Missing':
            quickRatio = 'Missing'
        else:
            quickRatio = round((CurrentAssets - Inventory)/CurrentLiabilities,2)
        if Inventory == 'Missing' or Inventory_old == 'Missing' or CostOfRevenue_q =='Missing':  
            daysInventory = 'Missing'
        elif Inventory == 0 or Inventory_old == 0 or CostOfRevenue_q ==0:
            daysInventory  = np.nan
        else:
            daysInventory = round((((Inventory + Inventory_old)/2)/CostOfRevenue_q)* 365 / 4,2)

        #Solvency
        if StockholdersEquity == 'Missing' or TotalDebt == 'Missing':
            debtToEquity = 'Missing'
        elif StockholdersEquity == 0:
            debtToEquity  = np.nan   
        else: 
            try:
                debtToEquity = round(TotalDebt/StockholdersEquity,2)
            except Exception as e: 
                debtToEquity = np.nan
                print(symbol +  " debtToEquity error: " + str(e))
                pass 

        if TotalAssets == 'Missing' or TotalDebt=='Missing':
            debtToAsset = 'Missing'
        elif TotalAssets == 0:
            debtToAsset  = np.nan  
        else:
            try:
                debtToAsset = round(TotalDebt/TotalAssets,2)
            except Exception as e: 
                debtToAsset = np.nan
                print(symbol +  "debtToAsset error: " + str(e))
                pass 

        if InterestExpense == 'Missing' or EBIT=='Missing':
            EBITToInterest = 'Missing'
        elif InterestExpense == 0:
            EBITToInterest = np.nan
        else:
            try:
                EBITToInterest   = round(EBIT / InterestExpense,2)
            except Exception as e: 
                EBITToInterest = np.nan
                print(symbol +  " EBITToInterest error: " + str(e))
                pass 

        if InterestExpense == 'Missing' or CashFlowFromContinuingOperatingActivities == 'Missing':
            CFOToInterest = 'Missing'
        elif InterestExpense == 0:
            CFOToInterest = np.nan
        else:
            try:
                CFOToInterest = round(CashFlowFromContinuingOperatingActivities/InterestExpense,2)
            except Exception as e: 
                CFOToInterest = np.nan
                print(symbol +  " CFOToInterest error: " + str(e))
                pass 

        if TotalDebt == 'Missing' or CashFlowFromContinuingOperatingActivities == 'Missing':
            CFOToDebt = 'Missing'
        elif TotalDebt == 0:
            CFOToDebt = np.nan
        else:
            try:
                CFOToDebt = round(CashFlowFromContinuingOperatingActivities/TotalDebt,2)
            except Exception as e: 
                CFOToDebt = np.nan
                print(symbol +  " CFOToDebt error: " + str(e))
                pass 

        if TotalDebt == 'Missing' or FreeCashFlow == "Missing":
            FCFToDebt = 'Missing'
        elif TotalDebt == 0:
            FCFToDebt = np.nan
        else:
            try:
                FCFToDebt = round(FreeCashFlow/TotalDebt,2)
            except Exception as e: 
                FCFToDebt = np.nan
                print(symbol +  " FCFToDebt error: " + str(e))
                pass 




        if TotalAssets =='Missing' or TotalLiabilitiesNetMinorityInterest == 'Missing' or CurrentAssets =='Missing' or CurrentLiabilities == 'Missing'  or ShareIssued == 'Missing' or RetainedEarnings == 'Missing' or EBIT == 'Missing' or price == 'Missing' or TotalRevenue == 'Missing':
            Altman = 'Missing'
    
        elif TotalAssets ==0 or TotalLiabilitiesNetMinorityInterest == 0 or math.isnan(CurrentAssets) == True or math.isnan(CurrentLiabilities) == True  or math.isnan(ShareIssued) == True or math.isnan(TotalAssets) == True :
            Altman = np.nan
        else:
            #Altman Z-score
            x1 = 0.012 * 100 * ((CurrentAssets - CurrentLiabilities)/TotalAssets)
            x2 = 0.014 * 100 * RetainedEarnings/TotalAssets
            x3 = 0.033 * 100 * EBIT/TotalAssets
            x4 = 0.006 * 100 * price * ShareIssued / TotalLiabilitiesNetMinorityInterest
            x5 = 0.999  * TotalRevenue/TotalAssets
            Altman = round(x1+x2+x3+x4+x5,2)


        ##DATAFRAME BUILD-UP##

        df = pd.DataFrame()
        df[symbol] = ""
        df.loc['Most Recent Quarter'] = mostRecentQuarter
        
        
        #Prices
        df.loc['Regular Market Price'] = price
        # df.loc['Post Market Price'] = price_AH

        #Growth
        df.loc['Revenue Growth Pct Current Q'] = revenue_growth_pct_currentQ
        df.loc['Revenue Growth Pct Previous Q'] =revenue_growth_pct_previousQ
        df.loc['Revenue Growth Pct Current Y']=revenue_growth_pct_currentY

        #Profitability TTM
        df.loc['Gross Margin TTM'] = GrossMargin
        df.loc['Operating Margin TTM'] = OperatingMargin
        df.loc['Net Margin TTM'] = NetMargin

        #Profitability Last Quarter
        df.loc['Gross Margin LastQ'] = GrossMargin_q
        df.loc['Operating Margin LastQ'] = OperatingMargin_q
        df.loc['Net Margin LastQ'] = NetMargin_q

        #Per Share Ratios
        df.loc['Book Value Per Share'] = bvpershare
        df.loc['Total Cash Per Share'] = TotalCashPerShare
        df.loc['Trailing EPS'] = eps
        df.loc['Net Cash/Share'] = NetCashPerShare



        #Price Ratios
        df.loc['PE Ratio']= peratio
        # df.loc['PE Ratio After Hours'] = peratio_AH
        df.loc['Forward PE'] = forwardPE
        df.loc['PEG Ratio'] = peg
        df.loc['Price to Sales'] = priceToSales
        df.loc['Price to T.Book'] = priceToTangibleBook
        df.loc['Price to FCF'] = pricetoFCF


        df.loc['EV/EBITDA'] = EVToEBITDA
        df.loc['EV/EBIT'] = EVToEBIT
        df.loc['EV/Sales'] = EVToTotalRevenue

        #Performance
        df.loc['Return On Assets'] = returnOnAssets
        df.loc['Return On Equity'] = returnOnEquity
        
        #Liquidity
        df.loc['Quick Ratio'] = quickRatio
        df.loc['Current Ratio'] = currentRatio
        df.loc['Days Inventory'] =daysInventory

        #Solvency
        df.loc['Debt To Equity'] = debtToEquity
        df.loc['Debt To Asset'] = debtToAsset
        df.loc['EBIT to Interest']= EBITToInterest 
        df.loc['CFO to Interest']= CFOToInterest
        df.loc['CFO to Debt']= CFOToDebt
        df.loc['FCF to Debt']= FCFToDebt
        df.loc['Altman Z-Score'] = Altman

        df_ratios_list.append(df)
        

    df_ratios = pd.concat(df_ratios_list, axis=1)

    prices = ['Regular Market Price']
    growth = ['Revenue Growth Pct Current Q','Revenue Growth Pct Previous Q','Revenue Growth Pct Current Y']
    margin_TTM = ['Gross Margin TTM','Operating Margin TTM','Net Margin TTM']
    margin_q = ['Gross Margin LastQ','Operating Margin LastQ','Net Margin LastQ']
    pershare = ['Book Value Per Share','Total Cash Per Share','Net Cash/Share','Trailing EPS',]
    liquidity = ['Quick Ratio','Current Ratio','Days Inventory']
    priceratios = ['PE Ratio','Forward PE','PEG Ratio','Price to T.Book','Price to Sales']
    performance = ['Return On Assets','Return On Equity']
    evratios = ['EV/EBITDA','EV/EBIT','EV/Sales']
    solvency = ['Debt To Equity','Debt To Asset','EBIT to Interest','CFO to Interest','CFO to Debt','FCF to Debt','Altman Z-Score']

    df_ratios ['Class']=""
    df_ratios['Class'].loc[prices] = "Price"
    df_ratios['Class'].loc[growth] = "Growth"
    df_ratios['Class'].loc[margin_TTM] = "Profitability TTM"
    df_ratios['Class'].loc[margin_q] = "Profitability LastQ"
    df_ratios['Class'].loc[pershare] = "Per Share"
    df_ratios['Class'].loc[priceratios] = "Price Ratios"
    df_ratios['Class'].loc[liquidity] = "Liquidity"
    df_ratios['Class'].loc[solvency] = "Solvency"
    df_ratios['Class'].loc[performance] = "Performance"
    df_ratios['Class'].loc[evratios] = "EV Ratios"

    df_ratios = df_ratios.set_index(['Class',pd.Index(list(df_ratios.index.values))])
    df_ratios.index.names = ['Class','Indicator']

    return(df_ratios)
#-------------------------------------------------------


def stock_info(symbol):
        print('')
        string = "Stock Report"
        new_string = (symbol+" - "+string).center(70)
        print(new_string)
        print('')
        print(web(symbol))
        print('')
        summary(symbol)
        print('')
        print ('STOCK INFO:')
        trend(symbol)
        print(pctchange(symbol))
        print(pcs(symbol))
        print(sps(symbol))
        print('-'*60)
        print('-'*60)
        print('')
        print ('EV AND SHARES SHORT:')
        print(kss_new(symbol))
        print(kss_old(symbol))
    
    
def finances(symbol):
    print('-'*60)
    print('-'*60)
    print('')
    print ('DILUTION:')
    display(dilution(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('BALANCE SHEET:')
    print(bss(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('FINANCIAL STATEMENT:')
    print(fss(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('CASH FLOWS:')
    print(cfs(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('CASH BURN:')
    print(cash(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('SALARIES:')
    print(salaries(symbol))
    print('-'*60)
    print('-'*60)
    print('')
    print ('MAJOR HOLDERS:')
    try:
        print(mhs(symbol))  
    except Exception as e: 
        print(e)
        pass
    
           
#-------------------------------------------------------

def insiders_buy():
    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")
        df_insiders_bio = pd.read_sql_query("select * from [*Insiders_bio_buyers_sorted] ORDER BY [SEC Form 4] DESC;", conn)

    except sqlite3.Error as error:
        print("Failed to select from biotech", error)  
    finally:
        if (conn):
            conn.close() 
    display(df_insiders_bio.head(100))

#-------------------------------------------------------

def insiders_all():
    try:
        conn = sqlite3.connect("/Users/ralph/Biotech/BiotechDatabase.db")
        df_insiders_bio = pd.read_sql_query("select * from [*Insiders_bio_all_sorted] ORDER BY [SEC Form 4] DESC;", conn)

    except sqlite3.Error as error:
        print("Failed to select from biotech", error)  
    finally:
        if (conn):
            conn.close() 
    display(df_insiders_bio.head(100))


def IPO():
    import pandas as pd
    from yahooquery import Ticker

    #List from biopharmcatalyst
    ipo_df = pd.read_csv("IPOs.csv")

    # make sure date columns are actual dates
    ipo_df["OFFER DATE"] = pd.to_datetime(ipo_df["OFFER DATE"])
    ipo_df = ipo_df[ipo_df['IPO PRICE'].notna()]
    ipo_df = ipo_df.reset_index(drop=True)
    ipo_df['OFFER DATE'] = pd.to_datetime(ipo_df['OFFER DATE'])

    cleaned_ipo_list = ipo_df['TICKER'].to_list()

    ipo_df.head(30)

    ipo_analysis={}
    for symbol in cleaned_ipo_list:
        symbol = symbol.upper()
        ticker = Ticker(symbol, asynchronous=True)
        start = str(ipo_df['OFFER DATE'].loc[ipo_df['TICKER'] == symbol].values[0].astype('datetime64[D]'))
        ipo_price = float(ipo_df['IPO PRICE'].loc[ipo_df['TICKER'] == symbol].values[0][1:])
        company = ipo_df['COMPANY'].loc[ipo_df['TICKER'] == symbol].values[0]
        try:
            price_after_first_day = float(ipo_df['PRICE AFTER FIRST DAY'].loc[ipo_df['TICKER'] == symbol].values[0][1:])
        except Exception as e:
            pass

        try:
            prices_df = ticker.history(start = start) 
            prices_df = prices_df.reset_index('symbol', drop=True)
            # prices_df = prices_df.rename(columns={"adjclose": symbol})
            prices_df = prices_df["close"].to_frame()
            prices_df.index = pd.to_datetime(prices_df.index)
            prices_df.reset_index(inplace=True)
            prices_df['1Wk % Return'] = round((prices_df["close"].shift(-5) - ipo_price)*100/ipo_price,2)
            prices_df['1Mo % Return'] = round((prices_df["close"].shift(-21) - ipo_price)*100/ipo_price,2)
            prices_df['3Mo % Return'] = round((prices_df["close"].shift(-63) - ipo_price)*100/ipo_price,2)
            prices_df['6Mo % Return'] = round((prices_df["close"].shift(-126) - ipo_price)*100/ipo_price,2)
            prices_df['12Mo % Return'] = round((prices_df["close"].shift(-252) - ipo_price)*100/ipo_price,2)
            prices_df.head(5)

            current_price = round(prices_df["close"].tail(1).values[0],2)

            ipo_analysis[symbol] = {} 
            ipo_analysis[symbol]['Company'] = company
            ipo_analysis[symbol]['IPO Date'] = start 
            ipo_analysis[symbol]['IPO Price'] = ipo_price 
            ipo_analysis[symbol]['Price post day 1'] = price_after_first_day
            ipo_analysis[symbol]['Current Price'] = current_price
            ipo_analysis[symbol]['Current Return'] = round((current_price - ipo_price)*100/ipo_price,2)

            ipo_analysis[symbol]['1Wk % Return'] = round(prices_df['1Wk % Return'].head(1).values[0],2)
            ipo_analysis[symbol]['1Mo % Return'] = round(prices_df['1Mo % Return'].head(1).values[0],2)
            ipo_analysis[symbol]['3Mo % Return'] = round(prices_df['3Mo % Return'].head(1).values[0],2)
            ipo_analysis[symbol]['6Mo % Return'] = round(prices_df['6Mo % Return'].head(1).values[0],2)
            ipo_analysis[symbol]['12Mo % Return'] = round(prices_df['12Mo % Return'].head(1).values[0],2)
        except Exception as e:
            print(e)
            pass

    ipo_analysis_df = pd.DataFrame.from_dict(ipo_analysis,orient='columns')
    ipo_analysis_df = ipo_analysis_df.transpose()
    ipo_analysis_df['IPO Date'] = pd.to_datetime(ipo_analysis_df['IPO Date'])

    ipo_analysis_df['Current Return'] = ipo_analysis_df['Current Return'].astype(float)
    ipo_analysis_df['1Wk % Return'] = ipo_analysis_df['1Wk % Return'].astype(float)
    ipo_analysis_df['1Mo % Return'] = ipo_analysis_df['1Mo % Return'].astype(float)
    ipo_analysis_df['3Mo % Return'] = ipo_analysis_df['3Mo % Return'].astype(float)
    ipo_analysis_df['6Mo % Return'] = ipo_analysis_df['6Mo % Return'].astype(float)
    ipo_analysis_df['12Mo % Return'] = ipo_analysis_df['12Mo % Return'].astype(float)
    
    ax1 = ipo_analysis_df.groupby(ipo_analysis_df['IPO Date'].dt.year)[['1Wk % Return','1Mo % Return','3Mo % Return','6Mo % Return','12Mo % Return']].median().plot(kind = "bar", grid = True, title = "Median Biotech Stocks' Returns Post IPO Since 2019",figsize = (16,8), rot=0)
    ax2 = ipo_analysis_df.groupby(ipo_analysis_df['IPO Date'].dt.year)[['1Wk % Return','1Mo % Return','3Mo % Return','6Mo % Return','12Mo % Return']].mean().plot(kind = "bar", grid = True, title = "Mean Biotech Stocks' Returns Post IPO Since 2019",figsize = (16,8), rot=0)

    return ax1,ax2