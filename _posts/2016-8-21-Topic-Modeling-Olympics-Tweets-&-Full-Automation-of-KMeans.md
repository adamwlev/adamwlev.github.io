---
layout: post
title: Topic Modeling Olympics Tweets & Full Automation of KMeans
excerpt: Choosing K in KMeans or the number of topics in LDA giving you a headache? Not to worry. There are solutions.
---

At the Metis Data Science Bootcamp, our fourth project was an unsupervised, Natural Language Processing assignment. We were to choose any topic we wanted as long as it dealt with text data and was an unsupervised problem.

For those unfamiliar with what unsupervised means in Machine Learning, I will quickly explain. Basically, instead a predicting or explaining a known outcome present in data, the task is to find structure in data and possibly assign labels to groups of observations.

Within NLP, one of the most useful unsupervised problems is summarization. Computers can aid humans if they can boil large quantities of text down to a few main topics, with keywords or crucial snippets of text representing each topic.

For my project, I chose to summarize tweets about the Rio Olympics. I gathered tweets both by interacting with Twitter's streaming API, and by scraping their search engine. I cleaned the tweets and organized them by sport. In total there are 41 Olympic sports and my goal was to model topics for each sport.

I gathered around 1 million tweets overall. However, some sports (Rhythmic Gymnastics, for example) were hard to find many tweets about. I ended up using sklearn's new implementation of Latent Dirichlet Allocation to model the topics and made a [flask app](https://twitter-olympics-topics.herokuapp.com) to display the top topics for each sport.

With this post I want to discuss a common issue with topic modeling and Unsupervised Learning in general - picking the number of topics. First I'll talk about the problem in the case of choosing the best K in KMeans, and then I'll mention a similiar strategy that could work for the number of topics in LDA.

Currently, this is a very challenging practical issue for anyone having to do this type of modeling. With some problems it might be feasible to manually inspect the resulting topics or clusters and access how well the model did. However, if one has to do many seperate topic models, this can quickly become unreasonable to take on manually.

With text data especially, it can be painstaking and bewildering to try to access how well a model has done. Not to worry however - after some research and thinking on the topic, it is my opinion that soon there will be an agreed upon method of choosing the number of clusters in KMeans or number of topics in LDA.

I will show two solutions to the problem with regard to KMeans clustering - the first is sort of a hack and still not fully automated, then the second is the more principled, more widley accepted way of accomplishing this task and is fully automated. Then I will propose a similiar in spirit method to apply to LDA.

## The AIC Elbow-Curve Method

The goal of clustering in general is to group like observations together. With KMeans the clusters are defined by K centroids that represent the center of a cluster. Which cluster an observation is assigned depends on which centroid it is closest to. If the model is doing well, all the points are very close to their respective clusters. Thus, an natural way of accessing the performance of the model, is the sum of the squared distances between the observations and the representative centroid:

![](https://raw.githubusercontent.com/adamwlev/adamwlev.github.io/master/images/OlympicKMeans/pic.gif)



  
