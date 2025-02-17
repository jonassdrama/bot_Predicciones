import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 TOKEN del bot de Telegram
TOKEN = "7939507064:AAGvU-qUNAIEwHHF14X6Vuvw-5uRFigjCTg"
ADMIN_ID = 1570729026 # ⚠️ REEMPLAZA con tu ID de Telegram

# 🔹 Autenticación con Google Sheets usando variable de entorno
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales desde la variable de entorno
creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)

# Conectar con Google Sheets
client = gspread.authorize(creds)

# 🔹 Abrir la hoja de cálculo
SHEET_NAME = "1uf5xu8CW7KDnElNeog2WH_DD5imEyhJ8qap_OwQjcz8"
sheet = client.open_by_key(SHEET_NAME).sheet1

# 🔹 Comando /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "¡Bienvenido a Isa Winning Bot! 🏆\n"
        "Envía tu predicción en formato: 'Equipo1 X - Equipo2 Y'"
    )

# 🔹 Guardar predicciones en Google Sheets
async def guardar_en_sheets(update: Update, context: CallbackContext) -> None:
    usuario = update.message.chat.username or update.message.chat.id
    texto = update.message.text

    # Validar formato
    if " - " not in texto:
        await update.message.reply_text("⚠️ Formato incorrecto. Usa: 'Equipo1 X - Equipo2 Y'")
        return

    # Guardar en Google Sheets
    sheet.append_row([str(usuario), texto])

    await update.message.reply_text("✅ Predicción guardada correctamente.")

# 🔹 Enviar un mensaje manualmente a un usuario
async def enviar(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso correcto: `/enviar ID mensaje`")
        return

    chat_id = context.args[0]
    mensaje = " ".join(context.args[1:])  

    try:
        await context.bot.send_message(chat_id=chat_id, text=mensaje)
        await update.message.reply_text(f"✅ Mensaje enviado a {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar mensaje: {e}")

# 🔹 Reenviar respuestas de los usuarios al admin
# 🔹 Reenviar respuestas de los usuarios al admin (incluye videos, fotos y documentos)
async def reenviar_respuesta(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat.id
    username = update.message.chat.username or f"ID: {user_id}"

    # Si el usuario envía un video
    if update.message.video:
        video = update.message.video.file_id
        caption = f"📩 *Nuevo video de un usuario*\n👤 Usuario: {username}\n🆔 ID: {user_id}"
        await context.bot.send_video(chat_id=ADMIN_ID, video=video, caption=caption, parse_mode="Markdown")

    # Si el usuario envía una foto
    elif update.message.photo:
        photo = update.message.photo[-1].file_id  # Tomamos la última (mayor calidad)
        caption = f"📩 *Nueva foto de un usuario*\n👤 Usuario: {username}\n🆔 ID: {user_id}"
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=caption, parse_mode="Markdown")

    # Si el usuario envía un documento (PDF, TXT, etc.)
    elif update.message.document:
        document = update.message.document.file_id
        caption = f"📩 *Nuevo documento de un usuario*\n👤 Usuario: {username}\n🆔 ID: {user_id}"
        await context.bot.send_document(chat_id=ADMIN_ID, document=document, caption=caption, parse_mode="Markdown")

    # Si el usuario envía un mensaje de voz
    elif update.message.voice:
        voice = update.message.voice.file_id
        caption = f"📩 *Nuevo mensaje de voz de un usuario*\n👤 Usuario: {username}\n🆔 ID: {user_id}"
        await context.bot.send_voice(chat_id=ADMIN_ID, voice=voice, caption=caption, parse_mode="Markdown")

    # Si el usuario envía solo texto
    elif update.message.text:
        mensaje = update.message.text
        mensaje_admin = f"📩 *Nueva respuesta de un usuario*\n👤 Usuario: {username}\n🆔 ID: {user_id}\n💬 Mensaje: {mensaje}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=mensaje_admin, parse_mode="Markdown")

    else:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"⚠️ Usuario {username} (ID: {user_id}) envió un tipo de archivo no soportado.")

# 🔹 Responder al usuario desde el bot
async def responder(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso correcto: `/responder ID mensaje`")
        return

    chat_id = context.args[0]
    mensaje = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=chat_id, text=mensaje)
        await update.message.reply_text(f"✅ Respuesta enviada a {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar respuesta: {e}")

# 🔹 Función principal
def main():
    app = Application.builder().token(TOKEN).build()

    # Manejar comandos y mensajes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enviar", enviar))
    app.add_handler(CommandHandler("responder", responder))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reenviar_respuesta))

    print("🤖 Bot en marcha con Webhooks...")

    # Configuración del Webhook en Render
    PORT = int(os.environ.get("PORT", 5000))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )

if __name__ == "__main__":
    main()


