import pytest
from app import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_library.db'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def auth_token(client):
    """Helper fixture to get a valid authentication token."""
    response = client.post('/login', json={"username": "rosansen", "password": "rosansen7"})
    assert response.status_code == 200
    return response.json['token']


def test_login_success(client):
    response = client.post('/login', json={"username": "rosansen", "password": "rosansen7"})
    assert response.status_code == 200
    assert 'token' in response.json


def test_login_failure(client):
    response = client.post('/login', json={"username": "wrong", "password": "wrong"})
    assert response.status_code == 200
    assert response.json['message'] == 'Invalid credentials!'


def test_get_books_empty(client, auth_token):
    headers = {'x-access-token': auth_token}
    response = client.get('/get_books', headers=headers)
    assert response.status_code == 200
    assert response.json == []


def test_add_book(client, auth_token):
    headers = {'x-access-token': auth_token}
    book_data = {
        "books": [
            {"id": 1, "title": "Book One", "author": "Author A", "available": "True"},
            {"id": 2, "title": "Book Two", "author": "Author B", "available": "False"},
            {"id": 3, "title": "Book Three", "author": "Author C", "available": "True"}
        ]
    }
    response = client.post('/add_book', json=book_data, headers=headers)
    assert response.status_code == 200
    assert response.json['result'] == 'all books added'

    # Verify books are added
    response = client.get('/get_books', headers=headers)
    assert len(response.json) == 3


def test_update_book(client, auth_token):
    headers = {'x-access-token': auth_token}
    # Add a book first
    book_data = {
        "books": [
            {"id": 1, "title": "Book One", "author": "Author A", "available": "True"}
        ]
    }
    client.post('/add_book', json=book_data, headers=headers)

    # Update the book
    update_data = {"title": "Updated Book", "available": "False"}
    response = client.put('/update_book/1', json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json['title'] == "Updated Book"
    assert response.json['available'] == False


def test_delete_book(client, auth_token):
    headers = {'x-access-token': auth_token}
    # Add a book first
    book_data = {
        "books": [
            {"id": 1, "title": "Book One", "author": "Author A", "available": "True"}
        ]
    }
    client.post('/add_book', json=book_data, headers=headers)

    # Delete the book
    response = client.put('/delete_book/1', headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Book deleted'

    # Verify deletion
    response = client.get('/get_books', headers=headers)
    assert len(response.json) == 0


def test_add_member(client, auth_token):
    headers = {'x-access-token': auth_token}
    member_data = {
        "id": 1,
        "name": "Member One",
        "email": "member1@gmail.com"
    }
    response = client.post('/add_member', json=member_data, headers=headers)
    assert response.status_code == 200
    assert response.json['name'] == "Member One"


def test_get_members(client, auth_token):
    headers = {'x-access-token': auth_token}
    # Add a member first
    member_data = {
        "id": 1,
        "name": "Member One",
        "email": "member1@example.com"
    }
    client.post('/add_member', json=member_data, headers=headers)

    # Get members
    response = client.get('/get_members', headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['name'] == "Member One"


def test_delete_member(client, auth_token):
    headers = {'x-access-token': auth_token}
    # Add a member first
    member_data = {
        "id": 1,
        "name": "Member One",
        "email": "member1@example.com"
    }
    client.post('/add_member', json=member_data, headers=headers)

    # Delete the member
    response = client.delete('/delete_member/1', headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Member deleted'

    # Verify deletion
    response = client.get('/get_members', headers=headers)
    assert len(response.json) == 0
