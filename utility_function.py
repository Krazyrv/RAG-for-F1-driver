from bs4 import BeautifulSoup as bs
import requests
import os
import pandas as pd
from urllib.parse import urljoin

BASE_URL = "https://www.formula1.com"
DRIVER_URL = "en/drivers"

def get_soup(url):
    """
        This function get html text into beautiful soup format
    """
    response = requests.get(url)
    return bs(response.text, "html.parser")

def get_driver_slug(driver_html, only_name=False):
    """This function get driver slug from a list of driver

    Parameter:
    - driver_html: beautifulsoup document
    - only_name: True -> "oscar-piastri" || False -> "drivers/oscar-piastri"
    """
    driver_slug = driver_html.a["href"]
    if only_name:
        driver_slug = driver_slug.split("/")[-1]
    return driver_slug

def get_driver_slug_from_url(url):
    driver_slug = url.split("/")[-1]
    return driver_slug

def get_driver_name_from_slug(driver_slug):
    driver_name = driver_slug.replace('-', ' ').title()
    return driver_name

def get_driver_name_from_url(url):
    driver_slug = get_driver_slug_from_url(url)
    driver_name = get_driver_name_from_slug(driver_slug)
    return driver_name

def url_join(url1,url2):
    url1 = f"{url1}/"
    url = urljoin(url1,url2)
    return url




def get_drivers_url(soup_all_driver_page):
    driver_url_list = []
    all_driver_html = soup_all_driver_page.main.div.div.div.div.contents[4].contents
    for driver_html in all_driver_html:
        # print(get_driver_slug(driver_html,only_name = True))
        driver_slug = get_driver_slug(driver_html,only_name = True)
        # driver_soup = get_soup(url_join(driver_url,driver_slug))
        driver_url = url_join(BASE_URL, DRIVER_URL)
        driver_url_list.append(url_join(driver_url,driver_slug))
    return driver_url_list


def get_data_from_grid(description_list, extra_key = None):
    # print("descriptop list: ",description_list.contents)
    data = {}
    for grid in description_list.contents:
        if extra_key:
            # print(f"{grid.dt.text} of {extra_key}: {grid.dd.text}")
            data[f"{grid.dt.text} of {extra_key}"] =  grid.dd.text
        else:
            # print(f"{grid.dt.text}: {grid.dd.text}")
            data[grid.dt.text] =  grid.dd.text
    return data

def scrape_driver_statistic(driver_soup):
    """Scrape driver data from 3 grids: Order 1, Order 2, Order 3"""
    # print(driver_soup.contents[1].div.div.div.div.contents)
    driver_stat = {}
    # Scrape h3
    driver_stat['Season'] = driver_soup.contents[1].div.div.div.div.contents[0].div.div.h3.text.split(" ")[0]

    # Scrape order 1
    soup_order_1 = driver_soup.contents[1].div.div.div.div.contents[0].div.div.find_all('dl')
    for dl in soup_order_1:
        dict = get_data_from_grid(dl)
        driver_stat.update(dict)
        # print(driver_stat)

    #Scrape order 2: None data

    #Scrape order 3
    soup_order_3 = driver_soup.contents[1].div.div.div.div.contents[2].dl
    dict2 = get_data_from_grid(soup_order_3,extra_key="Career")
    driver_stat.update(dict2)
    return driver_stat

def scrape_driver_biography(driver_soup):
    """Scrape Biography of a driver"""
    biography = ""
    soup_biography = driver_soup.contents[2].div.div.div.contents[0].contents[2].contents[2]
    # Order 1
    soup_order_1 = driver_soup.contents[2].div.div.div.contents[0].contents[2].contents[0]
    # Order 2 - Quotation
    soup_order_2 = driver_soup.contents[2].div.div.div.contents[0].contents[2].contents[1]
    # Order 3 - Biography
    soup_order_2 = driver_soup.contents[2].div.div.div.contents[0].contents[2].contents[2].find_all('p')
    # print(soup_order_2)
    for p in soup_order_2:
        biography += f"{p.text}\n"
        # print(p.text)
    # print(biography)
    return {"biography": biography}

def get_news_url_page(driver_soup, page: int = None):
    """Get driver's related articles url with a number of page

    Parameter:
    - driver_soup: Soup of driver page
    - page: number of page to scrape
    
    Return:
    - List of url"""
    all_news_url = []
    soup_all_news_url = driver_soup.contents[3].find("div", class_= "flex justify-between items-center").a["href"]
    driver_news_url = url_join(BASE_URL,soup_all_news_url)
    if page:
        for i in range(0,page):
            url = driver_news_url + f"?page={i+1}"
            all_news_url.append(url)
    else:
        all_news_url.append(driver_news_url)

    return all_news_url



def get_article_url(page_soup):
    """Get list of article URLs from page"""
    url_list = []
    date_list = []
    try:
        articles_soup = page_soup.main.div.contents[1].div.div.contents[1].ul.find_all("li")#.contents

        for ar in articles_soup:
            url_list.append(url_join(BASE_URL, ar.a['href']))
            print("ARRRR: ",ar)
    except Exception as e:
        print(f"Skipping article extraction due to error: {e}")
        pass
    return url_list


# def get_article_url(page_soup):
#     """Get list of article URLs from page"""
#     url_list = []
#     try:
#         li_tags = page_soup.select("main ul li")  
#         date = page_soup.select("span.ArticleListCard-module_time__AETqA typography-module_body-2-xs-semibold__ry7FM typography-module_lg_body-xs-semibold__lGWUi")
#         for li in li_tags:
#             a_tag = li.find("a")
#             if a_tag and a_tag.get("href"):
#                 full_url = url_join(BASE_URL, a_tag["href"])
#                 url_list.append(full_url)
#     except Exception as e:
#         print(f"Skipping article extraction due to error: {e}")
#         pass
#     return url_list



def get_article_content(article_soup):
    """Scrape article Title, Overview and Content"""
    header = article_soup.main.div.contents[0].div.div.find('div',class_ = "flex flex-col gap-px-16 lg:gap-px-24 justify-between md:max-w-content-fixed-md lg:max-w-content-fixed-lg")
    title = header.h1.text
    overview = header.find("div", class_ = "flex flex-col gap-rem-12 md:gap-rem-16 lg:gap-rem-24").p.text
    # date = header.find("span", class_ = "typography-module_body-xs-regular__0B0St colors-module_colour-text-text-3__cQJVX").find("time").text
    # print("Date: ",date)
    content = ""
    content_soup = article_soup.main.div.contents[1].div.find_all("p")
    # print("LEN ", len(content_soup))
    # print("Content: ",content_soup)
    for c in content_soup:
        # content += f"{c.text}\n\n"
        content += f"{c.text}\n||\n"
    return title, overview, content

    


def scrape_articles(url):
    """Scrape article from a page"""
    article_page_list = []
    article_url_list = []
    page_soup = get_soup(url)
    articles_url = get_article_url(page_soup)

    # print("ARTICLE LIST URL: ",articles_url)
    for arr_url in articles_url:
        try:
            article_soup = get_soup(arr_url)
            article_content = get_article_content(article_soup)
            article_page_list.append(article_content)
            article_url_list.append(arr_url)
        except:
            continue
    # article_soup = get_soup(articles_url[0])
    # article = get_article_content(article_soup)

    return article_page_list, article_url_list
    # print(article_soup)
    
def scrape_driver_news(driver_soup, driver_slug):
    """Scrape article news of driver"""
    driver_news_list = []
    url_list = get_news_url_page(driver_soup,5)
    print(url_list)
    # print(url_list)
    for url in url_list:
        article_list, arr_url = scrape_articles(url)
        for (title, overview, content), url in zip(article_list,arr_url):
            driver_news = {"title": title, "url": url, "driver_slug": driver_slug, "name": get_driver_name_from_slug(driver_slug), "overview":overview, "content": content}
            driver_news_list.append(driver_news)
        # title, overview, content = scrape_articles(url_list[0])
        # print("AAA",content)
    return driver_news_list

def scrape_driver_data(driver_soup,driver_slug = "Driver"):
    """Scrape driver data: Statistic, Biography and News"""
    driver_soup = driver_soup.main.div.div.contents[1]
    driver_data = {}
    driver_data['slug'] = driver_slug
    driver_data['name'] = get_driver_name_from_slug(driver_slug)

    # Statistic Scraping
    statictic = scrape_driver_statistic(driver_soup)
    driver_data.update(statictic)

    # Biography Scraping
    biography = scrape_driver_biography(driver_soup)
    driver_data.update(biography)
    #News Scraping
    driver_news = scrape_driver_news(driver_soup, driver_slug)
    # print(driver_news)
    # print("Driver Data: ",driver_data)
    return driver_data, driver_news