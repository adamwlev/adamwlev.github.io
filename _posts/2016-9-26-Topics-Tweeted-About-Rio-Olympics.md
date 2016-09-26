---
layout: post
title: Topics Tweeted About the Rio Olympics
excerpt: My process of employing unsupervised learning techniques to summarize the topics tweeted about the Rio Olympics.
---

For our fourth project at the Metis Data Science Bootcamp, we use Natural Language Processing and Unsupervised Learning techniques to extract meaning from text data. We had 11 days to conceive of an idea, collect data, clean data, perform analysis and create a front-end to display the work.

I enjoyed this project because I learned a lot about data pipelining, unsupervised learning techniques, and front-end development with Flask and Python. These were topics that I was not as familiar with compared to other topics in Data Science; supervised learning was what I was most familiar with and I had never done any front-end development.

At the time of the assignment of this project, the Rio Olympics were going on. My motivation for this project was to learn more about what was happening in the more obscure events in the Olympics - Table Tennis is a personal favorite. To do this I gathered Tweets about all the different events going on using the Twitter Streaming API, stored the data in MongoDB on an EC2 instance, cleaned the data using NLTK in Python, used the LDA function in scikit-learn to do topic modeling, and built a Flask app to display the work and deployed it using Heroku.

## Collecting the Data

I used the Twitter Streaming API to collect the data. There are 42 different Olympic Events and I wanted tweets about each one of them. I knew that eventually I wanted to do topic modeling on each sport individually so that every sport, even the more obscure ones, was on equal footing.

The way I achieved this was by setting up one large stream that had the following search criteria:

The tweet had to have the exact title of one of the 42 different sports AND the word "olympic" or the word "olympics" (case insensitive see [here](https://dev.twitter.com/streaming/overview/request-parameters) for more details). This amounted to 84 different queries joined with ORs, which, amazingly, the Twitter API handled with ease.

Then I put the tweets into categories according to whether they had the exact title of each sport.

A couple issues resulted from this strategy:

* Some sports have *long* names like "cycling mountain bike" or "gymnastics artistic" which people are fairly unlikely to tweet in their entirety without spelling errors in addition to including the word "olympics" or "olympic". I kept these long names because I wanted to find the topics for each of the 42 sports individually which necessitated distinguishing between events like "gymnastics artistic" and "gymnastics rythmic". This resulted in few tweets for these sports.
* Some tweets, while they had the name of a sport in them along with "olympic" or "olympics", were not necessarily about the sport in question. "Football" is one example. "football" is the name of an Olympic event (American Soccer) but there were a fair amount of tweets that included "football" and "olympic" or "olympics" but were really about the start of the US Football season.

Nevertheless, I was able to collect over a million tweets using the streaming API, categorize them, and store them all in a MongoDB database.

## Text Processing

I used Python and the NLTK package to cleanse each tweet of links, mentions, "RT"s, "#"s, and to lemmatize each word. This cleaning took a tweet that looked like this:

```u'RT @qz: Uh-oh, looks like we jinxed the Olympic water polo pool https://t.co/MMe3rqR8tK #olympicpool'```,

and made it look like this: 

```'uh-oh, look like we jinx the olympic water polo pool olympicpool'```.

Then, to further prepare the text for downstream bag-of-words modeling, I spent a lot of time creating a custom lists of stop words. I created a general list of stop words that contained words like "rio2016", "watch" and "live". These words were too prevalent in the Tweets and would get in the way of obtaining interesting results using clustering and topic modeling techniques.

Also I made stop word lists for each event. For example, for "equestrian jumping" my stop words were "equestrian", "jumping", "jump", and "horse". These decisions were informed by clustering the words using K-Means to see if there were words that were occuring in many different clusters.

## Topic Modeling

I started by using Tf-idf Vectorizer and mini-batch K-Means to do clustering of topics and that worked fairly well. Then I tried LDA. Addmitedly, I went with LDA because it is a fancier method. In retrospect, K-Means was equally effective and has advantages such as computational cost.

My biggest challenge with this process was choosing the correct number of clusters/topics. Since I was doing 42 seperate topic models, manually inspecting the results in order to choose the most correct seeming number of topics was impossible. The weekend after I completed the project, I looked into automated methods for choosing the number of clusters in K-means and learned about the Gap Statistic. This would have been a good choice.

Instead, I ended up using LDA and scaling the number of topics with the number of documents in each sport. With LDA, one can optimize the number of topics by choose the number that minimizes Perplexity. This method seems sound in theory, but in practice it is expensive to do with so many different models and [some people](http://qpleple.com/perplexity-to-evaluate-topic-models/) are not sold on it's effectiveness.

For purposes of displaying the work, I went through each model and selected the top two or three most coherent topics and selected one Tweet that was the most representative of each topic.

## Building an App

I used Flask to build a simple App that let's the user pick a sport he or she would like to see the topics for and then displays the topics. You can find the app deployed [here](https://twitter-olympics-topics.herokuapp.com/).

This process was challenging for someone who has little experience with front-end development. It took a lot of persistancy on my part and help from some of my classmates who were more versed in HTML and CSS.

## Conclusion

I learned a lot during this two week project and am grateful for the experience. In the future, if I encounter MongoDB, unsupervised learning, or Flask related problems, I will draw from my experience with this project.

You can find a repo with all the code for this project [here](https://github.com/adamwlev/Twitter-Topic-Modeling). Thank you for reading.




