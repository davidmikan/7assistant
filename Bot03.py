import telebot
import re
from datetime import datetime, timedelta
import difflib
import json

bot = telebot.TeleBot('1111789249:AAEGz9Tn20CzC7b6ZljLMjtRSakvN8Z7_H8')
subs = ['mathe', 'englisch', 'franz', 'psycho', 'deutsch', 'chemie', 'physik', 'geschichte', 'latein', 'geo', 'musik', 'be']
weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
hu = {} #dictionary von aufgaben, fächer als keys
now = datetime.now()
json_hws = 'homeworks.json'


def to_day(datum, forjson):
    test = datum - now.date()
    if test.days <= 7 and not forjson:
        wday = datum.weekday()
        datum = weekdays[wday]
    else:
        datum = str(datum.day) + '.' + str(datum.month) + '.'
    print('converted to ' + datum)
    return datum

def to_date(weekday):
    d = weekdays.index(weekday) - now.weekday()
    if d < 1:
        d = 7 + d
    d = timedelta(days = d)
    d = now + d
    return d.date()

def extract_date(s):
    p = re.compile(r'\d{1,2}\.\d{1,2}\.')
    x = p.search(s)
    if x:
        dat = ''
        datum = x.group()
        s = p.sub('',s)
        s = s.replace('  ',' ')
        datum = datum.split('.')
        del datum[2]
        for a in datum:
            a = a.replace(' ', '')
            if len(a) == 2:
                dat += a
                continue
            else:
                dat += '0' + a
        try:
            dat_formatted = datetime.strptime(str(now.year) + dat, '%Y%d%m')
            dif = dat_formatted - now
            if dif.days < 0:
                return None, s
        except Exception as e:
            print(e)
            return None, s
    else:
        return None, s
    dat_formatted = dat_formatted.date()
    return dat_formatted, s

def extract_day(s):
    p = re.compile(r'montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag', re.I)
    tag = p.search(s)
    if tag:
        s = p.sub('',s, 1)
        s = s.replace('  ', ' ')
        tag = tag.group()
        tag = tag.lower()
        tag = tag.capitalize()
    else:
        return None, s
    return tag, s

def add_task(fach, datum, text):
    neu = {'dead': datum, 'task': text}
    hu = read_json(json_hws)
    if fach in hu:
        hu[fach].append(neu)
    else:
        hu[fach] = []
        hu[fach].append(neu)
    write_json(hu, json_hws)

def show_tasks(tasks):
    hu = read_json(json_hws)
    print(hu)
    show_subs = {}
    for x in tasks:
        try:
            show_subs[x] = hu[x]
        except:
            continue
    if len(tasks) == 0:
        show_subs = hu
    return show_subs
	
def read_json(targetfile):
    try:
        with open(targetfile, 'r') as json_file:
            dictionary = json.load(json_file)
    except Exception as e:
        print('xxxxxxx\nReading JSON file failed:\n{}\nxxxxxxx\n'.format(e))
    for sub in dictionary:
        sub = dictionary[sub]
        for hw in sub:
            hw['dead'], s = extract_date(hw['dead'])
    return dictionary

def write_json(dictionary, targetfile):
    for sub in dictionary:
        sub = dictionary[sub] # list with dictionaries
        for hw in sub:
            hw['dead'] = to_day(hw['dead'], True)
    try:
        with open(targetfile, 'w') as jsonfile:
            json.dump(dictionary, jsonfile, indent=5)
    except Exception as ex:
        print('xxxxxxx\nWriting JSON file failed:\n{}\nxxxxxxx\n'.format(ex))
    return dictionary
		
#write_json(hu, json_hws) #ich habe die json initialisiert werde das aber demnächst in die funktion selbst einbauen

@bot.message_handler(commands = ['add'])
def dazu(message):
    # variables
    mest = message.text.split(' ', 2)
    del mest[0]
    if len(mest) < 2: bot.reply_to(message, '???')
    fach = mest[0].lower()
    text = mest[1]
    del mest
    datum, text = extract_date(text)
    if datum == None: 
        datum, text = extract_day(text)
        try: 
            datum = to_date(datum)
        except Exception as e: print(e)
    try: 
        print('checking request, subject: ' + fach + ', task: ' + text + ', deadline: ' + datum) 
    except: 
        print('checking request, variables failed.')
    # checking variables
    if not fach in subs: # checking subject
        try:
            similar = difflib.get_close_matches(fach, subs, n=1)
            print('couldn\'t find subject ' + fach + ', suggesting ' + similar[0])
            bot.reply_to(message, 'bruh, meintest du ' + similar[0] + '?')
        except:
            print('couldn\'t find subject ' + fach)
            bot.reply_to(message, 'Ich kenne dieses Fach nicht \U0001F928')
        return
    elif not datum: # checking date
        bot.reply_to(message, 'Falsches Eingabeformat für das Datum, bitte benutze einen Wochentag oder ein Datum im Format TT.MM., das nicht in der Vergangenheit liegt.')
    else:
        add_task(fach, datum, text)
        bot.reply_to(message, 'Hausaufgabe für ' + fach + ' hinzugefügt!')

@bot.message_handler(commands = ['show'])
def zeige(message):
    chid = message.chat.id
    msg = ''
    sticker = 'CAACAgQAAxkBAANmXmN_UmmKIbbRBlguyPCF9UnVXcYAAg0AA8l8pyHy3-tYPCcNPxgE'
    show_requests = message.text.split(' ')
    show_subs = []
    del show_requests[0]
    for hw in show_requests:
        if hw in subs:
            show_subs.append(hw)
        else:
            try: 
                simsub = difflib.get_close_matches(hw, subs, n=1)
                bot.reply_to(message, hw + '? Meintest du ' + simsub[0] + '?')
                return
            except:
                bot.reply_to(message, 'Ich kenne das Fach ' + hw + ' nicht :(')
                return
    show_subs = show_tasks(show_subs) # returns dictionary with lists of dictionaries!
    print(show_subs)
    if len(show_subs) == 0: 
        bot.send_sticker(chid, sticker)
        bot.send_message(chid, 'Keine HÜs!')
    else:
        msg = 'HÜs: \n'
        for sub in show_subs:
            msg += '- ' + str(sub) + ' - \n'
            for hw in show_subs[sub]:
                print(hw)
                datum = to_day(hw['dead'], False)
                msg += 'bis ' + str(datum) + ': ' + str(hw['task']) + '\n'
        bot.send_message(chid, msg)

@bot.message_handler(commands = ['del'])
def dele(message):
    clear = {}
    write_json(clear, json_hws)

@bot.message_handler(commands = ['print'])
def pr(message):
    hu = read_json(json_hws)
    print(hu)

while True:
    try:
        bot.polling(interval=1)
    except Exception as e:
        continue