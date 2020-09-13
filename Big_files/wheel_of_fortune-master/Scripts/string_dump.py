import pickle

WORDS_FILENAME = "Wheel_of_Fortune_words.txt"
openFile = open(WORDS_FILENAME, "r+")

words_unparsed = openFile.readlines()
words = []
puzzles_and_clues = {}

place_holder = 0

for i in range(len(words_unparsed)):

    if words_unparsed[i] == "\n":
        words.append(words_unparsed[place_holder : i])
        place_holder = i + 1
        i += 1

    if words_unparsed[i] == "Title\n":
        words.append(words_unparsed[i : -1])

words = words[:-1]

for i in range(len(words)):
    
    for j in range(len(words[i])):
        
        if words[i][j][len(words[i][j]) - 1:] == "\n":    
            words[i][j] = words[i][j][:-1]

for i in range(len(words)):

    for j in range(len(words[i])):

        if j == 0: 
            puzzles_and_clues[words[i][j]] = words[i][1:len(words[i])]

file = open("puzzles_and_clues.txt", "w")    
pickle.dump(puzzles_and_clues, file)
openFile.close()
