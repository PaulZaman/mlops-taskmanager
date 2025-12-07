# tests/test_e2e.py
import os
import sys
import uuid

import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# permettre d'importer si besoin des modules du projet
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

BASE_URL = os.getenv("E2E_BASE_URL", "http://127.0.0.1:5001")


@pytest.fixture
def driver():
    """Instancie un navigateur Chrome headless."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def _submit_form(driver):
    # bouton ou input submit
    submit = driver.find_element(
        By.XPATH, "//form//button[@type='submit'] | //form//input[@type='submit']"
    )
    submit.click()


def register_and_login(driver, username=None, password="secret123"):
    """Inscription + login via l'UI, retourne le username utilisé."""
    if username is None:
        username = f"user_{uuid.uuid4().hex[:6]}"

    # --- Register ---
    driver.get(BASE_URL + "/register")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confirm").send_keys(password)
    _submit_form(driver)

    # on doit arriver sur /login
    WebDriverWait(driver, 10).until(EC.url_contains("/login"))

    # --- Login ---
    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    _submit_form(driver)

    # on doit être redirigé vers la page d'accueil
    WebDriverWait(driver, 10).until(
        lambda d: d.current_url.rstrip("/") == BASE_URL.rstrip("/")
        or d.current_url.startswith(BASE_URL + "/?"),
    )
    return username


def create_task_via_ui(driver, title="E2E Task", description="desc"):
    """Crée une task via /tasks/new."""
    driver.get(BASE_URL + "/tasks/new")
    driver.find_element(By.NAME, "title").send_keys(title)
    driver.find_element(By.NAME, "description").send_keys(description)
    # due_date optionnelle → on peut laisser vide
    _submit_form(driver)

    # retour à la page d'index
    WebDriverWait(driver, 10).until(
        lambda d: d.current_url.startswith(BASE_URL + "/")
    )
    return title


# ------------------------ 1) Login flow ------------------------ #
def test_login_flow_e2e(driver):
    register_and_login(driver)
    # on vérifie qu'on est bien "loggé" (présence d'un élément typique)
    page = driver.page_source
    assert "Logout" in page or "Task" in page or "Title" in page


# ------------------------ 2) Création de tâche ------------------------ #
def test_create_task_e2e(driver):
    register_and_login(driver)
    title = "My E2E Task"
    create_task_via_ui(driver, title=title, description="from selenium")

    page = driver.page_source
    assert title in page


# ------------------------ 3) Toggle d'une tâche ------------------------ #
def test_toggle_task_e2e(driver):
    register_and_login(driver)
    title = "Toggle E2E Task"
    create_task_via_ui(driver, title=title)

    # on cherche un formulaire / bouton qui cible /tasks/<id>/toggle
    toggle_button = driver.find_element(
        By.XPATH, "//form[contains(@action, '/tasks/') and contains(@action, '/toggle')]"
                  "//button[@type='submit'] | "
                  "//form[contains(@action, '/tasks/') and contains(@action, '/toggle')]"
                  "//input[@type='submit']"
    )
    toggle_button.click()

    # si pas d'erreur serveur, la page se recharge
    WebDriverWait(driver, 10).until(
        lambda d: d.current_url.startswith(BASE_URL + "/")
    )
    page = driver.page_source
    assert title in page  # la tâche est toujours listée, mais avec statut changé côté backend
