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

2.  You need to **install the follwing required Python packages**, with your package manager (pip/conda/etc), if you don't have them already:
    - pandas
    - argparse
    - clrprint
    - configparser


# How to prepeare, execute and interact with TwitterSearch


## Preparing the configuration file

Before executing TwitterSearch, you need to make sure that configuration file settings have the proper value. These settings inside the configuration file are related to the Twitter bearer token that you received with your Twitter developer account.

Upon execution, TwitterSearch reads a configuration file containing all the settings with which the app has to be executed. Some settings may be overriden. The default configuration file (if none is provided in the command line) is *twitterSearch.conf* expected to reside in the local directory. If no configuration file is found, the app does not start execution (that's due to a bug in the way default settings -which are 'activated' when no config file is present- are handled).

You may open and edit the configuration file with your favorite text editor. The configuration is organized in named sections marked by square brackers [ ]. E.g. you may find sections [General]  [TwitterAPI] etc. Each section contains settings related to a specific part of the application. 

While a more detailed description of the available configuration settings can be found in another section, here we will describe the absolute necessary ones for executing succesfully the applications. These absolute necessary ones that need to be properly set before executing the app, are the settings related to the Twitter bearer tokens.  These settings can be found in the [TwitterAPI] section of the configuration file and are the following:

```
essentialBearer = <value of essential bearer token>
academicBearer = <value of academic bearer token>
Bearer = <value of bearer token actually used>
targetArchive = [recent | historic]
```


- `essentialBearer`: This setting is simply a place to store the essential bearer token generated by the Twitter developer account. If you got your essential bearer token, put its value in this setting. This setting is not used during requests.
- `academicBearer`: This setting is simply a place to store the academic bearer token generated by the Twitter developer account. If you got your academic bearer token, put its value in this setting. This setting is not used during requests.
- `Bearer`: The actual bearer token used in requests to the Twitter v2 endpoints. Bearer will always have a copy of the value in either the essentialBearer or the academicBearer setting.
- `targetArchive`: Specifies in which archive the search should be conducted. Take one of two values: recent or historic. Value recent means that the search will be conducted in the recent archive (i.e. tweets published in the last 5 days) while historic means that the search will be conducted on all tweets ever published since the beginning of Twitter. During startup, the application reads the value of targetArchive and sets the value of Bearer to the proper token (essential or academic bearer) in order to ensure consistency: if targetArchive has the value recent, the value of setting essentialBearer is copied to Bearer; if  targetArchive has the value historic, the value of the setting academicBearer is copied to Bearer. You may change the value of targetArchive at tuntime via the `set` command using the application's shell (see section [Supported shell commands](#supported-shell-commands) ).

In conclusion: set either the value of essentialBearer to the essential token or the value of academicBearer to the academic token that you got from your Twitter developer account (or set both). Set also the value of targetArchive to the value depending on the type of search you want to conduct (recent or historic). At least the **`essentialBearer`** and **`targetArchive`** settings  need to have a valid value/token.

I'm sorry if this sounds complicated; This needs definitely to be changed in future versions or the model needs to be redesigned.


## Running TwitterSearch

If you have prepared the configuration file, you may execute TwitterSearch using the command line or from within IDLE. From the command line, you may execute TwitterSearch as follows

```
C:\>python twitterSearch.py [-c configurationFile]
```
Argument -c specifies the *c*onfiguration file to load during startup. If no -c argument is present, TwitterSearch attempts to load the default configuration file named *twitterSearch.conf* assumed to reside in the same folder as twitterSearch.py . If no configuration file is found, TwitterSearch exists with error. This means that a configuration file is in the current version required.

From within IDLE, open the file twitterSearch.py and execute it by selecting ```Run --> Run Module``` or ```Run --> Run...Customized``` if you would like to specify the -c argument.

NOTE: this application has been developed and tested on IDLE. It has not been tested on Anaconda, Spyder or any other python IDE.

A successfull execution of TwitterSearch will display the following messages along with a prompt which is part of TwitterSearch's command shell:

```
v0.77 rd 18/03/2022
Loading configuration file [twitterSearch.conf]........OK
Target archive set to recent.

Type 'help' to see a list of supported commands.

{0}TwitterAPI v2 >>
```
The command shell of TwitterSearch allows allows users to interact with TwitterSearch and in particular to type and execute a limited set of commands (with their arguments) related to issuing queries and and downloading tweets meeting specific criteria, see the configuration settings, changing the target archive etc.

## Supported shell commands

TwitterSearch command shell supports the following commands and arguments:

- ```search [-f <datetime>] [-u datetime] [-t time step] [-o csvfile] [-n number of tweets] [-S] [-D] <query>```

The search command performs a search for tweets using the v2 API of Twitter. 


# Other related projects

- [TweetScraper](https://github.com/jonbakerfish/TweetScraper)
- [Tweepy](https://www.tweepy.org/)
- [Selenium based web scrapers](https://medium.com/@wyfok/web-scrape-twitter-by-python-selenium-part-1-b3e2db29051d)

# Acknowledgement

The code developed in this repository was based on the source code presented in the following article:
https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a
