from flask import Flask, make_response, jsonify, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import dotenv_values
from flask_bcrypt import Bcrypt
from sqlite3 import IntegrityError
from sqlalchemy import exc 
from models import db,Match,Fighter,Event,User,Comment

import json

config = dotenv_values(".env")

app = Flask(__name__)
app.debug = True
app.secret_key = config['FLASK_SECRET_KEY']
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.get('/fighters')
def get_fighters():
    fighters=Fighter.query.all()
    return [f.to_dict() for f in fighters],200

@app.get('/matches')
def get_matches():
    matches = Match.query.all()
    return [m.to_dict() for m in matches]

@app.get('/events')
def get_events():
    events = Event.query.all()
    return [e.to_dict() for e in events]

@app.get('/check_session')
def check_session():
    user = db.session.get(User, session.get('user_id'))
    print(f'check session {session.get("user_id")}')
    
    if user:
        return user.to_dict(rules=['-password_hash']), 200
    else:
        # The first time a user visits a page (i.e. is not logged in)
        # we will return this.
        return {"message": "No user logged in"}, 401
    
@app.route('/fighter_details', methods=['GET'])
def get_fighter_details():
    name = request.args.get('name')
    fighter = Fighter.query.filter_by(name=name).first()
    if fighter:
        return jsonify(fighter.serialize())  # Assuming you have a serialize method to format your ORM object
    return jsonify({"error": "Fighter not found"}), 404


@app.post('/login')
def login():
    # get the data from the post request (dict of username/password)
    data = request.json
    # get the user based on username
    user = User.query.filter(User.name == data.get('name')).first()

    # check that the hash of supplied password matches the hash stored in the db
    if user and bcrypt.check_password_hash(user.password_hash, data.get('password_hash')):
        # if successful, set a key in the session with the user id
        session["user_id"] = user.id
        print("success")
        
        return user.to_dict(), 200
    else:
        return { "error": "Invalid username or password" }, 401

@app.get("/comments")
def get_reviews():
    comments = Comment.query.all()

    return [c.to_dict() for c in comments]

@app.post('/signup')
def signup():
    data = request.json
    try:
        # make a new object from the request json
        user = User(
            name=data.get("name"),
            password_hash=bcrypt.generate_password_hash(data.get("password"))
        )
        # add to the db
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        # return object we just made
        return user.to_dict(), 201
    except IntegrityError as e:
        print("caught1")
        print(e)
        return {"error": f"username taken"}, 405
    except exc.IntegrityError as e:
        print("caught2")
        print(e)
        return {"error": f"username taken"}, 405
    # except Exception as e:
    #     # if anything in the try block goes wrong, execute this
    #     print(e)
    #     return {"error": f"could not post user {e}"}, 405

@app.post("/comments")
def post_comments():
    data = request.json
    try:
        new_review = Comment(
            review=data.get("review"),
            user_id=data.get("user_id"),
            event_id=data.get("event_id"),
        )
        db.session.add(new_review)
        db.session.commit()
        return new_review.to_dict(), 201
    except Exception as e:
        print(e)
        return {"error": f"could not post Comment: {e}"}, 405
    
@app.delete('/logout')
def logout():
    # logging out is simply removing the key we set in the session from log in
    session.pop('user_id')
    return { "message": "Logged out"}, 200


if __name__ == "__main__":
    app.run(port=5555, debug=True)