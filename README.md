# TwitterSearch
 
A simple python program to query and fetch tweets using using the [v2 of the Twitter API](https://developer.twitter.com/en/support/twitter-api/v2). The sole puprose is experiment with and get to know Twitter's v2 API. 

This is experimental and has been created hastily. Has not been tested thoroughly. Any bug or design error that you may see is exclusively my fault. Have mercy.



# Prerequisites

In order to succesfully execute the application, the following is required:

1.  A **Twitter bearer token**. You can get a free (essential) bearer token by creating a Twitter developer account which is also free. Instructions on how to create a Twitter developer account can be found here https://developer.twitter.com/en/support/twitter-api/developer-account . 
The Twitter bearer token is a unique string value that identifies your application and is required to be sent along with any request the application does to any v2 Twitter API endpoint e.g. for querying tweets. Twitter offers 3 different types of bearer tokens (this might be a little bit outdated and needs to be rechecked) each of which allows for different things, mainly related to the number of tweets that can be downloaded per month :

    - *Essential bearer token*: This bearer token is the default token that anyone gets freely, when opening a Twitter developer account. See here https://developer.twitter.com/en/docs/authentication/oauth-2-0/bearer-tokens on how to generate a (free) essential bearer token for your application. An essential token allows the application to search and download tweets that have been created in the last week. This set of tweets is referred to as the ***recent archive*** . It permits also downloading a total of ***500000 tweets per month***. You may see how your much of your monthly allowances you have spend by visiting the dashboard on your Twitter developer account. Once you have reached the limit of 500000 dwonloaded tweets, you won't be able to download any more for the rest of the month. This limit resets automatically every month (from the date you generated the token). For example if you generated the token on March 21 and until March 25 you have already downloaded the 500000 tweets, you'll be able to download tweets agan (500000) on April 21st. As already said, this is done automatically.
    - *Academic bearer token*: This bearer token allows doanloading up to 10000000 tweets per month and has no datetime limit on tweets i.e. you may search for tweets as long back in time as you like (this bearer searches also the recent archive). This set of tweets is referred to as the ***historic archive***.  Here too, the limit is automatically reset each month. To obtain an academic bearer token, you have to issue a special application which asks mainly about your cv and the purpose. The application is reviewed by TWitter and a response is given (not immediately though).
    - [TODO: Update me with premium etc] *Commercial bearer token*: I'm not knowledgeable enough to talk about this kind of bearer token. I've seen it mentioned but i do not know what it allows you to do.
  
    Once you have a valid bearer token, you need to add it to the application's configuration file twitterSearch.conf  (yes, i know it's very bad practice but i'm a uni professor and we a known to do things sloppy or as someone famously said *"Re 2: your job is being a professor and researcher: That's one hell of a good excuse for some of the brain-damages of minix. I can only hope (and assume) that Amoeba doesn't suck like minix does."* See https://www.oreilly.com/openbook/opensources/book/appa.html) . See blow where exactly to put the bearer value you have.

<br/>
<br/>

2.  You need to have **installed the follwing Python packages** on your system:
    - pandas
    - argparse
    - clrprint
    - configparser
    - pathlib




# How to prepeare, execute and interact with TwitterSearch


## Preparing the configuration file

Before executing TwitterSearch, you need to make sure that **some configuration file settings have the proper values**. These settings are related to the Twitter bearer token that you have received from your Twitter developer account.

### Why the need to prepare the configuration file
Upon execution, TwitterSearch reads a configuration file containing all the settings with which the application is to be executed. The configuration file contains some default settings required by the execution of commands. Some configuration file settings may be overridden at runtime by specifying arguments on TwitterSearch’s command shell (see section [Supported Shell Commands](#supported-shell-commands) ). However, for some other settings, the configuration file is the only way to set them. 

An example configuration file, *twitterSearch.conf*, containing all application supported settings is available in this repository. If TwitterSearch is executed without configuration file, it executes with default values for all settings.

You may open and edit the configuration file with your favorite text editor. The configuration is organized in named sections marked by square brackers [ ]. E.g. you may find sections [General]  [TwitterAPI] etc. Each section contains settings related to a specific part of the application. 

The settings that need to be set with valid values before the execution of TwitterSearch in order to guarantee its correct working.

### Minimum required settings
While a more detailed description of the available configuration settings can be found in section [Configuration files](#Configuration-File),  the absolute necessary ones that need to be properly set before executing the app, are the settings related to the Twitter bearer tokens.  These settings can be found in the [TwitterAPI] section of the configuration file and are the following:

```
essentialBearer = <value of essential bearer token>
academicBearer = <value of academic bearer token>
Bearer = <value of bearer token actually used>
targetArchive = [recent | historic]
```


- `essentialBearer`: This setting is simply a place to store the essential bearer token generated by the Twitter developer account. If you got your essential bearer token, put its value in this setting. This setting is not used during requests.
- `academicBearer`: This setting is simply a place to store the academic bearer token generated by the Twitter developer account. If you got your academic bearer token, put its value in this setting. This setting is not used during requests.
- `Bearer`: The actual bearer token used in requests to the Twitter v2 endpoints. Bearer will always have a copy of the value in either the essentialBearer or the academicBearer setting.
- `targetArchive`: Specifies in which archive the search should be conducted. Takes one of two values: ‘recent’ or ‘historic’. Value ‘recent’ means that the search will be conducted in the recent archive (i.e. tweets published in the last 5 days) and hence the essential bearer token will be used while ‘historic’ means that the search will be conducted on all tweets ever published since the beginning of Twitter and the academic bearer token will be used. During startup, the application reads the value of ``targetArchive`` and sets the value of setting Bearer to the proper token value (copying it from essentialBearer or academicBearer setting) in order to ensure consistency. You may change the value of ``targetArchive`` either by editing the configuration file or during runtime via the `set -G` command using the application's shell (see section [Supported shell commands](#supported-shell-commands) ).

In conclusion: 
- If you have a valid essential token, set the value of setting ``essentialBearer`` to the value of the essential token you got from your Twitter developer account and the value of setting ``targetArchive`` to ‘recent’ . This means that all requests will be directed to the recent archive. **This is the minimum settings to set in order for TwitterSearch to work correctly.**
- If you have a valid academic token, set the value of setting ``academicBearer`` to the value of the academic token you have and the value of setting ``targetArchive`` to ‘historic’. 
- If you have a valid essential and academic bearer token, set the value of ``targetArchive`` to either ‘recent’ or ‘historic’ to specify the bearer token to use.  

TwitterSearch, upon startup, reads the value of ``targetArchive`` and sets the value of the setting ``Bearer`` (holding the value of token to use during requests) to the appropriate value. ***If no valid bearer token is provided, all Twitter API requests will result in an error.***

I'm sorry if this sounds complicated; This model needs to be definitely redesigned in future versions.



## Running TwitterSearch

If you have prepared the configuration file, you may execute TwitterSearch using the command line or from within IDLE. From the command line, you may execute TwitterSearch as follows

```
C:\>python twitterSearch.py [-c configurationFile]
```
Argument -c specifies the *c*onfiguration file to load during startup. If no -c argument is present, TwitterSearch attempts to load the default configuration file named *twitterSearch.conf* assumed to reside in the same folder as twitterSearch.py . If no configuration file is found, TwitterSearch exists with error. This means that a configuration file is in the current version required.

From within IDLE, open the file twitterSearch.py and execute it by selecting ```Run --> Run Module``` or ```Run --> Run...Customized``` if you would like to specify a custom configuration file using the -c argument.

NOTE: this application has been developed and tested on IDLE. It has not been tested on Anaconda, Spyder or any other python IDE.

A successfull execution of TwitterSearch will display the following messages along with a prompt which is part of TwitterSearch's command shell:
***TODO: Change the next code snipped***
```
v0.77 rd 18/03/2022
Loading configuration file [twitterSearch.conf]........OK
Target archive set to recent.

Type 'help' to see a list of supported commands.

{0}TwitterAPI v2 >>
```
The command shell of TwitterSearch allows allows users to interact with TwitterSearch and in particular to type and execute a limited set of commands (with their arguments) related to issuing queries and and downloading tweets meeting specific criteria, see the configuration settings, changing the target archive etc.

## Supported shell commands

The application allows users to execute commands via the application's command shell. The following commands and their arguments are supported:

- ```get [-f <file name>] <list of tweet ids>```

     Downloads fields for specific tweets identified by their ids given as arguments. Fields of tweets retrieved are specified by the settings ``tweet.fields`` in the configuration file.
     - ``[-f <file name>]`` : filename containing list of tweet ids. Each id must be in a separate line
     
     - ``<list of tweet ids>``: list of tweet ids, separated by whitespace. Can be one or more. If a file name containing tweet ids is provided with the -f option and a list of tweet ids as arguments, these two lists are merged.
      
     For each successfully retrieved tweet, a set of fields are displayed that include: id, author id, date created, type ( op (meaning original tweet), reply, retweed etc) and the actual content/text of the tweet.
     
     ### Example
     
     ```
     {0}TwitterAPI v2 >>get 1509893250198298630 1509882219808100352
     get 1509893250198298630 1509882219808100352
     1/2) Tweet id:1509893250198298630
	 Author id: 1328650617800122369
	 Created: 01/04/2022 13:59:37
	 Lang: en
	 Type: ???
	 Tweet: One of the biggest anime glow ups https://t.co/txuh3kJgMW
     2/2) Tweet id:1509882219808100352
	 Author id: 1126523841604399105
	 Created: 01/04/2022 13:15:48
	 Lang: en
	 Type: ???
	 Tweet: WHERE'S THE MODEL FOR THIS VEGETA, I DON'T SEE IT https://t.co/8v6r4T3EsP
      {1}TwitterAPI v2 >>
      
      ```
      
     
- ```search [-f <start_date>] [-u end_date] [-t time_step] [-o csvfile] [-n number of tweets] [-S] [-D] <query>```

     The search command issues a query to the Twitter archive (recent or historic)  searching for and downloading tweets meeting the criteria specified in < query >. Returned tweets meeting the criteria will be saved in a csv file. Two types of searches are supported, depending on the supplied arguments: **_Simple and Period searches_**. A **_simple search_** is a type of search always carried out on the recent archive and does not impose any constraints related to the date the tweets were published (except of course the 7day period that defines the recent archive). A **_period search_** is a type of search that imposes constraints related to it creation time i.e. specifies a date period in which the tweet was created (or published). Period searches may be directed to the recent or historic archive and require a date range to be specified in which the tweets, meeting the querie's criteria, have been created.  

     - ``[-f start_date]`` : (from date) A date specifying the earliest creation date of tweets to consider. Used in period queries. start_date should be a valid datetime value in the following format: ``<day>/<month>/<year>T<hour>:<min>:<sec>`` . Example ``-f 3/4/2019T14:03:17`` which would limit the search to tweets created on April 3rd, 2019 at 14:03:17 and onwards (all datetime values are in UTC). If time component is missing, midnight is assumed (00:00:00). In period searches, if -f is not specified, the from date is considered two days earlier from today.
     - ``[-u end_date]`` : (until date) A date specifying the latest creation date of tweets to consider. Used in period queries. Together with argument -f specifies the date range in which the creation date of tweets, meeting the queries criteria, has to fall. This is also called a ***search period*** or ***period***. end_date should be a valid datetime value in the following format: ``<day>/<month>/<year>T<hour>:<min>:<sec>`` . Example ``-f 3/4/2019T14:03:17 -u 15/4/2019`` which would limit the search to tweets created in the period from April 3rd, 2019 at 14:03:17 until April 15, 2019 00:00:00 (all datetime values are in UTC). If time component is missing, midnight is assumed (00:00:00). In period searches, if -u argument is not specified, until date is considered as the day before today.
     - ``[-t time_step]`` : Specifies the how the period defined by the -f and -u arguments should be broken up into subperiods and issue a separate search with the same query in each and every subperiod. Time steps should be specified in the following manner: ``kDmHnMzS`` where k, m, n and z integer values specifying the length of each subperiod in days (D), hours(H), minutes(M) and seconds(S). For example the query search ``-f 3/2/2008 -u 10/2/2008 -t 
2D10H5M2S euro``  will break up the date range [3/2/2008, 10/2/2008] to subperiods of length 2 days, 10 hours, 5 minutes and 2seconds each and conduct  a search in each of these periods (last period may differ in length). In this example, search for tweets containing the term euro will be conducted in the following periods **separately**:
       - [ 03/02/2008 00:00:00 - 05/02/2008 10:05:02 ]
       - [ 05/02/2008 10:05:02 - 07/02/2008 20:10:04 ]
       - [ 07/02/2008 20:10:04 - 10/02/2008 00:00:00 ]

       The -t option allows to have a more fine grained control over the distribution of tweets in periods, especially if periods are great in length.<br/>
       ***IMPORTANT:*** The format ``kDmHnMzS`` requires value k to between 1 and 31, value m between 0 and 24, value n between 0 and 59 and value z between 0 and 59. This is due to the way this format is parsed (as a date actually). This needs to be changed in future versions. 

     - ``[-o csvfile]`` : Specifies the csv file where tweets meeting the criteria in < query > will be stored. If no ``-o`` argument is present, tweets will be stored in the file specified by ``csvFile`` in the configuration file. If no configuration setting csvFile is found, tweets will be stored in csv file ``data.csv``.
     
     - ``[-n number of tweets]``: Total number of tweets to download. If a period search is conducted, option -n specifies the number of tweets to download in each period or subperiod separately. If no -n argument is given, maximum number of tweets is equal to the value of setting ``maxTweetsPerPeriod`` in the configuration file.
     
     - ``[-S]``: Signals a simple search as defined in the above section. If missing, a period search is conducted. ``-S`` will ignore any -f or -u arguments given. 
     - ``[-D]``: Toggles debug mode for this command only (see ``debugMode`` option in configuration file). If debugMode is enabled, [DEBUG] messages are printed during execution of the search command. 
     - ``<query>``: Query specifying the criteria that tweets need to fullfil. Can use any valid operator defined by the v2 Twitter API. For a list of supported query operators and their use see https://developer.twitter.com/en/docs/twitter-api/v1/rules-and-filtering/search-operators  and https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query 

     ### Examples
     | search command  | Explanation |
     | ------------- | ------------- |
     | search -S -n 1000 -o myData.csv github client  | Does a simple search for tweets on the recent archive, downloading 1000 tweets containing the words github and client. Tweets will be stored in file myData.csv  |
     | search -S -n 1000 -o myData.csv github client -is:retweet -is:reply | Does a simple search for tweets on the recent archive, downloading 1000 tweets that are not retweets nor replies containing the words github and client. Tweets will be stored in file myData.csv  |
     | search -f 1/10/2015 -u 20/10/2015 -n 600 -o tesla.csv tesla from:elonmusk OR from:nasa | Does a period search on the historic archive for a maximum total of 600 tweets created between 1/10/2015 and 20/10/2015 that contain the string tesla and were published by the account elomusk or nasa. Tweets will be stored in file tesla.csv  |
     | search -f 1/10/2015 -u 20/10/2015 -t 7D5H3M2S -n 600 -o tesla.csv tesla from:elonmusk OR from:nasa  | Does a period search for tweets on the historic archive, dividing the period 1/10/2015 - 20/10/2015 into subperiods of length 7 days, 5 hours, 3 minutes and 2 seconds each and will download a maximum of 600 tweets in each of the 3 generated subperiods (which will be __[ 01/10/2015 00:00:00 - 08/10/2015 05:03:02 ], [ 08/10/2015 05:03:02 - 15/10/2015 10:06:04 ] and [ 15/10/2015 10:06:04 - 20/10/2015 00:00:00 ]__) that contain the string tesla and were published by the account elomusk or nasa. All tweets will be stored in the same csv file named tesla.csv  |
<br/>
<br/>

- ```config```

     Displays the current configuration settings, as loaded from the specified configuration file. Loaded configuration settings are shown in sections (defined inside the loaded configuration file). Last section with name ``__Runtime`` is not defined inside the configuration file; it contains settings added dynamically during runtime. E.g. which configuration file was actually loaded (see setting ``__configsource`` )
     
     ### Example
     
     ```
     {2}TwitterAPI v2 >>config
     Executing config >>>>>
     Configuration settings
     Section [General]
	- maxtweets = 4000
	- maxtweetsperperiod = 103
	- defaultlang = el
	- commandprompt = TwitterAPI v2 >>
     Section [TwitterAPI]
	- targetarchive = historic
	- recentapiendpoint = https://api.twitter.com/2/tweets/search/recent
	- historicapiendpoint = https://api.twitter.com/2/tweets/search/all
	- apiendpoint = https://api.twitter.com/2/tweets/search/all
     
     
     ...
     
     
     Section [Debug]
	- debugmode = false
	- showprogress = true
	- enabledebugging = false
	- savejsonresponses = true
	- logfile = TwitterAPIv2.log
     Section [__Runtime]
	- __configsource = searchsettings/twitterSearch.conf

     ```
     

<br/>
<br/>

- ```reaload [-c configuration file]```

     Allows loading a configuration file specified by the -c option. Relative file names are supported. If no -c option is provided, the configuration file  loaded during startup is reloaded (more specifically the file specified in  ``__configsource`` option in ``config`` command). If configuration file is not found, no new configuration is loaded.

     ### Example
     ```
     {1}TwitterAPI v2 >>reload
     Loading configuration file: [searchsettings/twitterSearch.conf]
     Configuration file [searchsettings/twitterSearch.conf] successfully loaded.
     Target archive set to historic.
     {2}TwitterAPI v2 >>
     ```
<br/>

- ```history (or h)```

     Displays a numbered list of the recent commands already executed via the application's command shell (the ***command history***). The number of recent commands kept in history is determined by setting ``historySize`` in the configuration file. Numbers can be used in conjunction with the ``!`` command (see below) to re-execute commands. Usefull to re-execute commands or copy-pasting complicated commands if you are bored to retype these again. Command history is saved in local file ``.history`` when TwitterSearch quits gracefully. Command history file ``.history`` is automatically loaded during startup if present. 

   ### Example
   ```
   {12}TwitterAPI v2 >>h
   1. search -S -n 88 biden
   2. search -S -n 144 oscars
   3. search -S -n 144 -o oscarsWillSmith.csv Will Smith
   4. config
   5. status
   6. search -f 2/3/2016T13:09:22 -u 10/4/2016 -t 11D5H58M59S -o russia.csv -n 1000 russia
   7. help
   8. set --target recent
   9. status
   10. search -f 1/10/2015 -u 20/10/2015 -t 7D5H3M2S -n 600 -D -o tesla.csv tesla from:elonmusk OR from:nasa
   11. help
   12. reload
   13. reload -c twitterSearch.conf
   14. search -S -n 15 bitcoin
   15. search -S -n 15 -o bitcoin.csv bitcoin from:elonmusk
   16. search -S -n 125 -o bitcoin.csv bitcoin -is:retweet
   17. config
   18. set -G historic
   19. status
   20. search -f 5/9/2017T14:09:22 -u 10/9/2017 -o euro.csv euro crisis
   21. search -f 5/9/2017T14:09:22 -u 10/9/2017 -n 500 -o euro.csv euro crisis
   22. config
   23. status
   24. reload
   25. reload
   {12}TwitterAPI v2 >>
   ```
<br/>


- ``showcsv [-n number of rows] [-s separator] [-N] [-T] [-F list of fields] <csv file name>``

    Allows displaying the head or tail of csv files containing downloaded tweets and created by TwitterSearch. Arguments:
    
    - ``[-n number of rows]`` Number of rows to display. Default 15.
    - ``[-s separator]`` Separator used to separate fields in lines. Default value of ``csvSeparator`` in configuration file.
    - ``[-N]`` Indicates that the csv file does not have a header. If missing, csv file has a header which is the first line in the file.
    - ``[-T]`` Show tail rows of csv file. If missing, head rows are displayed.
    - ``[-F field1 field2 field3...]`` Fields/columns of csv file to display. Default fields are username and url of tweets.
    
    HINT: Due to a bug, the -F option should not preceed the file name. Should be placed BEFORE any -T, -N or -n option.
    
    ### Example
    ```
    {1}TwitterAPI v2 >>showcsv -F username created_at(utc) -n 22 -T 2000.csv
    File:  2000.csv
    Number of rows:278
    Number of columns:10
    Column names: ['author_id', 'username', 'id', 'created_at(utc)', 'lang', 'tweet', 'tweetcount', 'followers', 'following', 'url']
    Last 22 rows:
                username      created_at(utc)
    256      PAULJOE2017  26/05/2018 01:22:16
    257      lecastilloh  26/05/2018 01:22:15
    258  mundocriptonews  26/05/2018 01:22:15
    259      Crypto_Popo  26/05/2018 01:22:15
    260         mbellias  26/05/2018 01:22:11
    261       noamipolmn  26/05/2018 01:22:05
    262         J3Crypto  26/05/2018 01:22:05
    263       arichduvet  26/05/2018 01:22:01
    264  trackingcryptos  26/05/2018 01:21:58
    265         Ifechigo  26/05/2018 01:21:57
    266  CryptoVinceTeam  26/05/2018 01:21:57
    267   GlobalSEOLinks  26/05/2018 01:21:55
    268         TayotSam  26/05/2018 01:21:54
    269       ayanapiokh  26/05/2018 01:21:53
    270      PapaShitake  26/05/2018 01:21:51
    271          cwundef  26/05/2018 01:21:48
    272   DoctorMbitcoin  26/05/2018 01:21:46
    273  GdHLy32luILFURA  26/05/2018 01:21:45
    274      Crypto_Popo  26/05/2018 01:21:37
    275      MdMohib1996  26/05/2018 01:21:35
    276      danaalikhan  26/05/2018 01:21:26
    277         BTClinks  26/05/2018 01:21:25
    ```



- ``set [-G | --target <historic | recent>]``

    Allows setting the value of specific loaded configuration settings. Currently, only setting of the search target (recent or historic) option [-G | --target] is supported. This does not modify the content of the configuration file loaded. Affects only settings loaded in memory furing execution of TwitterSearch.
    
    ### Example
    
    ```
    {0}TwitterAPI v2 >>set --target historic
    Target archive set to historic.
    {1}TwitterAPI v2 >>
    ```
- ``!< history index > ``

  Re-executes command at position < history index > in command history (the number displayed before each command when command history is shown). Belongs to the set of expansion commands (because these will be expanded before execution).

  ### Example
  ```
  {0}TwitterAPI v2 >>h
   1. search -S -n 88 biden
   2. search -S -n 144 oscars
   3. search -S -n 144 -o oscarsWillSmith.csv Will Smith
   4. config
   5. status
   6. search -f 2/3/2016T13:09:22 -u 10/4/2016 -t 11D5H58M59S -o russia.csv -n 1000 russia
   7. help
   8. set --target recent
   9. status
   10. search -f 1/10/2015 -u 20/10/2015 -t 7D5H3M2S -n 600 -D -o tesla.csv tesla from:elonmusk OR from:nasa
   11. help
   12. reload
   13. reload -c twitterSearch.conf
   14. search -S -n 15 bitcoin
   15. search -S -n 15 -o bitcoin.csv bitcoin from:elonmusk
   16. search -S -n 125 -o bitcoin.csv bitcoin -is:retweet
   17. config
   18. set -G historic
   19. status
   20. search -f 5/9/2017T14:09:22 -u 10/9/2017 -o euro.csv euro crisis
   21. search -f 5/9/2017T14:09:22 -u 10/9/2017 -n 500 -o euro.csv euro crisis
   22. config
   23. status
   24. reload
   25. reload
  {0}TwitterAPI v2 >>!20
  [search -f 5/9/2017T14:09:22 -u 10/9/2017 -n 500 -o euro.csv euro crisis]
  ```


- ``!< string > ``

  Re-executes last command that starts with < string >. If no such command is found, nothing is executed. 

  ### Example
  ```
  {0}TwitterAPI v2 >>h
   1. search -S -n 88 biden
   2. search -S -n 144 oscars
   3. search -S -n 144 -o oscarsWillSmith.csv Will Smith
   4. config
   5. status
   6. search -f 2/3/2016T13:09:22 -u 10/4/2016 -t 11D5H58M59S -o russia.csv -n 1000 russia
   7. help
   8. set --target recent
   9. status
   10. search -f 1/10/2015 -u 20/10/2015 -t 7D5H3M2S -n 600 -D -o tesla.csv tesla from:elonmusk OR from:nasa
   11. help
   12. reload
   13. reload -c twitterSearch.conf
   14. search -S -n 15 bitcoin
   15. search -S -n 15 -o bitcoin.csv bitcoin from:elonmusk
   16. search -S -n 125 -o bitcoin.csv bitcoin -is:retweet
   17. config
   18. set -G historic
   19. status
   20. search -f 5/9/2017T14:09:22 -u 10/9/2017 -o euro.csv euro crisis
   21. search -f 5/9/2017T14:09:22 -u 10/9/2017 -n 500 -o euro.csv euro crisis
   22. config
   23. status
   24. reload
   25. reload
  {0}TwitterAPI v2 >>!search -f 2
  [search -f 2/3/2016T13:09:22 -u 10/4/2016 -t 11D5H58M59S -o russia.csv -n 1000 russia]
  ```



- ``!!``

  Re-executes last command. Or the last command added to the command history.
  
  ### Example
  ```
  {0}TwitterAPI v2 >>h
   1. search -S -n 88 biden
   2. search -S -n 144 oscars
   3. search -S -n 144 -o oscarsWillSmith.csv Will Smith
   4. config
   5. status
   6. search -f 2/3/2016T13:09:22 -u 10/4/2016 -t 11D5H58M59S -o russia.csv -n 1000 russia
   7. help
   8. set --target recent
   9. status
   10. search -f 1/10/2015 -u 20/10/2015 -t 7D5H3M2S -n 600 -D -o tesla.csv tesla from:elonmusk OR from:nasa
   11. help
   12. reload
   13. reload -c twitterSearch.conf
   14. search -S -n 15 bitcoin
   15. search -S -n 15 -o bitcoin.csv bitcoin from:elonmusk
   16. search -S -n 125 -o bitcoin.csv bitcoin -is:retweet
   17. config
   18. set -G historic
   19. status
   20. search -f 5/9/2017T14:09:22 -u 10/9/2017 -o euro.csv euro crisis
   21. search -f 5/9/2017T14:09:22 -u 10/9/2017 -n 500 -o euro.csv euro crisis
   22. config
   23. status
   24. help
   25. reload
  {0}TwitterAPI v2 >>!!
  [reload]
  ```


- ``^X^Y``

  In the last command executed, replace all instances of X with Y and execute new command.

  ### Example
  
  ```
  {0}TwitterAPI v2 >>h
   1.config
   2. status
   3. search -f 2/3/2016T13:09:22 -u 10/4/2016 -t 11D5H58M59S -o russia.csv -n 1000 russia
   4. help
   5. set --target recent
   6. status
   7. search -f 5/9/2017T14:09:22 -u 10/9/2017 -n 500 -o euro.csv euro crisis
   {0}TwitterAPI v2 >>^500^2000
   search -f 5/9/2017T14:09:22 -u 10/9/2017 -n 2000 -o euro.csv euro crisis
  ```


- ``quit (or q)``

  Quits the shell and terminates the application.
  
  ### Example
  ```
  {18}TwitterAPI v2 >>q
   
   Finished. ByeBye!
  ```


# Configuration file

In this section we provide a brief overview of the settings supported by configuration files. Settings are organized into named sections, with each section holding parameters related to a particular aspect of TwitterSearch. For example section named [Shell] has settings related to TwitterSearche's command shell, [TwitterAPI] settings related to the v2 API etc. Settings in configuration files are loaded during startup. Configuration files can also be loaded via the shell during the programs execution. The configuration settings act as the default values for some (important) parameters. Some settings (in this version not all though) might be overitten by shell command arguments.

- Section ``General``

  Contains general settings. Supported settings in this section are:
  
  - ``maxTweets``. Integer values. Determines the total number of tweets to fetch, across all periods. Currently not supported and not used.
  - ``maxTweetsPerPeriod``. Integer value. Specifies the maximum number of tweets to fetch in each period. If a simple search is conducted, specifies the total number of tweets to fetch. Is overridden by option ``-n`` of the search command. A negative value indicates that no maximum value is specified (i.e. get as many as possible).
  - ``defaultLang`` Country codes (see https://developer.twitter.com/en/docs/twitter-for-websites/supported-languages ). Specifies the language of tweets to search for, if no language is specified in the query. Currently not supported or used. 
  - ``downloadSpeedWindow`` Integer value. The number of download speed values to keep in a list, out of which the average download speed (in tweets/sec) is calculated and reported.  


- Section ``Network``

  Contains settings related to lower level network requests. Supported settings in this section are:
  
  - ``netConnectTimeout`` Float value. Timeout value (in seconds) for establishing a tcp connection with the remote host. If the application waits longer than the value of this setting for a connection, an exception is raised. Negative values indicate no timeout.
  - ``netReadTimeout`` Float value. Timeout value (in seconds) for reading a response from the server. If the application waits longer than the value of this setting for reading a response from the server, an exception is raised. Negative values indicate no timeout.

- Section ``TwitterAPI``

  Contains settings related to the Twitter API. Supported settings in this section are:
  
  - ``targetArchive`` Takes one of two string value: historic or recent. Specifies in which archive the search should be conducted. Depending on the value of this setting, the appropriate bearer token will be used. TwitterSearch tries to make sure that the bearer token used is in accordance with the value in this setting.
  - ``recentApiEndPoint`` URI. A place to hold the endpoint URI for searching in the recent archive
  - ``historicApiEndPoint`` URI. A place to hold the endipoint URI for searching in the historic archive
  - ``apiEndPoint`` URI. The endpoint URI that will be actually used during requests. Will have the value of eiter ``recentApiEndPoint`` or ``historicApiEndPoint``
  - ``essentialBearer`` Essential bearer token. A place to hold the essential bearer token.
  - ``academicBearer`` Academic bearer token. A place to hold the academic bearer token.
  - ``Bearer`` bearer token. The bearer token that will actually be used during requests. Takes the value of setting ``essentialBearer`` or ``academicBearer``.
  - ``maxEndpointTweets`` Integer value. Number of tweets that should be returned by endpoint as a response to a query. Note: this is different from the ``maxTweetsPerPeriod`` setting. ``maxEndpointTweets`` determines in essence the maximum number of tweets returned by the endpoint with each request. If the ``maxTweetsPerPeriod`` has the value 100 and ``maxEndpointTweets`` has a value of 10, this means that at most 10 requests need to be done to the endpoint to reach the limit of 100 tweets. If ``maxEndpointTweets`` is set to 100, then you just need 1 request to the endpoint to reach the limit of 100 tweets.
  - ``tweet.fields`` String value (Comma-separated list of fields). Fields to request for Twitter's Tweet object. The data dictionary (i.e. available fields) for tweet objects can be found here: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
  - ``user.fields`` String value (Comma-separated list of fields). Fields to request for Twitter's user objects. The data dictionary for user objects can be found here: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
  - ``place.fields`` String value (Comma-separated list of fields). Fields to request for Twitter's place objects. The data dictionary for place objects can be found here: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/place
  - ``expansions`` String value (Comma-separated list of fields). Fields for which to return more data i.e. expand. For these objects, more fields will be returned.

For more information on Twitter fields and Twitter's object model see: https://developer.twitter.com/en/docs/twitter-api/fields , https://developer.twitter.com/en/docs/twitter-api/data-dictionary/using-fields-and-expansions .

- Section ``Request``

  Contains settings related to the requests to the endpoint. Supported settings in this section are:
  
  - ``sleepTime`` Float value. The time to sleep (in seconds) between two successive requests to the endpoint in order not to spam the server. If ``sleepTime`` is too short, the endpoint will return an error.
  
  
- Section ``Storage``

  Contains settings related to the way the tweets will stored localy. Supported settings in this section are:
  
  - ``format`` String value (csv). Currently only value csv is supported. The way the tweets and their metadata should be stored locally. The current version supports only storage of tweets and their metadata locally in csv format.
  - ``csvSeparator`` String value. The separator to use when storing tweets and their metadata in csv format.
  - ``csvFile`` String value. The name of the csv file where the tweets and their metadata will be stored. Can be overriden with the -o option during execution of search command.
 

- Section ``Shell``

  Contains settings related to the application command shell. Supported settings in this section are:
  
  - ``historySize`` Integer value. The maximum number of commands to store in the command history. If this number is reached, command history behaves like a FIFO queue: Oldest command added is removed; new command is added at the end. 
  - ``commandPrompt`` String value. The message/string displayed as the prompt of the shell; an indication that a user command is expected.

- Section ``Debug``

  Contains settings related to debugging the application. Supported settings in this section are:
  
  - ``debugMode`` Boolean value (true/false). Specifies if debug messages should be printed out on the screen. Debug messages can be identified by the prefix [DEBUG]. [-D] option of the ``search`` command, toggles the value of this setting.
  - ``showProgress`` Boolean value (true/false). Specifies if during querying and downloading of messages, reports should be displayed informing about some descriptive statistics. Enabling this setting will result in displaying 4 numbers after each requests in the form of ``.(k/l/m/n)`` where: k is the number of tweets received by the endpoint during the last request, l the number of tweets, out ot the k received, that were actually stored, m the total number of tweets downloaded until now (in period searches, this expresses the number of tweets downloaded during the current period) and n the average download speed in tweets/sec (calculated out of the samples whose number is specified by ``downloadSpeedWindow``). If ``showProgress`` is false, only one dot ``.`` is displayed signalling that tweets have been received by the endpoint.
  - ``saveJsonResponses`` Boolean value (true/false). If json responses, received byt the endpoint, should be saved to files. NOT USED in this version.
  - ``logFile`` String value. File to store log messages. NOT USED in this version.

# Other related projects

- [TweetScraper](https://github.com/jonbakerfish/TweetScraper)
- [Tweepy](https://www.tweepy.org/)
- [Selenium based web scrapers](https://medium.com/@wyfok/web-scrape-twitter-by-python-selenium-part-1-b3e2db29051d)

# Acknowledgements

The code developed in this repository was based on the source code presented in the following article:
https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a


# Contact

xxxxx 
