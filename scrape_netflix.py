import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
import numpy as np
import pandas as pd
from os.path import exists
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

if exists("scraped_activity_netlix.csv"):
    print('Not first run')
    # working with dataframes now. Next steps:
    # figure out why not everything on the loaded page is being scraped
    # get this if statement going:
        # copy mostly everything from below, but have it first load the last
        # entry in the csv file and press the button until this shows up on screen
        # THEN! after this matches, grab all the data on screen, convert it to the dataframe
        # delete the matched entry and everything after it. Invert it, and then
        # append it to the previously created csv (need to look up how to do this).
else:
    print('First data grab. Could take a while')
    # Grab ALL the data if it's the first run. Test tomorrow by removing counters
    file = open("scraped_activity_netlix.csv", "w")
    #writer = csv.writer(file)
    #writer.writerow(["DATE", "TITLE"])
    test_counter = 0 # temporary counter to keep it from loading all previous data
    while True:
        test_counter = test_counter + 1
        ## Previous method that works. 
        #for date, title in zip(date, title):
            #print(date.text + title.text)
            #writer.writerow([date.text, title.text])
        try:
            page_to_scrape.find_element(By.CLASS_NAME, "btn-blue").click()
        except NoSuchElementException:
            break
        if test_counter > 2:
            break
    date = page_to_scrape.find_elements(By.CLASS_NAME, "date")
    title = page_to_scrape.find_elements(By.CLASS_NAME, "title")
    #new method
    time.sleep(3)
    for date, title in zip(date, title):
        dates.append(date.text)
        titles.append(title.text)
    dates.reverse()
    titles.reverse()
    new_data = pd.DataFrame({'DATE': dates, 'TITLE': titles})
    new_data.to_csv('scraped_activity_netlix.csv', index=False, encoding='utf-8')
    print(new_data)
    file.close()