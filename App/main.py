from flask import Blueprint, redirect, render_template, request, flash, url_for
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    current_user,
    set_access_cookies,
    unset_jwt_cookies,
)
from .models import db, Book, Review

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def login():
    return render_template('login.html')


@main_bp.route('/login', methods=['POST'])
def login_action():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash('Please enter both username and password.', 'error')
        return redirect(url_for('main.login'))

    from .models import User
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        response = redirect(url_for('main.home'))
        set_access_cookies(response, access_token)
        return response

    flash('Invalid username or password. Please try again.', 'error')
    return redirect(url_for('main.login'))


@main_bp.route('/app')
@jwt_required()
def home():
    books = Book.query.order_by(Book.title).all()
    return render_template('index.html', books=books, user=current_user)


@main_bp.route('/book/<isbn>')
@jwt_required()
def book_detail(isbn):
    book = Book.query.filter_by(isbn=isbn).first_or_404()
    reviews = Review.query.filter_by(isbn=isbn).order_by(Review.id.desc()).all()
    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)
    return render_template(
        'book_detail.html',
        book=book,
        reviews=reviews,
        avg_rating=avg_rating,
        user=current_user,
    )


@main_bp.route('/add-review/<isbn>', methods=['POST'])
@jwt_required()
def add_review(isbn):
    book = Book.query.filter_by(isbn=isbn).first_or_404()

    rating_raw = request.form.get('rating', '')
    text = request.form.get('text', '').strip()

    if not rating_raw or not text:
        flash('Please provide both a rating and a review.', 'error')
        return redirect(url_for('main.home') + f'?book={isbn}')

    try:
        rating = int(rating_raw)
    except ValueError:
        flash('Invalid rating value.', 'error')
        return redirect(url_for('main.home') + f'?book={isbn}')

    if not (1 <= rating <= 5):
        flash('Rating must be between 1 and 5.', 'error')
        return redirect(url_for('main.home') + f'?book={isbn}')

    if len(text) > 2000:
        flash('Review text must be 2000 characters or fewer.', 'error')
        return redirect(url_for('main.home') + f'?book={isbn}')

    review = Review(text=text, rating=rating, isbn=isbn, user_id=current_user.id)
    db.session.add(review)
    db.session.commit()
    flash('Your review was posted successfully!', 'success')
    return redirect(url_for('main.home') + f'?book={isbn}')


@main_bp.route('/logout')
def logout():
    response = redirect(url_for('main.login'))
    unset_jwt_cookies(response)
    flash('You have been logged out.', 'info')
    return response


@main_bp.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found.'), 404


@main_bp.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Something went wrong on our end.'), 500


