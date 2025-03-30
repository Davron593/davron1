import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from PIL import Image

# Tokeningizni shu yerga kiriting
TOKEN = "7426950979:AAGwa5G701e7CBXd1yTh7zTYFWNVudFKH8k"

# Rasmlar va PDF saqlanadigan papka
SAVE_DIR = "C:/Users/user/Desktop/bot.py"
os.makedirs(SAVE_DIR, exist_ok=True)  # Papka mavjud bo'lmasa, yaratadi

# Foydalanuvchilar rasmlarini vaqtincha saqlash
user_images = {}

# Loglarni sozlash
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# /start komandasi
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("📸 Rasmlarni yuboring. Tugatgandan so‘ng 'To‘xtatish' tugmasini bosing.")

# Rasm qabul qilish
async def handle_photo(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_images:
        user_images[user_id] = []  # Agar foydalanuvchi uchun ro'yxat bo'lmasa, yaratish

    photo = update.message.photo[-1]  # Eng yuqori sifatli rasmni tanlash
    file = await context.bot.get_file(photo.file_id)  # Telegram serveridan faylni olish

    file_path = os.path.join(SAVE_DIR, f"user_{user_id}_{photo.file_id}.jpg")
    await file.download_to_drive(file_path)  # Rasmni yuklab olish

    user_images[user_id].append(file_path)  # Foydalanuvchi uchun rasmni saqlash
    await update.message.reply_text(f"✅ Rasm saqlandi! Jami {len(user_images[user_id])} ta rasm yuklandi.")

    # "To‘xtatish" va "Yana yuklash" tugmalarini yuborish
    keyboard = [
        [InlineKeyboardButton("📥 To‘xtatish (PDF yaratish)", callback_data="stop")],
        [InlineKeyboardButton("➕ Yana yuklash", callback_data="continue")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Tanlang:", reply_markup=reply_markup)

# Tugma bosilganda ishlaydi
async def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    if query.data == "stop":
        if user_id in user_images and user_images[user_id]:
            pdf_path = os.path.join(SAVE_DIR, f"user_{user_id}.pdf")

            # Rasmlarni PDFga aylantirish
            images = [Image.open(img).convert("RGB") for img in user_images[user_id]]
            images[0].save(pdf_path, save_all=True, append_images=images[1:])

            await query.message.reply_document(document=open(pdf_path, "rb"), caption="📄 Sizning PDF faylingiz tayyor!")
            
            # "Eski rasmlarni o‘chirish" tugmasi
            keyboard = [[InlineKeyboardButton("🗑 Eski rasmlarni o‘chirish", callback_data="delete")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("PDF yaratildi! Endi eski rasmlarni o‘chirish mumkin:", reply_markup=reply_markup)

        else:
            await query.message.reply_text("⚠️ Hech qanday rasm yuklanmagan!")

    elif query.data == "continue":
        await query.message.reply_text("📸 Yana rasmlar yuborishingiz mumkin.")

    elif query.data == "delete":
        if user_id in user_images:
            for img_path in user_images[user_id]:
                os.remove(img_path)  # Fayllarni o‘chirish
            user_images[user_id] = []  # Ro‘yxatni tozalash
            await query.message.reply_text("🗑 Eski rasmlar o‘chirildi!")

# Botni ishga tushirish
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
