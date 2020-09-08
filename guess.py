import random

#Change the (1, 99) to (1, ? ) if you want. But then also change all the 99 to the ? you made.
n = random.randint(1, 99)
guess = int(input("Enter an integer from 1 to 99: "))
while n != "guess":

    if guess < n:
        print ("Guess is low")
        guess = int(input("Enter an integer from 1 to 99: "))
    elif guess > n:
        print ("Guess is high")
        guess = int(input("Enter an integer from 1 to 99: "))
    else:
        print ("You guessed it!")
        break
