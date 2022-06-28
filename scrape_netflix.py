import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
import numpy as np
import pandas as pd
from os.path import exists
from datetime import datetime as dt
#Eventually go "headless" when don't need to watch everything happen anymore.
# This will reduce load times.
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

dates = []
titles = []

if exists("scraped_activity_netflix.csv"):
    print('Not first run')
    # Get last entry to see how many button presses are needed
    count=len(open("scraped_activity_netflix.csv").readlines()) 
    last_entry=pd.read_csv("scraped_activity_netflix.csv", skiprows=range(1,count-1), header=0)
    while True:
        dates = []
        titles = []
        date = page_to_scrape.find_elements(By.CLASS_NAME, "date")
        title = page_to_scrape.find_elements(By.CLASS_NAME, "title")
        for date, title in zip(date, title):
            dates.append(date.text)
            titles.append(title.text)
        temp_data = pd.DataFrame({'DATE': dates, 'TITLE': titles})
        # Check to see if any matches in temp_data to the last val in CSV
        df = temp_data.merge(last_entry, how='left', indicator=True, left_on=['DATE','TITLE'], right_on=['DATE','TITLE'])
        mask = df['_merge']=='both'
        selected_rows  = list(temp_data[mask].index)
        if len(selected_rows) >0:
            # cut out data we've already saved and invert the df to be saved
            temp_data = temp_data[:selected_rows[0]]
            temp_data = temp_data.iloc[::-1]
            #append the data to the CSV
            temp_data.to_csv('scraped_activity_netflix.csv', mode='a', index=False, header=False)
            break
        else:
            # verify haven't gone past date of previous saved entry. If so, print notice.
            current_date = dt.strptime(temp_data.iloc[-1].DATE, "%m/%d/%y")
            previous_date = dt.strptime(last_entry.iloc[-1].DATE, "%m/%d/%y")
            if current_date < previous_date:
                print("Looks like you've gone past the last saved entry. There might be a change to Netflix's naming convention.")
            try:
                page_to_scrape.find_element(By.CLASS_NAME, "btn-blue").click()
            except NoSuchElementException:
                break
else:
    print('First data grab. Could take a while')
    while True:
        if page_to_scrape.find_element(By.CLASS_NAME, "btn-blue").is_enabled():
            page_to_scrape.find_element(By.CLASS_NAME, "btn-blue").click()
        else:
            break
    time.sleep(3)
    date = page_to_scrape.find_elements(By.CLASS_NAME, "date")
    title = page_to_scrape.find_elements(By.CLASS_NAME, "title")
    for date, title in zip(date, title):
        dates.append(date.text)
        titles.append(title.text)
    dates.reverse()
    titles.reverse()
    new_data = pd.DataFrame({'DATE': dates, 'TITLE': titles})
    new_data.to_csv('scraped_activity_netflix.csv', index=False, encoding='utf-8')