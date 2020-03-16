import telebot
import matplotlib.pyplot as plt
import random
import re
from math import sin, cos

weini = telebot.TeleBot('928189418:AAH6SZbYLU5p7J12VhhfimKGvQZO080n0ek')

triggered = ['robert', 'weini', 'weinhandl']
ideen = []
chid = '-1001256312641'
	



def extract_fct(string):
    p = re.compile(r'f\(x\)=[x\d.\+\*\-/\^()coisn]+', re.I)
    m = p.search(string)
    if m:
        fct = m.group()
        print(fct)
        a = 'cosin'
        wfct = ['sin(x)', 'cos(x)']
        if any(i in fct for i in a):
            print('cosin enthalten')
            if any(i in fct for i in wfct):
                print('cos oder sin')
                fct = fct.replace('f(x)=', '')
                fct = fct.replace(' ','')
                print(fct)
                return fct
            else:
                print('error: kein sin oder cos')
                return none
        else:
            print('normale f(x)')
            fct = fct.replace('f(x)=', '')
            fct = fct.replace(' ','')
            return fct
    else:
        print('Nix')
        return None

def plot_fct(term):
    yvals = []
    for x in range(11):
        try:
            f = eval(term)
            yvals.append(f)
        except Exception as e:
            print('evaluation failed', e)
            weini.send_message(chid, 'Wer unterrichtet euch in Mathematik, wenn ihr nicht einmal ein Funktion aufstellen könnt?')
            return
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


