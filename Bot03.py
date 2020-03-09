import telebot
import re
from datetime import datetime, timedelta
import difflib

# variableeeeeen
bot = telebot.TeleBot('940159686:AAH2JNssVMyB0Dc0IKV0xxfZ3mA-LPY0kmg')
subs = ['mathe', 'englisch', 'franz', 'psycho', 'deutsch', 'chemie', 'physik', 'geschichte', 'latein', 'geo', 'musik', 'be']
weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
hu = {} #dictionary von aufgaben, fächer als keys
neu = {} #hilfsdictionary
now = datetime.now()

def to_day(datum):
    test = datum.date() - now.date()
    if test.days <= 7:
        wday = datum.weekday()
        datum = weekdays[wday]
        print('converted to ' + datum)
    else:
        print(datum + ' in more than 1 week, returning')
    return datum

def to_date(weekday):
    d = weekdays.index(weekday) - now.weekday()
    if d < 1:
        d = 7 + d
    d = timedelta(days = d)
    d = now + d
    return d.date()

def ext(s):
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
                return None
        except Exception as e:
            print(e)
            return None
    else:
        return None
    print('deadline: ' + dat_formatted)
    return dat_formatted, s

def tags(s):
    p = re.compile(r'montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag', re.I)
    tag = p.search(s)
    if tag:
        s = p.sub('',s, 1)
        s = s.replace('  ', ' ')
        tag = tag.group()
        tag = tag.lower()
        tag = tag.capitalize()
    else:
        tag = False
    return tag, s

def add_task():
    return

# message handlers
@bot.message_handler(commands = ['dazu'])
def dazu(message):
    # variables
    mest = message.text.split(' ', 2)
    del mest[0]
    fach = mest[0].lower()
    text = mest[1]
    del mest
    datum, text = ext(text)
    print('received request, subject: ' + fach + ', task: ' + text + ', deadline: ' + datum)
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
    if datum: # checking date
        datum = to_day(datum)
        try:
            neu = {'dead': str(datum.day) + "." + str(datum.month) + ".", 'task': text}
        except:
            neu = {'dead': datum, 'task': text}
        if fach in hu:
            hu[fach].append(neu)
        else:
            hu[fach] = [neu]
    else:
        tag, s = tags(text)
        if tag in weekdays:
            tag = to_date(tag)
            neu = {'dead': str(tag.day) + '.' + str(tag.month) + '.', 'task': s}
            if fach in hu:
                hu[fach].append(neu)
            else:
                hu[fach] = [neu]
        else:
            bot.reply_to(message, 'Falsches Eingabeformat')

@bot.message_handler(commands = ['zeige'])
def zeige(message):
    chid = message.chat.id
    sticker = 'CAACAgQAAxkBAANmXmN_UmmKIbbRBlguyPCF9UnVXcYAAg0AA8l8pyHy3-tYPCcNPxgE'
    show_requests = message.text.split(' ')
    del show_requests[0]
    print(show_requests)
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
                        try: 
                            simsub = difflib.get_close_matches(r, subs, n=1)
                            msg += r + '? Meintest du ' + simsub[0] + '?\n'
                        except:
                            msg += 'Ich kenne das Fach ' + r + ' nicht :(' + '\n'
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
