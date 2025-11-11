import sqlite3, pathlib

schema = pathlib.Path("db/schema.sql").read_text()
conn = sqlite3.connect("db/Words.db")
conn.executescript(schema)
conn.close
