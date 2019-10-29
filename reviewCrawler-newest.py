# @author Nahida Sultana Chowdhury <nschowdh@iu.edu>

import csv
import json
import time
from bs4 import BeautifulSoup
import sys, io
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select


import mysql.connector 
from mysql.connector import MySQLConnection, Error

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
chromedriver_loc = "/home/mitu/Desktop/gcrawlertest/my_crawler/env/bin/chromedriver"
driver = webdriver.Chrome(executable_path=chromedriver_loc)#, chrome_options=options)
wait = WebDriverWait( driver, 10 )

cnx = mysql.connector.connect(user='root', password='Cdash2017',
                              host='127.0.0.1',
                              database='journalDataSet')
cnx.set_charset_collation('latin1')
cursor = cnx.cursor()

# Append your app store urls here
urls = [
"https://play.google.com/store/apps/details?id=com.kayak.android",
"https://play.google.com/store/apps/details?id=com.expedia.bookings",
"https://play.google.com/store/apps/details?id=ctrip.english"
]
appCounter = 0
for url in urls:
    num_of_extracted_reviews = 0
    #print(url)
    time.sleep(5)
    try:
        url_all_rev_true = url + str("&showAllReviews=true")
        driver.delete_all_cookies()
        driver.get(url_all_rev_true)
        driver.maximize_window()
        
        appCounter = appCounter + 1
        page = driver.page_source
        
        soup_expatistan = BeautifulSoup(page, "html.parser")
        expatistan_table = soup_expatistan.find("h1", class_="AHFaub")
        
        appName = expatistan_table.string.encode('ascii', 'ignore')
        print("App name: ", appName)
        #cursor.execute('''INSERT INTO appDetails (appName) VALUES(%s) where appId =%s''', (appName, appCounter))
        #cnx.commit()
        
        try:            
            menu = driver.find_element_by_xpath("/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div[1]/div/div/div[1]/div[2]/c-wiz/div/div/div[1]").click()
            time.sleep(2)
            submenu = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div[1]/div/div/div[1]/div[2]/c-wiz/div/div/div[2]/div[1]')
            submenu.click()
            time.sleep(2)
                            
            actions = ActionChains(driver)
            
            for _ in range(15):
                actions.send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(2)
            actions.release()
            
            try:
                show_more_button = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div[1]/div/div/div[1]/div[2]/div[2]/div/span')
                

                #based on num of reviews need to extract the value can be adjusted
                crawlPageNum = 5
                for i in range(0, crawlPageNum):
                    time.sleep(2)
                    try:
                        show_more_button.click()

                        for _ in range(10):
                            actions.send_keys(Keys.PAGE_DOWN).perform()
                            time.sleep(2)
                    except Exception:
                        time.sleep(1)
                actions.release()
            except Exception:
                time.sleep(1)

            
            try:
                rev_all = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div[1]/div/div/div[1]').get_attribute("innerHTML")
            except:
                rev_all = driver.find_element_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz/div/div[2]/div/div[1]/div/div/div[1]/div[2]').get_attribute("innerHTML")

            soup_expatistan = BeautifulSoup(rev_all, "html.parser")
            time.sleep(2)
            expand_pages = soup_expatistan.find_all("div", class_="d15Mdf bAhLNe")
            time.sleep(2)

            with open('newestRev_'+str(appCounter)+'.csv', mode='w') as revSenti:
                revDetails = csv.writer(revSenti, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for expand_page in expand_pages:
                    
                    ind_rev_like = expand_page.find_all("div", class_="jUL89d y92BAb")
                    temp = str(ind_rev_like).split('>')
                    temp2 = temp[1].split('<')
                    like = int(temp2[0])
                    #print(like)
                    
                    ind_rev_date = expand_page.find("span", class_="p2TkOb").text.encode('utf8')
                    #print(ind_rev_date)
                    
                    ind_rev = ""
                    # Full Review
                    ind_rev = expand_page.find('span',{'jsname': 'fbQN7e'}).text.encode('ascii', 'ignore')
                    
                    if ind_rev == "":                    
                        ind_rev =expand_page.find('span',{'jsname': 'bN97Pc'}).text.encode('ascii', 'ignore')
                    #print(ind_rev)                    

                    ind_rev_owner = expand_page.find("span", class_="X43Kjb").text.encode('utf8')
                    #print(ind_rev_owner)                    

                    num_of_star = 0
                    star_count = expand_page.find_all("div", class_="vQHuPe bUWb7c")    
                    for star in star_count:
                        num_of_star = num_of_star + 1
                    #print(num_of_star)
                    
                    #print(like, ind_rev_owner, num_of_star, ind_rev_date, ind_rev)
                    
                    csvRow = [like, ind_rev_owner, num_of_star, ind_rev_date, ind_rev]
                    revDetails.writerow(csvRow)
                    try:
                        #cursor.execute('''INSERT INTO newRevDetails(appId, revOwner, revRating, revDate, text, revLike) VALUES(%s, %s, %s, %s,%s, %s)''', (appCounter, ind_rev_owner, num_of_star, ind_rev_date, ind_rev, like))
                        #cnx.commit()
                        print("2")
                    except Error as error:
                        print(error)

                    num_of_extracted_reviews = num_of_extracted_reviews + 1
                print(num_of_extracted_reviews)
            
            #closing the csv file
            revSenti.close()
        except Exception:
            time.sleep(1)
    except Exception:
            time.sleep(1)
cnx.close()
driver.quit()
