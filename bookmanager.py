import os

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect

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

    def __repr__(self):
        return "<Title: {}>".format(self.title)


@app.route("/", methods=["GET", "POST"])
def home():
    movies = None
    if request.form:
        try:
            movie = Movie(Movie_title=request.form.get("title"))
            db.session.add(movie)
            db.session.commit()
        except Exception as e:
            print("Failed to add movie")
            print(e)
    movies = Movie.query.all()
    return render_template("home.html", movies=movies)


@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle")
        oldtitle = request.form.get("oldtitle")
        movie = Movie.query.filter_by(Movie_title=oldtitle).first()
        movie.Movie_title = newtitle
        db.session.commit()
    except Exception as e:
        print("Couldn't update Movie title")
        print(e)
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    movie = Movie.query.filter_by(Movie_title=title).first()
    db.session.delete(movie)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0', port=8087, debug=True)
