import telebot
import re
from datetime import datetime, timedelta
import difflib

# variableeeeees
bot = telebot.TeleBot('940159686:AAH2JNssVMyB0Dc0IKV0xxfZ3mA-LPY0kmg')
subs = ['mathe', 'englisch', 'franz', 'psycho', 'deutsch', 'chemie', 'physik', 'geschichte', 'latein', 'geo', 'musik', 'be']
weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
hu = {} #dictionary von aufgaben, fächer als keys
now = datetime.now()

def to_day(datum):
    test = datum - now.date()
    if test.days <= 7:
        wday = datum.weekday()
        datum = weekdays[wday]
    else:
        datum = str(datum.day) + '.' + str(datum.month) + '.'
    print('converted to ' + datum)
    return datum

def to_date(weekday):
    print(weekday)
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
            if dif.days < 1:
                return None, s
        except Exception as e:
            print(e)
            return None, s
    else:
        return None, s
    dat_formatted = dat_formatted.date()
    print('deadline: ' + str(dat_formatted))
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
    if fach in hu:
            hu[fach].append(neu)
    else:
        hu[fach] = [neu]

def show_tasks(tasks):
    print(hu)
    show_subs = {}
    if len(tasks) == 0:
        show_subs = hu
    for x in tasks:
        try:
            show_subs[x] = hu[x]
        except:
            continue
    return show_subs

# message handlers
@bot.message_handler(commands = ['add'])
def dazu(message):
    # variables
    mest = message.text.split(' ', 2)
    del mest[0]
    fach = mest[0].lower()
    text = mest[1]
    del mest
    datum, text = extract_date(text)
    print(' current date is ' + str(datum))
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
        print(datum)
        add_task(fach, datum, text)
        bot.reply_to(message, 'Hausaufgabe für ' + fach + ' hinzugefügt!')

@bot.message_handler(commands = ['show'])
def zeige(message):
    # variables
    chid = message.chat.id
    msg = ''
    sticker = 'CAACAgQAAxkBAANmXmN_UmmKIbbRBlguyPCF9UnVXcYAAg0AA8l8pyHy3-tYPCcNPxgE'
    show_requests = message.text.split(' ')
    show_subs = []
    del show_requests[0]
    # determining subs to be checked
    for hw in show_requests:
        if hw in subs:
            show_subs.append(hw)
        else:
            try: 
                simsub = difflib.get_close_matches(r, subs, n=1)
                bot.reply_to(message, hw + '? Meintest du ' + simsub[0] + '?\n')
            except:
                bot.reply_to(message, 'Ich kenne das Fach ' + hw + ' nicht :(' + '\n')
    if len(show_subs) > 0:
        msg = 'HÜs:\n'
    else: # if not show all hw
        pass
    # ouput tasks
    show_subs = show_tasks(show_subs)
    if show_subs == {}:
        msg = 'Keine HÜs auf!'
    else:
        for sub in show_subs:
            msg += '- ' + sub + ' -\n'
            for task in show_subs[sub]:
                datum = to_day(task['dead'])
                msg += 'bis ' + datum + ': ' + task['task'] + '\n'
    bot.send_message(chid, msg)
"""
    if len(hu) == 0:
        bot.send_sticker(chid, sticker)
        bot.send_message(chid, 'Keine HÜs!')
    else:
        if len(show_requests) > 0:
            msg = 'HÜs:\n'
            for r in show_requests:
                print(r)
                msg += '- ' + r + ' -\n'
                try:
                    y = hu[r]
                    for z in y:
                        msg += 'bis ' + str(z['dead']) + ': ' + z['task'] + '\n'
                except:
                    if not r in subs:
                        
                    else: 
                        msg += 'Keine HÜs in ' + str(r) + ' \U0001F601' + '!\n'
        else:
            msg ='ALLE HÜS:\n'
            for x in hu:
                y = hu[x]
                msg += '- ' + x + ' -\n'
                for z in y:
                    msg += 'bis ' + str(z['dead']) + ': ' + z['task'] + '\n'
        bot.send_message(chid, msg)
"""
@bot.message_handler(commands = ['del'])
def dele(message):
    hu.clear()

@bot.message_handler(commands = ['print'])
def pr(message):
    print(hu)

while True:
    try:
        bot.polling(interval=1)
    except Exception as e:
        continue