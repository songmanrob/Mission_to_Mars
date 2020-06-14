# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

def scrape_all():
    # Set the executable path and initialize the chrome browser in splinter
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path)

    news_title, news_p = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "mars_hemispheres": mars_hemi(browser),
        "last_modified": dt.datetime.now()
    }

    browser.quit()

    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    # add try/except block for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None


    return news_title, news_p


# ### Featured Images
def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    #add try-except block for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

        # Use the base URL to create an absolute URL
        img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    except AttributeError:
        return None

    return img_url

def mars_facts():
    try:
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    return df.to_html()

def mars_hemi(browser):
    # Visit URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    html = browser.html
    hemi_soup = BeautifulSoup(html, 'html.parser')

    #add try-except block for error handling
    try:
        # Find the relative image url
        enhanced_imgs = [link.get('href') for link in hemi_soup.find_all('a', class_='itemLink product-item')]
        enhanced_imgs_unique = pd.unique(enhanced_imgs)
        img_list = enhanced_imgs_unique.tolist()

        # Use the base URL to create an absolute URL
        hemi_1 = f'https://astrogeology.usgs.gov{img_list[0]}'
        hemi_2 = f'https://astrogeology.usgs.gov{img_list[1]}'
        hemi_3 = f'https://astrogeology.usgs.gov{img_list[2]}'
        hemi_4 = f'https://astrogeology.usgs.gov{img_list[3]}'

        hemi_title_1 = hemi_soup.find_all('h3')[0].get_text()
        hemi_title_2 = hemi_soup.find_all('h3')[1].get_text()
        hemi_title_3 = hemi_soup.find_all('h3')[2].get_text()
        hemi_title_4 = hemi_soup.find_all('h3')[3].get_text()

        hemi_dict_1 = {'img_url': hemi_1,'title': hemi_title_1}
        hemi_dict_2 = {'img_url': hemi_2,'title': hemi_title_2}
        hemi_dict_3 = {'img_url': hemi_3,'title': hemi_title_3}
        hemi_dict_4 = {'img_url': hemi_4,'title': hemi_title_4}
        hemi_list = [hemi_dict_1, hemi_dict_2, hemi_dict_3, hemi_dict_4]

    except AttributeError:
        return None

    return hemi_list


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())