import os
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
import psycopg2

logging.basicConfig(level=logging.INFO)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "Bl@3e345")
DB_NAME = os.getenv("DB_NAME", "sports_db")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8084219997:AAFG3_uGNP-UjvFpsN_W1CN45g8ntw3ZVUM")  # For python-telegram-bot

async def add_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /addkeyword <keyword>
    """
    if not context.args:
        await update.message.reply_text("Usage: /addkeyword <keyword>")
        return

    keyword = context.args[0].lower()

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME
        )
        cur = conn.cursor()

        # Create table if not exists (just in case)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS keywords (
                id SERIAL PRIMARY KEY,
                keyword VARCHAR(255) UNIQUE NOT NULL
            );
        """)

        # Insert new keyword
        cur.execute("SELECT keyword FROM keywords WHERE keyword = %s", (keyword,))
        row = cur.fetchone()
        if row:
            await update.message.reply_text(f"Keyword '{keyword}' already exists.")
        else:
            cur.execute("INSERT INTO keywords (keyword) VALUES (%s)", (keyword,))
            conn.commit()
            await update.message.reply_text(f"Keyword '{keyword}' added.")
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("Error adding keyword. Check logs.")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

async def del_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /delkeyword <keyword>
    """
    if not context.args:
        await update.message.reply_text("Usage: /delkeyword <keyword>")
        return

    keyword = context.args[0].lower()

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME
        )
        cur = conn.cursor()
        
        cur.execute("DELETE FROM keywords WHERE keyword = %s", (keyword,))
        if cur.rowcount > 0:
            conn.commit()
            await update.message.reply_text(f"Keyword '{keyword}' deleted.")
        else:
            await update.message.reply_text(f"Keyword '{keyword}' not found.")
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("Error deleting keyword. Check logs.")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

async def list_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /listkeywords
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            dbname=DB_NAME
        )
        cur = conn.cursor()
        cur.execute("SELECT keyword FROM keywords;")
        rows = cur.fetchall()
        if rows:
            keywords_list = "\n".join([r[0] for r in rows])
            await update.message.reply_text("Current keywords:\n" + keywords_list)
        else:
            await update.message.reply_text("No keywords found.")
    except Exception as e:
        logging.error(e)
        await update.message.reply_text("Error listing keywords.")
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

def main():
    if not TELEGRAM_BOT_TOKEN:
        logging.error("TELEGRAM_BOT_TOKEN not set. Exiting.")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("addkeyword", add_keyword))
    app.add_handler(CommandHandler("delkeyword", del_keyword))
    app.add_handler(CommandHandler("listkeywords", list_keywords))

    logging.info("Telegram Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
