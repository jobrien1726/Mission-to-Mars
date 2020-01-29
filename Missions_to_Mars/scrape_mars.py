from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests

#Set up path to chromedriver
def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    # Visit NASA Mars News Site
    news_url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(news_url)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # Collect the latest News Title and Paragraph Text
    news_title = soup.find("div", class_= "content_title").a.text

    news_p = soup.find("div", class_= "article_teaser_body").text

    # Visit page w Featured Space Image
    space_img_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(space_img_url)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # Find the image url for the current Featured Mars Image
    base_url = "https://www.jpl.nasa.gov/"
    image_url = soup.find("a", class_= "button fancybox")["data-fancybox-href"]

    featured_image_url = base_url + image_url

    # Visit Twitter for Mars weather tweet, use requests to scrape info
    twitter_url = "https://twitter.com/marswxreport?lang=en"

    response = requests.get(twitter_url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(response.text, 'html.parser')

    mars_weather = soup.find("p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text

    # Visit Space Facts page for Mars Facts Table
    facts_url = "https://space-facts.com/mars/"

    # Use read_html to scrape table from Space Facts site
    mars_facts = pd.read_html(facts_url)

    # Save table as a pandas dataframe, rename columns and set index
    mars_facts_df = mars_facts[0]
    mars_facts_df = mars_facts_df.rename(columns={0:"planet_metrics", 1:"mars"})
    mars_facts_df.set_index("planet_metrics", inplace=True)

    # Convert dataframe to html table string
    mars_html_table = mars_facts_df.to_html()

    # Visit Mars Hemispheres Page
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    #Find all hemisphere titles
    results = soup.find_all("div", class_="description")

    #Create a list of all the Hemisphere Titles from the first page
    hemi_titles = []

    for result in results:
        hemi_title = result.h3.text
        hemi_titles.append(hemi_title)

    #Base url to be used later for full image url
    base_img_url = "https://astrogeology.usgs.gov"

    # Find image urls for each hemisphere
    hemi_img_urls = []

    for title in hemi_titles:
        # Format to put into url
        title = title.lower().replace(" hemisphere ", "_")
    
        # Navigate to page for each Hemisphere
        indiv_pg_url = f"https://astrogeology.usgs.gov/search/map/Mars/Viking/{title}"
        browser.visit(indiv_pg_url)

        # Scrape page into Soup
        html = browser.html
        soup = bs(html, "html.parser")

        # Find full size image url
        img_url = soup.find("img", class_="wide-image")["src"]

        full_img_url = base_img_url + img_url
        
        # Append image url to list of hemisphere image urls
        hemi_img_urls.append(full_img_url)

    # Save hemisphere titles and image urls to a dictionary
    hemisphere_image_urls = []

    for x in range(4):
        hemi_img_dict = {"title": hemi_titles[x], "img_url": hemi_img_urls[x]}
        hemisphere_image_urls.append(hemi_img_dict)

    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_p_text": news_p,
        "featured_image": featured_image_url,
        "mars_weather": mars_weather,
        "mars_facts_table": mars_html_table,
        "hemi_images": hemisphere_image_urls
    }
    
    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data



