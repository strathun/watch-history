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
page_to_scrape.get("http://netflix.com")

page_to_scrape.find_element(By.LINK_TEXT, "Sign In").click()


time.sleep(3) # wait 3 seconds for login to load
username = page_to_scrape.find_element(By.ID, "id_userLoginId")
password = page_to_scrape.find_element(By.ID, "id_password")

login_data = np.genfromtxt('login_info.csv', dtype=None, encoding=None, skip_header=1, names=("Service, Username, Password, Account"))
User = login_data[login_data['Service']=='Netflix']['Username']
Pass = login_data[login_data['Service']=='Netflix']['Password']
Account = login_data[login_data['Service']=='Netflix']['Account']
username.send_keys(User)
password.send_keys(Pass)

page_to_scrape.find_element(By.CSS_SELECTOR, "button.login-button").click()
time.sleep(3) # wait 3 seconds for login to load
page_to_scrape.find_element(By.LINK_TEXT, *Account).click()
time.sleep(3)

# Go into account menu
page_to_scrape.find_element(By.CSS_SELECTOR, "div.account-menu-item").click()
page_to_scrape.find_element(By.LINK_TEXT, "Account").click()

page_to_scrape.find_element(By.ID, "profile_3").click()
page_to_scrape.find_element(By.XPATH, '//*[@id="profile_3"]/ul/li[5]/a/div[1]').click()

file = open("scraped_activity.csv", "w")
writer = csv.writer(file)

writer.writerow(["DATE", "TITLE"])

date = page_to_scrape.find_elements(By.CLASS_NAME, "date")
title = page_to_scrape.find_elements(By.CLASS_NAME, "title")
for date, title in zip(date, title):
    print(date.text + title.text)
    writer.writerow([date.text, title.text])
file.close()

# while True:
#     quotes = page_to_scrape.find_elements(By.CLASS_NAME, "text")
#     authors = page_to_scrape.find_elements(By.CLASS_NAME, "author")
#     for quote, author in zip(quotes, authors):
#         print(quote.text + " - " + author.text)
#         writer.writerow([quote.text, author.text])
#     try:
#         page_to_scrape.find_element(By.PARTIAL_LINK_TEXT, "Next").click()
#     except NoSuchElementException:
#         break
# file.close()