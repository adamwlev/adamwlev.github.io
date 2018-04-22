import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import json

def parse_result(s):
    orig = s #works because strings are immutable
    try:
        s = s.split('Write-Ins')
        if len(s)==1:
            s = s[0]
        else:
            s = 'Write-Ins'.join(s[:-1])
        s = re.sub(r"\[\d*\]",'',s) #get rid of wiki citations
        s = s.replace('√','').strip().split('%')
        s = [[s_.split('(')[0].strip(),
              s_.split('(')[1].split(')')[0].strip(),
              float(s_.split(')')[-1])] for s_ in s
              if s_ and '[' not in s_ and 'unopposed' not in s_]
        return json.dumps(s) if s else None
    except:
        print("Couldn't Parse this: %s" % (orig,))
        return

r = requests.get('https://en.wikipedia.org/wiki/United_States_House_of_Representatives_elections,_2014')
assert r.status_code==200
soup = BeautifulSoup(r.content,'lxml')
records = []
for table in soup.find_all('table')[15:66]:
    df = pd.read_html(str(table))
    df = df[0].iloc[2:]
    for _,row in df.iterrows():
        race, results = None, None
        race = row[0]
        for value in row:
            if isinstance(value,str) and '√' in value:
                result = parse_result(value)
        records.append([race,result])    

house = pd.DataFrame(records,columns=['Race','Result'])
print(len(house))
house.dropna(inplace=True)
print(len(house))
print(house.Result.apply(len).describe())
house['Chamber'] = 'House'

r = requests.get('https://en.wikipedia.org/wiki/United_States_Senate_elections,_2014')
assert r.status_code==200
soup = BeautifulSoup(r.content,'lxml')
records = []
table = soup.find_all('table')[13]
df = pd.read_html(str(table))
df = df[0].iloc[2:-2]
for _,row in df.iterrows():
    race, results = None, None
    race = row[0]
    for value in row:
        if isinstance(value,str) and '√' in value:
            result = parse_result(value)
    records.append([race,result])

senate = pd.DataFrame(records,columns=['Race','Result'])
print(len(senate))
senate.dropna(inplace=True)
print(len(senate))
print(senate.Result.apply(len).describe())
senate['Chamber'] = 'Senate'

data = pd.concat([house,senate])
print(len(data))
print(data.Result.apply(len).describe())

data.to_csv('../data/race-metadata.csv',encoding='utf-8')
