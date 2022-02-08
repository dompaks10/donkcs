#Local Library
from distutils.log import error
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
from datetime import datetime
from tqdm import tqdm

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
    def __init__(self, key, secret, passphrase, quote, cap, topn):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.quote = quote
        self.cap = cap
        self.topn = topn
        self.histo = pd.DataFrame(columns=[['tlast','hh','vv','ll','qlast','vlast','qq','vv','a']])
        self.connect()
        self.pop_symbols()
        self.pop_history()
        self.get_balance()
        #self.get_topn()
        self.gen_lpair()

    def connect(self):
        ###Initializing all connection
        self.market = Market()
        self.trade = Trade(key=self.key, secret=self.secret, passphrase=self.passphrase, is_sandbox=False, url='')
        self.user = User(self.key, self.secret, self.passphrase)
        logging.info(str(datetime.now())+' : Connected successfully')

    def pop_symbols(self):
        stat = False
        while stat == False:
            try:
                self.symbols = pd.DataFrame(self.market.get_symbol_list())
                stat = True
            except Exception as e:
                err = repr(e)                    
                if '429000' in err:
                    time.sleep(10)
                else:
                    print(f'Error {repr(e)} in populating symbols')
                    logging.error(repr(e))
                    stat = True
        
        if len(self.symbols)>0: 
            self.symbols.set_index('symbol', inplace=True)
            lsymbols = self.symbols.index.to_list()
            self.lsymbols = []
            for symbol in lsymbols:
                squote = symbol[-4:]
                #sbase = symbol[:-5]
                if squote == self.quote:
                    self.lsymbols.append(symbol)
        
        #symbols keys = ['name', 'baseCurrency', 'quoteCurrency', 'feeCurrency', 'market',
        #'baseMinSize', 'quoteMinSize', 'baseMaxSize', 'quoteMaxSize',
        #'baseIncrement', 'quoteIncrement', 'priceIncrement', 'priceLimitRate',
        #'isMarginEnabled', 'enableTrading']

    def pop_history(self):
        #print('Fetching history...')
        #check current history
        pdkline = pd.DataFrame()
        histo = pd.read_csv('histo.csv',index_col=0)
        tlast = int(histo.iloc[0]['tlast'])
        tdiff = int(time.time()) - tlast
        if tdiff > 3600:
            for symbol in tqdm(self.lsymbols):
                stat = False
                while stat == False:
                    try:
                        pdkline = self.get_kline(symbol)
                        stat = True
                    except Exception as e:
                        err = repr(e)                    
                        if '429000' in err:
                            time.sleep(10)
                        else:
                            print(f'Error {repr(e)} in initializing kline history')
                            logging.error(repr(e))
                            stat = True                    
                
                if len(pdkline)>0:    
                    pdkline['h'] = pd.to_numeric(pdkline['h'])
                    pdkline['l'] = pd.to_numeric(pdkline['l'])
                    pdkline['q'] = pd.to_numeric(pdkline['q'])
                    pdkline['v'] = pd.to_numeric(pdkline['v'])
                    tlast = pdkline.iloc[0]['t']
                    hh = pdkline['h'].max()
                    ll = pdkline['l'].min()
                    qlast = pdkline.iloc[:24]['q'].sum()
                    vlast = pdkline.iloc[:24]['v'].sum()
                    qq = pdkline['q'].sum()
                    vv = pdkline['v'].sum()
                    a = qq/vv
                    self.histo.loc[symbol] = [tlast,hh,vv,ll,qlast,vlast,qq,vv,a]
            self.histo.to_csv('histo.csv')
        else:
            self.histo = histo
        #Generate topn
        self.get_topn(self.topn)

    def get_kline(self,symbol,timeframe='1hour'):
        pdkline = pd.DataFrame(self.market.get_kline(symbol=symbol,kline_type=timeframe),columns=['t','o','h','c','l','v','q'])
        return pdkline

    def pop_tickers(self):
        stat = False
        while stat == False:
            try:
                self.tickers = pd.DataFrame(self.market.get_all_tickers()['ticker'])
                stat = True
            except Exception as e:
                err = repr(e)                    
                if '429000' in err:
                    time.sleep(10)
                else:
                    print(f'Error {repr(e)} in populating tickers')
                    logging.error(repr(e))
                    stat = True
        
        if len(self.tickers)>0: 
            self.tickers.set_index('symbol',inplace=True)
            self.dprice = {}
            for idx, row in self.tickers.iterrows():
                rquote = idx[-4:]
                if rquote == self.quote:
                    self.dprice[idx] = float(row['last'])

        #Tickers  = {'symbol': 'TRIBE-USDT', 'symbolName': 'TRIBE-USDT', 'buy': '0.691', 'sell': '0.6917',
        #  'changeRate': '0.0015', 'changePrice': '0.0011', 'high': '0.7112', 'low': '0.6839', 'vol': '62561.43628495', 
        # 'volValue': '43760.877145039915', 'last': '0.6911', 'averagePrice': '0.69897778', 'takerFeeRate': '0.001', 
        # 'makerFeeRate': '0.001', 'takerCoefficient': '1', 'makerCoefficient': '1'}

    def get_balance(self):
        self.pop_tickers()
        self.lpaporto = []

        stat = False
        while stat == False:
            try:
                self.balance = pd.DataFrame(self.user.get_account_list())
                stat = True
            except Exception as e:
                err = repr(e)                    
                if '429000' in err:
                    time.sleep(10)
                else:
                    print(f'Error {repr(e)} in get balance')
                    logging.error(repr(e))
                    stat = True
        
        if len(self.balance)>0: 
            #self.balance = pd.DataFrame(self.user.get_account_list())     
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
                        if (self.dprice[pair] * row['available']) > self.cap:                            self.lpaporto.append(pair)
                self.lporto.append(idx)
                self.lpporto.append(pair)                
            self.balance['value'] = self.balance['balance']*self.balance['price']
        #strmsg = 'Total Kcsmain = free '+ str(round(self.valquote,2)) + ' USDT of ' + str(round(self.valtotal_usd,2))
        #print(strmsg)
        #send_tgmsg(bot_message=strmsg)
    
    def get_abuys(self, symbol):
        abuy = 0
        lbprice = 0
        try:
            trades = self.trade.get_fill_list(tradeType='TRADE',symbol=symbol, side='buy')
            for t in trades['items']:
                abuy += float(t['price'])/len(trades['items'])
                if lbprice == 0:
                    lbprice = float(t['price'])
        except Exception as e:
            print(f'Error {repr(e)} in get avg buys')
        #{'symbol': 'BTC-USDT', 'tradeId': '61f3a74c2e113d29233fd2fa', 'orderId': '61f399060bb106000113d23d', 
        #'counterOrderId': '61f3a74c19673d000144a651', 'side': 'buy', 'liquidity': 'maker', 'forceTaker': False, 
        #'price': '36600', 'size': '0.00003', 'funds': '1.098', 'fee': '0.001098', 'feeRate': '0.001', 
        #'feeCurrency': 'USDT', 'stop': '', 'tradeType': 'TRADE', 'type': 'limit', 'createdAt': 1643358028000}
        return abuy, lbprice
    
    def get_openorders(self, symbol):
        stat = False
        while stat == False:
            try:
                orders = self.trade.get_order_list(status='active', symbol=symbol)['items']
                stat = True
            except Exception as e:
                err = repr(e)                    
                if '429000' in err:
                    time.sleep(10)
                else:
                    print(f'Error {repr(e)} in get open orders')
                    logging.error(repr(e))
                    stat = True
        dorders = {}
        lorders = []
        for order in orders:
            if order['isActive'] == True:
                dorders[order['id']] = float(order['price'])
                lorders.append(float(order['price']))

        return dorders, lorders

    def create_order(self, symbol, side, size, price):
        oid = return_unique_id()
        stat = False
        while stat == False:
            try:
                result = self.trade.create_limit_order(symbol, side, size, price, oid)
                stat = True
                return result
            except Exception as e:
                err = repr(e)                    
                if '429000' in err:
                    time.sleep(10)
                else:
                    print(f'Error {repr(e)} in create orders')
                    logging.error(repr(e))
                    stat = True
                    return err

    def cancel_order(self, orderID):
        stat = False
        while stat == False:
            try:
                result = self.trade.cancel_order(orderID)
                stat = True
                return result
            except Exception as e:
                err = repr(e)                    
                if '429000' in err:
                    time.sleep(10)
                else:
                    print(f'Error {repr(e)} in cancel open orders')
                    logging.error(repr(e))
                    stat = True
                    return repr(e)

    def get_topn(self, top = 10):
        self.histo = pd.read_csv('histo.csv',index_col=0)
        self.histo.sort_values(by=['qlast'],ascending=False, inplace=True)
        self.ltopn = self.histo[:top].index.to_list()
    
    def setup_grid(self, symbol):
        price = float(self.tickers.loc[symbol]['last'])
        base = symbol[:-5]
        if base in self.lporto:
            value = float(self.balance.loc[base]['value'])
        else:
            value = 0
        limup,lbprice = self.get_abuys(symbol)
        limdn = float(self.histo.loc[symbol]['a'])
        grid = gen_grid(price,limdn, limup, lbprice)
        print(symbol, normalize(value,2), normalize(price,2), normalize(limdn,2), normalize(limup,2), lbprice, grid)
        return grid

    def check_obsorder(self, symbol):
        price = float(self.tickers.loc[symbol]['last'])
        dorders,lorders = self.get_openorders(symbol)
        if len(dorders)>0:
            for order in dorders:
                oprice = dorders[order]
                if (oprice > 1.05 * price) or (oprice < 0.95 * price) or ((oprice<price) and (symbol not in self.ltopn)):
                    stat = self.cancel_order(order)
                    logger.info(stat)

    def exe_grid(self,symbol, lgrid):
        price = float(self.tickers.loc[symbol]['last'])
        base = symbol[:-5]
        quote = symbol[-4:]
        if base in self.lporto:
            bbase = self.balance.loc[base]['available']
            vbase = self.balance.loc[base]['value']
        else:
            bbase = 0
            vbase = 0
        if quote in self.balance.index:
            bquote = self.balance.loc[quote]['available']
        else:
            bquote = 0
        if len(lgrid)>0:
            dorders,lporders = self.get_openorders(symbol)
            print('Open Orders Prices : ',normalize(price,2),lporders)
            #print('Grid Prices :',lgrid)
            for grid in lgrid:
                minpct = check_mindeltapct(grid,lporders)                
                bgrid = grid 
                if (minpct>0.5) & (bgrid not in lporders):    
                    size = calc_size(self.cap,price)
                    if base in self.lporto:
                        sbase = self.balance.loc[base]['available']
                    else:
                        sbase = 0
                    cbase = sbase/size           
                    if cbase < 2 and grid > price:
                        size = sbase
                    bmin_size = float(self.symbols.loc[symbol]['baseMinSize'])
                    bsize = max(size,bmin_size)
                    bcap = bsize * bgrid
                    bgrid = normalize(bgrid,3)                 
                    bsize = normalize(bsize,2)
                    if grid > price:                   
                        if bbase >= bsize:
                            side = 'sell'
                            strmsg = ' | Send ' + side +' '+ symbol +' : '+ str(bsize) + '@' + str(bgrid)
                            logger.info(str(datetime.now())+strmsg)
                            hasil = self.create_order(symbol,side,bsize,bgrid)
                            if 'Exception' not in hasil:
                                bbase-=bsize
                                bquote+=bcap
                                strmsg = ' | ' + side +' '+ symbol +' : '+ str(bsize) + '@' + str(bgrid)
                                logger.info(str(datetime.now())+strmsg)
                    else:
                        if (bquote >= bcap) and (symbol in self.ltopn) and (vbase < (self.valtotal_usd/10)):
                            side = 'buy'
                            strmsg = ' | Send : ' + side +' '+ symbol +' : '+ str(bsize) + '@' + str(bgrid)
                            logger.info(str(datetime.now())+strmsg)
                            hasil = self.create_order(symbol,side,bsize,bgrid)
                            if 'Exception' not in hasil:
                                bquote-=bcap    
                                strmsg = ' | ' + side +' '+ symbol +' : '+ str(bsize) + '@' + str(bgrid)
                                logger.info(str(datetime.now())+strmsg)             
                
    def gen_lpair(self):
        self.lpair = []
        for pair in self.lpaporto:
            self.lpair.append(pair) 
        for pair in self.ltopn:
            if pair not in self.lpair:
                self.lpair.append(pair)


def main(akun):
    akun.topn = min(maxtopn,akun.topn+1) if akun.valquote > 111 else max(mintopn,akun.topn-1)
    akun.get_topn(top = akun.topn)
    akun.gen_lpair()
    print('Top :',akun.ltopn, len(akun.ltopn))
    for pair in akun.lpair:
        if datetime.now().minute<10:
            akun.pop_history()
        akun.get_balance()
        lgrid = akun.setup_grid(pair)
        akun.check_obsorder(pair)
        akun.exe_grid(pair,lgrid)
    val_usd = str(normalize(akun.valquote,3))
    valtotal = str(normalize(akun.valtotal_usd,5))
    strmsg = 'Total Kcsmain = free '+ val_usd + ' USDT of ' + valtotal
    print(strmsg)
    send_tgmsg(bot_message=strmsg)

if __name__ == "__main__":
    akun = Akun(key=kcs_key, secret=kcs_secret, passphrase=kcs_passphrase, quote=quote, cap=cap, topn=topn)
    while True:
        try:
            print('=' * 50)
            main(akun)
            print('=' * 50)
            countdown(mnt * 60)
        except Exception as error:
            print('Error: ' + repr(error))
