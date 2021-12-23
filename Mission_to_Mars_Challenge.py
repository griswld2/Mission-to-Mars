#Import packages
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from urllib.request import urlopen
import requests

# Set up Splinter
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)

# Visit the mars nasa news site
url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

#BS4 Soup
html = requests.get(url)
soup = BeautifulSoup(html.content, 'html.parser')

#URL List
url_list = []
deduped_url_list = []

for a in soup.find_all('a', {'class':'itemLink product-item'}):
    x = (a.get('href'))
    #print(x)
    url_list.append('https://astrogeology.usgs.gov' + x)

#browser.quit()

for x in url_list:
    if x not in deduped_url_list:
        deduped_url_list.append(x)
        
deduped_url_list

images = []
titles = []
mars_image_urls = []
for url in deduped_url_list:
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # Scrape each page for the relative image path
    results = soup.find_all('img', class_='wide-image')
    relative_img_path = results[0]['src']

    img_link = 'https://astrogeology.usgs.gov' + relative_img_path
    result = soup.select('h2.title')[0].text.strip()

    mars = {}
    mars['img_url'] = img_link
    mars['title'] = result
    mars_image_urls.append(mars)

mars_image_urls

