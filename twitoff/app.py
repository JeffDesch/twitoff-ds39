from os import getenv
from flask import Flask, render_template, request
from .predict import predict_user
from .models import DB, User, Tweet
from .twitter import add_or_update_user, get_all_usernames



def create_app():

    # Initilaize our app
    app = Flask(__name__)

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        return render_template('base.html', title="Home", users=User.query.all())

    app_title = "Twitoff DS39"

    @app.route("/test")
    def test():
        return f"<p>Another {app_title} page</p>"

    @app.route('/update')
    def update():
        '''update all users'''
        usernames = get_all_usernames()
        for username in usernames:
            add_or_update_user(username)
        return "All users have been updated"
    
    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template("base.html", title="Reset Database")
    

    @app.route('/populate')
    def populate():
        users = ['numenoko', 'entouhouwiki', 'incorrect2hu', 'thekirbybot']
        for user in users:
            add_or_update_user(user)

        return "Created some users"

    @app.route('/user', methods=["POST"])
    @app.route('/user/<name>', methods=["GET"])
    def user(name=None, message=''):

        # we either take name that was passed in or we pull it
        # from our request.values which would be accessed through the
        # user submission
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = "User {} Succesfully added!".format(name)

            tweets = User.query.filter(User.username == name).one().tweets

        except Exception as e:
            message = "Error adding {}: {}".format(name, e)

            tweets = []

        return render_template("user.html", title=name, tweets=tweets, message=message)

    @app.route('/compare', methods=["POST"])
    def compare():
        user0, user1 = sorted(
            [request.values['user0'], request.values["user1"]])

        if user0 == user1:
            message = "Cannot compare users to themselves!"

        else:
            # prediction returns a 0 or 1
            prediction = predict_user(
                user0, user1, request.values["tweet_text"])
            message = "'{}' is more likely to be said by {} than {}!".format(
                request.values["tweet_text"],
                user1 if prediction else user0,
                user0 if prediction else user1
            )

        return render_template('prediction.html', title="Prediction", message=message)    


    # return our app object after attaching the routes to it.
    return app
