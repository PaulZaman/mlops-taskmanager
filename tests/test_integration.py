# tests/test_integration.py
import os
import sys
import pytest
from flask import Flask

# Ajouter la racine du projet (flask_app) au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from extensions import db
from models import User, Task  # noqa: F401
from app import register_routes
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(PROJECT_ROOT)

@pytest.fixture
def client():
    """
    App Flask minimale pour les tests d'intégration, avec SQLite en mémoire.
    On indique explicitement où se trouvent les templates.
    """
    templates_dir = os.path.join(PROJECT_ROOT, "templates")

    app = Flask(__name__, template_folder=templates_dir)
    app.config["SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    register_routes(app)

    with app.app_context():
        db.create_all()
        yield app.test_client()


# 1) Register + Login flow
def test_register_and_login(client):
    # Register
    resp = client.post(
        "/register",
        data={
            "username": "alice",
            "password": "secret123",
            "confirm": "secret123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    # Login
    resp = client.post(
        "/login",
        data={
            "username": "alice",
            "password": "secret123",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    # On ne fait pas d'assertions strictes sur le HTML, juste que ça marche


# 2) Create task via POST /tasks/new
def test_create_task(client):
    # Créer un user et le log in
    client.post(
        "/register",
        data={
            "username": "bob",
            "password": "pass",
            "confirm": "pass",
        },
        follow_redirects=True,
    )
    client.post(
        "/login",
        data={
            "username": "bob",
            "password": "pass",
        },
        follow_redirects=True,
    )

    # Créer une tâche
    resp = client.post(
        "/tasks/new",
        data={
            "title": "My Task",
            "description": "Test desc",
            "due_date": "",
        },
        follow_redirects=True,
    )

    assert resp.status_code == 200
    assert b"My Task" in resp.data


# 3) Toggle task via POST /tasks/<id>/toggle
def test_toggle_task(client):
    # Créer user + login
    client.post(
        "/register",
        data={
            "username": "carol",
            "password": "abc",
            "confirm": "abc",
        },
        follow_redirects=True,
    )
    client.post(
        "/login",
        data={
            "username": "carol",
            "password": "abc",
        },
        follow_redirects=True,
    )

    # Créer une tâche
    resp = client.post(
        "/tasks/new",
        data={
            "title": "Toggle Task",
            "description": "",
            "due_date": "",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    # Toggle la tâche avec id 1 (première tâche de la base de test)
    resp = client.post("/tasks/1/toggle", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Toggle Task" in resp.data
