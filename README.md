# Santa Barbara County COVID-19 Dashboard - Project Overview
* Wrote a Python script to scrape COVID-19 data from the Santa Barbara County Public Health [website](https://publichealthsbc.org/status-reports/) using BeautifulSoup   
* Set up a task to run this script daily to collect up to date data
* Built an interactive web app using Dash to visualize trends in Santa Barbara County COVID-19 data
* Deployed the app on an AWS EC2 instance so it can be accessed here: http://3.14.7.137:8050/  

# Packages Used and Sources Referenced     
**Python Version:** 3.7      
**Packages:**         
* **Web Scraping:** bs4, requests, os    
* **Data Cleaning:** pandas, numpy   
* **Creating Visualizations & Building Web App:** plotly, dash   
* **To Install Requirements to Run Web App:** `pip install -r requirements.txt`

**Sources Referenced:**      
* Dash [Styleguide](https://codepen.io/chriddyp/pen/dZVMbK)     
* [Dash Tutorial](https://www.datacamp.com/community/tutorials/learn-build-dash-python?utm_source=adwords_ppc&utm_campaignid=1565261270&utm_adgroupid=67750485268&utm_device=c&utm_keyword=&utm_matchtype=b&utm_network=g&utm_adpostion=&utm_creative=295208661496&utm_targetid=aud-299261629574:dsa-429603003980&utm_loc_interest_ms=&utm_loc_physical_ms=9031645&gclid=CjwKCAjwtNf6BRAwEiwAkt6UQlSmdbDhLHLgdjL4i0Zk2yoxg0N_5PAFsVQP1uH4GTCaTbDS0i2jnBoCW6gQAvD_BwE) on Data Camp   
* Dash [Documentation](https://dash.plotly.com/)    
* [Article](https://codeburst.io/50-shades-of-dark-mode-gray-d3e9907b1194) on dark mode color schemes     

## Static Image of Dashboard
<img src="https://github.com/bryandaetz1/SB_County_COVID-19_Data/blob/master/Images/dashboard.png" alt="dashboard_example" width = "900"/>
