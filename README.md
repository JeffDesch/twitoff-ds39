# twitoff-ds39 - "Twitoff" Twitter Predictor
Web: https://twitoff-jeffd.herokuapp.com/

Web-based tweet content predictor using simple token NLP. 
Based on Bloomtech project notes here: https://github.com/bloominstituteoftechnology/DS-Unit-3-Sprint-3-Productization-and-Cloud

Hosted with Heroku, a barebones frontend allows a user to input twitter handles and their own text, and then have the backend predictive model predict which twitter user would be most likely to have written the inputted text. Uses Flask to handle backend communication with a SQLite database storing the vectorized tweet data for the users retrieved from the Twitter dev API.

Somewhat unstable due to the limits of a free Heroku account: try the /reset path if something breaks  
