import math 
import random
import time
import datetime
global money
money = 0

game = input("""\nWelcome To Casino, an offline casino program.        

           Here you can play games like:             
           
           |Slot Machine
           |7 Roll Dice
           |3 in a line
           |Powerball
           |Guess the number
           
             More coming soon!

            Which game do you want to play? (if you need help, just type in "help")
            If you want to exit, say "no".
	                                                      \n""").lower()

if game == "guess the number" or "guess" in game:
	import random
	print("\nLets play Guess the number")
	answer = random.randint(1, 50)
	guess_count = range(1, 6) 
	print("I am thinking of a number between 1 and 50.")
	for guess_taken in guess_count:
	    guess_number = len(guess_count) - guess_taken + 1
	    print("You have " + str(guess_number) + " guesses. What is your guess?")
	    guess = int(input())
	# If guess too high -> tells you that it is too high
	    if guess > answer:
	        print("Your guess is too high!")
	# If guess too low -> tells you that it is too low
	    elif guess < answer:
	        print("Your guess is too low!")
	    else:
	        break # Our answer is correct
	if guess == answer:
	    print("Awesome!!! You guessed the number in " + str(guess_taken) + " guesses. You rock!")
	    money = 150
	else:
	    print("Nope. The number I was thinking about was " + str(answer))















# qwerty = input("""These are the prizes:
# 				|$10,000
# 				|$50,000
# 				|$100,000
# 				|$250,000
# 				|$500,000
# 				|$1,000,000
# 				|$2,000,000
# 				|$5,000,000
# 				|$10,000,000    
	                      
# 	                           """)









#  Idea for 3 in a line

# import time
# import sys

# done = 'false'
# #here is the animation
# def animate():
#     while done == 'false':
#         sys.stdout.write('\rloading |')
#         time.sleep(0.1)
#         sys.stdout.write('\rloading /')
#         time.sleep(0.1)
#         sys.stdout.write('\rloading -')
#         time.sleep(0.1)
#         sys.stdout.write('\rloading \\')
#         time.sleep(0.1)
#     sys.stdout.write('\rDone!     ')

# animate()
# #long process here
# done = 'false'
