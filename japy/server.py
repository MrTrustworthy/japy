from random import choice
from typing import Optional
from os import environ
from flask import Flask, session, request, render_template, redirect, url_for, flash

from japy.db_wrapper import ensure_tables, get_valid_vocables, make_new_session, register_chars_for_session, \
    get_vocables_for_session, add_log_entry, get_syllable_for_id, get_possible_session_configs, CharacterInfo

app = Flask(__name__)
app.secret_key = environ["COOKIE"]
ensure_tables()


def make_user_session(vocabulary: str, charset: str, *, limit: int = None, limit_min: int = 5) -> int:
    chars_in_scope = get_valid_vocables(vocabulary, charset)
    limit = max(min(limit, len(chars_in_scope)), limit_min)
    if limit is not None and limit > 0:
        chars_in_scope = [choice(chars_in_scope) for _ in range(limit)]

    training_session_id = make_new_session()
    register_chars_for_session(training_session_id, chars_in_scope)
    return training_session_id


def get_random_char(session_id: int, exclude: Optional[int]) -> CharacterInfo:
    chars = get_vocables_for_session(session_id)
    char_to_use = choice(chars)
    if exclude is not None and char_to_use.id == exclude:
        return get_random_char(session_id, exclude)
    return char_to_use


@app.route('/sessions', methods=["GET"])
def session_landingpage():
    session.pop("training_session_id", None)
    session.pop("current_char_id", None)
    config = get_possible_session_configs()
    return render_template("sessions.html", config=config)


@app.route('/sessions', methods=["POST"])
def session_handler():
    vocab, charset = request.form["vocabAndCharset"].split("/")
    number = int(request.form["vocableNumber"])
    training_session_id = make_user_session(vocab, charset, limit=number)
    session["training_session_id"] = training_session_id
    return redirect(url_for("index_handler"))


@app.route('/', methods=["GET"])
def index_handler():
    if not session.get("training_session_id", None):
        return redirect(url_for("session_landingpage"))

    char_to_use = get_random_char(session["training_session_id"], session.get("current_char_id", None))
    session["current_char_id"] = char_to_use.id
    return render_template("index.html", vocable=char_to_use.vocable)


@app.route('/submit', methods=["POST"])
def submit_handler():
    guessed = request.form.get("syllable").lower()

    char_id = session["current_char_id"]
    training_session_id = session["training_session_id"]
    correct = get_syllable_for_id(char_id)
    message = "Correct!" if guessed == correct else f"Sorry, the correct answer was {correct}"

    add_log_entry(training_session_id, char_id, guessed)

    flash(message, "SUBMITTED_STATUS")
    return redirect(url_for("index_handler"))

