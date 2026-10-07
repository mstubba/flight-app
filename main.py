import os
import secrets
from contextlib import contextmanager

import psycopg2
from flask import Flask, abort, render_template, request, session

# Konfiguracja bazy: w Kubernetes przychodzi ze zmiennych środowiskowych,
# lokalnie działają wartości domyślne (Postgres na localhost:5433).
DB_CONFIG = {
    "dbname": os.environ.get("POSTGRES_DB", "postgres"),
    "user": os.environ.get("POSTGRES_USER", "postgres"),
    "password": os.environ.get("POSTGRES_PASSWORD", "password"),
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "port": int(os.environ.get("POSTGRES_PORT", "5433")),
}


@contextmanager
def db_connection():
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def dbtest():
    """Ręczny test połączenia z bazą (do uruchamiania lokalnie, nie przez Flask)."""
    print("Losowy token:", secrets.token_hex(16))
    with db_connection() as cur:
        cur.execute("SELECT version();")
        print("PostgreSQL:", cur.fetchone())

    with db_connection() as cur:
        cur.execute("SELECT 1;")
        print("Wynik SELECT 1:", cur.fetchone())

    with db_connection() as cur:
        cur.execute("SELECT * FROM states;")
        print("Pierwszy wiersz z states:", cur.fetchone())


app = Flask(__name__)
# W klastrze stały klucz z Secretu; losowy tylko jako awaryjna wartość lokalnie.
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(16)


@app.route("/", methods=["GET", "POST"])
def sign_up():
    return render_template("sign-up.html")


@app.route("/sign-in", methods=["GET"])
def sign_in():
    return render_template("sign-in.html")


@app.route("/shop", methods=["POST"])
def shop_page():
    # Formularz rozpoznajemy po polach, a nie po nagłówku Referer:
    # rejestracja wysyła e-mail, logowanie nie.
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        abort(400)

    if "email" in request.form:
        email = request.form["email"]
        # TODO: zapis nowego użytkownika (hasło przez generate_password_hash)
    else:
        # TODO: weryfikacja hasła (check_password_hash)
        pass

    session["username"] = username
    return render_template("shop.html", name=username)


flight_object = {
    "departure": "California",
    "destination": "Wyoming",
    "departure_time": "2025-08-07 06:00",
    "arrival_time": "2025-08-17 01:00",
    "price": 371.92,
}


@app.route("/ticket", methods=["POST"])
def ticket_page():
    if "buy-departure" not in request.form:
        abort(400)

    departure = request.form["buy-departure"]
    destination = request.form["buy-destination"]
    # Docelowo zapytanie z parametrami (bez f-stringa, chroni przed SQL injection):
    # with db_connection() as cur:
    #     cur.execute(
    #         "SELECT * FROM flights WHERE arrival_state = %s AND departure_state = %s",
    #         (destination, departure),
    #     )
    #     flight_match = cur.fetchall()
    # flight_object = {"departure": flight_match[0][1], "destination": flight_match[0][2],
    #                  "departure_time": flight_match[0][3].strftime("%Y-%m-%d %H:%M"),
    #                  "arrival_time": flight_match[0][4].strftime("%Y-%m-%d %H:%M"),
    #                  "price": flight_match[0][5]}
    return render_template("ticket.html", action="buy", flight=flight_object)


@app.route("/health")
def health():
    return {"status": "ok"}


# Tymczasowa trasa do testu bazy - usuń albo zabezpiecz po testach.
@app.route("/dbcheck")
def dbcheck():
    with db_connection() as cur:
        cur.execute("SELECT version();")
        return {"postgres": cur.fetchone()[0]}


if __name__ == "__main__":
    # Tylko lokalnie. W kontenerze aplikację uruchamia gunicorn (patrz Dockerfile).
    app.run(host="0.0.0.0", port=5000, debug=True)