# TwitterSearch
 
A simple python program to demonstrate searching and downloading of Twitter tweets using v2 of the Twitter API. Experimental.
I may have been taken away and have overengineered some aspects. 
Any bug or design error that you may see is exclusively my fault. Have mercy.



# Prerequisites

In order to succesfully execute the application, the following is required:

1.  A **Twitter bearer token**. You can get a free (essential) bearer token by creating a Twitter developer account which is also free. Instructions on how to create a Twitter developer account can be found here https://developer.twitter.com/en/support/twitter-api/developer-account . 
The Twitter bearer token is a unique string value that identifies your application and is required to be sent along with any request the application does to any v2 Twitter API endpoint e.g. for querying tweets. Twitter offers 3 different types of bearer tokens (this might be a little bit outdated and needs to be rechecked) each of which allows for different things, mainly related to the number of tweets that can be downloaded per month :

    - *Essential bearer token*: This bearer token is the default token that anyone gets freely, when opening a Twitter developer account. See here https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens on how to generate a (free) essential bearer token for your application. An essential token allows the application to download tweets only from the recent archive (i.e. tweets published up until 5 days earlier and not earlier) and allows downloading a total of 500000 tweets per month. You may see how your much of your monthly allowances you have spend by visiting the dashboard on your Twitter developer account. Once you have reached the limit of 500000 dwonloaded tweets, you won't be able to download any more for the rest of the month. This limit resets automatically every month (from the date you generated the token). For example if you generated the token on March 21 and until March 25 you have already downloaded the 500000 tweets, you'll be able to download tweets agan (500000) on April 21st. As already said, this is done automatically.
    - *Academic bearer token*: This bearer token allows doanloading up to 10000000 tweets per month and has no datetime limit on tweets i.e. you may search for tweets as long back in time as you like (this bearer searches also the recent archive).  Here too, the limit is automatically reset each month. To obtain an academic bearer token, you have to issue a special application which asks mainly about your cv and the purpose. The application is reviewed by TWitter and a response is given (not immediately though).
    - *Commercial bearer token*: I'm not knowledgeable enough to talk about this kind of bearer token. I've seen it mentioned but i do not know what it allows you to do.
  
    Once you have a valid bearer token, you need to add it to the application's configuration file twitterSearch.conf  (yes, i know it's very bad practice but i'm a uni professor and we a known to do things sloppy or as someone famously said *"Re 2: your job is being a professor and researcher: That's one hell of a good excuse for some of the brain-damages of minix. I can only hope (and assume) that Amoeba doesn't suck like minix does."* See https://www.oreilly.com/openbook/opensources/book/appa.html) . See blow where exactly to put the bearer value you have.

<br/>
<br/>

2.  You need to **install the follwing required Python packages**, with your prefered package manager (pip/conda/etc), if you don't have them already:
    - pandas
    - argparse
    - clrprint
    - configparser



the program to search and fetch tweets properly, you need to create a Twitter developer account and get an access and bearer token. You may get a Twitter developer account and tokens for free using the instructions listed here: https://developer.twitter.com/en/support/twitter-api/developer-account . Once you got the tokens, you should add them to the configuration file as described in secton How to run.

# Other related projects

- [TweetScraper](https://github.com/jonbakerfish/TweetScraper)
- [Tweepy](https://www.tweepy.org/)
- [Selenium based web scrapers](https://medium.com/@wyfok/web-scrape-twitter-by-python-selenium-part-1-b3e2db29051d)

# Acknowledgement

The code developed in this repository was based on the source code presented in the following article:
https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a
