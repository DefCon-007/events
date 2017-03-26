Events
======

It is an API for KGP Dashboard which gives all the relevant events from facebook happening in KGP.

## How does it work?

It gets the content from the specified pages using Facebook's graph API. We
use [facepy](https://github.com/hargup/facepy) as the python frontefnd for the
api.


## How to use Events

* Get a Facebook API token and save it in file name `ACCESS_TOKEN`. See this [StackOverflow Answer](http://stackoverflow.com/a/16054555/1780891).
* The scraping script runs exclusively on Python 3, you can [conda](http://conda.pydata.org/miniconda.html) to easily switch between Python 2 and Python 3 environments.
* Install all the dependancies using `pip install -r requirements.txt`
* Run `fbscraper.py` by `python3 fbscraper.py`. You can setup up a cron job for running the file with referesh rate of your choice. 
* Now run the server by `python app.py`.

## API Endpoints 

### /all-events 
    This endpoint returns all the events 
    Parameters required :
        None 
    Parameters Returned :
        success : Boolean (Whether the request was a success or not)
        data    : JSON i.e. a list of Dictionaries of all the events, 
                  Parameter of dictionary : 
                        description : String, Description of the event
                        placeLocation: Dictionary containing details of geolocation of the venue or Null if location is not tagged
                            Paramenters :
                                  city: String,
                                  country: String,
                                  longitude: Float,
                                  latitude: Float,
                                  street: String,
                                  zip: String,
                        created_time: String, date and time when the event was created (ex :2017-03-22T20:59:49+0000)
                        source: String, Name of the page hosting the event
                        id: String, ID of the event 
                        link: String, Link to the event
                        startTime: String, Starting time of the event (ex : 03:00AM)
                        startDate: String, Starting date of the event (ex :23-03-2017)
                        pic: String, Link to cover picture of the event or Null if no picture is provided
                        placeName: String, Name of the venue 
                        attenders: Integer, Number of attendess of the event
                        name : String, Name of the event or Null if no name is present
                        
### /events-on-date  , method : POST
    This endpoint returns all the events happening on the suppiled date 
    Parameters required :
        date : Proper date in the format (DD-MM-YYYY)
    Parameters Returned :
        success : Boolean (Whether the request was a success or not)
        data    : JSON i.e. a list of Dictionaries of the events happening on supplied date , (if success == True)
                  Parameter of dictionary : 
                        description : String, Description of the event
                        placeLocation: Dictionary containing details of geolocation of the venue or Null if location is not tagged
                            Paramenters :
                                  city: String,
                                  country: String,
                                  longitude: Float,
                                  latitude: Float,
                                  street: String,
                                  zip: String,
                        created_time: String, date and time when the event was created (ex :2017-03-22T20:59:49+0000)
                        source: String, Name of the page hosting the event
                        id: String, ID of the event 
                        link: String, Link to the event 
                        startTime: String, Starting time of the event (ex : 03:00AM)
                        startDate: String, Starting date of the event (ex :23-03-2017)
                        pic: String, Link to cover picture of the event or Null if no picture is provided
                        placeName: String, Name of the venur 
                        attenders: Integer, Number of attendess of the event
                        name : String, Name of the event or Null if no name is present
