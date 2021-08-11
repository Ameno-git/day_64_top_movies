from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = "f18df7898ea8561c5dd1baa74171d160"
API_URL = "https://api.themoviedb.org/3/search/movie"
API_URL_ID = "https://api.themoviedb.org/3/movie/"
IMAGE_URL = "https://image.tmdb.org/t/p/w500/"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///video-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(4), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Float(250), nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


db.create_all()


class EditForm(FlaskForm):
    rating = StringField(label="Your Rating Out of 10 e.g. 7.5")
    review = StringField(label="Your Review")
    submit = SubmitField(label="Done")


class AddForm(FlaskForm):
    title = StringField(label="Movie title", validators=[DataRequired()])
    subnit = SubmitField(label="Add movie")


@app.route("/")
def home():
    # movie_list = Movie.query.order_by(Movie.rating).all()
    # for i in range(len(movie_list)):
    #     movie_list[i].ranking = len(movie_list) - i

    movie_list = db.session.query(Movie).order_by(Movie.rating.asc()).all()
    for movie in movie_list:
        movie.ranking = len(movie_list) - movie_list.index(movie)
    db.session.commit()
    return render_template("index.html", movie_list=movie_list)


@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = EditForm()
    movie_id = request.args.get("id")
    movie_to_edit = Movie.query.get(movie_id)
    if request.method == "POST":
        movie_to_edit.rating = form.rating.data
        movie_to_edit.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, movie=movie_to_edit)


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["POST", "GET"])
def add_movie():
    form = AddForm()
    if request.method == "POST":
        movie_name = form.title.data

        params = {
            "api_key": API_KEY,
            "query": movie_name,
            "include_adult": False
        }
        response = requests.get(API_URL, params=params)
        data = response.json()["results"]

        return render_template("select.html", data=data)
    return render_template("add.html", form=form)


@app.route("/select")
def select():
    movie_id = request.args.get("movie_id")
    params = {
        "api_key": API_KEY,
        "movie_id": movie_id
    }
    response = requests.get(API_URL_ID + movie_id, params=params)
    data = response.json()

    new_movie = Movie(
        title=data["original_title"],
        year=data["release_date"][0:4],
        description=data["overview"],
        img_url=IMAGE_URL + data["poster_path"],
    )
    db.session.add(new_movie)
    db.session.commit()

    return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
