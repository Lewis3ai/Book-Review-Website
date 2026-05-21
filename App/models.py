from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Book(db.Model):
    __tablename__ = 'book'

    isbn = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    publication_year = db.Column(db.Integer)
    publisher = db.Column(db.String(150))
    image = db.Column(db.String(500))

    reviews = db.relationship('Review', back_populates='book', cascade='all, delete-orphan')

    @property
    def avg_rating(self):
        if not self.reviews:
            return None
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)

    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    isbn = db.Column(db.String(20), db.ForeignKey('book.isbn'), nullable=False)

    user = db.relationship('User', back_populates='reviews')
    book = db.relationship('Book', back_populates='reviews')

    def __repr__(self):
        return f'<Review rating={self.rating} for isbn={self.isbn}>'

