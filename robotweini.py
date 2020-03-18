import telebot
import matplotlib.pyplot as plt
import random
import re
from numpy import sin,cos,linspace
import json

weini = telebot.TeleBot('928189418:AAH6SZbYLU5p7J12VhhfimKGvQZO080n0ek')

triggered = ['robert', 'weini', 'weinhandl']
ideen = []
chid = '-1001256312641'
late = 'late.json'


triggers = {1:['geogebra','geo gebra'], 2:['starwars', 'star wars', 'jedi', 'r2d2', 'c3po', 'laserschwert', 'ich bin dein vater', 'yoda', 'baby yoda'], 3:['weini', 'robert'], 4:['shit', 'scheisse','scheiße', 'ruhe', 'spamt', 'fuck', 'scheiß', 'leise', 'hört'], 5:['pichler', 'mayerhofer', 'prammer', 'staudner', 'huber', 'kandl', 'mollnar'], 6:['grömer', 'niedertscheider', 'oberthaler', 'fennes', 'höfferer', 'villarme', 'schwarz', 'gillinger', 'speiss', 'zinkl', 'bucher', 'schreiber'], 8:['aller',]}
answer = {1:['i (x²+y²-1)3-x²y³=0 GeoGebra', 'GG = GeoGebra ≠ Gossip Girl ≠ Good Game', 'geozebra'], 2:['dön dön dön dün dü dün, dün dü düu, dü dü dü di do do', 'Deine Mathehausübungen machen du musst!', 'Sei Mahara mit dir!', 'Luke, ich bin dein Klassenvorstand'], 3:['Gibt\'s Probleme? Willst du welche?', 'ICH WERD DICH AN DIE WAND FAHREN', 'Cave Canem'], 7:['Schon in WebUntis vermerkt.','Die drei-viertel-acht Regelung folgt auf dem Fuße!'], 8:['Du solltest nirgendwo hin, außer in den Deutschunterricht', 'Bruda wer kommt aller Digga!','AlleR guten Dinge sind drei. Deine Rechtschreibung zählt nicht dazu.','Das klingt so als würde ein Serbe versuchen Deutsch zu sprechen!']}

##utilities
def wr_json(dictio, targetfile):
    with open(targetfile, 'w') as f:
        json.dump(dictio, f, indent=5)
    return

def re_json(targetfile):
    with open(targetfile, 'r') as f:
        di = json.load(f)
    return di

##main functions
def weinhandler(message):
    text = message.text
    text = text.lower()
    print('Scanning for Keywords...')
    found = []
    lu = {}
    ##searching for keywords
    for x in triggers:
        trig = triggers[x]
        if any(i in text for i in trig):
            found.append(x)
    if found:
        ## adding to late pupils and checking
##        if 7 in found:
##            lu = re_json(late)
##            user = message.from_user.first_name
##            if user in lu:
##                lu[user] += 1
##            else:
##                lu[user] = 1
##            wr_json(lu, late)
        print('Found Keywords!')
        ## chosing random answer
        key = random.choice(found)
        if key == 4:
            weini.send_sticker(chid, 'CAACAgQAAxkBAANyXnE1eMKQkpiSeMOVo2nmKCk8AXgAAhUAA8l8pyFcPa6h4vaXuxgE') 
        elif key == 5:
            tetext = text
            for teacher in triggers[5]:
                a = 'prof ' + teacher
                b = 'professor ' + teacher
                c = 'professor' + teacher
                d = 'prof' + teacher
                if a in tetext or b in tetext or c in tetext or d in tetext:
                    tetext = tetext.replace(a, '')
                    tetext = tetext.replace(b, '')
                    tetext = tetext.replace(c, '')
                    tetext = tetext.replace(d, '')                    
            ftm = [i for i in triggers[5] if i in tetext]
            if ftm:
                tm = random.choice(ftm)
                msg = 'Es heißt HERR PROFESSOR ' + tm.capitalize()
                weini.send_message(chid, msg)
        elif key == 6:
            tetext = text
            for teacher in triggers[6]:
                a = 'prof ' + teacher
                b = 'professor ' + teacher
                c = 'professor' + teacher
                d = 'prof' + teacher
                if a in tetext or b in tetext or c in tetext or d in tetext:
                    tetext = tetext.replace(a, '')
                    tetext = tetext.replace(b, '')
                    tetext = tetext.replace(c, '')
                    tetext = tetext.replace(d, '')
            ftw = [i for i in triggers[6] if i in tetext]
            if ftw:
                tw = random.choice(ftw)
                msg = 'Es heißt FRAU PROFESSOR ' + tw.capitalize()
                weini.send_message(chid, msg)
        elif key == 8:
            if 'wer' in text and 'kommt' in text:
                ch = answer[key]
                msg = random.choice(ch)
                weini.reply_to(message, msg) 
        else:
            ch = answer[key]
            msg = random.choice(ch)
            weini.reply_to(message, msg)
            if msg == "geozebra": weini.send_sticker(chid,'CAACAgEAAxkBAANzXnHuKw46bz26QFKBETYLuLcGgZUAAicAAzgOghF9an6UHkupzRgE')
            print('Sent Answer:',msg)
        return
    else:
        return

rwfct = ''

def fctval(string):
    print('Extracting function value request...')
    global rwfct
    p = re.compile(r'f\(\d+\.?\d*')
    m = p.search(string)
    if m:
        if rwfct:
            x = m.group()
            x = x.replace('f(','')
            x = x.replace(')','')
            x = int(x)
            y = eval(rwfct)
            rwmsg = 'Der gesuchte Wert von f(x) ist: ' + str(y)
            weini.send_message(chid, rwmsg)
            return True
        else:
            weini.send_message(chid, 'Auf Mahara ist keine Funktion zu finden!')
            return True
    else:
        return None

def extract_fct(string):
    print('-'*20)
    print('Exctrating function from', string,'...')
    global rwfct
    p = re.compile(r'f\(x\)=[x\d.\+\*\-/\^()coisn]+', re.I)
    m = p.search(string)
    if m:
        fct = m.group()
        print(fct)
        a = 'cosin'
        wfct = ['sin', 'cos']
        ##search for cosin indicators
        if any(i in fct for i in a):
            print('Found function containing cosin indicators...')
            ##found cos or sin
            if any(i in fct for i in wfct):
                print('Cos or Sin found!')
                fct = fct.replace('f(x)=', '')
                fct = fct.replace(' ','')
                fct = fct.replace('^','**')
                print('Extracted', fct, 'sucessfully')
                print('-'*20)
                rwfct = fct
                return fct
            ##foung cosin, but no cos or sin
            else:
                print('ERROR: No cos or sin found!')
                print('-'*20)
                return None
        #found no cos or sin
        else:
            print('Found no cosin indicators...')
            fct = fct.replace('f(x)=', '')
            fct = fct.replace(' ','')
            fct = fct.replace('^','**')
            print('Extracted', fct, 'sucessfully')
            print('-'*20)
            rwfct = fct
            return fct
    ##found no function
    else:
        print('Extraction failed, found no satisfying pattern!')
        print('-'*20)
        return None

def plot_fct(term):
    print('-'*20)
    print('Plotting function', term)
    yvals = []
    x = linspace(-10,10,200)
    lab = 'f(x)=' + term
    print(lab)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.plot(x,eval(term),'g')
    plt.title(lab)
    plt.savefig('plot.png')
    print('Exported plot sucessfully!')
    with open('plot.png', 'rb') as image:
          weini.send_photo(chid, image)
          print('Sent plot sucessfully!')
          print('-'*20)
   
