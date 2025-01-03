import logging
import psycopg2
from scrapy.exceptions import DropItem

from sports_scraper.telegram_client.telegram_alerts import send_telegram_alert


class DatabasePipeline:
    def __init__(self, db_host, db_port, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        
        self.connection = None
        self.cursor = None
        
        # We will dynamically load the keywords from DB in open_spider
        self.keywords = set()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_host=crawler.settings.get("DB_HOST", "localhost"),
            db_port=crawler.settings.get("DB_PORT", 5432),
            db_user=crawler.settings.get("DB_USER", "postgres"),
            db_password=crawler.settings.get("DB_PASS", "Bl@3e345"),
            db_name=crawler.settings.get("DB_NAME", "sports_db"),
        )

    def open_spider(self, spider):
        try:
            self.connection = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                dbname=self.db_name
            )
            self.cursor = self.connection.cursor()

            # Create articles table if not exists
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    author TEXT,
                    date TEXT,
                    body TEXT,
                    source TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            
            # Create keywords table if not exists
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS keywords (
                    id SERIAL PRIMARY KEY,
                    keyword VARCHAR(255) UNIQUE NOT NULL
                );
            """)

            self.connection.commit()

            # Load existing keywords from DB
            self.cursor.execute("SELECT keyword FROM keywords;")
            rows = self.cursor.fetchall()
            self.keywords = {r[0].lower() for r in rows}
            
            logging.info(f"Keywords loaded from DB: {self.keywords}")

        except Exception as e:
            logging.error(f"Error setting up DB or loading keywords: {e}")
            raise e

    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def process_item(self, item, spider):
        try:
            title = item.get('title', '')
            body_list = item.get('body', [])
            body_text = " ".join(body_list).strip()
            url = item.get('url', '')
            source = item.get('source', '')
            date = item.get('date', '')
            author = item.get('author', '')

            article_text = f"{title} {body_text}".lower()
            matched_keywords = [kw for kw in self.keywords if kw in article_text]

            # If no keywords in DB, treat as "no filtering" so it always matches
            needs_alert = (len(self.keywords) == 0) or (len(matched_keywords) > 0)

            # Check if already in DB by URL
            self.cursor.execute("SELECT id FROM articles WHERE url = %s", (url,))
            existing_id = self.cursor.fetchone()

            if existing_id:
                logging.debug(f"Article already exists in DB (ID={existing_id[0]}): {title}")
            else:
                # Insert new article
                insert_sql = """
                    INSERT INTO articles (title, url, author, date, body, source)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(
                    insert_sql,
                    (title, url, author, date, body_text, source)
                )
                self.connection.commit()

                logging.info(f"Inserted new article: {title}")

                # Send alert only if there's a match (or if no keywords exist in DB)
                if needs_alert:
                    send_telegram_alert(
                        title=title,
                        url=url,
                        source=source,
                        date=date,
                        matched_keywords=matched_keywords
                    )

        except Exception as e:
            logging.error(f"Error processing item: {e}")
            self.connection.rollback()
            raise DropItem(f"Error inserting item {title}: {e}")

        return item
