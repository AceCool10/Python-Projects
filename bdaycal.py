#imports all that I need
import datetime
import random
import time
from words import word_list
import math

#makes variables                     #TODO Make a skip all this thing, try indent and if statement 
secret = 0 
admin = False
admin_thing = 0
ester_egg = 0

#Decides fate. hehehe...
user_name = input("What is your name?\n ")
if user_name == "":
	print("Hello there anonymous ;)")
	secret = 3
if user_name == "aiden":
	print("\nADMIN is back")
	secret = 3
	admin = True
if user_name != "" and user_name != "ADMIN":
	print("\nHello, " + user_name.title())	

#gets starting times
current_date = datetime.date.today()
current_time = datetime.datetime.now()

#this was to test millisecond accuracy
#print(current_time.strftime("%f"))

# This is used to find the time (more info, go to https://strftime.org)
print("\nThe year is " + current_date.strftime("%Y"))
print("\nThe month is " + current_date.strftime("%B"))
print("\nToday is " + current_date.strftime("%A"))
print("\nThe time is " + current_time.strftime("%X:%p"))

milliseconds = input("\nDo you want to see the milliseconds?\n ")
if milliseconds == "yes" or "yes" in milliseconds:
	current_time_milli = datetime.datetime.now()

	print("\n" + current_time_milli.strftime("%f"))
if milliseconds == "no" or "no" in milliseconds:
	ester_egg = 1

more_accurate_time = input("\nDo you want a more accurate time?\n ")
if more_accurate_time == "yes" or "yes" in more_accurate_time:
	time_one = datetime.datetime.now()
	print("\n" + time_one.strftime("%c:%f") + " <--- (Is the milliseconds)" + "\n")
if more_accurate_time == "no" and "no" in milliseconds:
	ester_egg = 2

if ester_egg == 2:
	print("\nTHEN WHY DID YOU RUN ME!!!")

if admin == False:
	admin_thing = 0
if admin == True:
	admin_thing = 5


if secret == 3:
	game = input("\n ")
	if game == "words":
		admin_thing = 0
		while True:
			def get_word():
				word = random.choice(word_list)
				return word

			word = get_word()

			print("\n ", word)
			time.sleep(0.2)


if admin_thing == 5:
	fun = input("\n ")
	if fun == "zen":
		print("""\nThe Zen of Python, by Tim Peters

Beautiful is better than ugly. 
 Explicit is better than implicit.
\\  Simple is better than complex.
 \\   Complex is better than complicated.
  \\   Flat is better than nested.
   \\   Sparse is better than dense.
    \\   Readability counts.
     \\   Special cases aren't special enough to break the rules.
      \\   Although practicality beats purity.
       \\   Errors should never pass silently.
        \\   Unless explicitly silenced.
         \\   In the face of ambiguity, refuse the temptation to guess.
          \\   There should be one-- and preferably only one --obvious way to do it.
           \\   Although that way may not be obvious at first unless you're Dutch.
            \\   Now is better than never.
             \\   Although never is often better than *right* now.
              \\   If the implementation is hard to explain, it's a bad idea.
               \\   If the implementation is easy to explain, it may be a good idea.
                \\   Namespaces are one honking great idea -- let's do more of those!
		""")
		