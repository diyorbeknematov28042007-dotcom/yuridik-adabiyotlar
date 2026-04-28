from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    get_books_by_direction, get_book_by_id, search_books,
    get_books_count, get_books_stats_by_direction, get_all_directions,
    increment_download
)
from keyboards.keyboards import (
    main_menu_kb, subscription_kb, directions_kb,
    books_list_kb, book_detail_kb, search_results_kb
)
from middlewares.subscription import check_user_subscribed

router = Router()


class SearchState(StatesGroup):
    waiting_query = State()


# ─── /start ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    subscribed, missing = await check_user_subscribed(bot, message.from_user.id)

    if not subscribed:
        text = (
            "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            "Obuna bo'lgandan so'ng <b>«✅ Obunani tekshirish»</b> tugmasini bosing."
        )
        await message.answer(text, reply_markup=subscription_kb(missing), parse_mode="HTML")
        return

    await message.answer(
        "⚖️ <b>Yuridik adabiyotlar botiga xush kelibsiz!</b>\n\n"
        "📚 Bu botda yuridik soha bo'yicha kitoblar, darsliklar, kodekslar va "
        "qo'llanmalar to'plangan.\n\n"
        "Quyidagi menyudan foydalaning 👇",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


# ─── SUBSCRIPTION CHECK ───────────────────────────────────────────────────────

@router.callback_query(F.data == "check_subscription")
async def check_sub_callback(call: CallbackQuery, bot: Bot):
    subscribed, missing = await check_user_subscribed(bot, call.from_user.id)

    if not subscribed:
        await call.answer("❌ Siz hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
        text = (
            "⚠️ <b>Quyidagi kanallarga obuna bo'lishingiz kerak:</b>\n\n"
            "Obuna bo'lgandan so'ng <b>«✅ Obunani tekshirish»</b> tugmasini bosing."
        )
        await call.message.edit_text(text, reply_markup=subscription_kb(missing), parse_mode="HTML")
        return

    await call.answer("✅ Obuna tasdiqlandi!", show_alert=True)
    await call.message.delete()
    await call.message.answer(
        "⚖️ <b>Yuridik adabiyotlar botiga xush kelibsiz!</b>\n\n"
        "📚 Bu botda yuridik soha bo'yicha kitoblar, darsliklar, kodekslar va "
        "qo'llanmalar to'plangan.\n\n"
        "Quyidagi menyudan foydalaning 👇",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


# ─── MAIN MENU ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        "🏠 <b>Bosh menyu</b>\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu_kb(),
        parse_mode="HTML"
    )


# ─── BOOKS PANEL ──────────────────────────────────────────────────────────────

@router.message(F.text == "📚 Kitoblarni yuklab olish")
async def books_panel(message: Message, bot: Bot):
    subscribed, missing = await check_user_subscribed(bot, message.from_user.id)
    if not subscribed:
        await message.answer(
            "⚠️ Avval kanallarga obuna bo'ling:",
            reply_markup=subscription_kb(missing)
        )
        return

    directions = await get_all_directions()
    if not directions:
        await message.answer("📭 Hozircha yo'nalishlar qo'shilmagan.")
        return

    await message.answer(
        "📚 <b>Kitoblarni yuklab olish</b>\n\nYo'nalishni tanlang:",
        reply_markup=directions_kb(directions),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "books_panel")
async def books_panel_callback(call: CallbackQuery):
    directions = await get_all_directions()
    await call.message.edit_text(
        "📚 <b>Kitoblarni yuklab olish</b>\n\nYo'nalishni tanlang:",
        reply_markup=directions_kb(directions),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("dir_"))
async def direction_books(call: CallbackQuery):
    direction_id = int(call.data.split("_")[1])
    books = await get_books_by_direction(direction_id)

    if not books:
        await call.answer("📭 Bu yo'nalishda hozircha kitoblar yo'q.", show_alert=True)
        return

    directions = await get_all_directions()
    dir_name = next((d["name"] for d in directions if d["id"] == direction_id), "Yo'nalish")

    await call.message.edit_text(
        f"📂 <b>{dir_name}</b>\n\n📖 Jami: <b>{len(books)} ta kitob</b>\n\nKitobni tanlang:",
        reply_markup=books_list_kb(books, direction_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("bookspage_"))
async def books_page(call: CallbackQuery):
    _, direction_id, page = call.data.split("_")
    direction_id = int(direction_id)
    page = int(page)
    books = await get_books_by_direction(direction_id)

    directions = await get_all_directions()
    dir_name = next((d["name"] for d in directions if d["id"] == direction_id), "Yo'nalish")

    await call.message.edit_text(
        f"📂 <b>{dir_name}</b>\n\n📖 Jami: <b>{len(books)} ta kitob</b>\n\nKitobni tanlang:",
        reply_markup=books_list_kb(books, direction_id, page),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("book_"))
async def book_detail(call: CallbackQuery):
    book_id = int(call.data.split("_")[1])
    book = await get_book_by_id(book_id)

    if not book:
        await call.answer("Kitob topilmadi.", show_alert=True)
        return

    text = (
        f"📖 <b>{book['title']}</b>\n\n"
        f"✍️ <b>Muallif:</b> {book['author']}\n"
        f"📅 <b>Yil:</b> {book['year'] or 'Noma\'lum'}\n"
        f"🗂 <b>Yo'nalish:</b> {book['direction']}\n"
        f"📑 <b>Kategoriya:</b> {book['category'] or 'Noma\'lum'}\n"
        f"📚 <b>Fan nomi:</b> {book['subject'] or 'Noma\'lum'}\n"
        f"📥 <b>Yuklangan:</b> {book['downloads']} marta\n\n"
        f"Kitobni yuklab olish uchun tugmani bosing 👇"
    )

    await call.message.edit_text(
        text,
        reply_markup=book_detail_kb(book_id, direction_id=0),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("download_"))
async def download_book(call: CallbackQuery, bot: Bot):
    book_id = int(call.data.split("_")[1])
    book = await get_book_by_id(book_id)

    if not book:
        await call.answer("Kitob topilmadi.", show_alert=True)
        return

    await call.answer("📥 Yuklanmoqda...")
    await increment_download(book_id)

    caption = (
        f"📖 <b>{book['title']}</b>\n"
        f"✍️ {book['author']} | 📅 {book['year'] or ''}\n"
        f"🗂 {book['direction']} | 📑 {book['category'] or ''}\n"
        f"📚 {book['subject'] or ''}"
    )

    await bot.send_document(
        call.from_user.id,
        document=book["file_id"],
        caption=caption,
        parse_mode="HTML"
    )


# ─── SEARCH ───────────────────────────────────────────────────────────────────

@router.message(F.text == "🔍 Qidiruv")
async def search_start(message: Message, state: FSMContext, bot: Bot):
    subscribed, missing = await check_user_subscribed(bot, message.from_user.id)
    if not subscribed:
        await message.answer("⚠️ Avval kanallarga obuna bo'ling:", reply_markup=subscription_kb(missing))
        return

    await state.set_state(SearchState.waiting_query)
    await message.answer(
        "🔍 <b>Kitob qidirish</b>\n\n"
        "Kitob nomi yoki muallif ismini kiriting:",
        parse_mode="HTML"
    )


@router.message(SearchState.waiting_query)
async def process_search(message: Message, state: FSMContext):
    await state.clear()
    query = message.text.strip()

    if len(query) < 2:
        await message.answer("❌ Kamida 2 ta harf kiriting.")
        return

    books = await search_books(query)

    if not books:
        await message.answer(
            f"😔 <b>«{query}»</b> bo'yicha hech narsa topilmadi.\n\nBoshqa so'z bilan qidiring.",
            parse_mode="HTML"
        )
        return

    await message.answer(
        f"🔍 <b>«{query}»</b> bo'yicha <b>{len(books)} ta</b> natija topildi:\n\nKitobni tanlang:",
        reply_markup=search_results_kb(books),
        parse_mode="HTML"
    )


# ─── STATISTICS ───────────────────────────────────────────────────────────────

@router.message(F.text == "📊 Statistika")
async def statistics(message: Message):
    total_books = await get_books_count()
    stats = await get_books_stats_by_direction()

    text = f"📊 <b>Kutubxona statistikasi</b>\n\n📚 Jami kitoblar: <b>{total_books} ta</b>\n\n"
    text += "📂 <b>Yo'nalishlar bo'yicha:</b>\n"

    for s in stats:
        if s["count"] > 0:
            text += f"\n{s['emoji']} {s['direction']}: <b>{s['count']} ta</b>"

    await message.answer(text, parse_mode="HTML")


# ─── ABOUT ────────────────────────────────────────────────────────────────────

@router.message(F.text == "ℹ️ Bot haqida")
async def about_bot(message: Message):
    await message.answer(
        "⚖️ <b>Yuridik adabiyotlar boti</b>\n\n"
        "Bu bot yuridik soha mutaxassislari, talabalar va huquqshunoslar uchun "
        "yaratilgan kutubxona.\n\n"
        "📚 <b>Mavjud bo'limlar:</b>\n"
        "• Konstitutsiyaviy huquq\n"
        "• Fuqarolik huquqi\n"
        "• Oila huquqi\n"
        "• Xalqaro huquq\n"
        "• Jinoyat huquqi\n"
        "• Ma'muriy huquq\n"
        "• Soliq huquqi\n"
        "• Mehnat huquqi va boshqalar\n\n"
        "🔍 Kitoblarni nom yoki muallif bo'yicha qidirish mumkin.",
        parse_mode="HTML"
    )
