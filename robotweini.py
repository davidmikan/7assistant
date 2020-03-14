import telebot
import random
import re
import assistant_help

bot = telebot.TeleBot('928189418:AAH6SZbYLU5p7J12VhhfimKGvQZO080n0ek')

triggered = ['robert', 'weini', 'weinhandl']
ideen = []
chid = '-1001256312641'
bot.send_message(chid, 'Gibt\'s Probleme? Will man welche??')

# def error(chid, errortype):
#     if errortype == 'subject':
#         bot.send_message(chid, 'Offensichtlich hast du nichts verstanden. Für eine Liste aller Fächer schreibe /help subjects.')
#     elif errortype == 'date':
#         bot.send_message(chid, 'Nunja, ein Datum sollte man schon richtig benutzen können.')

# @bot.message_handler(commands = ['help'])
# def helpcommand(message):
#     chid = message.chat.id
#     msg = assistant_help.helpmsg(message.text)
#     bot.send_message(chid, msg)

# def handle_messages(messages):
#     for message in messages:
#         text = message.text
#         msg = ''
#         x = random.randint(1, 6)
#         if any(ext in text.lower() for ext in triggered) and x == 1:
#             msg = 'Gibt\'s Probleme?? \nWill man welche????'
#         if msg: bot.reply_to(message, msg)
        
# bot.set_update_listener(handle_messages)

# while True:
#     try:
#         bot.polling(interval=1)
#     except Exception as e:
#         print(str(e))
#         continue