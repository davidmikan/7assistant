commands = {
    'add': 'Fügt eine Hausübung hinzu. \nBenutze /add FACH ABGABETERMIN AUFGABE. Als Abgabetermin kannst du entweder ein Datum im Format `TT.MM.` angeben, oder einen Wochentag.',
    'show': 'Zeigt dir zu erledigende Hausübungen. \nBenutze entweder /show für alle unerledigten HÜs, oder /show FÄCHER für zu erledigende HÜs in diesen Fächern'
}

def helpmsg(command):
    command = command.split(' ')
    del command[0]
    try: command = command[0]
    except: command = 'all'
    command = str(command)
    if command == 'all':
        requested_commands = commands
        msg = 'Befehle für 7Assistant:\n'
        for key in requested_commands:
            msg += '/' + str(key) + '\n' + commands[key] + '\n'
    elif command in commands:
        msg = '7Assistants /' + command + ' Befehl\n' + commands[command]
    else:
        msg = 'Befehl nicht erkannt...'
    return msg