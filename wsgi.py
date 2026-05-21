import csv
import os
import click
from App import create_app
from App.models import db, User, Book, Review

app = create_app()


@app.cli.command('init')
def initialize():
    with app.app_context():
        db.create_all()
        print('Database tables created.')
        _seed_books()
        print('Done.')


def _seed_books():
    csv_path = os.path.join(os.path.dirname(__file__), 'books.csv')
    if not os.path.exists(csv_path):
        print('books.csv not found, skipping seed.')
        return

    count = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            isbn = str(row.get('isbn', '')).strip()
            if not isbn:
                continue
            if Book.query.filter_by(isbn=isbn).first():
                continue
            book = Book(
                isbn=isbn,
                title=row.get('title', '').strip(),
                author=row.get('author', '').strip(),
                publication_year=int(row['pub_year']) if row.get('pub_year', '').strip().isdigit() else None,
                publisher=row.get('publisher', '').strip(),
                image=row.get('image_medium', '').strip() or row.get('image_small', '').strip(),
            )
            db.session.add(book)
            count += 1
    db.session.commit()
    print(f'Seeded {count} books.')


@app.cli.command('create-user')
@click.argument('username')
@click.argument('password')
def create_user_command(username, password):
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print(f"Error: user '{username}' already exists.")
            return
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        print(f"User '{username}' created successfully.")


@app.cli.command('list-books')
def list_books():
    with app.app_context():
        books = Book.query.order_by(Book.title).all()
        if not books:
            print('No books in database. Run: flask init')
            return
        for b in books:
            print(f'[{b.isbn}] {b.title} — {b.author} ({b.publication_year})')


@app.cli.command('list-users')
def list_users():
    with app.app_context():
        users = User.query.all()
        for u in users:
            print(f'[{u.id}] {u.username} — {len(u.reviews)} reviews')


