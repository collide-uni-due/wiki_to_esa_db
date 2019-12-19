

term_table = """
CREATE TABLE terms (
id INTEGER PRIMARY KEY,
term TEXT
);
"""

article_table = """
CREATE TABLE articles(
id INTEGER PRIMARY KEY,
article TEXT
);
"""

term_article_table = """
CREATE TABLE term_article_score(
term_id INTEGER,
article_id INTEGER,
tf_idf REAL,
FOREIGN KEY (term_id) REFERENCES terms (id),
FOREIGN KEY (article_id) REFERENCES articles (id),
PRIMARY KEY (term_id, article_id)
);
"""

term_index = """
CREATE INDEX term_index on terms(term);
"""

term_article_index = """
CREATE INDEX term_article_index on term_article_score(term_id)
"""

article_index = """
CREATE INDEX article_index on articles(article);
"""
article_term_index = """
CREATE INDEX article_term_index on term_article_score(article_id)
"""

delete_articles_containing = """
DELETE 
FROM articles
WHERE articles.article LIKE ?
;
"""