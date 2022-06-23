'''Handles connection to Twitter API using Tweepy'''
from os import getenv
import tweepy
import spacy
from .models import DB, Tweet, User

# Get API Key from environment vars.
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

# Connect to the Twitter API
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)

# Load our pretrained SpaCy Word Embeddings model
nlp = spacy.load('my_model/')

# Turn tweet text into word embeddings
def vectorize_tweets(tweet_text):
    return nlp(tweet_text).vector

# retrieve the username attributes
def get_all_usernames():
    usernames = []
    Users = User.query.all()
    for user in Users:
        usernames.append(user.username)
    return usernames

# add user from twitter to local db
# or update local db with new tweets
def add_or_update_user(username):
    """
    Gets twitter user and tweets from twitter DB
    Gets user by "username" parameter.
    """
    try:
        # gets back twitter user object
        twitter_user = TWITTER.get_user(screen_name=username)
        # Either updates or adds user to our DB
        db_user = User.query.get(twitter_user.id)
        if not db_user:
            # Add new user to DB
            db_user = User(id=twitter_user.id, username=username)

        DB.session.add(db_user)

        # retrieve latest if newest != null
        if db_user.newest_tweet_id:
            # Grabbing tweets from "twitter_user"
            tweets = twitter_user.timeline(
                count=200,
                exclude_replies=True,
                include_rts=False,
                tweet_mode="extended",
                since_id=db_user.newest_tweet_id
            )
        else:
            tweets = twitter_user.timeline(
                count=200,
                exclude_replies=True,
                include_rts=False,
                tweet_mode="extended",
            )

        # check to see if the newest tweet in the DB is equal to the newest
        # tweet from the Twitter API, if they're not equal then that means
        # that the user has posted new tweets that we should add to our DB.
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # tweets is a list of tweet objects
        for tweet in tweets:
            db_tweet = Tweet(
                id=tweet.id,
                text=tweet.full_text[:300],
                vect=vectorize_tweets(tweet.full_text)
            )
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)

        DB.session.commit()

    except Exception as e:
        print("Error processing {}: {}".format(username, e))
        raise e
