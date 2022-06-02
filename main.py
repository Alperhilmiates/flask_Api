from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

movie_db = 'sqlite:///top_movies.db'
app.config['SQLALCHEMY_DATABASE_URI'] = movie_db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api_key = '51b90a95d5f14acdf23f8b60a8d97326'
api_token = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1MWI5MGE5NWQ1ZjE0YWNkZjIzZjhiNjBhOGQ5NzMyNiIsInN1YiI6IjYyNWIyOTkwZGQ3MzFiMDA2NzAyZjU5NCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Olgg9WiqwDHWDbGYTeuIyq9BqKtnscgYOWbVL0soh2I'
api_request_example = 'https://api.themoviedb.org/3/movie/550?api_key=51b90a95d5f14acdf23f8b60a8d97326'


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(240), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(240), nullable=True)
    img_url = db.Column(db.String(240),  nullable=False)

    def __repr__(self):
        return '<Movie %r>' % self.title

if not os.path.isfile(movie_db):
    db.create_all()

class RateMovieForm(FlaskForm):
    new_rating = FloatField(label="Your Rating out of 10 eg: 7.5", validators=[DataRequired()])
    new_review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField('Done')

class AddMovieForm(FlaskForm):
    movie_title = StringField(label='Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

@app.route("/")
def home():
    # all_movies = db.session.query.(Movies).all()
    # print(all_movies)
    # ranking= 1
    # rating = 0
    # loop= True
    # loop_time = 0
    # for movies in all_movies:
    #     if movies.rating > rating:
    #         rating = movies.rating
    # while loop:
    #     for movies in all_movies:
    #         loop_time += 1
    #         print(movies.rating)
    #         print(rating)
    #         print(ranking)
    #         if movies.rating == rating:
    #             print('here')
    #             movies.ranking = ranking
    #             db.session.commit()
    #             ranking += 1
    #     rating = round(rating - 0.1, ndigits=1)
    #     if loop_time > 500:
    #         loop = False
    all_movies = Movies.query.order_by(Movies.rating).all()
    for i in range(len(all_movies)):
        #This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    return render_template("index.html", all_movies=all_movies)

@app.route("/edit<int:num>", methods= ["GET", "POST"])
def edit(num):
    rate_form = RateMovieForm()
    movie_id = num
    if rate_form.validate_on_submit():
        new_rating = rate_form.new_rating.data
        new_review = rate_form.new_review.data
        movie_update = Movies.query.get(movie_id)
        movie_update.rating = new_rating
        movie_update.review = new_review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", rate_form=rate_form, movie_id=num)

@app.route("/delete", methods= ["GET", "POST"])
def delete():
    movie_id = request.args.get('id')
    movie_delete = Movies.query.get(movie_id)
    db.session.delete(movie_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/addmovie", methods= ["GET","POST"])
def addmovie():
    add_form = AddMovieForm()
    if add_form.validate_on_submit():
        movie_search_title = add_form.movie_title.data
        respond = requests.request(url= f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=en-US&query={movie_search_title}&page=1&include_adult=false", method= 'GET')
        respond_json = respond.json()
        result_movies = respond_json['results']
        print(result_movies)
        # for movie_json in respond_json['results']:
        #     if movie_json['original_title'].lower() == movie_search_title.lower():
        #         print(movie_json)
        return render_template('select.html', result_movies= result_movies)
    return render_template("add.html", add_form=add_form)

@app.route("/moviedetail", methods= ["GET","POST"])
def moviedetail():
    movie_search_id = request.args.get('id')
    # respond_movie_img = requests.get(f'https://api.themoviedb.org/3/movie/{movie_search_id}/images?api_key={api_key}&language=en-US')
    respond_detail = requests.request(url= f'https://api.themoviedb.org/3/movie/{movie_search_id}?api_key={api_key}', method= 'GET')
    movie_title = respond_detail.json()['title']
    movie_img_url = respond_detail.json()['poster_path']
    movie_img_url_full_path = f'https://image.tmdb.org/t/p/w500{movie_img_url}'
    movie_year = respond_detail.json()['release_date']
    movie_description = respond_detail.json()['overview']
    add_new_movie = Movies(title= movie_title, year= movie_year, description= movie_description, rating= None, ranking= None, review= None, img_url=movie_img_url_full_path)
    db.session.add(add_new_movie)
    db.session.commit()
    movie_added = Movies.query.filter_by(title=movie_title).first()
    return redirect(url_for('edit',num=movie_added.id))

# new_movie = Movies(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")
#
# db.session.add(new_movie)
# db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
