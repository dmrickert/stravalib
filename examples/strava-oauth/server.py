#!flask/bin/python
import logging

from flask import Flask, render_template, redirect, url_for, request, jsonify
from stravalib import Client
import json

app = Flask(__name__)
app.config.from_envvar('APP_SETTINGS')

@app.route("/")
def login():
    c = Client()
    url = c.authorization_url(client_id=app.config['STRAVA_CLIENT_ID'],
                              redirect_uri=url_for('.logged_in', _external=True),
                              approval_prompt='auto')
    return render_template('login.html', authorize_url=url)


@app.route("/strava-oauth")
def logged_in():
    """
    Method called by Strava (redirect) that includes parameters.
    - state
    - code
    - error
    """
    error = request.args.get('error')
    state = request.args.get('state')
    if error:
        return render_template('login_error.html', error=error)
    else:
        code = request.args.get('code')
        client = Client()
        access_token = client.exchange_code_for_token(client_id=app.config['STRAVA_CLIENT_ID'],
                                                      client_secret=app.config['STRAVA_CLIENT_SECRET'],
                                                      code=code)
        # Probably here you'd want to store this somewhere -- e.g. in a database.
        strava_athlete = client.get_athlete()

        store_athlete(access_token, strava_athlete)

        return render_template('login_results.html', athlete=strava_athlete, access_token=access_token)

def store_athlete(access_token, strava_athlete):
    athlete = {}
    athlete['firstname'] = strava_athlete.firstname
    athlete['lastname'] = strava_athlete.lastname
    athlete['id'] = strava_athlete.id
    athlete.update(access_token)

    with open(str(athlete['id']) + ".json", "w") as f: 
        json.dump(athlete, f)
    

if __name__ == '__main__':
    app.run(debug=True)
