from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://localhost/books-authors'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

modus = Modus(app)

class Author(db.Model):

    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    books = db.relationship('Book', cascade="all, delete-orphan", backref='author', lazy='dynamic')

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return "Full author name is {} {}".format(self.first_name, self.last_name)


class Book(db.Model):

    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    def __init__(self, title, author_id):
        self.title = title
        self.author_id = author_id

    def __repr__(self):
        return "Book title: {}".format(self.title)

@app.route('/')
def root():
    return redirect(url_for('index'))


# =============================================================================
# routes for authors
# =============================================================================
@app.route('/authors', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        db.session.add(Author(first_name, last_name))
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('authors/index.html', authors=Author.query.all())


@app.route('/authors/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def show(id):
    if id in [author.id for author in Author.query.all()]:
        found_author = Author.query.get(id)
        if request.method == b'PATCH':
            found_author.first_name = request.form.get('first_name')
            found_author.last_name = request.form.get('last_name')

            db.session.add(found_author)
            db.session.commit()

            return redirect(url_for('index'))

        if request.method == b'DELETE':
            db.session.delete(found_author)
            db.session.commit()

            return redirect(url_for('index'))

        return render_template('authors/show.html', author=found_author)
    else:
        return render_template('404.html')


@app.route('/authors/<int:id>/edit')
def edit(id):
    if id in [author.id for author in Author.query.all()]:
        found_author = Author.query.get(id)
        return render_template('authors/edit.html', author=found_author)
    else:
        return render_template('authors/404.html')


@app.route('/authors/new')
def new():
    return render_template('authors/new.html')


# =============================================================================
# routes for books
# =============================================================================
@app.route('/authors/<int:author_id>/books', methods=['GET', 'POST'])
def index_books(author_id):
    if author_id in [author.id for author in Author.query.all()]:
        if request.method == 'POST':
            title = request.form.get('title')
            db.session.add(Book(title, author_id))
            db.session.commit()

            return redirect(url_for('index'))
        else:
            author = Author.query.get(author_id)
            books = author.books.all()

            return render_template('books/index.html', books=books)
    else:
        return render_template('404.html')


@app.route('/authors/<int:author_id>/show/<int:book_id>', methods=['GET', 'PATCH', 'DELETE'])
def show_book(author_id, book_id):
    if author_id in [author.id for author in Author.query.all()] and book_id in [book.id for book in Book.query.all()]:
        found_book = Book.query.get(book_id)
        if request.method == b'PATCH':
            found_book.title = request.form.get('title')

            db.session.add(found_book)
            db.session.commit()

            return redirect(url_for('index_books', author_id=author_id))

        if request.method == b'DELETE':
            db.session.delete(found_book)
            db.session.commit()

            return redirect(url_for('index_books', author_id=author_id))

        return render_template('books/show.html', book=found_book)


@app.route('/authors/<int:author_id>/edit/<int:book_id>')
def edit_book(author_id, book_id):
    if author_id in [author.id for author in Author.query.all()] and book_id in [book.id for book in Book.query.all()]:
        found_book = Book.query.get(book_id)
        return render_template('books/edit.html', book=found_book)
    else:
        return render_template('404.html')


@app.route('/authors/<int:author_id>/books/new')
def new_book(author_id):
    return render_template('books/new.html', author_id=author_id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(port=3002, debug=True)