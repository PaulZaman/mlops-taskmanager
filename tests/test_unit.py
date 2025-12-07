# tests/test_unit.py
import os
import sys
from datetime import date, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from datetime import date, timedelta

from models import User, Task


def test_set_password_and_check_password():
    user = User(username="alice")

    user.set_password("secret123")

    # le mot de passe en clair ne doit pas être stocké
    assert user.password_hash != "secret123"
    assert user.password_hash is not None

    # check_password doit renvoyer True pour le bon mot de passe
    assert user.check_password("secret123") is True
    # et False pour un mauvais
    assert user.check_password("wrong") is False


def test_task_not_overdue_if_no_due_date_or_completed():
    # pas de due_date
    task1 = Task(title="Test 1", user_id=1, due_date=None, is_completed=False)
    assert task1.is_overdue() is False

    # tâche complétée même si due_date passée
    past_date = date.today() - timedelta(days=5)
    task2 = Task(title="Test 2", user_id=1, due_date=past_date, is_completed=True)
    assert task2.is_overdue() is False


def test_task_is_overdue_only_when_past_and_not_completed():
    past_date = date.today() - timedelta(days=1)
    today = date.today()
    future_date = date.today() + timedelta(days=3)

    # due_date passée et non complétée → overdue = True
    overdue_task = Task(title="Overdue", user_id=1, due_date=past_date, is_completed=False)
    assert overdue_task.is_overdue() is True

    # due_date aujourd'hui → pas encore en retard
    today_task = Task(title="Today", user_id=1, due_date=today, is_completed=False)
    assert today_task.is_overdue() is False

    # due_date future → pas en retard
    future_task = Task(title="Future", user_id=1, due_date=future_date, is_completed=False)
    assert future_task.is_overdue() is False
