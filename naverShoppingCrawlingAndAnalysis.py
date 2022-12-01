from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import matplotlib.pyplot as plt
import time
import csv
import pandas as pd
import re
import numpy as np
import warnings
import seaborn as sns


# 1. Data collection(Collect data from a website that fits topic and create and leverage my own dataset)


# Chrome Driver Automatic Updates
from webdriver_manager.chrome import ChromeDriverManager

# Browser Turn Off Protection
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

# Eliminate unnecessary error messages
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

service = Service(executable_path=ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=chrome_options)

# Open Website
browser.get("https://naver.com")
browser.implicitly_wait(30)

# Click shopping menu
shopping = browser.find_element(By.CSS_SELECTOR, 'a.nav.shop')
shopping.click()

# Click search menu
search = browser.find_element(By.CSS_SELECTOR, 'input._searchInput_search_text_3CUDs')
search.click()

# Enter search terms
search.send_keys("keyboard")
search.send_keys(Keys.ENTER)

# Create File
f = open(r'C:/Users/cksdn/Desktop/data.csv', 'w', encoding='cp949', newline='')
cswriter = csv.writer(f)

all = 0
for i in range(20):
    # Infinite Scroll(Because Naver -> dynamic site)
    before_h = browser.execute_script("return window.scrollY")

    while True:
        browser.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.END)

        time.sleep(3)

        after_h = browser.execute_script("return window.scrollY")

        if after_h == before_h:
            break
        
        before_h = after_h
    #  Product information div
    items = browser.find_elements(By.CSS_SELECTOR, '.basicList_info_area__TWvzp')
    for item in items:
        name = item.find_element(By.CSS_SELECTOR, '.basicList_title__VfX3c').text
        try:
            price = item.find_element(By.CSS_SELECTOR, '.price_num__S2p_v').text
        except:
            price = "Suspension of sales"
        link = item.find_element(By.CSS_SELECTOR, '.basicList_title__VfX3c > a').get_attribute('href')
        day = item.find_element(By.CSS_SELECTOR, '.basicList_etc__LSkN_').text
        like = item.find_element(By.CSS_SELECTOR, '.basicList_num__sfz3h').text
        print(name, price[:-1], link, day, like)
        
        # Exclude if any information you want to know is missing
        if name=="" or price=="" or link == "" or day[4:] == "" or day[4:].find(" ") != -1 or day[4:].find(".") == -1 or like=="":
            pass
        else:
            if price!="Suspension of sales":
                price = re.sub(r"[^0-9]", "", price) # Leaving only numbers
            day = re.sub(r"[^0-9]", "", day) # Leaving only numbers
            cswriter.writerow([name, price, day, like, link])
    
    # Click next button
    next = browser.find_element(By.CSS_SELECTOR, '.pagination_next__pZuC6')
    next.click()
    
    # Print a notice
    print("Data extraction on {}th page completed".format(i+1))
    all += 1

print("Data extraction completed for {} pages in {} pages".format(all, all))
f.close()


# 2. Data analysis

# Remove FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# Read CSV File
df = pd.read_csv('C:/Users/cksdn/Desktop/data.csv', encoding='cp949', header=None)
df.columns = ['name', 'cost', 'Registration date', 'The number of likes', 'link']


# 2.1 Simple statistical analysis after grouping data using groupby
print(df.groupby(['cost', 'Registration date']).mean())
print(df.groupby(['Registration date']).size())
print(df.groupby('The number of likes').agg(np.mean))


# 2.2 Drawing a graph using matplotlib

# Set graph size, extract some data
fig = plt.figure(figsize=(10,10))
ndf = df[['cost', 'Registration date', 'The number of likes']]

# Relationship between cost of goods(cost) and consumer preference (The number of likes)
ax1 = fig.add_subplot(2, 1, 1)
sns.regplot(x='cost', y='The number of likes', data=ndf, ax=ax1)

# Relationship between Registration date of goods(Registration Date) and consumer preference (The number of likes)
ax2 = fig.add_subplot(2, 1, 2)
sns.regplot(x='Registration date', y='The number of likes', data=ndf, ax=ax2)
ax2.set_ylim(0,500)

plt.show()
plt.close()
