def count_step(num):
    if num>100000:
        step = 500
    elif num>10000:
        step = 50
    elif num>1000:
        step = 5
    elif num>100:
        step = 0.5
    elif num>10:
        step = 0.05
    elif num>1:
        step = 5/1000
    elif num>