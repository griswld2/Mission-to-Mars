#Import Packages
from splinter import Browser
from flask import Flask, render_template, redirect, url_for
from flask_pymongo import PyMongo
from bs4 import BeautifulSoup
from urllib.request import urlopen
from webdriver_manager.chrome import ChromeDriverManager
import requests
import datetime as dt
import pandas as pd

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    image_titles = mars_hemisphere_images(browser)
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        'img_url_titles': image_titles,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemisphere_images(browser):
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
    
    return mars_image_urls

if __name__ == "__main__":
    print(scrape_all())