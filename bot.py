from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = "7939507064:AAGvU-qUNAIEwHHF14X6Vuvw-5uRFigjCTg"

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Bienvenido a Isa Winning Bot! Envía tu predicción en formato 'Equipo1 X - Equipo2 Y'")

async def recibir_prediccion(update: Update, context: CallbackContext) -> None:
    texto = update.message.text
    await update.message.reply_text(f"Recibí tu pronóstico: {texto}. ¡Suerte!")

import os

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
recibir_prediccion))

    print("🤖 Bot en marcha con Webhooks...")

    PORT = int(os.environ.get("PORT", 5000))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        
webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    )

if __name__ == "__main__":
    main()

