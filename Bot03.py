import telebot
import re
from datetime import datetime, timedelta
import difflib
import json
import schedule
import time
import threading
import copy
import robotweini as rw


bot = telebot.TeleBot('1070998367:AAExa_Zd5Hjtt-JOoHMGwgxeu9-FA_9x0iw')
subs = ['mathe', 'deutsch', 'latein', 'englisch', 'franz-f', 'franz-a', 'psycho', 'chemie', 'physik', 'geschichte', 'geo', 'musik', 'be', 'reminder']
weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
hu = {} #dictionary von aufgaben, fächer als keys
now = datetime.now()
json_hws = 'homeworks.json'
late = 'late.json'
hu_sav = {}
chid = -1001256312641 #für siebenaalpha gruppe
commandids = []

userf = '7auser.txt'

def save(message, targetf):
    uid = message.from_user.id
    uname = message.from_user.first_name
    utext = message.text
    cont = '-'*30 + '\r\n'
    cont += '>> MESSAGE' + '\r\n'
    cont += '[+]ID: '+ str(uid) + '\r\n'
    cont += '[+]First Name: '+ uname + '\r\n'
    cont += 'Content:' + '\r\n'
    cont += utext + '\r\n'
    cont += '-'*30
    with open(targetf, 'a+') as f:
        f.write(cont)
    return
        

def to_day(datum, forjson):
    if not forjson: print('(to_day) converting ' + str(datum) + '...')
    test = datum - now.date()
    if test.days <= 7 and not forjson:
        wday = datum.weekday()
        datum = weekdays[wday]
    else:
        datum = str(datum.day) + '.' + str(datum.month) + '.'
    if not forjson: print('(to_day) converted to ' + str(datum) + '!')
    return datum

def to_date(weekday):
    print('(to_date) converting ' + str(weekday) + '...')
    d = weekdays.index(weekday) - now.weekday()
    if d < 1:
        d = 7 + d
    d = timedelta(days = d)
    d = now + d
    print('(to_date) converted to ' + str(d.date()) + '!')
    return d.date()

def extract_date(s, forjson):
    if not forjson: print('(extract_date) extracting from ' + str(s) + '...')
    p = re.compile(r'\d{1,2}\.\d{1,2}\.')
    x = p.search(s)
    if x:
        dat = ''
        datum = x.group()
        #s filter
        ps = re.compile(r'\d{1,2}\.\d{1,2}\.|bis ?\d{1,2}\.\d{1,2}\.|\S+\d{1,2}\.\d{1,2}\.\S+|\d{1,2}\.\d{1,2}\.2020')    
        if ps.search(s): s = ps.sub('', s)
        ps = re.compile(r' $')
        if ps.search(s): s = ps.sub('', s)
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
                if not forjson: print('(extract_date) extraction failed, date ' + str(dat_formatted) + ' is today/in the past')
                return None, s
        except Exception as e:
            if not forjson: print('(extract_date) extraction failed, error: ' + str(e))
            return None, s
    else:
        return None, s
    dat_formatted = dat_formatted.date()
    if not forjson: print('(extract_date) extracted ' + str(dat_formatted) + '!')
    return dat_formatted, s

def extract_day(s):
    print('(extract_day) extracting day from ' + str(s) + '...')
    p = re.compile(r'montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag', re.I)
    tag = p.search(s)
    if tag:
        ps = re.compile(r'bis (montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)|\S+(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)\S+|(montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)', re.I)    
        if ps.search(s): s = ps.sub('', s)
        ps = re.compile(r' $')
        if ps.search(s): s = ps.sub('', s)
        tag = tag.group()
        tag = tag.lower()
        tag = tag.capitalize()
    else:
        print('(extract_day) extraction failed, found no day')
        return None, s
    print('(extract_day) extracted ' + str(tag) + '!')
    return tag, s

def add_task(fach, datum, text):
    print('(add_task) adding task: ' + str(fach) + ', date + text:' + str(datum) + ', ' + str(text) + '...')
    neu = {'dead': datum, 'task': text}
    hu = read_json(json_hws)
    if fach in hu:
        hu[fach].append(neu)
    else:
        hu[fach] = []
        hu[fach].append(neu)
    write_json(hu, json_hws)
    print('(add_task) task added!')

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
    print('(show_tasks) showing tasks for subs ' + str(show_subs) + '...')
    return show_subs
	
def read_json(targetfile):
    print('(read_json) fetching homeworks from json...')
    try:
        with open(targetfile, 'r') as json_file:
            dictionary = json.load(json_file)
    except Exception as e:
        print('xxxxxxx\nReading JSON file failed:\n{}\nxxxxxxx\n'.format(e))
    for sub in dictionary:
        sub = dictionary[sub]
        for hw in sub:
            hw['dead'], s = extract_date(hw['dead'], True)
    print('(read_json) succesfullly fetched!')
    return dictionary

def write_json(dictionary, targetfile):
    print('(write_json) writing to json, homeworks: ' + str(dictionary) + '...')
    for sub in dictionary:
        sub = dictionary[sub] # list with dictionaries
        for hw in sub:
            hw['dead'] = to_day(hw['dead'], True)
    try:
        with open(targetfile, 'w') as jsonfile:
            json.dump(dictionary, jsonfile, indent=5)
    except Exception as ex:
        print('xxxxxxx\nWriting JSON file failed:\n{}\nxxxxxxx\n'.format(ex))
    print('(write_json) writing succesful!')
    return dictionary

def show_daily(reminder=False):
    now = datetime.now().date()
    print('(show_daily) showing tasks, today is ' + str(now) + '...')
    hu = read_json(json_hws)
    #delete every unactual task
    delsub = []
    for sub in hu:
        for task in hu[sub]: 
            deadline = task['dead']
            if deadline == None:
                if len(hu[sub]) == 1:
                    delsub.append(sub)
                else:
                    ind = hu[sub].index(task)
                    del hu[sub][ind]
    for x in delsub:
        del hu[x]
    write_json(hu, json_hws)
    print('Deleted unactual tasks sucessfully...')
    if reminder:
        #find all actual tasks
        actual_hu = {}
        hu = read_json(json_hws)
        for sub in hu:
            for task in hu[sub]:
                 deadline = task['dead']
                 delta = deadline - now
                 if delta.days == 1:
                     if not 'sub_tasks' in locals(): sub_tasks = []
                     sub_tasks.append(task)
            if 'sub_tasks' in locals():
                actual_hu[sub] = sub_tasks
                del sub_tasks
        print('Filtered actual tasks sucessfully...')
        #generate message
        if not actual_hu:
            msg = 'Es gibt keine HÜs zu erledigen bis morgen! \U0001F973'
            bot.send_message(chid, msg)
        else:
            msg = '\U0001F4CB HÜs bis morgen'
            for sub in actual_hu:
                msg += '\n' + sub + ':\n'
                for task in actual_hu[sub]:
                    msg += '\u00BB ' + task['task'] + '\n'
            bot.send_message(chid, msg)
        print('Sent reminder sucessfully...')
                 
def add_sub(message, botmsg):
    bot.delete_message(chid, botmsg)
    markup = telebot.types.ReplyKeyboardRemove()
    if message.text.lower() in subs:
        botmsg = bot.send_message(chid, 'Bis wann ist die HÜ zu erledigen?', reply_markup=markup)
        bot.register_next_step_handler(message, add_date, message.text.lower(), botmsg.message_id)
        msgid = message.message_id
        bot.delete_message(chid, msgid)
    else:
        try:
            similar = difflib.get_close_matches(message.text.lower(), subs, n=1)
            bot.reply_to(message, str(fach) + '? Meintest du ' + similar[0] + '? \U0001F928', reply_markup=markup)
        except:
            bot.reply_to(message, 'Ich kenne das Fach ' + message.text.lower() + ' nicht \U0001F928', reply_markup=markup)
        # bot.send_message(chid, 'Für welches Fach willst du eine HÜ hinzufügen?')
        # bot.register_next_step_handler(message, add_sub)

def add_date(message, fach, botmsg):
    bot.delete_message(chid, botmsg)
    datum, s = extract_date(message.text, False)
    if datum == None: 
        datum, s = extract_day(message.text)
        if not datum == None: datum = to_date(datum)
    if not datum == None:
        botmsg = bot.send_message(chid, 'Was ist zu erledigen?')
        bot.register_next_step_handler(message, add_hw, fach, datum, botmsg.message_id)
        msgid = message.message_id
        bot.delete_message(chid, msgid)
    else:
        bot.reply_to(message, 'Falsches Eingabeformat für das Datum, bitte benutze einen Wochentag oder ein Datum im Format `TT.MM.`, das nicht in der Vergangenheit liegt. /help', parse_mode='Markdown')
        # bot.send_message(chid, 'Bis wann ist die HÜ zu erledigen?')
        # bot.register_next_step_handler(message, add_date, fach)

def add_hw(message, fach, datum, botmsg):
    bot.delete_message(chid, botmsg)
    add_task(fach, datum, message.text)
    msgid = message.message_id
    bot.delete_message(chid, msgid)
    bot.send_message(chid, 'HÜ "' + message.text + '" für ' + fach.capitalize() + ' hinzugefügt!')

@bot.message_handler(commands = ['add'])
def dazu(message):
    if not message.chat.id == chid:
        bot.reply_to(message, 'Dieser Befehl kann in diesem Chat nicht ausgeführt werden.')
        return
    print('-'*20 + '\nRECEIVED COMMAND "' + str(message.text) + '"')
    #make saving
    global hu_sav
    hu_sav = read_json(json_hws)
    # variables
    mest = message.text.split(' ', 2)
    if len(mest) == 1:
        markup = telebot.types.ReplyKeyboardMarkup()
        msgid = message.message_id
        bot.delete_message(chid, msgid)
        for sub in subs:
            markup.add(telebot.types.KeyboardButton(sub.capitalize()))
        botmsg = bot.send_message(chid, 'Für welches Fach willst du eine HÜ hinzufügen?', reply_markup=markup)
        bot.register_next_step_handler(message, add_sub, botmsg.message_id)
        #bot.delete_message(chid, botmsg.message_id)
        return
    del mest[0]
    if len(mest) < 2: 
        bot.reply_to(message, 'Falsches Eingabeformat, bitte schreibe `/add` <fach> <deadline und aufgabe>, oder einfach `/add`! /help', parse_mode='Markdown')
        return
    fach = mest[0].lower()
    text = mest[1]
    del mest
    datum, text = extract_date(text, False)
    if datum == None: 
        datum, text = extract_day(text)
        try: 
            datum = to_date(datum)
        except Exception as e: print(e)
    try: 
        print('checking request, subject: ' + str(fach) + ', task: ' + str(text) + ', deadline: ' + (datum)) 
    except: 
        print('checking request, variables failed.')
    # checking variables
    if not fach in subs: # checking subject
        try:
            similar = difflib.get_close_matches(fach, subs, n=1)
            bot.reply_to(message, fach + '? Meintest du ' + similar[0] + '? \U0001F928')
        except:
            bot.reply_to(message, 'Ich kenne das Fach ' + fach + ' nicht \U0001F928')
        print('COULD NOT ADD TASK, WRONG SUBJECT\n' + '-'*20)
        return
    elif not datum: # checking date
        bot.reply_to(message, 'Falsches Eingabeformat für das Datum, bitte benutze einen Wochentag oder ein Datum im Format `TT.MM.`, das nicht in der Vergangenheit liegt.', parse_mode='Markdown')
        print('COULD NOT ADD TASK, WRONG DATE\n' + '-'*20)
    else:
        add_task(fach, datum, text)
        bot.send_message(chid, 'HÜ "' + text + '" in ' + fach + ' hinzugefügt!')
        msgid = message.message_id
        bot.delete_message(chid, msgid)
        print('SUCCESFULLY ADDED TASK\n' + '-'*20)

@bot.message_handler(commands = ['show'])
def zeige(message):
    print('-'*20 + '\nRECEIVED COMMAND "' + str(message.text) + '"')
    #chid = message.chat.id
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
                bot.reply_to(message, str(hw) + '? Meintest du ' + str(simsub[0]) + '? \U0001F928')
                print('COULD NOT DISPLAY TASK, UNKNOWN SUBJECT' + str(hw) + '\n' + '-'*20)
                return
            except:
                bot.reply_to(message, 'Ich kenne das Fach ' + str(hw) + ' nicht \U0001F928')
                print('COULD NOT DISPLAY TASK, UNKNOWN SUBJECT' + str(hw) + '\n' + '-'*20)
                return
    show_subs = show_tasks(show_subs) # returns dictionary with lists of dictionaries!
    print(show_subs)
    if len(show_subs) == 0:
        bot.send_message(chid, '\U0001F389 Keine HÜs!')
        print('SUCCESFUL, NO TASKS\n' + '-'*20)
    else:
        msg = '\U0001F4DA HÜs'
        for sub in show_subs:
            msg += '\n' + str(sub).capitalize() + ': \n'
            for hw in show_subs[sub]:
                print(hw)
                datum = to_day(hw['dead'], False)
                msg += 'bis ' + str(datum) + ': ' + str(hw['task']) + '\n'
        bot.send_message(chid, msg)
        print('SUCCESFULLY DISPLAYED TASKS\n' + '-'*20)

@bot.message_handler(commands = ['del'])
def dele(message):
    if not message.chat.id == chid:
        bot.reply_to(message, 'Dieser Befehl kann in diesem Chat nicht ausgeführt werden.')
        return
    print('-'*20 + '\nRECEIVED COMMAND "' + str(message.text) + '"')
    text = message.text.split(' ')
    hu = read_json(json_hws)
    global hu_sav
    hu_sav = read_json(json_hws)
    anydels = False
    del text[0]
    if not text:
        clear = {}
        write_json(clear, json_hws)
        bot.reply_to(message, '\U0001F5D1 Alle HÜs gelöscht!')
        print('SUCCESFULLY CLEARED TASKS\n' + '-'*20)
    else:
        for sub in text:
            sub = sub.lower()
            if sub in hu:
                anydels = True
                del hu[sub]
                write_json(hu, json_hws)
                #bot.reply_to(message, 'HÜs in ' + sub + ' gelöscht!')
                print('Sucessfully deleted tasks from' + sub + '\n' + '-'*20)
            else:
                if sub in subs:
                    anydels = True
                    #bot.reply_to(message, 'HÜs in ' + sub + ' gelöscht!')
                    print(sub + ' already empty!')
                else:
                    try: 
                        simsub = difflib.get_close_matches(sub, subs, n=1)
                        bot.reply_to(message, str(sub) + '? Meintest du ' + str(simsub[0]) + '? \U0001F928')
                        print('COULD NOT DISPLAY TASK, UNKNOWN SUBJECT' + str(sub) + '\n' + '-'*20)
                    except:
                        bot.reply_to(message, 'Ich kenne das Fach ' + str(sub) + ' nicht \U0001F928')
                        print('COULD NOT DISPLAY TASK, UNKNOWN SUBJECT' + str(sub) + '\n' + '-'*20)
        if anydels: bot.send_message(chid, '\U0001F5D1 HÜs gelöscht!')
        
@bot.message_handler(commands = ['revert'])
def rev(message):
    if not message.chat.id == chid:
        bot.reply_to(message, 'Dieser Befehl kann in diesem Chat nicht ausgeführt werden.')
        return
    global hu_sav
    hu = copy.deepcopy(hu_sav)
    hu_sav = read_json(json_hws)
    write_json(hu, json_hws)
    bot.send_message(chid, '\U000021A9 Letzten Schritt rückgängig gemacht!')

@bot.message_handler(commands = ['info'])
def info(message):
    bot.send_message(chid,'Hallo! Ich bin 7Assistant, ich helfe unserer Klassengruppe mit ihrem HÜ-Management! Um zu lernen, wie ich funktioniere, schreib /help, dann wird der Weini dir über alle Befehle Bescheid geben!')

@bot.message_handler(commands = ['print'])
def pr(message):
    hu = read_json(json_hws)
    print(hu)

@bot.message_handler(commands = ['id'])
def idf(message):
    print('-'*20, 'RECEIVED COMMAND: /id')
    thisid = message.chat.id
    msgid = message.message_id
    bot.delete_message(chid, msgid)
    print('The id of this chat is:', thisid)
    print('-'*20)
    return

@bot.message_handler(commands = ['math'])
def weinimath(message):
    print('-'*20)
    print('RECEIVVED COMMAND', message.text)
    text = message.text
    text = message.text.replace('/math ','')
    text = text.lower()
    fct = rw.extract_fct(text)
    if fct: ##found function
        rw.plot_fct(fct)
    else:
        val = rw.fctval(text)
        if val: ##found value request
            return
        else:     
            rwmsg = 'Wer unterrichtet euch in Mathe, dass ihr nicht einmal fähig seid einen Bot zu benutzen?'
            rw.weini.reply_to(message, rwmsg)

@bot.message_handler(commands = ['todo'])
def todo(message):
    show_daily(True)

@bot.message_handler(content_types=['text'])
def weini(message):
    save(message, userf)
    print('-'*20)
    print('Starting weinhandler...')
    rw.weinhandler(message)

		

class ScheduleThread(threading.Thread):
     def run(self):
         schedule.every().day.at('14:00').do(show_daily, reminder=True)
         schedule.every().day.at('00:01').do(show_daily)
         while True:
             schedule.run_pending()
             time.sleep(1)

class BotThread(threading.Thread):
    def run(self):
        while True:
            try:
                bot.polling(interval=1)
            except Exception as e:
                print(str(e))
                continue

thread1 = BotThread()
thread2 = ScheduleThread()
thread1.start()
thread2.start()
