num = 32010.54
num = 3150.25
#num = 0.0234
#num = 0.000345
#num = 0.0000254
num = 2.623

def round_base(num,base):
    return (base*round(num/base))-base


def count_step(num):
    snum = str("{:.9f}".format(num))
    if num>=10:
        ndot = snum.find('.')
        snumn = snum[:ndot]
        nten = ndot-1
    elif num>=1:
        snumn = snum[0]
        nten = 0
    else:
        ndot = snum.find('.')
        snumn = snum[ndot+1:]
        ndec=-1
        for s in snumn:
            ndec-=1
            if int(s)>0:                
                break
        nten = ndec-1

    nn = int(snumn[0])    
    tens = (10**nten)
    step = nn*tens/200
    
    return step

step = count_step(num)
print(step)
print(num,round_base(num, step))
print(100*step/num)