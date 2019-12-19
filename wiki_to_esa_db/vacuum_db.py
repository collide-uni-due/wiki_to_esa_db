import sqlite3 as sql
import pathlib as pl

db_path = pl.Path("./data/esa.db")

conn = sql.connect(str(db_path))
with conn:
    conn.execute("VACUUM")
