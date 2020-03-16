import telebot
import matplotlib.pyplot as plt
import random

weini = telebot.TeleBot('928189418:AAH6SZbYLU5p7J12VhhfimKGvQZO080n0ek')

triggered = ['robert', 'weini', 'weinhandl']
ideen = []
chid = '-1001256312641'
gg = ['I (x²+y²-1)³-x²y³=0 GeoGebra', 'gg = geogebra ≠ gossip girl ≠ good game']	

def plot_fct(term):
    #term in form "k*x+t" wobei k eine zahl und t einzahl
    k = int(term[0])
    t = int(term[-1])
    yvals = []
    for x in range(11):
        f = k*x+t
        yvals.append(f)
    print(yvals)
    plt.plot(yvals, "--c",
             yvals, "xb"
             ) 
    xmin, xmax, ymin, ymax = -1, 11, int(yvals[0])- 1, int(yvals[-1]) + 1
    plt.axis([xmin, xmax, ymin, ymax])
    plt.xlabel('x')
    plt.ylabel('f (x)')
    plt.savefig('plot.png')
    with open('plot.png', 'rb') as image:
         weini.send_photo(chid, image)
         weini.send_message(chid, random.choice(gg))


