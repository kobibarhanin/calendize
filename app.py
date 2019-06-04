from flask import render_template, jsonify, request
import datetime

import flask
import requests
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

import main as main

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = b'j\x187N<\x8ci-\xd5\x7f\x84\x8diqz\xd1\xfb\x93DB\x82\xf2\x101'



@app.route('/')
def index():
    print("* Landing Page rendered *")
    return render_template('CalCendar-landing.html')

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    # authorization_response = authorization_response.replace('http', 'https')
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('render_homePage'))


@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return 'Credentials successfully revoked.'
    else:
        return 'An error occurred.'


@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return 'Credentials have been cleared.<br><br>'


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


@app.route("/calculator")
def render_homePage():
    print("* Home Page rendered *")
    return render_template('CalCendar.html')


@app.route("/fetch")
def get_instances_fetch():
    print("* Fetching instances from calendar *")

    startDate = datetime.datetime.fromtimestamp(int(request.args.get('_startDate'))/1000.0)
    endDate = datetime.datetime.fromtimestamp(int(request.args.get('_endDate'))/1000.0)
    startDate=startDate.replace(hour=0)
    endDate=endDate.replace(hour=0)

    print("from: " + str(startDate) + " ,to: " + str(endDate))

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    data = main.fetch(startDate.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),endDate.strftime('%Y-%m-%dT%H:%M:%S.%fZ'), service=service)

    return jsonify(data)


@app.route("/calculate")
def get_instances():
    print("* Calculating optimal schedule *")

    startDate = datetime.datetime.fromtimestamp(int(request.args.get('_startDate'))/1000.0)
    endDate = datetime.datetime.fromtimestamp(int(request.args.get('_endDate'))/1000.0)
    startDate=startDate.replace(hour=0)
    endDate=endDate.replace(hour=0)
    print("from: " + str(startDate) + " ,to: " + str(endDate))

    anchor_instances = request.args.get('_anchor_instances').split(",")
    anchor_instances.pop(len(anchor_instances)-1)
    floating_instances = request.args.get('_floating_instances').split(",")
    floating_instances.pop(len(floating_instances)-1)

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    data = main.run(startDate=startDate.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),endDate=endDate.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),anchor_instances=anchor_instances,floating_instances=floating_instances,service=service)

    return jsonify(data)


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run('localhost', 8080, debug=True)
