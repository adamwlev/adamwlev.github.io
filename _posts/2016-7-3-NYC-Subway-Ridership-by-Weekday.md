---
layout: post
title: NYC Subway Ridership by Weekday
---

At Metis, our first projects is a group project. We were given an intentionally open-ended task. We were told that there was a company (WomenTechWomenYes) that wants to obtain email addresses from individuals in order to send them a free invitation to a gala. The organization wants individuals to come to the gala that are likely to contribute to the cause (monetarily or in some other fashion). The 'street teams' are to be placed outside NYC's subway stations. Our task was to find the best times and stations to place the street teams in order to acquire the best email addresses. We were told to use the [MTA Turnstile Data](http://web.mta.info/developers/turnstile.html) and any other data we'd like. This project was challenging and enjoyable, but I do not think it makes for a good blog post since there is no clean cut solution. In my opinion, analytically unsatisfying posts do not make for enjoyable reads. Instead I will craft up my own question that is relatively simple, and will produce a satisfying, objective result.

On my way to Metis this Friday morning, I noticed the 6 train, which is normally a complete zoo at 8:30 am, was relatively calm. Additionally, some of the groups in my cohort seemed to find different results for which days of the week have the most riders (which in retrospect probably had to do with considering different blocks of time). So, I'd like to get to the bottom of this. My goal is to read in some of the turnstile data, and then clean it and arrange it so that I can investigate if there is a difference in the number of subway patrons on weekday mornings during commuting time.

We want to have a big enough sample size so let's download 25 weeks of data. In order to avoid anomalies like holidays, I have selected 25 normal-seeming-holiday-free weeks from 2015 and 2016.


```python
weeks = ['151010','151024','151121','151212','151219','160109','160116','160130','160206','160213',
         '160227','160305','160312','160326','160409','160416','160430','160507','160514','160521',
         '160528','160611','160618','160625','160702']

!touch data.txt
for week in weeks:
    !curl {'http://web.mta.info/developers/data/nyct/turnstile/turnstile_%s.txt' % week} >> data.txt
```

      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100 24.1M    0 24.1M    0     0  1162k      0 --:--:--  0:00:21 --:--:-- 1202k
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100 24.1M    0 24.1M    0     0  1150k      0 --:--:--  0:00:21 --:--:-- 1242k
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
    100 24.2M    0 24.2M    0     0  1181k      0 --:--:--  0:00:20 --:--:-- 1237k
                                          .
                                          .
                                          .


Reading it in and taking a look.


```python
import pandas as pd
data = pd.read_csv('data.txt')
```


```python
data.columns = [col.strip() for col in data.columns]
```


```python
print data.shape
print data.columns.tolist()
print data.dtypes
print data.head(3)
```

    (4858536, 11)
    ['C/A', 'UNIT', 'SCP', 'STATION', 'LINENAME', 'DIVISION', 'DATE', 'TIME', 'DESC', 'ENTRIES', 'EXITS']
    C/A         object
    UNIT        object
    SCP         object
    STATION     object
    LINENAME    object
    DIVISION    object
    DATE        object
    TIME        object
    DESC        object
    ENTRIES     object
    EXITS       object
    dtype: object
        C/A  UNIT       SCP        STATION LINENAME DIVISION        DATE  \
    0  A002  R051  02-00-00  LEXINGTON AVE   NQR456      BMT  10/03/2015   
    1  A002  R051  02-00-00  LEXINGTON AVE   NQR456      BMT  10/03/2015   
    2  A002  R051  02-00-00  LEXINGTON AVE   NQR456      BMT  10/03/2015   
    
           TIME     DESC  ENTRIES    EXITS  
    0  00:00:00  REGULAR  5338884  1804026  
    1  04:00:00  REGULAR  5338909  1804032  
    2  08:00:00  REGULAR  5338930  1804068  


Time is in four hour intervals (generally). The time listed is when a particular time interval ends. Entries, and Exits are cumulative counts. C/A - Control Area - and Unit are station identifiers. SCP is a turnstile identifier. Turnstiles are the most granular level of collection. [After a little research](https://github.com/bmander/mta-station-entrance-turnstile) a teammate of mine discovered that a unit can have up to four turnstiles. So we'll be able to uniquely identify a count by a Station-Unit-SCP tuple. Control Area will not be useful for us. Neither will Linename or Division or DESC so I will drop these.


```python
data = data.drop(['C/A','LINENAME','DIVISION','DESC'],axis=1)
```


```python
data.columns.tolist()
```




    ['UNIT', 'SCP', 'STATION', 'DATE', 'TIME', 'ENTRIES', 'EXITS']



Now we want to transform the cumulative counts for entries and exits into raw number of entries and exits. We will do so on the turnstile level. First things first let's make the Date and time columns into one column with a Datetime object in it. And just quickly before I do that, I will remove all the header rows of the data.


```python
data = data.drop(data[data.DATE=='DATE'].index,axis=0)
```


```python
from datetime import datetime, date, timedelta, time
```


```python
data.insert(3,'datetime',[datetime.strptime(d+t,'%m/%d/%Y%X') for d,t in zip(data.DATE,data.TIME)])
data = data.drop(['DATE','TIME'],axis=1)
```


```python
data.head(3)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>UNIT</th>
      <th>SCP</th>
      <th>STATION</th>
      <th>datetime</th>
      <th>ENTRIES</th>
      <th>EXITS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>R051</td>
      <td>02-00-00</td>
      <td>LEXINGTON AVE</td>
      <td>2015-10-03 00:00:00</td>
      <td>5338884</td>
      <td>1804026</td>
    </tr>
    <tr>
      <th>1</th>
      <td>R051</td>
      <td>02-00-00</td>
      <td>LEXINGTON AVE</td>
      <td>2015-10-03 04:00:00</td>
      <td>5338909</td>
      <td>1804032</td>
    </tr>
    <tr>
      <th>2</th>
      <td>R051</td>
      <td>02-00-00</td>
      <td>LEXINGTON AVE</td>
      <td>2015-10-03 08:00:00</td>
      <td>5338930</td>
      <td>1804068</td>
    </tr>
  </tbody>
</table>
</div>



Now let's investigate the length of these time intervals. Since the data that I grabbed is from many different weeks and the time intervals between different weeks might be unmeaningful because I might not have grabbed the data from the next week, I will start by inserting a week column that will be the number of weeks since 10/03/2015. Then I will group by this variable in addition to Unit and SCP and do a diff operation on the datetime column.


```python
d_start = datetime.combine(date(2015,10,3), datetime.min.time())
sec_in_week = timedelta(weeks=1).total_seconds()
```


```python
data.insert(4,'week',[int((dt.to_pydatetime() - d_start).total_seconds()/sec_in_week) for dt in data.datetime])
```


```python
print len(pd.unique(data.week))
```

    25



```python
print data.week.value_counts().head()
```

    20    198884
    22    196533
    33    195729
    17    195366
    13    195361
    Name: week, dtype: int64



```python
data.insert(4,'dt_diffs',data.groupby(['UNIT','SCP','week'])['datetime'].transform(pd.Series.diff))
print data.dt_diffs.head()
```

    0                   NaT
    1   1970-01-01 04:00:00
    2   1970-01-01 04:00:00
    3   1970-01-01 04:00:00
    4   1970-01-01 04:00:00
    Name: dt_diffs, dtype: datetime64[ns]


The first value is 'NaT' which I guess stands for Not a Time. This is good. Now let's take a look at the values.


```python
print data.dt_diffs.value_counts().head()
```

    1970-01-01 04:00:00    4327446
    1970-01-01 04:12:00     260925
    1970-01-01 00:01:20       6253
    1970-01-01 08:00:00       5183
    1970-01-01 04:26:00       3859
    Name: dt_diffs, dtype: int64



```python
print (data.dt_diffs.value_counts()/len(data)).head()
```

    1970-01-01 04:00:00    0.890694
    1970-01-01 04:12:00    0.053705
    1970-01-01 00:01:20    0.001287
    1970-01-01 08:00:00    0.001067
    1970-01-01 04:26:00    0.000794
    Name: dt_diffs, dtype: float64


So, we can see that the data are messy. This is good information, but it actually should not matter for the question at hand. If we assume that the irregularities in the time intervals do not occur more or less often on any day of the week, we can just ignore this irregularity. To me this seems like a safe assumption so I will proceed under it. Now let's do a diff operation on the Cumulative entries and exits to see what this data look like.


```python
data['ENTRIES'] = pd.to_numeric(data['ENTRIES'])
data['ent_diffs'] = data.groupby(['UNIT','SCP','week'])['ENTRIES'].transform(pd.Series.diff)
```


```python
data['EXITS'] = pd.to_numeric(data['EXITS'])
data['ex_diffs'] = data.groupby(['UNIT','SCP','week'])['EXITS'].transform(pd.Series.diff)
```


```python
data.head(3)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>UNIT</th>
      <th>SCP</th>
      <th>STATION</th>
      <th>datetime</th>
      <th>dt_diffs</th>
      <th>week</th>
      <th>ENTRIES</th>
      <th>EXITS</th>
      <th>ent_diffs</th>
      <th>ex_diffs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>R051</td>
      <td>02-00-00</td>
      <td>LEXINGTON AVE</td>
      <td>2015-10-03 00:00:00</td>
      <td>NaT</td>
      <td>0</td>
      <td>5338884</td>
      <td>1804026</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>R051</td>
      <td>02-00-00</td>
      <td>LEXINGTON AVE</td>
      <td>2015-10-03 04:00:00</td>
      <td>1970-01-01 04:00:00</td>
      <td>0</td>
      <td>5338909</td>
      <td>1804032</td>
      <td>25.0</td>
      <td>6.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>R051</td>
      <td>02-00-00</td>
      <td>LEXINGTON AVE</td>
      <td>2015-10-03 08:00:00</td>
      <td>1970-01-01 04:00:00</td>
      <td>0</td>
      <td>5338930</td>
      <td>1804068</td>
      <td>21.0</td>
      <td>36.0</td>
    </tr>
  </tbody>
</table>
</div>




```python
print data.ent_diffs.sort_values()[0:10]
print data.ex_diffs.sort_values()[0:10]
```

    2758447   -2.130766e+09
    3354679   -1.961790e+09
    4036622   -1.609770e+09
    3644285   -1.424900e+09
    4427516   -1.409337e+09
    153098    -1.160589e+09
    1541412   -9.808771e+08
    1046187   -8.053204e+08
    4553424   -5.521416e+08
    4222961   -5.199925e+08
    Name: ent_diffs, dtype: float64
    2758447   -2.097170e+09
    1544178   -1.946115e+09
    3644285   -1.876058e+09
    1541412   -1.722088e+09
    4427516   -1.610668e+09
    4083737   -1.325653e+09
    1098742   -1.320534e+09
    1098320   -1.316971e+09
    1046187   -1.073768e+09
    4660685   -1.023434e+09
    Name: ex_diffs, dtype: float64


There are negative diff values for both Entries and Exits. This makes no sense. Since we can't explain these values, I say we drop them from the set so they don't effect the analysis. Again this assumes that these negative values are not meaningful and further that any meaning they have is not different between different days of the week. Personally, I think this is reasonable. Short of calling an MTA official and asking him about the negative values, there's not much else I can do.


```python
before = len(data)
data = data.drop(data[(data.ent_diffs<0) | (data.ex_diffs<0)].index, axis=0)
after = len(data)
shrinkage = float(before-after)/before * 100
print 'Data have been shrunk by %g %%' % shrinkage
```

    Data have been shrunk by 0.951608 %


Now let's look at the other end of the spectrum to make sure the largest values are reasonable.


```python
print data.ent_diffs.sort_values(ascending=False)[0:10]
print data.ex_diffs.sort_values(ascending=False)[0:10]
```

    2174315    2.122355e+09
    2883382    1.936970e+09
    3396751    1.906771e+09
    3211633    1.738040e+09
    3703613    1.717967e+09
    1848948    1.675035e+09
    319105     1.568515e+09
    3644286    1.424901e+09
    4427491    1.403818e+09
    3637648    1.289812e+09
    Name: ent_diffs, dtype: float64
    2174315    2.088919e+09
    3396751    2.022960e+09
    3897134    2.022116e+09
    1969985    2.004292e+09
    4508940    1.906299e+09
    3644286    1.876059e+09
    3703613    1.754728e+09
    4427491    1.604317e+09
    2883382    1.487318e+09
    2288245    1.342195e+09
    Name: ex_diffs, dtype: float64


Those values are definitely not reasonable. Let's just make a quick assumption that no more than 14,400 people can exit or enter per turnstile in a given interval (that's one person per second).


```python
before = len(data)
data = data.drop(data[(data.ent_diffs>14400) | (data.ex_diffs>14400)].index, axis=0)
after = len(data)
shrinkage = float(before-after)/before * 100
print 'Data have been shrunk by %g %%' % shrinkage
```

    Data have been shrunk by 0.00293001 %


Now we are getting closer and closer to what we'll consider to be clean data. As a next step let's say the measure of overall traffic is entries plus exits. Also let's add a day of the week column, and drop all the columns we won't need from the point forward.


```python
data['tot_traffic'] = data.ent_diffs + data.ex_diffs
data.insert(0,'day_of_week',[dt.weekday() for dt in data.datetime])
data = data[['datetime','week','day_of_week','tot_traffic']]
```


```python
data.head() ## 5 is for Saturday
```




<div>
<table border="3" class="dataframe">
  <thead>
    <tr style="text-align: center;">
      <th></th>
      <th>datetime</th>
      <th>week</th>
      <th>day_of_week</th>
      <th>tot_traffic</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2015-10-03 00:00:00</td>
      <td>0</td>
      <td>5</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2015-10-03 04:00:00</td>
      <td>0</td>
      <td>5</td>
      <td>31.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2015-10-03 08:00:00</td>
      <td>0</td>
      <td>5</td>
      <td>57.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2015-10-03 12:00:00</td>
      <td>0</td>
      <td>5</td>
      <td>193.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2015-10-03 16:00:00</td>
      <td>0</td>
      <td>5</td>
      <td>322.0</td>
    </tr>
  </tbody>
</table>
</div>



Now we are only concerned with the morning commute time. Remember the time listed is for when the interval ends. Now I will select only the observations that correspond to the morning commute window. At the beginning I said I was interested in the time around 8:30 am. Getting that specific with these 4(ish) hour intervals is impossible. So I will subset the data to only intervals that end between 9 am and 12 pm (inclusive). This will capture all morning commuting times.


```python
t_beg, t_end = time(9,0,0), time(12,0,0)
data.insert(1,'time',[dt.time() for dt in data.datetime])
data = data[(data.time>=t_beg) & (data.time<=t_end)]
```


```python
data.reset_index().head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>index</th>
      <th>datetime</th>
      <th>time</th>
      <th>week</th>
      <th>day_of_week</th>
      <th>tot_traffic</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>3</td>
      <td>2015-10-03 12:00:00</td>
      <td>12:00:00</td>
      <td>0</td>
      <td>5</td>
      <td>193.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>9</td>
      <td>2015-10-04 12:00:00</td>
      <td>12:00:00</td>
      <td>0</td>
      <td>6</td>
      <td>165.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>15</td>
      <td>2015-10-05 12:00:00</td>
      <td>12:00:00</td>
      <td>0</td>
      <td>0</td>
      <td>515.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>21</td>
      <td>2015-10-06 12:00:00</td>
      <td>12:00:00</td>
      <td>0</td>
      <td>1</td>
      <td>472.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>27</td>
      <td>2015-10-07 12:00:00</td>
      <td>12:00:00</td>
      <td>0</td>
      <td>2</td>
      <td>486.0</td>
    </tr>
  </tbody>
</table>
</div>



Now we are ready to drop all but week, day_of_week, and tot_traffic. Then we can group by week and day_of_week and sum tot_traffic so that we just have 175 = 25 * 7 rows, one for each observed day.


```python
data = data[['week','day_of_week','tot_traffic']]
grouped = data.groupby(['week','day_of_week'],as_index=False)
```


```python
grouped.tot_traffic.sum().head(10)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>week</th>
      <th>day_of_week</th>
      <th>tot_traffic</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>2524218.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>1</td>
      <td>2606302.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>2</td>
      <td>2684601.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>3</td>
      <td>2712457.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>4</td>
      <td>2537956.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0</td>
      <td>5</td>
      <td>883408.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0</td>
      <td>6</td>
      <td>688101.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2</td>
      <td>0</td>
      <td>2602713.0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2</td>
      <td>1</td>
      <td>2670711.0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2</td>
      <td>2</td>
      <td>2715946.0</td>
    </tr>
  </tbody>
</table>
</div>



I kept the weekends (day_of_week = 5 or 6) in up to this point just to see how the traffic values would compare to weekdays. Now we can see the weekend values are consistently about half of the weekday values. Now I'll drop the weekend values so we can just focus on the task at hand.


```python
nice_data = grouped.tot_traffic.sum()[~grouped.tot_traffic.sum().day_of_week.isin([5,6])]
```


```python
nice_data.head(10)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>week</th>
      <th>day_of_week</th>
      <th>tot_traffic</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>2524218.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>1</td>
      <td>2606302.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>2</td>
      <td>2684601.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>3</td>
      <td>2712457.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>4</td>
      <td>2537956.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2</td>
      <td>0</td>
      <td>2602713.0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2</td>
      <td>1</td>
      <td>2670711.0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2</td>
      <td>2</td>
      <td>2715946.0</td>
    </tr>
    <tr>
      <th>10</th>
      <td>2</td>
      <td>3</td>
      <td>2662762.0</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2</td>
      <td>4</td>
      <td>2596656.0</td>
    </tr>
  </tbody>
</table>
</div>



It'd be nice to make each week a row and each day of the week a column with tot_traffic in each cell. 


```python
nice_data = nice_data.pivot(index='week', columns='day_of_week', values='tot_traffic')
```


```python
nice_data.iloc[0:10]
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>day_of_week</th>
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
    </tr>
    <tr>
      <th>week</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2524218.0</td>
      <td>2606302.0</td>
      <td>2684601.0</td>
      <td>2712457.0</td>
      <td>2537956.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2602713.0</td>
      <td>2670711.0</td>
      <td>2715946.0</td>
      <td>2662762.0</td>
      <td>2596656.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2848868.0</td>
      <td>2994457.0</td>
      <td>3036015.0</td>
      <td>2959637.0</td>
      <td>2862192.0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2857451.0</td>
      <td>2992901.0</td>
      <td>2998239.0</td>
      <td>2946667.0</td>
      <td>2834486.0</td>
    </tr>
    <tr>
      <th>10</th>
      <td>2835655.0</td>
      <td>2937453.0</td>
      <td>2926121.0</td>
      <td>2905600.0</td>
      <td>2739509.0</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2696814.0</td>
      <td>2533843.0</td>
      <td>2744399.0</td>
      <td>2790644.0</td>
      <td>2620060.0</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2805843.0</td>
      <td>2807194.0</td>
      <td>2704567.0</td>
      <td>2797535.0</td>
      <td>2698391.0</td>
    </tr>
    <tr>
      <th>16</th>
      <td>2714404.0</td>
      <td>2717886.0</td>
      <td>2855564.0</td>
      <td>2648136.0</td>
      <td>2735195.0</td>
    </tr>
    <tr>
      <th>17</th>
      <td>2573940.0</td>
      <td>2998963.0</td>
      <td>2955538.0</td>
      <td>2837238.0</td>
      <td>2736329.0</td>
    </tr>
    <tr>
      <th>18</th>
      <td>2532682.0</td>
      <td>2945345.0</td>
      <td>2859865.0</td>
      <td>2765023.0</td>
      <td>2561699.0</td>
    </tr>
  </tbody>
</table>
</div>



Now we can hypothesis test whether the mean of Mondays is different from the mean of Tuesdays and mean of Wednesdays as so on. First lets visualize the data a little.


```python
import matplotlib.pyplot as plt
%matplotlib inline
```


```python
plt.figure(figsize=(12,7))
plt.boxplot([nice_data[col] for col in nice_data.columns.tolist()], showmeans=True);
plt.xticks(nice_data.columns + 1, ['Mon','Tues','Wed','Thur','Fri']);
plt.tick_params(top='off',bottom='off');
plt.ylabel('Total Number of Entries and Exits',fontsize=16);
plt.xlabel('Day of the Week',fontsize=13);
plt.title('Entries and Exits for 25 weeks Grouped by Day of Week',fontsize=14);
```


![png](/images/2016-7-3-NYC-Subway-Ridership-by-Weekday_files/2016-7-3-NYC-Subway-Ridership-by-Weekday_53_0.png)


The means are the dots and the medians are the lines. The Friday data seems to be skewed left based on one observation. Let's see which week it is just to make sure that I didn't accidentily choose a holiday.


```python
nice_data.sort_values(4).iloc[0]
```




    day_of_week
    0    2511194.0
    1    2579068.0
    2    2531054.0
    3    2485099.0
    4    1840694.0
    Name: 24, dtype: float64



'Name: 24' means that the week variable was 24 before the pivot table. Since the week variable started at 0 from 10/3/2015, we need to consider the week which is 25 weeks after 10/03/2015. This is the week ending on 3/26/2016. This seems to be a normal Friday to me.

Alright, now let's do some sort of test to see if the mean of total riders is different for Mondays versus Tuesdays versus Wednesday, etc. The Monday mean seems a little small and the Friday mean seems a little small as we saw in the graph. Here are the means as numbers:


```python
[nice_data[col].mean() for col in nice_data.columns]
```




    [2604911.36, 2693216.96, 2693120.36, 2651391.84, 2505906.6]



The means do seem to be different, but how likely is this difference to be due to random chance?

There are two different roads to investigate this. The first is this:
* Pool all the observations from all groups.
* Draw random samples without replacement of the size of the group that you are interested in.
* Keep track of how many of the means of the random samples are as different as the mean of the group.

For these data, this means drawing samples of size 25 from the population of 175 'total riders' variable and observing the distribution of means for each sample and comparing them to the means for each day of the week.


```python
import numpy as np
```


```python
def draw_samples(population,size,iters):
    means = []
    for _ in xrange(iters):
        mean = np.mean(np.random.choice(population,size,replace=False))
        means.append(mean)
    return means
```


```python
means = draw_samples(np.ravel(nice_data),25,10000)
```


```python
fig, ax = plt.subplots(figsize=(12,7))
plt.boxplot(means,whis=[.5, 99.5]);
plt.xticks([.25,.5,.75,1.33,1.66], ['Mon','Tues','Wed','Thur','Fri']);
plt.scatter([.25,.5,.75,1.33,1.66],[nice_data[col].mean() for col in nice_data.columns])
ax.set_xlim([0, 2]);
plt.ylabel('Mean of Groups/Mean of Samples',fontsize=14);
plt.xlabel('Day of the Week/Samples',fontsize=12);
plt.title('Mean Total Traffic for each Day of Week AND Means of 10,000 Samples of size 25 from All Days');
```


![png](/images/2016-7-3-NYC-Subway-Ridership-by-Weekday_files/2016-7-3-NYC-Subway-Ridership-by-Weekday_65_0.png)


I've set the whiskers of the boxplot to enclose 99% of the means. As you can see, the mean of the Fridays falls just outside this range. In this fashion, we can conclude the mean of the Friday group does not present itself in the range that encloses 99% of the means from randomly selected samples from the population of all weekdays. In other words, this indicates it's very unlikely that this big of a difference in the mean of 25 points from the population is due to chance. Not impossible, but unlikely. Exactly how likely you may ask?


```python
liklihood = float(sum(1 for mean in means if mean<nice_data[4].mean())) / len(means)
print liklihood
```

    0.0006


Now, let's do this one other way. Instead of a pool then sample method, I'll use resampling. Since I am investigating the difference in each day of the week's ridership to the average weekday, I'll use this strategy:

* Subtract the week's average ridership from each group's observed ridership.
* Resample each of the 25 groups with replacement.
* Observe the distributions.


```python
minus_the_mean = pd.DataFrame(nice_data.values - np.array([[mean] for mean in nice_data.mean(1)]))
```


```python
minus_the_mean.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-88888.8</td>
      <td>-6804.8</td>
      <td>71494.2</td>
      <td>99350.2</td>
      <td>-75150.8</td>
    </tr>
    <tr>
      <th>1</th>
      <td>-47044.6</td>
      <td>20953.4</td>
      <td>66188.4</td>
      <td>13004.4</td>
      <td>-53101.6</td>
    </tr>
    <tr>
      <th>2</th>
      <td>-91365.8</td>
      <td>54223.2</td>
      <td>95781.2</td>
      <td>19403.2</td>
      <td>-78041.8</td>
    </tr>
    <tr>
      <th>3</th>
      <td>-68497.8</td>
      <td>66952.2</td>
      <td>72290.2</td>
      <td>20718.2</td>
      <td>-91462.8</td>
    </tr>
    <tr>
      <th>4</th>
      <td>-33212.6</td>
      <td>68585.4</td>
      <td>57253.4</td>
      <td>36732.4</td>
      <td>-129358.6</td>
    </tr>
  </tbody>
</table>
</div>




```python
def resample(sample,iters):
    means = []
    for _ in xrange(iters):
        mean = np.mean(np.random.choice(sample,len(sample),replace=True))
        means.append(mean)
    return means
```


```python
fig, ax = plt.subplots(figsize=(12,7));
plt.boxplot([resample(minus_the_mean[col],10000) for col in range(5)],whis=[.5, 99.5]);
plt.axhline(0,ls='--',color='black')
plt.xticks(range(1,6), ['Mon','Tues','Wed','Thur','Fri']);
plt.ylabel("Observed Ridership Minus Week's Average Ridership",fontsize=14);
plt.xlabel('Day of the Week',fontsize=12);
plt.title('Resampled Distribution of Means of Observed Ridership Minus Average Ridership Across Week');
```


![png](/images/2016-7-3-NYC-Subway-Ridership-by-Weekday_files/2016-7-3-NYC-Subway-Ridership-by-Weekday_72_0.png)


From this method, we can say definitively that the number of Riders on Fridays is different than the average number of riders during the week as a whole. There is an indication that Monday's might be below average but we can't say for sure.
