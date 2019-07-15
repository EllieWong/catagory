import httplib2 as httplib2
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response, json
from flask import session as login_session
import random, string, requests

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Connect to Database and create database session
engine = create_engine('sqlite:///cagegory.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'my_app_name'
SCOPES = [
    'email',
    'profile',
    'https://www.googleapis.com/auth/calendar',
    # Add other requested scopes.
]


# Create anti-forgery state token
@app.route('/login/', methods=['GET', 'POST'])
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    print state
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['GET', 'POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    print code
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')

        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    print access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    print user
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/home')
@app.route('/catalog/')
def showCategory():
    """
            Home page of application
        """
    session = DBSession()
    categores = session.query(Category).order_by(Category.name)
    latest_items = session.query(Item).order_by(Item.id)[0:10]
    return render_template('publicatalog.html', categores=categores, items=latest_items)


@app.route('/catalog/<string:cat_name>/items/')
def showItems(cat_name):
    """
        Generate page for a single category
    """
    session = DBSession()
    category = session.query(Category).filter_by(name=cat_name).one()
    categores = session.query(Category).order_by(Category.name)
    items = session.query(Item).filter_by(category_id=category.id).all()

    return render_template('publicItems.html', items=items, cat_name=cat_name, categores=categores)


@app.route('/catalog/<string:cat_name>/<string:item_name>/')
def showItem(cat_name, item_name):
    """
        Generate page for a single item
    """
    session = DBSession()
    category = session.query(Category).filter_by(name=cat_name).one()
    item = session.query(Item).filter(Item.category_id == category.id, Item.title == item_name).one()

    return render_template('publicitem.html', item=item, cat_name=cat_name)


@app.route('/catalog/addItem', methods=['GET', 'POST'])
def addItem():
    """
            sends a post form to client to be able to add
            new item to catalog
    """
    if 'username' not in login_session:
        flash('You must be logged in to view add item!')
        return redirect('/home')

    session = DBSession()
    # Process form from client to add item
    if request.method=='POST':
        cat_id = session.query(Category) \
            .filter_by(name=request.form['category']) \
            .one() \
            .id
        print getUserID(login_session['email'])
        new_item = Item(title=request.form['name'],
                        description=request.form['description'],
                        user_id=getUserID(login_session['email']),
                        category_id=cat_id)
        session.add(new_item)
        session.commit()
        flash("Added New Item: {}".format(new_item.title))
        return redirect('/home')
    else:
        cat_names = [cat.name for cat in session.query(Category).all()]
        return render_template('addItem.html',cat_list=cat_names)


@app.route('/catalog/<cat_name>/<item_name>/edit',methods=['GET','POST'])
def editItem(cat_name,item_name):
    """
            sends a post form to client to be able to edit
            a item to catalog
    """
    if 'username' not in login_session:
        flash('You must be logged in to view add item!')
        return redirect('/home')

    session = DBSession()
    category = session.query(Category).filter_by(name=cat_name).one()
    print category.id
    print item_name
    item_to_edit = session.query(Item).filter(Item.category_id == category.id, Item.title == item_name).one()
    print item_to_edit.user_id
    # Verify if logged in user can edit item
    item_user_id = session.query(User).filter_by(id=item_to_edit.user_id).one().id
    if 'user_id' not in login_session or login_session['user_id'] != item_user_id:
        flash("You do not have permission to edit: {}"
              .format(item_to_edit.title))

        return url_for('editItem',cat_name=cat_name,item_name=item_name)
    # Process form from client to edit item

    if request.method=='POST':

        return ''
    else:
        cat_names = [i.name for i in session.query(Category).all()]
        return render_template('editItem.html',item=item_to_edit,cat_name=cat_name,cat_list=cat_names)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.run(host='localhost', port='5001', debug=True)
