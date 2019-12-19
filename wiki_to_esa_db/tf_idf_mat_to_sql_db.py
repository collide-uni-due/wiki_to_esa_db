from gensim.corpora import Dictionary, MmCorpus
from gensim import utils
import time
import sqlite3 as sql
from wiki_to_esa_db.sql_statements import *

import pathlib as pl


del_articles_strings = ["list of", "liste der", "liste von"]

TF_IDF_THRESHOLD = 50
dp = pl.Path("data_de_snowball_stemmed")
tfidf_mat_path = dp / "corpus_tfidf.mm"

tfidf_corpus = MmCorpus(str(tfidf_mat_path))
id_to_titles = utils.unpickle(str(dp / "bow.mm.metadata.cpickle"))
titles_to_id = utils.unpickle(str(dp / "titles_to_id.pickle"))
dictionary = Dictionary.load_from_text(str(dp / "dictionary.txt.bz2"))

db_path = dp / "esa.db"
if db_path.exists():
    db_path.unlink()

conn = sql.connect(str(db_path))
with conn:
    cursor = conn.cursor()
    cursor.execute(term_table)
    cursor.execute(article_table)
    cursor.execute(term_article_table)
    cursor.execute(term_index)
    cursor.execute(term_article_index)
    cursor.execute(article_index)
    cursor.execute(article_term_index)

    id_title_list = [(article_id, article.lower()) for article_id, (_id, article) in id_to_titles.items()]
    id_term_list = [(term_id, term.lower()) for term_id, term in dictionary.items()]

    cursor.executemany("INSERT INTO articles VALUES (?,?)", id_title_list)
    print("Inserted {} articles into db".format(cursor.rowcount))
    cursor.executemany("INSERT INTO terms VALUES (?,?)", id_term_list)
    print("Inserted {} terms into db".format(cursor.rowcount))
    print("Inserted term and article tables")

    for c_id, c_vector in enumerate(tfidf_corpus):
        c_vector = [item for item in c_vector if item[1] >= TF_IDF_THRESHOLD]
        values = ((item[0], c_id, item[1]) for item in c_vector)
        cursor.executemany("INSERT into term_article_score VALUES (?, ?, ?)", values)
        if c_id % 10000 == 0:
            print("{} - Processed {} articles".format(time.ctime(), c_id))

    for article_string in del_articles_strings:
        article_string = "%" + article_string + "%"
        cursor.execute(delete_articles_containing, [article_string])
        print("Number of \"{}\" articles deleted: {}".format(article_string, cursor.rowcount))

    cursor.close()

# sqlite Error : Cannnot vacuum within transaction. WTF?
# need to close transaction by getting out of with statement and make new one
with conn:
    conn.execute("VACUUM")
