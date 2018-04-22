from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time, sys, json, codecs
from subprocess import call
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date, timedelta  

chrome_options = Options()  
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-java')
chrome_options.add_argument('--incognito')
prefs = {"profile.managed_default_content_settings.images":2}
chrome_options.add_experimental_option("prefs",prefs)

def intify(s):
    return int(s.split(' ')[0].replace(',',''))

def make_ascii(s):
    return s.encode('ascii','ignore').decode('ascii')

def get_tweets(search_str, start_date, end_date, num_scrolls, only_english=True):
    beg = start.isoformat().replace('-0','-')
    beg = start_date.isoformat().replace('-0','-')
    end = end_date.isoformat().replace('-0','-')
    tries = 0
    while tries<=5:
        tries += 1
        try:
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.set_page_load_timeout(60)
            driver.get('https://twitter.com/search-advanced')
            time.sleep(1.3)
            driver.find_element_by_name('phrase').send_keys(search_str)
            driver.find_element_by_xpath("//select[@name='lang']/option[text()='English (English)']").click()
            driver.find_element_by_name('since').send_keys(beg)
            driver.find_element_by_name('until').send_keys(end)
            driver.find_element_by_xpath("//button[@class='EdgeButton EdgeButton--primary submit']").click()

            time.sleep(2.3)
            for _ in range(num_scrolls):
                before = len(driver.page_source)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.85)
                after = len(driver.page_source)
                if before==after:
                    break

            html_doc = driver.page_source
            driver.quit()
            soup = BeautifulSoup(html_doc,'html.parser')
            
            print('Num Tweets Found = %d' % (len(soup.find_all('div',class_="content")),))

            tweets = []

            for tweet in soup.find_all('div',class_="content"):
                text = tweet.find('div',class_="js-tweet-text-container").text
                num_replies = intify(tweet.find('span',id=lambda x: x and x.startswith("profile-tweet-action-reply-count")).text)
                num_retweets = intify(tweet.find('span',id=lambda x: x and x.startswith("profile-tweet-action-retweet-count")).text)
                num_favorites = intify(tweet.find('span',id=lambda x: x and x.startswith("profile-tweet-action-favorite-count")).text)
                tweets.append([text,num_replies,num_retweets,num_favorites])
            
            return tweets

        except Exception as e:
            print(e)
            try:
                driver.quit()
            except:
                pass
            call(['sudo','killall','chrome'])
            call(['sudo','killall','chromedriver'])
            time.sleep(2)

    return 'Made 5 attempts, all unsucessful.'

data = pd.read_csv('../data/race-metadata.csv').iloc[369:409]
election_day = date(2014,11,4)

for _,race in data.iterrows():
    tweets = {}
    race_result = json.loads(race.Result)
    for candidate,party,percentage in race_result:
        print(candidate)
        tweets[candidate] = {}
        for num_days in range(1,31):
            start = election_day - timedelta(days=num_days)
            end = start + timedelta(days=1)
            print(start,end)
            tweets[candidate][str(start)] = get_tweets(candidate,start,end,45)
            time.sleep(2.1)

    with codecs.open('../data/tweets/%s.json' % (make_ascii(race.Race).replace(' ',''),),'w','utf-8-sig') as f:
        f.write(json.dumps(tweets))
