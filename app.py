from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import datetime
import secrets

app = Flask(__name__)

# Configure the SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(32)

db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Boolean, default=True)


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


# Token Authentication Decorator
def token_required(f):
    """
       Decorator to ensure a valid JWT token is present in the request headers.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing!'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'})
        except InvalidTokenError:
            return jsonify({'message': 'Invalid token!'})

        return f(*args, **kwargs)

    return decorated


# Generate Token Route
@app.route('/login', methods=['POST'])
def login():
    """
        Generate a JWT token for a user after validating credentials.
    """
    auth = request.json

    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify!', 'WWW-Authenticate': 'Basic auth="Login required"'})

    # Replace with real authentication logic
    if auth['username'] == 'rosansen' and auth['password'] == 'rosansen7':
        token = jwt.encode({
            'user': auth['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials!'})


# Book Routes
@app.route('/get_books', methods=['GET'])
@token_required
def get_books():
    """
        Fetch all books in the library.
    """
    books = Book.query.all()
    return jsonify([{
        'book_id': book.id,
        'title': book.title,
        'author': book.author,
        'available': book.available
    } for book in books])


@app.route('/get_book_author/<string:author_name>', methods=['GET'])
@token_required
def get_book_author(author_name):
    """
        Fetch a book by the author's name (case-insensitive).
        """
    book = Book.query.filter(Book.author.ilike(f"%{author_name}%")).all()[0]

    if book and book.available:
        return jsonify({
            'book_id': book.book_id,
            'title': book.title,
            'author': book.author,
            'available': book.available
        })
    return jsonify({'error': 'Book not found'})


@app.route('/get_book_title/<string:name>', methods=['GET'])
@token_required
def get_book_title(name):
    """
        Fetch a book by its title (case-insensitive).
        """
    book = Book.query.filter(Book.title.ilike(f"%{name}%")).all()[0]
    if book and book.available:
        return jsonify({
            'book_id': book.book_id,
            'title': book.title,
            'author': book.author,
            'available': book.available
        })
    return jsonify({'error': 'Book not found'})


@app.route('/add_book', methods=['POST'])
@token_required
def add_book():
    """
        Add books to the library.
    """
    datas = request.json
    for data in datas.get("books"):
        new_book = Book(
            book_id=data.get("id"),
            title=data.get("title"),
            author=data.get("author"),
            available=True if data.get("available") == "True" else False
        )
        db.session.add(new_book)
    db.session.commit()
    return jsonify({
        'result': 'all books added'
    })


@app.route('/update_book/<int:book_id>', methods=['PUT'])
@token_required
def update_book(book_id):
    """
       Update details of an existing book in the library.
    """
    data = request.json
    book = Book.query.filter_by(book_id=book_id).first()
    if not book:
        return jsonify({'error': 'Book not found'})

    book.book_id = data.get('id',book.book_id)
    book.title = data.get('title', book.title)
    book.author = data.get('author',book.author)
    book.available = False if data.get("available",book.available)=="False" else True
    db.session.commit()
    return jsonify({
        'book_id': book.book_id,
        'title': book.title,
        'author': book.author,
        'available': book.available
    })


@app.route('/delete_book/<int:book_id>', methods=['PUT'])
@token_required
def delete_book(book_id):
    """
        Delete a book from the library by its ID.
        """
    book = Book.query.filter_by(book_id=book_id).first()
    if not book:
        return jsonify({'error': 'Book not found'})

    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})


# Member Routes
@app.route('/get_members', methods=['GET'])
@token_required
def get_members():
    """
        Fetch all members of the library.
    """
    members = Member.query.all()
    return jsonify([{
        'member_id': member.member_id,
        'name': member.name,
        'email': member.email
    } for member in members])


@app.route('/get_member/<int:get_id>', methods=['GET'])
@token_required
def get_member(get_id):
    """
        Fetch details of a specific member by ID.
        """
    member = Member.query.filter_by(member_id=get_id).first()
    if member:
        return jsonify({
            'id': member.id,
            'name': member.name,
            'email': member.email
        })
    return jsonify({'error': 'Member not found'})


@app.route('/add_member', methods=['POST'])
@token_required
def add_member():
    """
        Add a new member to the library.
        """
    data = request.json
    new_member = Member(
        member_id=data['id'],
        name=data['name'],
        email=data['email']
    )
    db.session.add(new_member)
    db.session.commit()
    return jsonify({
        'member_id': new_member.id,
        'name': new_member.name,
        'email': new_member.email
    })


@app.route('/update_member/<int:update_id>', methods=['PUT'])
@token_required
def update_member(update_id):
    """
        Update details of an existing member by id.
        """
    member = Member.query.filter_by(member_id=update_id).first()
    if not member:
        return jsonify({'error': 'Member not found'})

    member.name = request.form.get("name", member.name)
    member.email = request.form.get("email", member.email)
    db.session.commit()
    return jsonify({
        'member_id': member.member_id,
        'name': member.name,
        'email': member.email
    })


@app.route('/delete_member/<int:delete_id>', methods=['DELETE'])
@token_required
def delete_member(delete_id):
    """
        Delete a member from the library by ID.
        """
    member = Member.query.filter_by(member_id=delete_id).first()
    if not member:
        return jsonify({'error': 'Member not found'})

    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted'})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()
