import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 TOKEN del bot de Telegram
TOKEN = "7939507064:AAGvU-qUNAIEwHHF14X6Vuvw-5uRFigjCTg"
ADMIN_ID = 1570729026  # ⚠️ REEMPLAZA con tu ID de Telegram

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
        await update.message.reply_text("✅ Mensaje enviado correctamente.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar mensaje: {e}")

# 🔹 Iniciar el envío de un video manualmente a un usuario
async def enviar_video(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ Uso correcto: `/enviarvideo ID` (luego adjunta el video)")
        return

    chat_id = context.args[0]  # ID del usuario al que enviar el video
    context.user_data["video_destino"] = chat_id  # Guardamos el destinatario temporalmente

    await update.message.reply_text("📹 Ahora adjunta el video para enviarlo.")

# 🔹 Capturar el video adjunto y enviarlo al usuario correcto
async def recibir_video(update: Update, context: CallbackContext) -> None:
    chat_id = context.user_data.get("video_destino")  # Obtener destinatario

    if not chat_id:
        await update.message.reply_text("⚠️ Primero usa `/enviarvideo ID` antes de adjuntar un video.")
        return

    video = update.message.video.file_id  # Obtener el ID del video

    try:
        await context.bot.send_video(chat_id=chat_id, video=video, caption="🎥 Video enviado.")
        await update.message.reply_text("✅ Video enviado correctamente.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar el video: {e}")

    del context.user_data["video_destino"]  # Limpiar el destinatario después del envío

# 🔹 Reenviar respuestas de los usuarios al admin (incluye videos, fotos y documentos)
async def reenviar_respuesta(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat.id
    username = update.message.chat.username or f"ID: {user_id}"

    if update.message.video:
        video = update.message.video.file_id
        await context.bot.send_video(chat_id=ADMIN_ID, video=video, caption="📩 Nuevo video recibido.")

    elif update.message.photo:
        photo = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption="📩 Nueva foto recibida.")

    elif update.message.document:
        document = update.message.document.file_id
        await context.bot.send_document(chat_id=ADMIN_ID, document=document, caption="📩 Nuevo documento recibido.")

    elif update.message.voice:
        voice = update.message.voice.file_id
        await context.bot.send_voice(chat_id=ADMIN_ID, voice=voice, caption="📩 Nuevo mensaje de voz recibido.")

    elif update.message.text:
        mensaje = update.message.text
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📩 Nuevo mensaje recibido:\n{mensaje}")

# 🔹 Responder al usuario desde el bot
async def responder(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso correcto: `/responder ID mensaje`")
        return

    chat_id = context.args[0]
    mensaje = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=chat_id, text=mensaje)
        await update.message.reply_text("✅ Respuesta enviada correctamente.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar respuesta: {e}")

# 🔹 Función principal
def main():
    app = Application.builder().token(TOKEN).build()

    # Manejar comandos y mensajes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enviar", enviar))
    app.add_handler(CommandHandler("enviarvideo", enviar_video))
    app.add_handler(MessageHandler(filters.VIDEO, recibir_video))  # 🔹 Capturar videos adjuntos
    app.add_handler(CommandHandler("responder", responder))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reenviar_respuesta))
    app.add_handler(MessageHandler(filters.VIDEO | filters.PHOTO | filters.DOCUMENT | filters.VOICE, reenviar_respuesta))

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


