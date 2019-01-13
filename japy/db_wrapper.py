from collections import namedtuple, defaultdict
from typing import Tuple, List, Dict

from .letters import LETTERS
from .db_connector import cursor

CharacterInfo = namedtuple("CharacterInfo", ["id", "vocable", "syllable"])


def _char_row_to_charinfo(rows: List[Tuple[int, str, str]]) -> List[CharacterInfo]:
    return [CharacterInfo(*args) for args in rows]


# SESSION UTILS
@cursor
def get_valid_vocables(c, vocabulary, chartype) -> List[CharacterInfo]:
    c.execute("SELECT id, vocable, syllable FROM vocables WHERE vocabulary=%s AND chartype=%s",
              (vocabulary, chartype))
    return _char_row_to_charinfo(c.fetchall())


@cursor
def get_vocables_for_session(c, session_id: int) -> List[CharacterInfo]:
    c.execute(
        """SELECT id, vocable, syllable FROM vocables WHERE id IN(SELECT vocableid FROM chars_in_sessions WHERE sessionid=%s)""",
        (session_id,))
    return _char_row_to_charinfo(c.fetchall())


@cursor
def make_new_session(c) -> int:
    c.execute("""INSERT INTO sessions DEFAULT VALUES""")
    c.execute("""SELECT currval('sessions_id_seq')""")
    return c.fetchone()[0]


@cursor
def register_chars_for_session(c, sessionid: int, vocables: List[CharacterInfo]):
    params = [(sessionid, vocable.id) for vocable in vocables]
    c.executemany("""INSERT INTO chars_in_sessions (sessionid, vocableid) VALUES (%s, %s)""", params)


@cursor
def add_log_entry(c, sessionid: int, vocableid: int, guessed: str):
    c.execute("""INSERT INTO guess_logs (sessionid, vocableid, guessed) VALUES (%s, %s, %s)""",
              (sessionid, vocableid, guessed))


@cursor
def get_syllable_for_id(c, vocableid: int) -> str:
    c.execute("""SELECT syllable FROM vocables WHERE id=%s""", (vocableid,))
    return c.fetchone()[0]


@cursor
def get_possible_session_configs(c) -> Dict[str, List[str]]:
    c.execute("""SELECT vocabulary, chartype FROM vocables GROUP BY vocabulary, chartype""")

    configs = defaultdict(list)
    for (v, c) in c.fetchall():
        configs[v].append(c)
    return configs


# MIGRATIONS
@cursor
def ensure_tables(c):
    ensure_vocable_table(c)
    ensure_log_tables(c)


def ensure_log_tables(c):
    c.execute(
        """CREATE TABLE IF NOT EXISTS guess_logs (id SERIAL PRIMARY KEY, sessionid INTEGER, vocableid INTEGER, guessed TEXT, entry TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute(
        """CREATE TABLE IF NOT EXISTS sessions (id SERIAL PRIMARY KEY, start TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    c.execute(
        """CREATE TABLE IF NOT EXISTS chars_in_sessions (sessionid INTEGER, vocableid INTEGER)""")


def ensure_vocable_table(c):

    c.execute("""CREATE TABLE IF NOT EXISTS vocables (id SERIAL PRIMARY KEY, vocabulary TEXT, chartype TEXT, vocable TEXT, syllable TEXT);""")

    c.execute("""SELECT count(*) FROM vocables""")
    if c.fetchone()[0] == 0:
        voc = "Hiragana"
        params = [(voc, chartype, l["vocable"], l["syllable"]) for chartype, letters in LETTERS.items() for l in letters]

        c.executemany("INSERT INTO vocables (vocabulary, chartype, vocable, syllable) VALUES (%s, %s, %s, %s)", params)
