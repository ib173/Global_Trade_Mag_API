import time
from time import strptime
from six.moves import urllib
import requests
from bs4 import BeautifulSoup
from config import LAST_ACCESS, post_article
from process_image import process_and_post


def GTM_update():
    response = collect(get_recent_articles())
    print(response)

def get_recent_articles():
    address = "http://www.globaltrademag.com/global-trade-daily/"
    request = urllib.request.Request(address, None, {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'})
    urlfile = urllib.request.urlopen(request)
    page = urlfile.read()
    soup = BeautifulSoup(page, 'html.parser')
    links = []
    main_article_link = soup.find_all('article') # fix this, need to add the main article to links
    data = soup.findAll('div',attrs={'class':'category-article'})
    for div in data:
        temp_links = div.findAll('a')
        for pot_link in temp_links:
            try:
                links.append(pot_link.get('href'))
            except:
                pass
    links = filter_unwanted_urls(links)
    print(links)
    # print('links: ', links)
    return links

def collect(weblinks):
    pagelinks = weblinks
    title = []
    thearticle = []

    for link in pagelinks[:1]:
        paragraphtext = []
        url = link
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        # date published
        date_published = soup.find(class_="updated").get_text().replace(',', '')
        if LAST_ACCESS in date_published:
            print('**********finished update**************')
            return "finished update"
        # author name
        try:
            aname = soup.find(itemprop='author').get_text()[1:]
        except:
            aname = 'Global Trade Mag'

        # article title
        title = soup.find('h1', class_='entry-title').get_text()

        # image link
        image = []
        for img_link in soup.find_all(class_='banner'):
            if img_link.img:
                image.append(img_link.img['src'])
        main_img = image[0]

        # Unix date accessed
        unix_access = time.time()

        # article text
        paragraphtext = []
        article = ''
        articlesoup = soup.find(itemprop='articleBody')
        articletext = articlesoup.find_all('p')
        for paragraph in articletext[:-1]:
            text = paragraph.get_text()
            paragraphtext.append(text)
            # thearticle.append(paragraphtext)

        # print(paragraphtext)

        for paragraph in paragraphtext:
            # print(paragraph)
            article += (paragraph + '</br>')

        # article summary
        summary = article[0:155] + '...'

        final_date = format_publish_date(date_published, LAST_ACCESS[-4:])
        guid = process_and_post(main_img)
        post_article(aname, final_date, title, article, summary, guid)
        return "updated: __article_count____"


def filter_unwanted_urls(urls):
    cleaned_urls = []
    for url in urls:
        if url is not None:
            if not all(['webcache' in url, 'search' in url, 'youtube' in url, url == '', url == '#']):
                cleaned_urls.append(url)
    cleaned_urls = set(cleaned_urls)
    cleaned_urls = list(cleaned_urls)
    return cleaned_urls

def format_publish_date(date, year):
    month = str(strptime(date[0:3],'%b').tm_mon)
    day = date[-9:][0:2]
    postfix = "T00:00:00+02:00"
    if len(str(day)) == 1:
        day = '0' + day
    if len(str(month)) == 1:
        month = '0' + str(month)
    final_date = year + '-' + month + '-' + day + postfix
    return final_date

GTM_update()
