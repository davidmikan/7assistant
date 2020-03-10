# 7assistant
### What does this bot do?

This telegram bot stores your classes homeworks and displays them on demand in telegram groups.

### Commands

You only need 3 commands: 
`/add`, `/show` and `/del`

`/add <subject> <deadline / task>`

With this command you can add a homework to a certain subject. 

The subject has to be in the subjects list, otherwise the bot will try to suggest a similar subject or reply with a error message. 

The date can either be a weekday "Montag"-"Freitag" or a date in the format DD.&#8203;MM. 

The task is just any string of text and can contain weekdays, as long as the deadline ( if it's a weekday ) comes before it

`/show <subjects>`

With this command you can view the stored homeworks.

If you don't enter any subjects, the bot will reply with all the stored homeworks. If you enter subjects, the bot will reply with the homeworks for the subjects that arent empty.

`/del`

This command simply deletes all stored homeworks.