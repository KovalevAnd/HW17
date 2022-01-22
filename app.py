# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


api = Api(app)
api.app.config['RESTFUL_JSON'] = {'ensure_ascii': False}

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
movie_ns = api.namespace('movies')

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)
director_ns = api.namespace('directors')

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)
genre_ns = api.namespace('genres')


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        director_id = request.args.get('director_id', '%%')
        genre_id = request.args.get('genre_id', '%%')
        all_movies = Movie.query.filter(Movie.director_id.like(director_id), Movie.genre_id.like(genre_id)).paginate(
            page, 5, False).items
        return jsonify(movies_schema.dump(all_movies), 200)

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movie_ns.route('/<int:uid>')
class MoviesView(Resource):
    def get(self, uid: int):
        movie = Movie.query.get(uid)
        if not movie:
            return '404', 404
        return jsonify(movie_schema.dump(movie), 200)

    def put(self, uid):
        movie = Movie.query.get(uid)
        req_json = request.json
        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        movie.genre_id = req_json.get("genre_id")
        movie.director_id = req_json.get("director_id")
        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, uid: int):
        movie = Movie.query.get(uid)
        db.session.delete(movie)
        db.session.commit()
        return "", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = Director.query.all()
        return jsonify(directors_schema.dump(all_directors), 200)


@director_ns.route('/<int:uid>')
class DirectorsView(Resource):
    def get(self, uid: int):
        director = Director.query.get(uid)
        if not director:
            return '404', 404
        return jsonify(director_schema.dump(director), 200)


@genre_ns.route('/')
class GenreView(Resource):
    def get(self):
        all_genres = Genre.query.all()
        return jsonify(genres_schema.dump(all_genres), 200)


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid: int):
        genre = Genre.query.get(uid)
        if not genre:
            return '404', 404
        return jsonify(genre_schema.dump(genre), 200)


if __name__ == '__main__':
    app.run(debug=True)
