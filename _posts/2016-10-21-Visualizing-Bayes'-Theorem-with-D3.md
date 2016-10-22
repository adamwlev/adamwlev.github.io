
---
layout: post
title: Visualizing Bayes' Theorem with D3
excerpt: Visualize a Bayesian update of a Normal Random Variable.
---

I have been interested in getting better at Bayesian statistics recently. For my Ranking PGA Tour golfers project, I have been looking at Approximate Bayes' Computation. This involves discretizing a probabilility distribution and updating the distribution according to data observed and a liklihood function. [Here](http://stats.stackexchange.com/questions/237862/bayesian-update-for-two-normal-random-variables-following-one-observation-of-dif) is a discussion I had online which leads me to the ABC approach.

In the process of playing around with updating normal distributions, I was really enjoying visualizing the updating process. I also wanted to keep practicing developing visualizations with D3 after learning the basics at [Metis](http://www.thisismetis.com/).

For this project, I actually did the computations properly. Instead of resorting to discretizing the distribution, I have a user set a prior and then I follow the conjugate-prior updating steps. The conjugate prior distribution for a normal random variable with unknown mean and variance is a Normal-Gamma (or equivelently a Normal-Inverse-Gamma). The user specifies the expected mean, a precision on this estimate, the expected standard deviation, and the precision on this estimate (unbeknownst to the user, the presision on the standard deviation is actually the precision on the variance; this is a minor technical detail). [This](http://webuser.bus.umich.edu/plenk/Bam2%20Short.pdf) resourse was really helpful.

I learned a lot of D3 with this project. I was originally going to make this a Flask app and carry out the computations in Python. However, I realized that D3 is capable of doing this sort of math! This was a fun exersize in learning the limits of D3's computational ability. The one consequence that I notice is that the memory cost starts to effect D3's ability to render smoothly - you can see this if you scale the number of points up to 100.

[Here](https://bayes-app.herokuapp.com/) is the app deployed with Heroku and [here](https://github.com/adamwlev/Bayes-App) is the code for the project.

As always, if anyone has feedback for improvements, please comment below!