# Adapted from Tinkernut's video:
# https://www.youtube.com/watch?v=tRNwTXeJ75U&t=18s
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
import numpy as np

#IF USING A RASPBERRY PI, FIRST INSTALL THIS OPTIMIZED CHROME DRIVER
#sudo apt-get install chromium-chromedriver
browser_driver = Service('/usr/lib/chromium-browser/chromedriver')
page_to_scrape = webdriver.Chrome(service=browser_driver)
page_to_scrape.get("http://quotes.toscrape.com")

page_to_scrape.find_element(By.LINK_TEXT, "Login").click()


time.sleep(3) # wait 3 seconds for login to load
username = page_to_scrape.find_element(By.ID, "username")
password = page_to_scrape.find_element(By.ID, "password")

login_data = np.genfromtxt('login_info.csv', dtype=None, encoding=None, skip_header=1, names=("Service, Username, Password"))
User = login_data[login_data['Service']=='quotes']['Username']
Pass = login_data[login_data['Service']=='quotes']['Password']
username.send_keys(User)
password.send_keys(Pass)

page_to_scrape.find_element(By.CSS_SELECTOR, "input.btn-primary").click()

file = open("scraped_quotes.csv", "w")
writer = csv.writer(file)

writer.writerow(["QUOTES", "AUTHORS"])

while True:
    quotes = page_to_scrape.find_elements(By.CLASS_NAME, "text")
    authors = page_to_scrape.find_elements(By.CLASS_NAME, "author")
    for quote, author in zip(quotes, authors):
        print(quote.text + " - " + author.text)
        writer.writerow([quote.text, author.text])
    try:
        page_to_scrape.find_element(By.PARTIAL_LINK_TEXT, "Next").click()
    except NoSuchElementException:
        break
file.close()