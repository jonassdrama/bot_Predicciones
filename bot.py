import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Token del bot de Telegram
TOKEN = "7939507064:AAGvU-qUNAIEwHHF14X6Vuvw-5uRFigjCTg"

# 🔹 Cargar credenciales de Google Sheets desde Render
import json

import json
import os

creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

# 🔹 Conectar con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 🔹 Abrir la hoja de cálculo
SHEET_ID = "1uf5xu8CW7KDnElNeog2WH_DD5imEyhJ8qap_OwQjcz8"
sheet = client.open_by_key(SHEET_ID).sheet1

# 🔹 Comando /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "¡Bienvenido a Isa Winning Bot! 🏆\n"
        "Envía tu predicción en formato: 'Equipo1 X - Equipo2 Y'"
    )

# 🔹 Función para guardar predicciones en Google Sheets
async def recibir_prediccion(update: Update, context: CallbackContext) -> None:
    usuario = update.message.chat.username or update.message.chat.id
    texto = update.message.text

    try:
        # Dividir el texto en partes (Ejemplo: "Real Madrid 2 - Barcelona 1")
        partes = texto.split("-")
        
        if len(partes) != 2:
            await update.message.reply_text("⚠️ Formato incorrecto. Usa: 'Equipo1 X - Equipo Y'")
            return
        
        equipo1 = partes[0].strip()
        equipo2 = partes[1].strip()

        # Guardar en Google Sheets
        sheet.append_row([usuario, equipo1, equipo2])

        await update.message.reply_text("✅ Predicción guardada correctamente.")
        print(f"✅ Guardado en Sheets: {usuario}, {equipo1}, {equipo2}")  # Debugging en terminal

    except Exception as e:
        print(f"❌ Error al guardar en Sheets: {e}")
        await update.message.reply_text("❌ Hubo un error al guardar la predicción.")

# 🔹 Configuración de Webhooks en Render
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_prediccion))

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

