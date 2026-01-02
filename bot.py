import json
import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8555066285:AAFT14hwN1KWMIq7GkPf9SEdOJvXsEQpuI8"
ADMIN_CODE = "121314"  
MOVIES_FILE = "movies.json"
ADMINS_FILE = "admins.json" 
if os.path.exists(MOVIES_FILE):
    try:
        with open(MOVIES_FILE, "r", encoding="utf-8") as f:
            movies = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        movies = {}
else:
    movies = {}
if os.path.exists(ADMINS_FILE):
    try:
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            admins = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        admins = []
else:
    admins = []

def save_movies():
    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=4)

def save_admins():
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(admins, f, ensure_ascii=False, indent=4)

def is_admin(user_id):
    return str(user_id) in admins

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    keyboard = [
        [InlineKeyboardButton("🔍 Kino qidirish", callback_data="search_movie")],
        [InlineKeyboardButton("📞 Admin bilan bog'lanish", callback_data="contact_admin")]
    ]
    
    text = (
        "🎬 Salom! Xush kelibsiz!\n\n"
        "🔍 Kino yoki video topish uchun kod yuboring yoki quyidagi tugmalardan foydalaning."
    )
    
    await update.message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    if len(context.args) == 0:
        context.user_data["awaiting_admin_code"] = True
        await update.message.reply_text(
            "🔐 <b>Admin paneliga kirish</b>\n\nIltimos, admin kodini kiriting:",
            parse_mode="HTML"
        )
        return
    
    code = context.args[0]
    if code == ADMIN_CODE:
        if str(user.id) not in admins:
            admins.append(str(user.id))
            save_admins()
        
        keyboard = [
            [InlineKeyboardButton("➕ Kino qo'shish", callback_data="add_movie")],
            [InlineKeyboardButton("🗑 Kino o'chirish", callback_data="delete_movie")],
            [InlineKeyboardButton("📜 Kinolar ro'yxati", callback_data="list_movies")],
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")]
        ]
        
        await update.message.reply_text(
            "👑 <b>Admin paneli</b>\n\nQuyidagi amallardan birini tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    else:
        try:
            admin_id = admins[0] 
            await context.bot.send_message(
                admin_id,
                f"⚠️ <b>Ogohlik!</b>\n\n"
                f"Foydalanuvchi admin paneliga kirishga urindi:\n"
                f"👤 Ism: {user.first_name}\n"
                f"🆔 ID: {user.id}\n"
                f"📧 Username: @{user.username if user.username else 'Mavjud emas'}\n"
                f"🔐 Kiritilgan kod: {code}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Adminga xabar yuborishda xatolik: {e}")
        
        await update.message.reply_text("❌ Noto'g'ri admin kodi! Siz admin emassiz.")

async def handle_admin_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    if context.user_data.get("awaiting_admin_code"):
        code = update.message.text.strip()
        
        if code == ADMIN_CODE:
            if str(user.id) not in admins:
                admins.append(str(user.id))
                save_admins()
            
            context.user_data["awaiting_admin_code"] = False
            
            # Admin paneli tugmalari
            keyboard = [
                [InlineKeyboardButton("➕ Kino qo'shish", callback_data="add_movie")],
                [InlineKeyboardButton("🗑 Kino o'chirish", callback_data="delete_movie")],
                [InlineKeyboardButton("📜 Kinolar ro'yxati", callback_data="list_movies")],
                [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
                [InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")]
            ]
            
            await update.message.reply_text(
                "👑 <b>Admin paneli</b>\n\nQuyidagi amallardan birini tanlang:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
        else:
            try:
                admin_id = admins[0]  
                await context.bot.send_message(
                    admin_id,
                    f"⚠️ <b>Ogohlik!</b>\n\n"
                    f"Foydalanuvchi admin paneliga kirishga urindi:\n"
                    f"👤 Ism: {user.first_name}\n"
                    f"🆔 ID: {user.id}\n"
                    f"📧 Username: @{user.username if user.username else 'Mavjud emas'}\n"
                    f"🔐 Kiritilgan kod: {code}",
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Adminga xabar yuborishda xatolik: {e}")
            
            await update.message.reply_text("❌ Noto'g'ri admin kodi! Siz admin emassiz.")
    else:
        await handle_user_code(update, context)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    keyboard = [
        [InlineKeyboardButton("🔍 Kino qidirish", callback_data="search_movie")],
        [InlineKeyboardButton("📞 Admin bilan bog'lanish", callback_data="contact_admin")]
    ]
    
    await query.edit_message_text(
        "🏠 <b>Bosh menyu</b>\n\nQuyidagi amallardan birini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def search_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔍 <b>Kino izlash</b>\n\nIltimos, kino kodini kiriting:",
        parse_mode="HTML"
    )

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    
    for admin_id in admins:
        try:
            await context.bot.send_message(
                admin_id,
                f"📞 <b>Yangi bog'lanish so'rovi</b>\n\n"
                f"👤 Foydalanuvchi: {user.first_name}\n"
                f"🆔 ID: {user.id}\n"
                f"📧 Username: @{user.username if user.username else 'Mavjud emas'}\n"
                f"📞 Telefon raqam: {user.phone_number if hasattr(user, 'phone_number') and user.phone_number else 'Mavjud emas'}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Adminga xabar yuborishda xatolik: {e}")
    
    await query.edit_message_text(
        "📞 <b>Admin bilan bog'lanish</b>\n\n"
        "Sizning so'rovingiz adminlarga yuborildi. Tez orada siz bilan bog'lanishadi.\n\n"
        "Agar shoshilinch bo'lsa, to'g'ridan-to'g'ri xabar yozishingiz mumkin.",
        parse_mode="HTML"
    )

async def admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if not is_admin(user.id):
        if query.data == "search_movie":
            await search_movie(update, context)
        elif query.data == "contact_admin":
            await contact_admin(update, context)
        elif query.data == "main_menu":
            await main_menu(update, context)
        return

    if query.data == "add_movie":
        context.user_data["admin_mode"] = "add_code"
        await query.edit_message_text(
            "🔑 <b>Yangi kino qo'shish</b>\n\nKod kiriting (masalan: <code>A123</code>):",
            parse_mode="HTML"
        )

    elif query.data == "delete_movie":
        context.user_data["admin_mode"] = "delete"
        if not movies:
            return await query.edit_message_text("📭 Hozircha kino yo'q.")
        
        keyboard = []
        row = []
        for i, code in enumerate(movies.keys()):
            row.append(InlineKeyboardButton(code, callback_data=f"delete_{code}"))
            if (i + 1) % 3 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_admin")])
        
        await query.edit_message_text(
            "🗑 <b>Kino o'chirish</b>\n\nO'chirmoqchi bo'lgan kino kodini tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    elif query.data.startswith("delete_"):
        code = query.data.replace("delete_", "")
        if code in movies:
            del movies[code]
            save_movies()
            await query.edit_message_text(f"✅ <b>Kino o'chirildi</b>\n\nKod: <code>{code}</code>", parse_mode="HTML")
        else:
            await query.edit_message_text("❌ Bunday kod topilmadi.")

    elif query.data == "list_movies":
        if not movies:
            return await query.edit_message_text("📭 Hozircha kino yo'q.")
        
        text = "📜 <b>Kinolar ro'yxati:</b>\n\n"
        for code, data in movies.items():
            text += f"🔑 <code>{code}</code> — {data['desc'][:50]}"
            if len(data['desc']) > 50:
                text += "..."
            text += "\n"
        
        if len(text) > 4000:
            text = text[:4000] + "\n\n...ro'yxat juda uzun, to'liq ko'rish uchun fayl yuklab oling."
        
        await query.edit_message_text(text, parse_mode="HTML")

    elif query.data == "admin_stats":
        total_movies = len(movies)
        video_count = sum(1 for m in movies.values() if m.get('type') == 'video')
        photo_count = sum(1 for m in movies.values() if m.get('type') == 'photo')
        text_count = sum(1 for m in movies.values() if m.get('type') == 'text')
        document_count = sum(1 for m in movies.values() if m.get('type') == 'document')
        
        stats_text = (
            f"📊 <b>Admin statistikasi</b>\n\n"
            f"🎬 Jami kinolar: <code>{total_movies}</code>\n"
            f"🎥 Videolar: <code>{video_count}</code>\n"
            f"🖼 Rasmlar: <code>{photo_count}</code>\n"
            f"📝 Matnlar: <code>{text_count}</code>\n"
            f"📎 Hujjatlar: <code{document_count}</code>"
        )
        
        await query.edit_message_text(stats_text, parse_mode="HTML")

    elif query.data == "back_to_admin":
        keyboard = [
            [InlineKeyboardButton("➕ Kino qo'shish", callback_data="add_movie")],
            [InlineKeyboardButton("🗑 Kino o'chirish", callback_data="delete_movie")],
            [InlineKeyboardButton("📜 Kinolar ro'yxati", callback_data="list_movies")],
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            "👑 <b>Admin paneli</b>\n\nQuyidagi amallardan birini tanlang:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )
    
    elif query.data == "main_menu":
        await main_menu(update, context)

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    if not is_admin(user.id):
        return await handle_user_code(update, context)

    mode = context.user_data.get("admin_mode")

    if mode == "add_code":
        code = update.message.text.strip().upper()
        if not code:
            return await update.message.reply_text("❌ Kod bo'sh bo'lmasligi kerak.")
        
        if code in movies:
            return await update.message.reply_text("❗ Bu kod allaqachon mavjud. Boshqa kod kiriting.")
        
        context.user_data["new_code"] = code
        context.user_data["admin_mode"] = "add_desc"
        return await update.message.reply_text("✏️ Kino tavsifini yozing:")

    elif mode == "add_desc":
        desc = update.message.text
        if not desc:
            return await update.message.reply_text("❌ Tavsif bo'sh bo'lmasligi kerak.")
        
        context.user_data["new_desc"] = desc
        context.user_data["admin_mode"] = "add_file"
        return await update.message.reply_text("🎥 Endi video, rasm yoki matn yuboring:")

    elif mode == "delete":
        code = update.message.text.strip().upper()
        if code in movies:
            del movies[code]
            save_movies()
            context.user_data["admin_mode"] = None
            return await update.message.reply_text(f"✅ Kino o'chirildi: {code}")
        else:
            return await update.message.reply_text("❌ Bunday kod topilmadi.")
    
    else:
        return await handle_user_code(update, context)

async def handle_admin_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    if not is_admin(user.id):
        return
    
    if context.user_data.get("admin_mode") == "add_file":
        code = context.user_data.get("new_code")
        desc = context.user_data.get("new_desc")
        
        if not code or not desc:
            context.user_data["admin_mode"] = None
            return await update.message.reply_text("❌ Xatolik yuz berdi. Qaytadan boshlang.")

        if update.message.video:
            movies[code] = {"type": "video", "file_id": update.message.video.file_id, "desc": desc}
        elif update.message.photo:
            movies[code] = {"type": "photo", "file_id": update.message.photo[-1].file_id, "desc": desc}
        elif update.message.document:
            movies[code] = {"type": "document", "file_id": update.message.document.file_id, "desc": desc}
        elif update.message.text:
            movies[code] = {"type": "text", "file_id": update.message.text, "desc": desc}
        else:
            return await update.message.reply_text("❗ Faqat video, rasm, hujjat yoki matn yuboring.")

        save_movies()
        context.user_data["admin_mode"] = None
        
        keyboard = [
            [InlineKeyboardButton("➕ Yangi kino qo'shish", callback_data="add_movie")],
            [InlineKeyboardButton("🔙 Admin paneli", callback_data="back_to_admin")]
        ]
        
        await update.message.reply_text(
            f"✅ <b>Kino muvaffaqiyatli qo'shildi!</b>\n\n"
            f"🔑 Kod: <code>{code}</code>\n"
            f"📄 Tavsif: {desc}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

async def handle_user_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    code = update.message.text.strip().upper()
    
    if code in movies:
        movie = movies[code]
        caption = (
            f"🎬 <b>Kino topildi!</b>\n\n"
            f"🔑 Kod: <code>{code}</code>\n"
            f"📄 {movie['desc']}\n\n"
            f"⭐️ Yana kodlar yuboring!"
        )

        try:
            if movie["type"] == "video":
                await update.message.reply_video(
                    movie["file_id"], 
                    caption=caption, 
                    parse_mode="HTML"
                )
            elif movie["type"] == "photo":
                await update.message.reply_photo(
                    movie["file_id"], 
                    caption=caption, 
                    parse_mode="HTML"
                )
            elif movie["type"] == "document":
                await update.message.reply_document(
                    movie["file_id"], 
                    caption=caption, 
                    parse_mode="HTML"
                )
            elif movie["type"] == "text":
                full_text = f"{caption}\n\n{movie['file_id']}"
                await update.message.reply_text(full_text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Xatolik: {e}")
            await update.message.reply_text(
                "❌ Kontentni yuborishda xatolik yuz berdi. Iltimos, keyinroq urunib ko'ring."
            )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Boshqa kod orqali izlash", callback_data="search_movie")],
            [InlineKeyboardButton("📞 Admin bilan bog'lanish", callback_data="contact_admin")],
            [InlineKeyboardButton("🔙 Bosh menyu", callback_data="main_menu")]
        ])
        
        await update.message.reply_text(
            f"❌ <b>Bunday koddagi kino topilmadi</b>\n\n"
            f"🔍 Kod: <code>{code}</code>\n\n"
            f"Kodni tekshirib, qayta yuboring yoki admin bilan bog'laning.",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    if is_admin(user.id) and context.user_data.get("admin_mode"):
        return
    
    keyboard = [
        [InlineKeyboardButton("🔍 Kino qidirish", callback_data="search_movie")],
        [InlineKeyboardButton("📞 Admin bilan bog'lanish", callback_data="contact_admin")]
    ]
    
    await update.message.reply_text(
        "🎬 <b>Kino botiga xush kelibsiz!</b>\n\n"
        "🔍 Kino topish uchun faqat kod yuboring (masalan: <code>A123</code>) yoki quyidagi tugmalardan foydalaning",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

  
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))

    app.add_handler(CallbackQueryHandler(admin_callbacks))
    
    app.add_handler(MessageHandler(
        filters.VIDEO | filters.PHOTO | filters.Document.ALL, 
        handle_admin_media
    ))
    
    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE, 
        handle_admin_login
    ))
    
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_user_code
    ))
    
    app.add_handler(MessageHandler(filters.ALL, handle_other_messages))
    
    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
