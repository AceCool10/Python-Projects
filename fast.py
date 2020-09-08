start1 = input("This short program is designed to show you how fast a computor counts to 1000000. Do you want to start?  ")

# Lots of problems with this backdoor so it is discontinued
#
#if start1 == "qwerty":
#    for i in range(1, 10000001, 1):
#        print(i)

start2 = input("\nAre you sure?  ")
start3 = input("\nOK, but just to be safe, pres CTRL + C to stop because this program uses a lot of memory.  ")
start4 = input("\nLastly, you have to move the mouse on some computers for you to visualy see how fast your computor can count because of lag.\n\nSay yes to start.\n\n")

if "yes" in start4:
    for i in range(1, 10000001, 1):
        print(i)
else:
	print("\nBye!!!")
