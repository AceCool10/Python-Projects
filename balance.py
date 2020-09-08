import random
import time



max_blocks = random.randint(2, 10)
blocks = 0

print("See how high you can build the tower before it tumbles!\n")

while True:
	if blocks == max_blocks:
		if input("Oh no, The tower of blocks tumbled down! Try again? y/n  ") == "y":
			blocks = 0
		else:
			break
#------------------------------------------MAIN--------------------------------------------------
	if input("There are {} blocks balancing on top of each other, add a block? y/n  ".format(blocks)) == "y":
		print("Adding...")
		time.sleep(random.randint(0,3))
		blocks = blocks + 1
#------------------------------------------MAIN--------------------------------------------------
	else:
		blocks2 = max_blocks - blocks
		print("You were {} blocks close from tumbling.".format(blocks2))
		break

