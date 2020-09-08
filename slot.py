from random import *
import time
import sys
 
reel_1 = ''
reel_2 = ''
reel_3 = ''
bank = 0
name = ''
qwerty = 0
admin = False                            #make thing so place bid: if it is lol 
current_bet = 0
spin_count = 0 # For Testing Purposes
total_won = 0
total_lost = 0

def slow_reel(reel1, reel2, reel3):
    for symbol in (reel_1,reel_2,reel_3):
        sys.stdout.write(symbol)
        sys.stdout.flush()
        time.sleep(0.1)
slow_reel(reel_1, reel_2, reel_3)
def game_loop():
    global reel_1, reel_2, reel_3, bank, current_bet, spin_count, total_lost, total_won
    if bank <= 0:
        print("GAME OVER LOSER!")
    while bank > 0:
        if current_bet > 0 and bank >= current_bet:
            bet_r = input("\n[ENTER] TO REPEAT BET, 'NO' TO PLACE NEW ONE: ")
            if bet_r == "" or bet_r == "Y":
                bet = current_bet
            else:
                current_bet = 0
                bet = 0
                game_loop()
        else:
            try:
                bet = int(input("PLACE YOUR BET!: "))
            except ValueError:
                return game_loop()
 
        if bet >= 0 and bank >= bet:
            bank -= bet
            total_lost += bet
            current_bet = bet
            try:
                reel1 = ['$', '@', '@', '#', '#', '#', '&', '&', '&', '&', '%', '%', '%',
                '%', '%']
                reel2 = ['$', '@', '@', '#', '#', '#', '&', '&', '&', '&', '%', '%', '%',
                '%', '%']
                reel3 = ['$', '@', '@', '#', '#', '#', '&', '&', '&', '&', '%', '%', '%',
                '%', '%']
                if name == "Admin":
                    reel1 = ['$', '$']#<--- ADMIN Luck...
                    reel2 = ['$', '$']
                    reel3 = ['$', '$']

                reel_1 = choice(reel1)
                reel_2 = choice(reel2)
                reel_3 = choice(reel3)
                print("\n-----SPINNING FOR: ${}-----\n".format(current_bet))
                for c in reel_1:
                    time.sleep(0.4)
                    print(" (","<",c,">", end=' | ', flush=True)
                for c in reel_2:
                    time.sleep(0.9)
                    print("<",c,">", end=' | ', flush=True)
                for c in reel_3:
                    time.sleep(2.0)
                    print("<",c,">", end=' )', flush=True)
                    time.sleep(1.0)
                print("\n")
                print("----------------------------")
                spin_count += 1
 
                if reel_1 == '$' and reel_2 == '$' and reel_3 == '$':
                    bank += 100 * current_bet
                    total_won += 100 * current_bet
                    print("YOU WON THE JACKPOT!!!: $",100 * current_bet)
                elif reel_1 == '@' and reel_2 == '@' and reel_3 == '@':
                    bank += 50 * current_bet
                    total_won += 50 * current_bet
                    print("YOU WON!!: $",50 * current_bet)
                elif reel_1 == '#' and reel_2 == '#' and reel_3 == '#':
                    bank += 20 * current_bet
                    total_won += 20 * current_bet
                    print("YOU WON!!: $",20 * current_bet)
                elif reel_1 == '&' and reel_2 == '&' and reel_3 == '&':
                    bank += 10 * current_bet
                    total_won += 10 * current_bet
                    print("YOU WON!!: $",10 * current_bet)
                elif reel_1 == '%' and reel_2 == '%' and reel_3 == '%':
                    bank += 5 * current_bet
                    total_won += 5 * current_bet
                    print("YOU WON!!: $",5 * current_bet)
                elif reel_1 == '%' and reel_2 == '%':
                    bank += current_bet
                    total_won += current_bet
                    print("YOU WON!!: $",current_bet)
                elif reel_1 == '%' and reel_3 == "%":
                    bank += current_bet
                    total_won += current_bet
                    print("YOU WON!!: $", current_bet)
                else:
                    pass
                print("\nYour Statistics")
                print("Won: $", total_won, "Spent: $", total_lost, "\nCurrent Balance: $", bank)
            except (Exception):
                pass
def start():
    global bank
    global name
    global qwerty
    global admin
    if qwerty == 0:
        name = input("What is your name? ").title()
        if name == "Admin":
            admin = True            
    print("\nWelcome to Python Slots, " + name)
    command = input("YOU START WITH $10,000 \n\nPRESS [ENTER] TO BEGIN \n(If you need help, just type in 'help') ")
    if command == "":
        bank = 10000
        game_loop()
    if command == "help" or "help" in command:
        print("""\n$:$:$ means JACKPOT!!! (times 100)
                   @:@:@ means times bid by 50
                   #:#:# means times bid by 20
                   &:&:& means times bid by 10
                   %:%:% means times bid by 5
                   %:%:_ means bid
                   %:_:% means bid

                     Others mean nothing...
                              """)
        qwerty = 2
        start()
    else:
        print("ALL YOU HAD TO DO WAS PRESS ENTER")
        qwerty = 2
        start()
 
start()

