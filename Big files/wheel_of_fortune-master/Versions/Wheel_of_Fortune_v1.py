##for Raleigh & Grant
##who contributed more than they know
################################################################################
############################## WHEEL OF FORTUNE ################################
################################################################################

import random
import string

WORDLIST_FILENAME = "words.txt"

def load_words():
    """
    Returns a list of valid words. Words are strings of lowercase letters.
    Depending on the size of the word list, this function may
    take a while to finish.
    """

##    print "Loading word list from file..."
    inFile = open(WORDLIST_FILENAME, 'r', 0)
    line = inFile.readline()
    wordlist = string.split(line)
##    print "  ", len(wordlist), "words loaded."
    return wordlist

def choose_word(wordlist):
    """
    wordlist (list): list of words (strings)

    Returns a word from wordlist at random
    """
    return random.choice(wordlist)

wordlist = load_words()

def start():
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    print string.center("Welcome to WHEEL OF FORTUNE!", 80)
    print string.center("I'm your host, Pat Sajak, with your hostess Vanna White.", 80)
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    playerNames_hum = ["Player 1", "Player 2", "Player 3"]
    playerNames_comp = ["Chad Ledouche", "Roger"]
    playerOrder_val = [[0, 0], [0, 0], [0, 0]]
    rounds = ["first", "second", "third", "fourth"]
    gameSetup(playerNames_hum, playerNames_comp, playerOrder_val, rounds)
    
def gameSetup(playerNames_hum, playerNames_comp, playerOrder_val, rounds):
    numPlayers = get_numPlayers()
    players = get_playerNames(numPlayers, playerNames_hum, playerNames_comp)
    game(players, playerOrder_val)

def game(players, playerOrder_val):
    playerOrder = preRound_one(players, playerOrder_val)
##    print "playerOrder is:", playerOrder
##    print "playerOrder_val is equal to:", playerOrder_val
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    print string.center("BEGIN ROUND ONE", 80, "~")
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    raw_input("Press 'ENTER' to continue: ")
    playerOrder_val = round_one(playerOrder, playerOrder_val)
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    print string.center("BEGIN ROUND TWO", 80)
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    raw_input("Press 'ENTER' to continue: ")
    playerOrder_val = round_two(playerOrder, playerOrder_val)
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    print string.center("BEGIN ROUND THREE", 80)
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    raw_input("Press 'ENTER' to continue: ")
    playerOrder_val = round_three(playerOrder, playerOrder_val)
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    print string.center("BEGIN ROUND FOUR", 80)
    print string.center(("*" * 80), 80)
    print string.center(("*" * 80), 80)
    raw_input("Press 'ENTER' to continue: ")
    playerOrder_val = round_four(playerOrder, playerOrder_val)
    end_game(players)
    
def preRound_one(players, playerOrder_val):
    playerOrder = get_playerOrder(players, playerOrder_val)
    return playerOrder

def round_one(playerOrder, playerOrder_val):
    game_round = 1
    hidden_word = choose_word(wordlist).lower()
    alpha = string.ascii_lowercase
    disp_word = "_ " * len(hidden_word)
    incom_word = "_" * len(hidden_word)
##    print "The hidden_word is:", hidden_word
    counter = 11
    while counter > 0:
##        for i in range(counter):
##            counter -= 1
##            print "counter is equal to:", counter
        print "The first round puzzle is:", disp_word
        for j in [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]:
##              counter -= 1
##              print "counter is equal to:", counter
            possession = True
            if counter == 0:
                break
            while possession == True:
                counter -= 1
                if counter == 0:
                    break
##                print "counter is equal to:", counter
                selection = 0
                print "Remaining letters are:", string.upper(alpha)
                selection = get_playerSelection(playerOrder, hidden_word, disp_word, j)
                if selection == 1:
                    prize = get_prize(game_round)
                    if (type(prize) is int) or (prize == "freePlay"):
                        print playerOrder[j] + " spun for $" + str(prize) + "!"
                        guess = get_guessLetter()
                        guess = string.lower(guess)
                        if guess in alpha:
                            alpha = alpha.replace(guess, "")
                        else:
                            print "Sorry, '" + string.upper(guess) + "' has already been called in this round."
                            print playerOrder[j + 1] + " now takes possession of The Wheel."
                            break
                        print "----------------------"
                        print "Vanna, does the puzzle contain any '" + guess.upper() + "'s?"
                        raw_input("----------------------")
                        if guess in hidden_word:
                            for i in range(len(hidden_word)):
                                if hidden_word[i] == guess:
                                    disp_word = disp_word[0:(i * 2)] + guess + disp_word[((i * 2) +  1):]
                                    incom_word = incom_word[0:i] + guess + incom_word[(i + 1):]
                            letter_app = 0
                            for i in range(len(hidden_word)):
                                if hidden_word[i] == guess:
                                    letter_app += 1
                            if letter_app == 1:
                                print disp_word
                                print "Good guess:", playerOrder[j] + "! There is 1", guess.upper(), "in the puzzle!"
                                print "That adds $" + str(prize) + " to your total prize score!"
                                playerOrder_val[j][0] = playerOrder_val[j][0] + prize
                                print "Your total prize score is now $" + str(playerOrder_val[j][0]) + "!"
                            else:
                                print disp_word
                                print "Good guess:", playerOrder[j] + "! There are", letter_app, "'" + guess.upper() + "'s in the puzzle!"
                                print "That adds $" + str(prize * letter_app) + " to your total prize score!"
                                playerOrder_val[j][0] = playerOrder_val[j][0] + (prize * letter_app)
                                print "Your total prize score is now $" + str(playerOrder_val[j][0]) + "!"
                                raw_input("----------------------")
                            possession = True
                            if incom_word == hidden_word:
                                break
                        else:
                            possession = False
                            print "I'm sorry", playerOrder[j] + ", but there are no '" + guess.upper() + "'s in the puzzle."
                    if prize == "bankrupt":
                        print playerOrder[j], "spun for BANKRUPT!"
                        
                        print "Sorry, " + playerOrder[j] + ". Possession of The Wheel passes to", playerOrder[(j + 1)] + "."
                        raw_input("----------------------")
                        break
                    if prize == "loseATurn":
                        print playerOrder[j], "spun for LOSE A TURN!"
                        "Sorry, " + playerOrder[j] + ". Possession of The Wheel passes to " + playerOrder[j + 1] + "."
                        raw_input("----------------------")
                        break
                else:
                    guess = get_guessWord()
                    if guess == hidden_word:
                        incom_word = guess
                        break
                    break
            if incom_word == hidden_word:
##                print "j is equal to:", j
                print "Congratulations,", playerOrder[j] + ". You correctly solved the puzzle:", hidden_word + "."
                break
##    if incom_word == hidden_word:
##            break
        break
    return playerOrder_val

def round_two(playerOrder, playerOrder_val):
    game_round = 1
    hidden_word = choose_word(wordlist).lower()
    alpha = string.ascii_lowercase
    disp_word = "_ " * len(hidden_word)
    incom_word = "_" * len(hidden_word)
##    print "The hidden_word is:", hidden_word
    counter = 11
    while counter > 0:
##        for i in range(counter):
##            counter -= 1
##            print "counter is equal to:", counter
        print "The first round puzzle is:", disp_word
        for j in [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]:
##              counter -= 1
##              print "counter is equal to:", counter
            possession = True
            if counter == 0:
                break
            while possession == True:
                counter -= 1
                if counter == 0:
                    break
##                print "counter is equal to:", counter
                selection = 0
                print "Remaining letters are:", string.upper(alpha)
                selection = get_playerSelection(playerOrder, hidden_word, disp_word, j)
                if selection == 1:
                    prize = get_prize(game_round)
                    if (type(prize) is int) or (prize == "freePlay"):
                        print playerOrder[j] + " spun for $" + str(prize) + "!"
                        guess = get_guessLetter()
                        guess = string.lower(guess)
                        if guess in alpha:
                            alpha = alpha.replace(guess, "")
                        else:
                            print "Sorry, '" + string.upper(guess) + "' has already been called in this round."
                            print playerOrder[j + 1] + " now takes possession of The Wheel."
                            break
                        print "----------------------"
                        print "Vanna, does the puzzle contain any '" + guess.upper() + "'s?"
                        raw_input("----------------------")
                        if guess in hidden_word:
                            for i in range(len(hidden_word)):
                                if hidden_word[i] == guess:
                                    disp_word = disp_word[0:(i * 2)] + guess + disp_word[((i * 2) +  1):]
                                    incom_word = incom_word[0:i] + guess + incom_word[(i + 1):]
                            letter_app = 0
                            for i in range(len(hidden_word)):
                                if hidden_word[i] == guess:
                                    letter_app += 1
                            if letter_app == 1:
                                print disp_word
                                print "Good guess:", playerOrder[j] + "! There is 1", guess.upper(), "in the puzzle!"
                                print "That adds $" + str(prize) + " to your total prize score!"
                                playerOrder_val[j][0] = playerOrder_val[j][0] + prize
                                print "Your total prize score is now $" + str(playerOrder_val[j][0]) + "!"
                            else:
                                print disp_word
                                print "Good guess:", playerOrder[j] + "! There are", letter_app, "'" + guess.upper() + "'s in the puzzle!"
                                print "That adds $" + str(prize * letter_app) + " to your total prize score!"
                                playerOrder_val[j][0] = playerOrder_val[j][0] + (prize * letter_app)
                                print "Your total prize score is now $" + str(playerOrder_val[j][0]) + "!"
                                raw_input("----------------------")
                            possession = True
                            if incom_word == hidden_word:
                                break
                        else:
                            possession = False
                            print "I'm sorry", playerOrder[j] + ", but there are no '" + guess.upper() + "'s in the puzzle."
                    if prize == "bankrupt":
                        print playerOrder[j], "spun for BANKRUPT!"
                        
                        print "Sorry, " + playerOrder[j] + ". Possession of The Wheel passes to", playerOrder[(j + 1)] + "."
                        raw_input("----------------------")
                        break
                    if prize == "loseATurn":
                        print playerOrder[j], "spun for LOSE A TURN!"
                        "Sorry, " + playerOrder[j] + ". Possession of The Wheel passes to " + playerOrder[j + 1] + "."
                        raw_input("----------------------")
                        break
                else:
                    guess = get_guessWord()
                    if guess == hidden_word:
                        incom_word = guess
                        break
                    break
            if incom_word == hidden_word:
##                print "j is equal to:", j
                print "Congratulations,", playerOrder[j] + ". You correctly solved the puzzle:", hidden_word + "."
                break
##    if incom_word == hidden_word:
##            break
        break
    return playerOrder_val

def round_three(playerOrder, playerOrder_val):
    game_round = 1
    hidden_word = choose_word(wordlist).lower()
    alpha = string.ascii_lowercase
    disp_word = "_ " * len(hidden_word)
    incom_word = "_" * len(hidden_word)
##    print "The hidden_word is:", hidden_word
    counter = 11
    while counter > 0:
##        for i in range(counter):
##            counter -= 1
##            print "counter is equal to:", counter
        print "The third round puzzle is:", disp_word
        for j in [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]:
##              counter -= 1
##              print "counter is equal to:", counter
            possession = True
            if counter == 0:
                break
            while possession == True:
                counter -= 1
                if counter == 0:
                    break
##                print "counter is equal to:", counter
                selection = 0
                print "Remaining letters are:", string.upper(alpha)
                selection = get_playerSelection(playerOrder, hidden_word, disp_word, j)
                if selection == 1:
                    prize = get_prize(game_round)
                    if (type(prize) is int) or (prize == "freePlay"):
                        print playerOrder[j] + " spun for $" + str(prize) + "!"
                        guess = get_guessLetter()
                        guess = string.lower(guess)
                        if guess in alpha:
                            alpha = alpha.replace(guess, "")
                        else:
                            print "Sorry, '" + string.upper(guess) + "' has already been called in this round."
                            print playerOrder[j + 1] + " now takes possession of The Wheel."
                            break
                        print "----------------------"
                        print "Vanna, does the puzzle contain any '" + guess.upper() + "'s?"
                        raw_input("----------------------")
                        if guess in hidden_word:
                            for i in range(len(hidden_word)):
                                if hidden_word[i] == guess:
                                    disp_word = disp_word[0:(i * 2)] + guess + disp_word[((i * 2) +  1):]
                                    incom_word = incom_word[0:i] + guess + incom_word[(i + 1):]
                            letter_app = 0
                            for i in range(len(hidden_word)):
                                if hidden_word[i] == guess:
                                    letter_app += 1
                            if letter_app == 1:
                                print disp_word
                                print "Good guess:", playerOrder[j] + "! There is 1", guess.upper(), "in the puzzle!"
                                print "That adds $" + str(prize) + " to your total prize score!"
                                playerOrder_val[j][0] = playerOrder_val[j][0] + prize
                                print "Your total prize score is now $" + str(playerOrder_val[j][0]) + "!"
                            else:
                                print disp_word
                                print "Good guess:", playerOrder[j] + "! There are", letter_app, "'" + guess.upper() + "'s in the puzzle!"
                                print "That adds $" + str(prize * letter_app) + " to your total prize score!"
                                playerOrder_val[j][0] = playerOrder_val[j][0] + (prize * letter_app)
                                print "Your total prize score is now $" + str(playerOrder_val[j][0]) + "!"
                                raw_input("----------------------")
                            possession = True
                            if incom_word == hidden_word:
                                break
                        else:
                            possession = False
                            print "I'm sorry", playerOrder[j] + ", but there are no '" + guess.upper() + "'s in the puzzle."
                    if prize == "bankrupt":
                        print playerOrder[j], "spun for BANKRUPT!"
                        
                        print "Sorry, " + playerOrder[j] + ". Possession of The Wheel passes to", playerOrder[(j + 1)] + "."
                        raw_input("----------------------")
                        break
                    if prize == "loseATurn":
                        print playerOrder[j], "spun for LOSE A TURN!"
                        "Sorry, " + playerOrder[j] + ". Possession of The Wheel passes to " + playerOrder[j + 1] + "."
                        raw_input("----------------------")
                        break
                else:
                    guess = get_guessWord()
                    if guess == hidden_word:
                        incom_word = guess
                        break
                    break
            if incom_word == hidden_word:
##                print "j is equal to:", j
                print "Congratulations,", playerOrder[j] + ". You correctly solved the puzzle:", hidden_word + "."
                break
##    if incom_word == hidden_word:
##            break
        break
    return playerOrder_val

def round_four(playerOrder, playerOrder_val):
    game_round = 1
    hidden_word = choose_word(wordlist).lower()
    alpha = string.ascii_lowercase
    disp_word = "_ " * len(hidden_word)
    incom_word = "_" * len(hidden_word)
##    print "The hidden_word is:", hidden_word
    counter = 11
    while counter > 0:
##        for i in range(counter):
##            counter -= 1
##            print "counter is equal to:", counter
        print "The fourth and final round puzzle is:", disp_word
        for j in [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]:
##              counter -= 1
##              print "counter is equal to:", counter
            possession = True
            if counter == 0:
                break
            while possession == True:
                counter -= 1
                if counter == 0:
                    break
##                print "counter is equal to:", counter
                selection = 0
                print "Remaining letters are:", string.upper(alpha)
                selection = get_playerSelection(playerOrder, hidden_word, disp_word, j)
                if selection == 1:
                    prize = get_prize(game_round)
                    if (type(prize) is int) or (prize == "freePlay"):
                        print playerOrder[j] + " spun for $" + str(prize) + "!"
                        guess = get_guessLetter()
                        guess = string.lower(guess)
                        if guess in alpha:
                            alpha = alpha.replace(guess, "")
                        else:
                            print "Sorry, '" + string.upper(guess) + "' has already been called in this round."
                            print playerOrder[j + 1] + " now takes possession of The Wheel."
                            break
                        print "----------------------"
                        print "Vanna, does the puzzle contain any '" + guess.upper() + "'s?"
                        raw_input("----------------------")
                        if guess in hidden_word:
                            for i in range(len(hidden_word)):
                                if hidden_word[i] == guess:
                                    disp_word = disp_word[0:(i * 2)] + guess + disp_word[((i * 2) +  1):]
                                    incom_word = incom_word[0:i] + guess + incom_word[(i + 1):]
                            letter_app = 0
                            for i in range(len(hidden_word)):
                                if hidden_word[i] == guess:
                                    letter_app += 1
                            if letter_app == 1:
                                print disp_word
                                print "Good guess:", playerOrder[j] + "! There is 1", guess.upper(), "in the puzzle!"
                                print "That adds $" + str(prize) + " to your total prize score!"
                                playerOrder_val[j][0] = playerOrder_val[j][0] + prize
                                print "Your total prize score is now $" + str(playerOrder_val[j][0]) + "!"
                            else:
                                print disp_word
                                print "Good guess:", playerOrder[j] + "! There are", letter_app, "'" + guess.upper() + "'s in the puzzle!"
                                print "That adds $" + str(prize * letter_app) + " to your total prize score!"
                                playerOrder_val[j][0] = playerOrder_val[j][0] + (prize * letter_app)
                                print "Your total prize score is now $" + str(playerOrder_val[j][0]) + "!"
                                raw_input("----------------------")
                            possession = True
                            if incom_word == hidden_word:
                                break
                        else:
                            possession = False
                            print "I'm sorry", playerOrder[j] + ", but there are no '" + guess.upper() + "'s in the puzzle."
                    if prize == "bankrupt":
                        print playerOrder[j], "spun for BANKRUPT!"
                        
                        print "Sorry, " + playerOrder[j] + ". Possession of The Wheel passes to", playerOrder[(j + 1)] + "."
                        raw_input("----------------------")
                        break
                    if prize == "loseATurn":
                        print playerOrder[j], "spun for LOSE A TURN!"
                        "Sorry, " + playerOrder[j] + ". Possession of The Wheel passes to " + playerOrder[j + 1] + "."
                        raw_input("----------------------")
                        break
                else:
                    guess = get_guessWord()
                    if guess == hidden_word:
                        incom_word = guess
                        break
                    break
            if incom_word == hidden_word:
##                print "j is equal to:", j
                print "Congratulations,", playerOrder[j] + ". You correctly solved the puzzle:", hidden_word + "."
                break
##    if incom_word == hidden_word:
##            break
        break
    return playerOrder_val

def end_game(players):
    print "----------------------"
    print "GAME OVER!"
    print "----------------------"
    print "Would you like to play again? (y/n)"
    selection = string.lower(raw_input())
    if selection == "y" or selection == "yes":
        playerOrder_val = [[0, 0], [0, 0], [0, 0]]
        game(players, playerOrder_val)        

def get_numPlayers():
    numPlayers = 0
    while numPlayers <= 0 or numPlayers > 3:
        print "How many contestants (max: 3) will be playing today?"
        numPlayers = raw_input("Number of players: ",)
        if numPlayers == "One" or numPlayers == "one" or numPlayers == "ONE" or numPlayers == "1":
            numPlayers = 1
            print "You have selected play for 1 player."
        if numPlayers == "Two" or numPlayers == "two" or numPlayers == "TWO" or numPlayers == "2":
            numPlayers = 2
            print "You have selected play for 2 players."
        if numPlayers == "Three" or numPlayers == "three" or numPlayers == "THREE" or numPlayers == "3":
            numPlayers = 3
            print "You have selected play for 3 players."
        if numPlayers < 1 or numPlayers > 3 or numPlayers == type(int):
            print string.center(("-" * 80), 80)
            print "ERROR: INVALID PLAYER NUMBER"
            raw_input (string.center(("-" * 80), 80))
    return numPlayers

def get_playerNames(numPlayers, playerNames_hum, playerNames_comp):
    players = ["Player 1", "Player 2", "Player 3"]
    print string.center(("-" * 80), 80)
    print string.center(("-" * 80), 80)
    for i in range(numPlayers):
        name = ""
        while name == "":
            name = raw_input(players[i] + ", what is your name? ")
            name = name.title()
            if name == "":
                print string.center(("-" * 80), 80)
                print string.center(("-" * 80), 80)
                print string.expandtabs("ERROR, FIELD EMPTY")
                print string.expandtabs("Please try again.")
                print string.center(("-" * 80), 80)
                print string.center(("-" * 80), 80)
        players[i] = name
    if numPlayers == 3:
        print string.center(("-" * 80), 80)
        print "Welcome", players[0] + ",", players[1] + ", and", players[2] + "!"
    if numPlayers == 2:
        players[2] = playerNames_comp[0]
        print string.center(("-" * 80), 80)
        print "Welcome", players[0] + " and", players[1] + "! Today you will be playing against", players[2] + "."
    if numPlayers == 1:
        players[1] = playerNames_comp[0]
        players[2] = playerNames_comp[1]
        print string.center(("-" * 80), 80)
        print "Welcome", players[0] + "! Today you will be playing against", players[1], "and", players[2] + "."    
    return players

def get_playerOrder(players, playerOrder_val):
    playerOrder = [0, 0, 0]
    print "We will now play the Toss-Up Spin for possession of The Wheel in the first"
    print "round."
    print string.center(("-" * 80), 80)
    raw_input ("Press 'ENTER' to continue: ")
    for i in (0, 1, 2):
        if i == 0:
            print players[i] + " will spin first."
        print "Get ready! " + players[i] + " is up next."
        print "It is " + players[i] + "'s turn to spin."
##        print string.center(("-" * 80), 80)
        raw_input("Press 'ENTER' to spin The Wheel. ")
        print string.center(("-" * 80), 80)
        print string.center((players[i] + " received $" + str(i * 100) + "."), 80)
        print string.center(("-" * 80), 80)
        for j in (0, 1):
            if j == 0:
                playerOrder_val[i][j] = (i * 100)
            else:
                playerOrder_val[i][j] = players[i]
    playerOrder_val.sort(reverse=True)
    for i in range(3):
        playerOrder[i] = playerOrder_val[i][1]
    print "Congratulations,", playerOrder[0] + "! You have won the Toss-Up Spin and will take possession"
    print "of The Wheel at the beginning of the first round."
    print ""
    print playerOrder[1] + " will Take possession of The Wheel after", playerOrder[0] + ", followed by", playerOrder[2] + "."
    print string.center(("-" * 80), 80)
    raw_input ("Press 'ENTER' to continue: ")
    return playerOrder

def get_playerOrder_val(playerOrder_val):
    for i in (0, 1):
            if j == 0:
                playerOrder_val[i][j] = (i * 100)

def get_guessLetter():
    check = False
    while check == False:
        guess = string.lower(raw_input("Please guess a letter: ",))
        if len(guess) == 1 and guess in string.ascii_lowercase:
            check = True
        else:
            print "----------------------"
            print "ERROR: INVALID ENTRY!"
            print "Please enter one letter per guess."
            print "----------------------"
    return guess
def get_prize(game_round):
    prize = 0
    if game_round == 1:
        prizes = ["bankrupt", "bankrupt", "bankrupt", "bankrupt", "bankrupt",
          "bankrupt", "bankrupt", "bankrupt", 500, 500, 500, 500, 500, 500, 500, 500,
          500, 500, 500, 500, 550, 550, 550, 600, 600, 600, 600, 600,
          600, 650, 650, 650, 650, 650, 650, 700, 700, 700, 700, 700,
          700, 700, 700, 700, 800, 800, 800, 800, 800, 800, 900, 900,
          900, 900, 900, 900, 900, 900, 900, 2500, 2500, 2500, "loseATurn", 
          "loseATurn", "loseATurn", "freePlay", "freePlay", "freePlay", 750, 750,
          750, 750]
        prize = prizes[random.randint(0, 71)]
    if game_round == 2:
        prizes = ["bankrupt", "bankrupt", "bankrupt", "bankrupt", "bankrupt",
          "bankrupt", "bankrupt", "bankrupt", 500, 500, 500, 500, 500, 500, 500, 500,
          500, 500, 500, 500, 550, 550, 550, 600, 600, 600, 600, 600,
          600, 650, 650, 650, 650, 650, 650, 700, 700, 700, 700, 700,
          700, 700, 700, 700, 800, 800, 800, 800, 800, 800, 900, 900,
          900, 900, 900, 900, 900, 900, 900, 2500, 2500, 2500, "loseATurn", 
          "loseATurn", "loseATurn", "freePlay", "freePlay", "freePlay", 750, 750,
          750, 750]
        prize = prizes[random.randint(0, 71)]
    if game_round == 3:
        prizes = ["bankrupt", "bankrupt", "bankrupt", "bankrupt", "bankrupt",
          "bankrupt", "bankrupt", "bankrupt", 500, 500, 500, 500, 500, 500, 500, 500,
          500, 500, 500, 500, 550, 550, 550, 600, 600, 600, 600, 600,
          600, 650, 650, 650, 650, 650, 650, 700, 700, 700, 700, 700,
          700, 700, 700, 700, 800, 800, 800, 800, 800, 800, 900, 900,
          900, 900, 900, 900, 900, 900, 900, 2500, 2500, 2500, "loseATurn", 
          "loseATurn", "loseATurn", "freePlay", "freePlay", "freePlay", 750, 750,
          750, 750]
        prize = prizes[random.randint(0, 71)]
    if game_round == 4:
        prizes = ["bankrupt", "bankrupt", "bankrupt", "bankrupt", "bankrupt",
          "bankrupt", "bankrupt", "bankrupt", 500, 500, 500, 500, 500, 500, 500, 500,
          500, 500, 500, 500, 550, 550, 550, 600, 600, 600, 600, 600,
          600, 650, 650, 650, 650, 650, 650, 700, 700, 700, 700, 700,
          700, 700, 700, 700, 800, 800, 800, 800, 800, 800, 900, 900,
          900, 900, 900, 900, 900, 900, 900, 2500, 2500, 2500, "loseATurn", 
          "loseATurn", "loseATurn", "freePlay", "freePlay", "freePlay", 750, 750,
          750, 750]
        prize = prizes[random.randint(0, 71)]
    return prize

def get_guessWord():
    guess = string.lower(raw_input("Input puzzle solution: ",))
    return guess

def check_guessLetter(guess, hidden_word, disp_word):
##    Exact same as bodies of rounds one through four! Figure out implementation
    if guess in hidden_word:
        for i in range(len(hidden_word)):
            if hidden_word[i] == guess:
                disp_word = disp_word[0:(i * 2)] + guess + disp_word[((i * 2) +  1):]
                print "Good guess:", disp_word
                return true
    else:
        return false

def get_playerSelection(playerOrder, hidden_word, disp_word, j):
    selection = 0
    while selection != "solve" or selection != "spin" or selection != "s" or selection != "pick":
        print "----------------------"
        print playerOrder[j] + ", would you like to SPIN or SOLVE THE PUZZLE?"
        selection = raw_input("Selection: ")
        selection = selection.lower()
        if selection == "solve" or selection == "pick" or selection == "spin" or selection == "solve the puzzle":
            break
        else:
            print "----------------------"
            print "ERROR: UNRECOGNIZED COMMAND."
            print "Please select from the following and try again:"
            print "'SOLVE'"
            print "'SOLVE THE PUZZLE'"
            print "'SPIN'"
            print "----------------------"
    if selection == "pick a letter" or selection == "pick" or selection == "spin" or selection == "letter":
        selection = 1
        return selection
    else:
        selection = 2
        return selection

def remove_letterGuess(guess, alpha):
    alpha = alpha.strip(guess)
    return alpha

def get_hidden_word(hidden_word, used_letters):
    """Returns a string of the form __ad___ by filling in correct guesses"""
    visible_word = ""
    for letter in hidden_word:
        if letter in used_letters:
            visible_word += letter
        else:
            if len(visible_word) > 0 and visible_word[-1] == '_':
                visible_word += " "
            visible_word += "_"
    return visible_word

start()
