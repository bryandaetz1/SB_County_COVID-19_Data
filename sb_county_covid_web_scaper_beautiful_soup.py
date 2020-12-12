# -*- coding: utf-8 -*-
"""
Created on Sun Sep 20 13:58:41 2020

@author: bdaet
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import os

#set working directory to folder with chrome driver (necessary to run script as a task)
os.chdir('C:/Users/bdaet/OneDrive/Documents/Data Science/SB_County_Public_Health')

#specify URL/web page to scrape
url = 'https://publichealthsbc.org/status-reports/'

#create user-agent (Windows 10 with Google Chrome)
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '\
'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.03987.149 '\
'Safara/537.36'

headers = {'User-Agent': user_agent}

response = requests.get(url, headers = headers).text

#parse the HTML from the URL into the BeautifulSoup parse tree format
soup = BeautifulSoup(response, 'html.parser')

#date data was posted
dates = soup.find_all('a',{'class':'elementor-accordion-title'}) #not sure why this isn't working

#getting the element for each historical date where covid data was posted
items = soup.find_all('div',{'class':'elementor-accordion-item'})

#iterating through available data for each date
master_list = []    #master list with all tables for each date
date_list = []      #list to store dates where data is available
index = -1
while dates[index + 1].text.strip() != 'July 7, 2020':      #getting error for dates prior to July 8: 6 columns passed, passed data had 5 columns
    index = index + 1                                       #found this is because prior to July 8, there were only 5 columns in that table (no Still Infectious by Region column)
    
    tables = items[index].find_all('table')
    if tables == []:    #some dates didn't have data available, including this condition to skip those dates
        continue
    else:
        date_list.append(dates[index].text.strip())
        item_list = []      #list of tables for each date where data was available
        for table in tables:
            rows = table.find_all('tr')
            table_list = []     #list of rows in table
            for row in rows:
                contents = row.find_all('td')
                row_list = []   #list of data in each row
                for content in contents:
                    row_list.append(content.text)
                table_list.append(row_list) 
            item_list.append(table_list)
        master_list.append(item_list)
        
          
        
#x is the index of the table to create a dataframe from
def create_df(x):
    columns = master_list[0][x][0]
    df = pd.DataFrame(master_list[0][x][1:], columns = columns)
    df['Date'] = [date_list[0]] * len(df)
    for i in range(len(master_list)):
        if i == 0:
            continue
        else:
            temp_df = pd.DataFrame(master_list[i][x][1:], columns = columns)
            temp_df['Date'] = [date_list[i]] * len(temp_df)
            df = pd.concat([df, temp_df], axis = 0, sort = False)   
    return df   

#after Dec. 9th, the SB county public health website added another table before ethnicity, which broke the orginal create_df function
def create_ethnicity_df():
    columns = master_list[0][10][0]
    df = pd.DataFrame(master_list[0][10][1:], columns = columns)
    df['Date'] = [date_list[0]] * len(df)
    
    switch = date_list.index('December 9, 2020')    #getting index where table format switches
    for i in range(len(master_list)):
        if i == 0:
            continue
        elif i <= switch:
            temp_df = pd.DataFrame(master_list[i][10][1:], columns = columns)
            temp_df['Date'] = [date_list[i]] * len(temp_df)
            df = pd.concat([df, temp_df], axis = 0, sort = False)
        else:
            temp_df = pd.DataFrame(master_list[i][9][1:], columns = columns)
            temp_df['Date'] = [date_list[i]] * len(temp_df)
            df = pd.concat([df, temp_df], axis = 0, sort = False)
        
    return df   
            

#creating dataframe for cases by area tables, currently cases_by_area is the only csv file being used for the web app        
cases_by_area = create_df(0)
cases_by_area.replace({'—':np.nan}, inplace = True)
cases_by_area.to_csv('cases_by_area.csv', index = False)

#creating dataframe for recovery status tables
recovery_status = create_df(1)
recovery_status.replace({'—':np.nan}, inplace = True)
recovery_status.to_csv('recovery_status.csv', index = False)

#creating dataframe for cases by age tables
cases_by_age = create_df(3)
cases_by_age.replace({'—':np.nan}, inplace = True)
cases_by_age.to_csv('cases_by_age.csv', index = False)

#creating dataframe for cases by gender tables
cases_by_gender = create_df(4)
cases_by_gender.replace({'—':np.nan}, inplace = True)
cases_by_gender.to_csv('cases_by_gender.csv', index = False)

#creating dataframe for testing status tables
testing_status = create_df(6)
testing_status.replace({'—':np.nan}, inplace = True)
testing_status.to_csv('testing_status.csv', index = False)

#creating dataframe for transmission method tables
transmission_method = create_df(7)
transmission_method.replace({'—':np.nan}, inplace = True)
transmission_method.to_csv('transmission_method.csv', index = False)

#creating dataframe for cases by race/ethnicity tables
ethnicity = create_ethnicity_df()
ethnicity.replace({'—':np.nan}, inplace = True)
ethnicity.to_csv('ethnicity.csv', index = False)