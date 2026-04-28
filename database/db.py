import aiosqlite
import os

DB_PATH = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Mandatory channels table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mandatory_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT NOT NULL,
                channel_name TEXT,
                channel_link TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Directions (Yo'nalishlar) table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS directions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                emoji TEXT DEFAULT '📚',
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Books table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER,
                direction_id INTEGER,
                category TEXT,
                subject TEXT,
                file_id TEXT NOT NULL,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                download_count INTEGER DEFAULT 0,
                FOREIGN KEY (direction_id) REFERENCES directions(id)
            )
        """)

        # Seed default directions
        default_directions = [
            ("Konstitutsiyaviy huquq", "⚖️"),
            ("Fuqarolik huquqi", "🏛️"),
            ("Oila huquqi", "👨‍👩‍👧"),
            ("Xalqaro huquq", "🌍"),
            ("Jinoyat huquqi", "🔒"),
            ("Ma'muriy huquq", "📋"),
            ("Soliq huquqi", "💰"),
            ("Mehnat huquqi", "👷"),
        ]
        for name, emoji in default_directions:
            await db.execute(
                "INSERT OR IGNORE INTO directions (name, emoji) VALUES (?, ?)",
                (name, emoji)
            )

        await db.commit()


# ─── USERS ────────────────────────────────────────────────────────────────────

async def add_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name)
        )
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [r[0] for r in rows]

async def get_users_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
            return row[0]

async def get_new_users_today():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE DATE(joined_at) = DATE('now')"
        ) as cursor:
            row = await cursor.fetchone()
            return row[0]

async def get_new_users_week():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE joined_at >= datetime('now', '-7 days')"
        ) as cursor:
            row = await cursor.fetchone()
            return row[0]


# ─── MANDATORY CHANNELS ───────────────────────────────────────────────────────

async def add_mandatory_channel(channel_id: str, channel_name: str, channel_link: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO mandatory_channels (channel_id, channel_name, channel_link) VALUES (?, ?, ?)",
            (channel_id, channel_name, channel_link)
        )
        await db.commit()

async def remove_mandatory_channel(channel_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM mandatory_channels WHERE channel_id = ?", (channel_id,))
        await db.commit()

async def get_mandatory_channels():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT channel_id, channel_name, channel_link FROM mandatory_channels") as cursor:
            rows = await cursor.fetchall()
            return [{"id": r[0], "name": r[1], "link": r[2]} for r in rows]


# ─── DIRECTIONS ───────────────────────────────────────────────────────────────

async def add_direction(name: str, emoji: str = "📚"):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR IGNORE INTO directions (name, emoji) VALUES (?, ?)", (name, emoji))
        await db.commit()

async def get_all_directions():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name, emoji FROM directions ORDER BY name") as cursor:
            rows = await cursor.fetchall()
            return [{"id": r[0], "name": r[1], "emoji": r[2]} for r in rows]

async def delete_direction(direction_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM directions WHERE id = ?", (direction_id,))
        await db.commit()


# ─── BOOKS ────────────────────────────────────────────────────────────────────

CATEGORIES = ["Darslik", "Sharh", "Kodeks", "Qo'llanma", "Sohaga doir normalar"]

async def add_book(title, author, year, direction_id, category, subject, file_id, added_by):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO books (title, author, year, direction_id, category, subject, file_id, added_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, author, year, direction_id, category, subject, file_id, added_by)
        )
        await db.commit()

async def get_books_by_direction(direction_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT b.id, b.title, b.author, b.year, b.category, b.subject, b.download_count, d.name
               FROM books b JOIN directions d ON b.direction_id = d.id
               WHERE b.direction_id = ?
               ORDER BY b.title""",
            (direction_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"id": r[0], "title": r[1], "author": r[2], "year": r[3],
                     "category": r[4], "subject": r[5], "downloads": r[6], "direction": r[7]}
                    for r in rows]

async def get_book_by_id(book_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT b.id, b.title, b.author, b.year, b.category, b.subject,
                      b.file_id, b.download_count, d.name
               FROM books b JOIN directions d ON b.direction_id = d.id
               WHERE b.id = ?""",
            (book_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"id": row[0], "title": row[1], "author": row[2], "year": row[3],
                        "category": row[4], "subject": row[5], "file_id": row[6],
                        "downloads": row[7], "direction": row[8]}
            return None

async def search_books(query: str):
    async with aiosqlite.connect(DB_PATH) as db:
        q = f"%{query}%"
        async with db.execute(
            """SELECT b.id, b.title, b.author, b.year, b.category, b.subject, b.download_count, d.name
               FROM books b JOIN directions d ON b.direction_id = d.id
               WHERE b.title LIKE ? OR b.author LIKE ?
               ORDER BY b.title
               LIMIT 20""",
            (q, q)
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"id": r[0], "title": r[1], "author": r[2], "year": r[3],
                     "category": r[4], "subject": r[5], "downloads": r[6], "direction": r[7]}
                    for r in rows]

async def increment_download(book_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE books SET download_count = download_count + 1 WHERE id = ?", (book_id,))
        await db.commit()

async def get_books_count():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM books") as cursor:
            row = await cursor.fetchone()
            return row[0]

async def get_books_stats_by_direction():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """SELECT d.name, d.emoji, COUNT(b.id) as book_count
               FROM directions d LEFT JOIN books b ON b.direction_id = d.id
               GROUP BY d.id ORDER BY book_count DESC"""
        ) as cursor:
            rows = await cursor.fetchall()
            return [{"direction": r[0], "emoji": r[1], "count": r[2]} for r in rows]

async def delete_book(book_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM books WHERE id = ?", (book_id,))
        await db.commit()
