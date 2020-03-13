import telebot
import re
from datetime import datetime, timedelta
import difflib
import json
import schedule
import time
import threading

bot = telebot.TeleBot('1111789249:AAEGz9Tn20CzC7b6ZljLMjtRSakvN8Z7_H8')
subs = ['mathe', 'englisch', 'franz', 'psycho', 'deutsch', 'chemie', 'physik', 'geschichte', 'latein', 'geo', 'musik', 'be', 'reminder']
weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
hu = {} #dictionary von aufgaben, fächer als keys
now = datetime.now()
json_hws = 'homeworks.json'
json_sav = 'savedhws.json'
chid = '-1001256312641' #für siebenaalpha gruppe

bot.send_message(chid, 'Bot successfully started! ^^')

def to_day(datum, forjson):
    if forjson == False: print('converting ' + str(datum) + '...')
    test = datum - now.date()
    if test.days <= 7 and not forjson:
        wday = datum.weekday()
        datum = weekdays[wday]
    else:
        datum = str(datum.day) + '.' + str(datum.month) + '.'
    if forjson == False: print('converted to ' + str(datum) + '!')
    return datum

def to_date(weekday):
    print('converting ' + str(weekday) + '...')
    d = weekdays.index(weekday) - now.weekday()
    if d < 1:
        d = 7 + d
    d = timedelta(days = d)
    d = now + d
    print('converted to ' + str(d.date()) + '!')
    return d.date()

def extract_date(s, forjson):
    if forjson == False: print('extracting date from ' + str(s) + '...')
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
                if forjson == False: print('extraction failed, date ' + str(dat_formatted) + ' is today/in the past')
                return None, s
        except Exception as e:
            if forjson == False: print('extraction failed, error: ' + str(e))
            return None, s
    else:
        return None, s
    dat_formatted = dat_formatted.date()
    if forjson == False: print('extracted ' + str(dat_formatted) + '!')
    return dat_formatted, s

def extract_day(s):
    print('extracting day from ' + str(s) + '...')
    p = re.compile(r'montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag', re.I)
    tag = p.search(s)
    if tag:
        s = p.sub('',s, 1)
        s = s.replace('  ', ' ')
        tag = tag.group()
        tag = tag.lower()
        tag = tag.capitalize()
    else:
        print('extraction failed, found no day')
        return None, s
    print('extracted ' + str(tag) + '!')
    return tag, s

def add_task(fach, datum, text):
    print('adding task: ' + str(fach) + ', date + text:' + str(datum) + ', ' + str(text) + '...')
    neu = {'dead': datum, 'task': text}
    hu = read_json(json_hws)
    if fach in hu:
        hu[fach].append(neu)
    else:
        hu[fach] = []
        hu[fach].append(neu)
    write_json(hu, json_hws)
    print('added!')

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
    print('showing subs: ' + str(show_subs))
    return show_subs
	
def read_json(targetfile):
    print('fetching homeworks from json...')
    try:
        with open(targetfile, 'r') as json_file:
            dictionary = json.load(json_file)
    except Exception as e:
        print('xxxxxxx\nReading JSON file failed:\n{}\nxxxxxxx\n'.format(e))
    for sub in dictionary:
        sub = dictionary[sub]
        for hw in sub:
            hw['dead'], s = extract_date(hw['dead'], True)
    print('succesfullly fetched!')
    return dictionary

def write_json(dictionary, targetfile):
    print('writing to json, homeworks: ' + str(dictionary))
    for sub in dictionary:
        sub = dictionary[sub] # list with dictionaries
        for hw in sub:
            hw['dead'] = to_day(hw['dead'], True)
    try:
        with open(targetfile, 'w') as jsonfile:
            json.dump(dictionary, jsonfile, indent=5)
    except Exception as ex:
        print('xxxxxxx\nWriting JSON file failed:\n{}\nxxxxxxx\n'.format(ex))
    print('writing succesful!')
    return dictionary

def show_daily(reminder=False):
    print('Start excecution of show_daily() ...')
    now = datetime.now().date()
    print('now:',now)
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
    if reminder == True:
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
            msg = 'Juhu, nichts zu tun bis morgen'
            bot.send_message(chid, msg)
            bot.send_sticker(chid, 'CAACAgIAAxkBAANxXmu2tkoO1Kr6nkNRGO5h7B2MIiIAAqAAA_cCyA_DRx0BoJvAGhgE')
        else:
            msg = 'ZU TUN BIS MORGEN:\n'
            for sub in actual_hu:
                msg += '[' + sub + ']\n'
                for task in actual_hu[sub]:
                    msg += '- ' + task['task'] + '\n'
            bot.send_message(chid, msg)
        print('Sent reminder sucessfully...')
                 
def add_sub(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('a')
    itembtn2 = telebot.types.KeyboardButton('v')
    itembtn3 = telebot.types.KeyboardButton('d')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(chid, 'Für welches Fach willst du eine HÜ hinzufügen?', reply_markup=markup)
    if message.text in subs:
        fach = message.text
        bot.send_message(chid, 'Bis wann ist die HÜ zu erledigen?')
        bot.register_next_step_handler(message, add_date, fach)
    else:
        try:
            similar = difflib.get_close_matches(fach, subs, n=1)
            bot.reply_to(message, 'bruh, meintest du ' + similar[0] + '?')
        except:
            bot.reply_to(message, 'Ich kenne dieses Fach nicht \U0001F928')
        # bot.send_message(chid, 'Für welches Fach willst du eine HÜ hinzufügen?')
        # bot.register_next_step_handler(message, add_sub)

def add_date(message, fach):
    datum, s = extract_date(message.text, False)
    if datum == None: 
        datum, s = extract_day(message.text)
        if not datum == None: datum = to_date(datum)
    if not datum == None:
        bot.send_message(chid, 'Was ist zu erledigen?')
        bot.register_next_step_handler(message, add_hw, fach, datum)
    else:
        bot.reply_to(message, 'Falsches Eingabeformat für das Datum, bitte benutze einen Wochentag oder ein Datum im Format TT.MM., das nicht in der Vergangenheit liegt.')
        # bot.send_message(chid, 'Bis wann ist die HÜ zu erledigen?')
        # bot.register_next_step_handler(message, add_date, fach)

def add_hw(message, fach, datum):
    add_task(fach, datum, message.text)
    bot.send_message(chid, 'Erfolgreich hinzugefügt!')

    
@bot.message_handler(commands = ['add'])
def dazu(message):
    print('-'*20 + '\nRECEIVED COMMAND "' + str(message.text) + '"')
    #make saving
    saving = read_json(json_hws)
    write_json(saving, json_sav)
    del saving
    # variables
    mest = message.text.split(' ', 2)
    if len(mest) == 1:
        bot.send_message(chid, 'Für welches Fach willst du eine HÜ hinzufügen?')
        bot.register_next_step_handler(message, add_sub)
        return
    del mest[0]
    if len(mest) < 2: 
        bot.reply_to(message, '???')
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
            bot.reply_to(message, 'bruh, meintest du ' + similar[0] + '?')
        except:
            bot.reply_to(message, 'Ich kenne dieses Fach nicht \U0001F928')
        print('COULD NOT ADD TASK, WRONG SUBJECT\n' + '-'*20)
        return
    elif not datum: # checking date
        bot.reply_to(message, 'Falsches Eingabeformat für das Datum, bitte benutze einen Wochentag oder ein Datum im Format TT.MM., das nicht in der Vergangenheit liegt.')
        print('COULD NOT ADD TASK, WRONG DATE\n' + '-'*20)
    else:
        add_task(fach, datum, text)
        bot.reply_to(message, 'Hausaufgabe für ' + fach + ' hinzugefügt!')
        print('SUCCESFULLY ADDED TASK\n' + '-'*20)

@bot.message_handler(commands = ['show'])
def zeige(message):
    print('-'*20 + '\nRECEIVED COMMAND "' + str(message.text) + '"')
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
                bot.reply_to(message, str(hw) + '? Meintest du ' + str(simsub[0]) + '?')
                print('COULD NOT DISPLAY TASK, UNKNOWN SUBJECT' + str(hw) + '\n' + '-'*20)
                return
            except:
                bot.reply_to(message, 'Ich kenne das Fach ' + str(hw) + ' nicht :(')
                print('COULD NOT DISPLAY TASK, UNKNOWN SUBJECT' + str(hw) + '\n' + '-'*20)
                return
    show_subs = show_tasks(show_subs) # returns dictionary with lists of dictionaries!
    print(show_subs)
    if len(show_subs) == 0: 
        bot.send_sticker(chid, sticker)
        bot.send_message(chid, 'Keine HÜs!')
        print('SUCCESFUL, NO TASKS\n' + '-'*20)
    else:
        msg = 'HÜs: \n'
        for sub in show_subs:
            msg += '- ' + str(sub).capitalize() + ' - \n'
            for hw in show_subs[sub]:
                print(hw)
                datum = to_day(hw['dead'], False)
                msg += 'bis ' + str(datum) + ': ' + str(hw['task']) + '\n'
        bot.send_message(chid, msg)
        print('SUCCESFULLY DISPLAYED TASKS\n' + '-'*20)

@bot.message_handler(commands = ['del'])
def dele(message):
    print('-'*20 + '\nRECEIVED COMMAND "' + str(message.text) + '"')
    msg = message.text.split(' ')
    hu = read_json(json_hws)
    del msg[0]
    if not msg:
        clear = {}
        write_json(clear, json_hws)
        print('SUCCESFULLY CLEARED TASKS\n' + '-'*20)
    else:
        sub = msg[0].lower()
        if sub in subs:
            if sub in hu:
                del hu[sub]
                write_json(hu, json_hws)
                bot.reply_to(message, 'Gelöscht!')
                print('Sucessfully deleted tasks from' + sub + '-'*20)
            else:
                bot.reply_to(message, 'Keine Aufgaben für dieses Fach vorhanden!')
                print('Deleting tasks failed as subject not existing...' + sub + '-'*20)
                
        else:
            try: 
                simsub = difflib.get_close_matches(sub, subs, n=1)
                bot.reply_to(message, str(sub) + '? Meintest du ' + str(simsub[0]) + '?')
                print('COULD NOT DISPLAY TASK, UNKNOWN SUBJECT' + str(sub) + '\n' + '-'*20)
                return
            except:
                bot.reply_to(message, 'Ich kenne das Fach ' + str(sub) + ' nicht :(')
                print('COULD NOT DISPLAY TASK, UNKNOWN SUBJECT' + str(sub) + '\n' + '-'*20)
                return
        
@bot.message_handler(commands = ['revert'])
def rev(message):
    hu = read_json(json_hws)
    hu_sav = read_json(json_sav)
    write_json(hu_sav, json_hws)
    write_json(hu, json_sav)

@bot.message_handler(commands = ['info'])
def info(message):
    bot.send_message(chid,'Hallo! Ich bin 7Assistant, ich helfe Klassengruppen mit ihrem HÜ-Management! Um zu lernen, wie ich funktioniere, schreib /help, dann wird der Weini dir über alle Befehle bescheid geben!')

@bot.message_handler(commands = ['print'])
def pr(message):
    hu = read_json(json_hws)
    print(hu)

@bot.message_handler(commands = ['id'])
def idf(message):
    chid = message.chat.id
    print(chid)

#def handle_messages(messages):
	#for message in messages:
		# Do something with the message
		#bot.reply_to(message, 'Hi')

class ScheduleThread(threading.Thread):
     def run(self):
         schedule.every().day.at('14:01').do(show_daily, reminder=True)
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

bot.send_message(chid, 'Bot successfully started! ^^')
#bot.set_update_listener(handle_messages)
thread1 = BotThread()
thread2 = ScheduleThread()
thread1.start()
thread2.start()
