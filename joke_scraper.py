#imports everything
from bs4 import BeautifulSoup
import requests

#loops over all pages
i = 1
while i <= 3:
	#gets the data
	URL = f"https://www.gotlines.com/jokes/{i}"
	headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/86.0.4240.111 Safari/537.36"}
	data = requests.get(URL, headers=headers)

	#load the bs4 data into soup variable
	soup = BeautifulSoup(data.content, "html.parser")

	#finds all classes with span "linetxt" and prints results on text form
	for linebox in soup.find_all("span", { "class": "linetext" }):
		print("• " + linebox.text)
	#goes to the next page
	i = i + 1
