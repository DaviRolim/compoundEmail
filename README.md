# compoundEmail
A python script for send email with some basics stock info for the day

I'm creating this to summarize some basics info of some portfolio and send me a email at the end of the day.

## TO DO's
  - Free the user to choose the indicators from the command line (now it's fixed with bollinger bands, RSI, MA20)
  - Implement more indicators

I'm going to use crontab (for windows would be scheduler) for schedule the email to be sent every weekday at the end of the stock day. (6pm here in Brazil)

## Requirements (libs)
  - numpy
  - pandas
  - plotly ( you actually have to creat an account so you can save images generetad from plotly )
  - pandas_datareader
  - fix_yahoo_finances
  - smtplib
  - email
  - os
  - argparse
  
## Usability
  To use the script you simple need to pass the Stock's symbols, email, password, plotly username and secretkey
  python emailStock.py -s TIMP3.SA FLRY3.SA SMLS3.SA MGLU3.SA -e email@gmail.com -p password -u userplotly -a secretkey
