# ⚖️ Yuridik Adabiyotlar Boti

Telegram bot — yuridik kitoblar kutubxonasi.

---

## 🚀 O'rnatish

### 1. Fayllarni yuklab oling

```bash
git clone <repo>
cd yuridik_bot
```

### 2. Virtual muhit yarating

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Kutubxonalarni o'rnating

```bash
pip install -r requirements.txt
```

### 4. .env fayl yarating

```bash
cp .env.example .env
```

`.env` faylini oching va quyidagilarni to'ldiring:

```
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=6206932601,8013328081
```

**Bot token olish:** [@BotFather](https://t.me/BotFather) dan yangi bot yarating.

### 5. Botni ishga tushiring

```bash
python main.py
```

---

## 📋 Imkoniyatlar

### 👤 Foydalanuvchilar uchun

| Funksiya | Tavsif |
|----------|--------|
| 📚 Kitoblarni yuklab olish | Yo'nalishlar bo'yicha kitoblar |
| 🔍 Qidiruv | Nom yoki muallif bo'yicha qidirish |
| 📊 Statistika | Kitoblar soni va yo'nalishlar |
| ✅ Majburiy obuna | Kanallarni tekshirish |

### 🔐 Adminlar uchun

| Funksiya | Buyruq/Tugma |
|----------|-------------|
| Admin panel | `/admin` |
| Kitob qo'shish | Admin panel → 📚 Kitob qo'shish |
| Yo'nalish qo'shish | Admin panel → 🗂 Yo'nalishlar |
| Kanal qo'shish | Admin panel → 📌 Majburiy kanallar |
| Ommaviy post | Admin panel → 📢 Ommaviy post |
| Monitoring | Admin panel → 📊 Monitoring |

---

## 📁 Loyiha tuzilishi

```
yuridik_bot/
├── main.py                 # Asosiy fayl
├── config.py               # Konfiguratsiya
├── requirements.txt        # Kutubxonalar
├── .env                    # Muhit o'zgaruvchilari
├── database/
│   ├── __init__.py
│   └── db.py               # Ma'lumotlar bazasi
├── handlers/
│   ├── __init__.py
│   ├── user.py             # Foydalanuvchi handlerlari
│   └── admin.py            # Admin handlerlari
├── keyboards/
│   ├── __init__.py
│   └── keyboards.py        # Klaviaturalar
└── middlewares/
    ├── __init__.py
    └── subscription.py     # Obuna middleware
```

---

## 📚 Kitob Kategoriyalari

- Darslik
- Sharh
- Kodeks
- Qo'llanma
- Sohaga doir normalar

## 🗂 Standart Yo'nalishlar

- ⚖️ Konstitutsiyaviy huquq
- 🏛️ Fuqarolik huquqi
- 👨‍👩‍👧 Oila huquqi
- 🌍 Xalqaro huquq
- 🔒 Jinoyat huquqi
- 📋 Ma'muriy huquq
- 💰 Soliq huquqi
- 👷 Mehnat huquqi

---

## ⚙️ Texnik talablar

- Python 3.10+
- aiogram 3.13+
- SQLite (aiosqlite)

---

## 🔧 Muammolar

**Bot ishlamayapti?**
- BOT_TOKEN to'g'ri ekanini tekshiring
- `pip install -r requirements.txt` qaytadan ishlatib ko'ring

**PDF yuklamayapti?**
- Faqat `.pdf` formatdagi fayllar qabul qilinadi
- Fayl hajmi Telegram limiti (50MB) dan oshmasin
