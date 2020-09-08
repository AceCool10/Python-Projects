import random
from words import word_list

def get_word():
    word = random.choice(word_list)
    return word

word = get_word()
print(word)
