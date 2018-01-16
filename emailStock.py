#Lets start importing the Libraries and the Data
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#%matplotlib inline

# Candlestick plot
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls

# Finances libraries
from pandas_datareader import data as web
import fix_yahoo_finance as yf
from datetime import datetime

# Send email libraries
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid

# Operational System -> to delete the images after I send the email
import os

# Get arguments from commandline
import argparse


# Create the parser for command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s','--stocks', nargs='+', help='Put one or more stocks, The real name e.g: PETR4 TIMP3 GGRD4', required=True)
parser.add_argument('-e','--email', help='Your email', required=True) # TO DO add a sender latter
parser.add_argument('-u','--user', help='Your email', required=True) # TO DO add a sender latter
parser.add_argument('-a','--secret', help='Your email', required=True) # TO DO add a sender latter
parser.add_argument('-p','--password', help='Your passord for email', required=True)
# TO DO -> parser.add_argument('-i','--indicators', nargs='*', help='List of indicators available: MA5, MA7, MA9, MA20,EWMA,BB(Bollinger Bands),RSI', required=False)
args = parser.parse_args()
# I can get the list of stocks with args.stocks or args['stocks']

# I need this to get the financial Data from yahoo finance
yf.pdr_override()

# Sign in plotly (to create a candlestick)
py.sign_in(args.user, args.secret) # I have to creat a parser for this as well (TO DO)

# Start and end Date to get the historical data
start = datetime(2017,1,1)
end = datetime.today()

# Initializing a empty list to add DataFrames (one for each stock)
df_list = []
for symbol in args.stocks:
    df = web.get_data_yahoo(symbol,start=start, end=end)
    df_list.append(df)
dfs = dict(zip(args.stocks,df_list))

# Indicators
def bollinger_Bands(stock_price, window_size=20, num_of_std=2):
    
    rolling_mean = stock_price.rolling(window=window_size).mean()
    rolling_std  = stock_price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std*num_of_std)
    lower_band = rolling_mean - (rolling_std*num_of_std)

    return rolling_mean, upper_band, lower_band

#RSI (Relative Strenght Index)
def rsi(stock_price, n_days=2):
    delta = stock_price.diff() 
    # Get rid of the first row, which is NaN since it did not have a previous 
    # row to calculate the differences
    delta = delta[1:] 
    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    # Calculate the EWMA (Exponentially weighted moving average)
    roll_up1 = pd.stats.moments.ewma(up, n_days)
    roll_down1 = pd.stats.moments.ewma(down.abs(), n_days)

    # Calculate the RSI based on EWMA
    RS1 = roll_up1 / roll_down1
    RSI1 = 100.0 - (100.0 / (1.0 + RS1))
    
    return RSI1

# MA 9
def moving_averages(stock_price, window_size=9):
    ma9 = stock_price.rolling(window=window_size).mean()
    return ma9

# EWMA 20 
def ewma(stock_price, window_size=20):
    ewma = pd.stats.moments.ewma(stock_price, window_size)
    return ewma

# Appending the indicators
for df in df_list:
    df['MA 20'], df['Upper'], df['Lower'] = bollinger_Bands(df['Adj Close'], num_of_std = 2)
    df['RSI'] = rsi(df['Adj Close'])
    df['pctChange'] = df['Adj Close'].pct_change(1)*100


# Making the chart with plot.ly
for symbol,df in dfs.items():
    filename = symbol.split('.')[0].lower()
    trace = go.Candlestick(x=df.tail(60).index,
                           open=df.tail(60).Open,
                           high=df.tail(60).High,
                           low=df.tail(60).Low,
                           close=df.tail(60).Close)
    trace1 = go.Scatter(x=df.tail(60).index,
                        y=df.tail(60).Upper,
                        name='Bollinger Bands Upper')

    trace2 = go.Scatter(x=df.tail(60).index,
                        y=df.tail(60).Lower,
                        name='Bollinger Bands Lower')

    trace3 = go.Scatter(x=df.tail(60).index,
                        y=df.tail(60)['MA 20'],
                        name='MA 20')
    data = [trace,trace1,trace2,trace3]
    layout = {
        'title': symbol + ' Last 60 Days'    
    }
    fig = dict(data=data, layout=layout)
    #py.iplot(fig, filename=filename) (if i want to plot on jupyter)
    py.image.save_as(fig, filename=filename+'.png')


# Sending the Email
email_user = args.email
email_send = args.email
subject = 'Stocks'

msg = EmailMessage()
msg['Subject'] = 'Stocks For the day'
msg['From'] =email_user
msg['To'] = email_send
i=0
filenames = []
body = """"""
msgids = []
for symbol,df in dfs.items():
    stock = make_msgid()
    msgids.append(stock)
    filename = symbol.split('.')[0].lower()
    # Now add the related image to the html part.
    file = filename+'.png'
    filenames.append(file)

    body+="""\
        <p>The stock <b>%s</b> closed with price %s</p>
         <p>RSI(2) = %s</p>
         <p>Percent change = %s </p>
         <img src="cid:{}" />
        <p>See more on -> https://finance.yahoo.com/quote/%s</p>
         """.format(stock[1:-1]) %(symbol,df[-1:]['Adj Close'].values,
                               df[-1:].RSI.values, df[-1:].pctChange.values, symbol)
msg.add_alternative(body, subtype='html')    

for i,ids in enumerate(msgids):
    file = filenames[i]
    with open(file, 'rb') as img:
        msg.get_payload()[0].add_related(img.read(), 'image', 'png',cid=ids)  
        

# Send the message via local SMTP server.
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(args.email, args.password)
server.send_message(msg)
server.quit()

# Deleting the images generated from plotly
filenames = [x.split('.')[0].lower() for x in args.stocks]
current_dir = os.getcwd()
for filename in filenames:
    os.remove(current_dir+'/'+filename+'.png')