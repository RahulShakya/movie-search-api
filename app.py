import os
from flask import Flask
from flask import request
from flask import jsonify, make_response
import xml.etree.cElementTree as e
import secrets, requests
from slugify import slugify
from webargs import flaskparser, fields

from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "movieratings.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Movie(db.Model):
    __tablename__ = "Movies"
    Movie_title = db.Column(db.String(255), unique=True, nullable=False, primary_key=True)
    Release_year = db.Column(db.Integer)
    Plot_description = db.Column(db.String)
    Genre = db.Column(db.String)
    Average_Rating = db.Column(db.Float)
    Number_of_votes = db.Column(db.Integer)
    def __repr__(self):
        return "<Title: {}>".format(self.title)
class Rating(db.Model):
    __tablename__ = "Ratings"
    Username    = db.Column(db.String(255), unique=True, nullable=False,primary_key=True)
    Movie_title = db.Column(db.String(255), nullable=False)
    Rating      = db.Column(db.Integer)
    def __repr__(self):
        return "<Rating: {}>".format(self.Rating)
class User(db.Model):
    __tablename__ = "Users"
    Username    = db.Column(db.String(255), unique=True, nullable=False,primary_key=True)
    First_name  = db.Column(db.String(255), nullable=False)
    Last_name   = db.Column(db.String(255))
    def __repr__(self):
        return "<Username: {}>".format(self.Username)

@app.route("/", methods=["get"])
def home():
    return "Home Page Movie App";
@app.route("/api/search-movie", methods=["POST"])
def search():
    title = request.form.get("title")
    if(title ==''):
        return {'code':403,'message':"Search Keyword is required"},403
    movies = Movie.query.filter(Movie.Movie_title.like('%' + title + '%'))
    movies = movies.order_by(Movie.Movie_title).all()
    search_result = requests.get('https://www.omdbapi.com/?t='+str(title)+'&apikey=add5d497')
    data = []
    file_name = "movie_xml_file"+ secrets.token_hex(5) +".xml"
    if(movies):
        i=0
        for movie in movies:
            data.append({'title':movie.Movie_title,'year':movie.Release_year,'Plot_description':movie.Plot_description,'genre':movie.Genre,'Average_rating':movie.Average_Rating,'Number_of_votes':movie.Number_of_votes})
            i = i+1
        ##create XML FIle
        create_xml(data,file_name)
        return jsonify({'code':200,'message':'Movies Found','data':search_result.json(),'xml_file':file_name})
    return {'code':404,'message':"No Record Found"},404

@app.route("/api/rating", methods=['GET',"POST"])
def rating():
    Ratings = None
    if request.method == 'POST':
        if request.form:
            try:
                
                
                last_name   = str(request.form.get("last_name"))
                
                if(request.form.get("rating")):
                    rating      = str(request.form.get("rating"))
                else:
                    return {'code':403,'message':"Rating is required"},403
                if(request.form.get("first_name")):
                    first_name  = str(request.form.get("first_name"))
                else:
                    return {'code':403,'message':"First name is required"},403
                if(request.form.get("movie")):
                    movie_title = str(request.form.get("movie"))
                else:
                    return {'code':403,'message':"Movie title is required"},403
                usernames = str(slugify(first_name));
                users       = User.query.filter(User.Username ==usernames).all()
                username    = ''             
                for user in users:
                    username = str(user.Username)
                if(username !=''):
                    rating_data = Rating(Username=username,Rating=rating,Movie_title=movie_title)
                    db.session.add(rating_data)
                    db.session.commit()
                    return jsonify({'code':200,'message':'Rating Added'})
                else:
                    username = slugify(first_name)
                    user_data = User(Username=username,First_name=first_name,Last_name=last_name)
                    db.session.add(user_data)
                    db.session.commit()
                    ## Add Rating...
                    rating_data = Rating(Username=username,Rating=rating,Movie_title=movie_title)
                    db.session.add(rating_data)
                    db.session.commit()
                    return jsonify({'code':200,'message':'Rating Added!'})
            except Exception as e:
                return jsonify({'code':200,'message':'Failed to add Rating','error':str(e)})
    else:
        return {'code':404,'message':"Pleas try again!!"},404
def create_xml(d,file_name):
    r = e.Element("Movie")
    
    for z in d:
        e.SubElement(r,"Title").text = z["title"]
        e.SubElement(r,"Year").text = str(z["year"])
        e.SubElement(r,"Description").text = z["Plot_description"]
        e.SubElement(r,"Average_rating").text = str(z["Average_rating"])
        e.SubElement(r,"Number_of_votes").text = str(z["Number_of_votes"])
        e.SubElement(r,"genre").text = str(z["genre"])
        a = e.ElementTree(r)
        a.write(file_name)

if __name__ == "__main__":
    db.create_all()
    app.run(host='localhost', port=8087, debug=True)
