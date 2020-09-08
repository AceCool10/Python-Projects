import webbrowser
import time
import random

while True:
	sites = random.choice(['google.com', 'youtube.com'])
	visit = "http://{}".format(sites)
	webbrowser.open(visit)
	time.sleep(5)
