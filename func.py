import requests
from uuid import uuid1
from key import tgbot_token, tgbot_chatID
import time

def send_tgmsg(bot_message = 'Hello', token=tgbot_token, chatID=tgbot_chatID):

    send_text = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)

    return response.json()

def return_unique_id():
    return ''.join([each for each in str(uuid1()).split('-')])


def isNaN(num):
    return num != num

def check_mindeltapct(number, lnumber):
    delta = 99
    for num in lnumber:
        numdelta = deltapct(num, number)
        if numdelta < delta:
            delta = numdelta
    return delta * 100

def deltapct(num, num0):
    return abs(num - num0) / num0
    
def calc_step(number):
    nround = count_dec(number)
    step = ((10 ** (-nround - 2)) / 2) * (int(str(number)[0]) + 1)

    return step

def gen_grid(number, limdn, limup):
    step = calc_step(number)
    nround = count_dec(step) + 1
    # Median value
    median = number - (number % step)

    # Lower grid
    grid = []
    vgrid = median - step
    for x in range(3):
        vgrid -= step
        if vgrid < (0.995*limdn):
            grid.append(numround(vgrid, nround))
    # Higher grid
    vgrid = median + step
    for x in range(3):
        vgrid += step
        if vgrid>(1.005*limup):
            grid.append(numround(vgrid, nround))

    return grid

def rounddown(num, pres):
    const = 10 ** pres
    hasil = int(num * const) / const

    return hasil

def roundup(num, pres):
    const = 10 ** pres
    hasil = (int(num * const) + 1) / const
    hasil = numround(hasil, pres)

    return hasil

def numround(num, rnd):
    nnum = round(num, rnd)
    nint = len(str(int(nnum)))
    nrnd = int(rnd) + nint + 2
    nout = float(str(nnum)[:nrnd])

    return nout

def count_dec(x):
    ns = str(format(x, ".9f"))
    if x > 1:
        n = 1
        for s in ns:
            if s == '.':
                break
            else:
                n -= 1
    elif x == 1:
        n = 0
    else:
        n = 1
        for s in ns:
            if s == '.':
                n = 1
            elif int(s) > 0:
                break
            else:
                n += 1

    dec = n
    return dec

def calc_size(cap, price):
    msize = cap / price
    dec = count_dec(msize)
    size = roundup(msize, dec)
    return size

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

def normalize(num, add=0):
    decnum = count_dec(num) + add
    nnum = rounddown(num, decnum)

    return nnum