#Local Library
from key import *
from func import *
from var import *

#Kucoin-python Lib
from kucoin.client import Market
from kucoin.client import Trade
from kucoin.client import User

#Import standard lib
import pandas as pd
import time

#Logging
import logging, sys
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler('donkcs.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

# Initialize Class Akun
class Akun(object):
    def __init__(self, key, secret, passphrase, quote, cap):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.quote = quote
        self.cap = cap
        self.connect()
        self.pop_symbols()
        self.pop_tickers()
        self.get_balance()

    def connect(self):
        ###Initializing all connection
        self.market = Market()
        self.trade = Trade(key=self.key, secret=self.secret, passphrase=self.passphrase, is_sandbox=False, url='')
        self.user = User(self.key, self.secret, self.passphrase)

    def pop_symbols(self):
        try: 
            self.symbols = pd.DataFrame(self.market.get_symbol_list())
            self.symbols.set_index('symbol', inplace=True)
            lsymbols = self.symbols.index.to_list()
            self.lsymbols = []
            for symbol in lsymbols:
                squote = symbol[-4:]
                #sbase = symbol[:-5]
                if squote == self.quote:
                    self.lsymbols.append(symbol)
        except Exception as e:
            print(f'Error {repr(e)} in populate symbol')
        
        #symbols keys = ['name', 'baseCurrency', 'quoteCurrency', 'feeCurrency', 'market',
        #'baseMinSize', 'quoteMinSize', 'baseMaxSize', 'quoteMaxSize',
        #'baseIncrement', 'quoteIncrement', 'priceIncrement', 'priceLimitRate',
        #'isMarginEnabled', 'enableTrading']
    
    def pop_tickers(self):
        try:
            self.tickers = pd.DataFrame(self.market.get_all_tickers()['ticker'])
            time.sleep(1)
            self.tickers.set_index('symbol',inplace=True)
            self.dprice = {}
            for idx, row in self.tickers.iterrows():
                rquote = idx[-4:]
                if rquote == self.quote:
                    self.dprice[idx] = float(row['last'])
        except Exception as e:
            print(f'Error {repr(e)} in get tickers')

        #Tickers  = {'symbol': 'TRIBE-USDT', 'symbolName': 'TRIBE-USDT', 'buy': '0.691', 'sell': '0.6917',
        #  'changeRate': '0.0015', 'changePrice': '0.0011', 'high': '0.7112', 'low': '0.6839', 'vol': '62561.43628495', 
        # 'volValue': '43760.877145039915', 'last': '0.6911', 'averagePrice': '0.69897778', 'takerFeeRate': '0.001', 
        # 'makerFeeRate': '0.001', 'takerCoefficient': '1', 'makerCoefficient': '1'}

    def get_balance(self):
        try:
            self.balance = pd.DataFrame(self.user.get_account_list())     
            time.sleep(1)   
            self.balance.set_index('currency', inplace=True)
            self.balance.drop(delist,inplace=True)
            self.balance['balance'] = pd.to_numeric(self.balance['balance'])
            self.balance['available'] = pd.to_numeric(self.balance['available'])
            self.balance['holds'] = pd.to_numeric(self.balance['holds'])
            self.valfree_usd = 0
            self.valtotal_usd = 0
            self.balance = self.balance[(self.balance['balance'] > 0) & (self.balance['type']=='trade')]
            self.balance = self.balance[['balance', 'available', 'holds']]
            self.lporto = []
            self.lpporto = []
            self.balance['price'] = [self.dprice[x+'-'+self.quote] if ((x != self.quote) & (str(x+'-'+self.quote) in self.dprice)) else 1 for x in self.balance.index]
            for idx, row in self.balance.iterrows():
                pair = idx+'-'+self.quote
                if idx == self.quote:
                    self.valtotal_usd += row['balance']
                    self.valfree_usd += row['available']
                    self.valquote = row['available']
                else:
                    pair = idx + '-' + self.quote
                    if pair in self.dprice:
                        self.valtotal_usd += (self.dprice[pair] * row['balance'])
                        self.valfree_usd += (self.dprice[pair] * row['available'])
                self.lporto.append(idx)
                self.lpporto.append(pair)
            self.balance['value'] = self.balance['balance']*self.balance['price']
            #self.balance['avgbuy'] = [self.get_abuys(x+'-'+self.quote) if x != self.quote else 0 for x in self.balance.index]
        except Exception as e:
            print(f'Error {repr(e)} in get balance')
    
    def get_abuys(self, symbol):
        abuy = 0
        try:
            trades = self.trade.get_fill_list(tradeType='TRADE',symbol=symbol, side='buy')
            time.sleep(1)
            for t in trades['items']:
                abuy += float(t['price'])/len(trades['items'])
        except Exception as e:
            print(f'Error {repr(e)} in get avg buys')
        #{'symbol': 'BTC-USDT', 'tradeId': '61f3a74c2e113d29233fd2fa', 'orderId': '61f399060bb106000113d23d', 
        #'counterOrderId': '61f3a74c19673d000144a651', 'side': 'buy', 'liquidity': 'maker', 'forceTaker': False, 
        #'price': '36600', 'size': '0.00003', 'funds': '1.098', 'fee': '0.001098', 'feeRate': '0.001', 
        #'feeCurrency': 'USDT', 'stop': '', 'tradeType': 'TRADE', 'type': 'limit', 'createdAt': 1643358028000}
        return abuy

if __name__ == "__main__":
    akun = Akun(key=kcs_key, secret=kcs_secret, passphrase=kcs_passphrase, quote=quote, cap=cap)
    #print(akun.balance)
    #print(akun.valtotal_usd)
    #print(akun.lporto)
    pdkline = pd.DataFrame(akun.market.get_kline(symbol='BTC-USDT',kline_type='1day'),columns=['t','o','h','c','l','v','q'])
    pdkline = pdkline[:500]
    pdkline['q'] = pd.to_numeric(pdkline['q'])
    pdkline['v'] = pd.to_numeric(pdkline['v'])
    meanprice = pdkline['q'].sum()/pdkline['v'].sum()
    print(meanprice)
    #print(akun.market.get_all_tickers())
    #print(akun.get_abuys('BTC-USDT'))
    #for p in akun.lpporto:
    #    print(p,akun.get_abuys(p))


#Trial Telegram message
#message = "Hello test"
#stat = send_tgmsg(tgbot_token, tgbot_chatID, message)
#print(stat)