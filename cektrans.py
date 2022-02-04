import asyncio
from kucoin.client import WsToken
from kucoin.ws_client import KucoinWsClient
from func import send_tgmsg
from key import *
from var import *
from datetime import datetime

# Initialize Class Akun
class Akun(object):
    def __init__(self, key, secret, passphrase, quote, cap):
        self.key = key
        self.secret = secret
        self.passphrase = passphrase
        self.quote = quote
        self.cap = cap
        self.connect()

    def connect(self):
        ###Initializing all connection
        self.wsprv = WsToken(key=self.key, secret=self.secret, passphrase=self.passphrase, is_sandbox=False, url='')

async def main(akun):
    async def deal_msg(msg):
        topic = msg['topic']
        data = msg['data']    
        if topic == '/spotMarket/tradeOrders':
            symbol = data['symbol']
            side = data['side']
            size = data['size']
            type = data['type']
            price = float(data['price'])
            print(type, side, symbol, size, '@', price)
            if type == 'filled':
                strmsg = 'kcsmain: ' + side +' '+ symbol +' : '+ str(size) + '@' + str(price)
                send_tgmsg(bot_message=strmsg)
        else:
            pass

    ##Declare await
    wscprv = await KucoinWsClient.create(None, akun.wsprv, deal_msg, private=True)
    await wscprv.subscribe('/spotMarket/tradeOrders')

    while True:
        print('----Heartbeat------------',datetime.now())
        await asyncio.sleep(60)


if __name__ == "__main__":
    akun = Akun(key=kcs_key, secret=kcs_secret, passphrase=kcs_passphrase, quote=quote, cap=cap)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(akun))
    loop.run_forever()