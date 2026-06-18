import os
import telebot
import sqlite3
from dotenv import load_dotenv

# Cargar el token desde el archivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
# ========================================================
# FUNCIONES DE BASE DE DATOS (Tareas de Servicio)
# ========================================================

def conectar_bd():
    "Función para conectar a la base de datos SQLite y crear la tabla 'tramites' si no existe."
    conexion = sqlite3.connect("Glados.db")
    cursor = conexion.cursor()
    # Se crea la tabla 'tramites' con una columna 'estado' para gestionar la memoria
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tramites (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            estado INTEGER DEFAULT 0,
            tipo_tramite TEXT,
            dato_adicional TEXT
        )
    """)
    conexion.commit()
    return conexion, cursor

def obtener_estado_usuario(chat_id, nombre):
    conexion, cursor = conectar_bd()
    cursor.execute("SELECT estado FROM tramites WHERE id = ?", (chat_id,))
    resultado = cursor.fetchone()
    
    if resultado is None:
        # Estado 0: Inicio del proceso administrativo
        cursor.execute("INSERT INTO tramites (id, nombre, estado) VALUES (?, ?, 0)", (chat_id, nombre))
        conexion.commit()
        estado = 0
    else:
        estado = resultado[0]
        
    conexion.close()
    return estado

def actualizar_registro(chat_id, nuevo_estado, tipo_tramite=None, dato_adicional=None):
    conexion, cursor = conectar_bd()
    if tipo_tramite and dato_adicional:
        cursor.execute("""
            UPDATE tramites 
            SET estado = ?, tipo_tramite = ?, dato_adicional = ? 
            WHERE id = ?
        """, (nuevo_estado, tipo_tramite, dato_adicional, chat_id))
    elif tipo_tramite:
        cursor.execute("UPDATE tramites SET estado = ?, tipo_tramite = ? WHERE id = ?", (nuevo_estado, tipo_tramite, chat_id))
    elif dato_adicional:
        cursor.execute("UPDATE tramites SET estado = ?, dato_adicional = ? WHERE id = ?", (nuevo_estado, dato_adicional, chat_id))
    else:
        cursor.execute("UPDATE tramites SET estado = ? WHERE id = ?", (nuevo_estado, chat_id))
    conexion.commit()
    conexion.close()

def reiniciar_tramite(chat_id):
    conexion, cursor = conectar_bd()
    cursor.execute("UPDATE tramites SET estado = 0, tipo_tramite = NULL, dato_adicional = NULL WHERE id = ?", (chat_id,))
    conexion.commit()
    conexion.close()

# ========================================================
# CONTROLADORES DE TRAFICO (Lógica de Compuertas BPMN)
# ========================================================

@bot.message_handler(commands=['start'])
def comando_start(message):
    chat_id = message.chat.id
    nombre_usuario = message.from_user.first_name
    
    # Inicializa o consulta el estado actual
    obtener_estado_usuario(chat_id, nombre_usuario)
    reiniciar_tramite(chat_id)
    
    bienvenida = (
        f"¡Hola {nombre_usuario}! Bienvenido al Asistente de Gestión GLADOS_PROTOTYPE.\n\n"
        "Por favor, elija el código del trámite que desea iniciar:\n"
        "- Ingrese 101 para: Rendicion de Gastos\n"
        "- Ingrese 202 para: Solicitud de Vacaciones\n\n"
        "Escriba únicamente el número."
    )
    bot.send_message(chat_id, bienvenida)

@bot.message_handler(func=lambda message: True)
def gestionar_flujo(message):
    chat_id = message.chat.id
    texto_recibido = message.text.strip()
    nombre_usuario = message.from_user.first_name
    
    # Recuperamos en qué paso del proceso se encuentra el usuario
    estado = obtener_estado_usuario(chat_id, nombre_usuario)
    
    # ------------------------------------------------------------
    # ESTADO 0: Selección del Tipo de Trámite
    # ------------------------------------------------------------
    if estado == 0:
        # CAMINO INFELIZ: Validación de tipo de dato
        if not texto_recibido.isdigit():
            bot.reply_to(message, "[ERROR - CAMINO INFELIZ]\nEl código de trámite debe ser únicamente un número entero. Por favor, inténtelo de nuevo (101 o 202):")
            return
            
        codigo = int(texto_recibido)
        
        # COMPUERTA DE DECISIÓN: Evaluación del catálogo de trámites
        if codigo == 101:
            actualizar_registro(chat_id, nuevo_estado=1, tipo_tramite="Rendicion de Gastos")
            bot.reply_to(message, "Ha seleccionado: *Rendición de Gastos*.\nPor favor, ingrese el *monto total* del gasto en pesos (solo números enteros sin signos ni puntos):", parse_mode="Markdown")
        elif codigo == 202:
            actualizar_registro(chat_id, nuevo_estado=2, tipo_tramite="Solicitud de Vacaciones")
            bot.reply_to(message, "Ha seleccionado: *Solicitud de Vacaciones*.\nPor favor, ingrese la *cantidad de días* que desea solicitar (máximo disponible: 14 días):")
        else:
            # Camino infeliz alternativo: número válido pero fuera del catálogo
            bot.reply_to(message, "El número ingresado no corresponde a ningún trámite activo. Ingrese *101* o *202*:", parse_mode="Markdown")

    # ------------------------------------------------------------
    # ESTADO 1: Validación de Regla de Negocio - Rendición de Gastos
    # ------------------------------------------------------------
    elif estado == 1:
        # CAMINO INFELIZ: Validación numérico
        if not texto_recibido.isdigit():
            bot.reply_to(message, "[ERROR - CAMINO INFELIZ]\nMonto inválido. Ingrese el valor numérico entero correspondiente al gasto:")
            return
            
        monto = int(texto_recibido)
        
        # COMPUERTA LÓGICA DE NEGOCIO (Límite de aprobación automática)
        if monto <= 50000:
            msg_exito = f"*Tramite Completado.*\nMonto: ${monto}. Al ser menor o igual a $50,000, su rendición fue aprobada de forma AUTOMÁTICA por el sistema. Proceso Finalizado."
            actualizar_registro(chat_id, nuevo_estado=3, dato_adicional=f"Aprobado Automatico - ${monto}")
            bot.reply_to(message, msg_exito, parse_mode="Markdown")
        else:
            msg_revision = f"*Tramite en Revisión.*\nMonto: ${monto}. Al superar el límite de $50,000, el trámite requiere una auditoría y firma de la Gerencia de Finanzas. Proceso Finalizado."
            actualizar_registro(chat_id, nuevo_estado=3, dato_adicional=f"Requiere Auditoria Manual - ${monto}")
            bot.reply_to(message, msg_revision, parse_mode="Markdown")

    # ------------------------------------------------------------
    # ESTADO 2: Validación de Regla de Negocio - Solicitud de Vacaciones
    # ------------------------------------------------------------
    elif estado == 2:
        # CAMINO INFELIZ: Validación numérico
        if not texto_recibido.isdigit():
            bot.reply_to(message, "[ERROR - CAMINO INFELIZ]\nCantidad inválida. Ingrese el número de días solicitados en caracteres numéricos:")
            return
            
        dias = int(texto_recibido)
        
        # COMPUERTA LÓGICA DE NEGOCIO (Validación de Saldo Disponible Simulado)
        if dias <= 14:
            msg_vac_ok = f"*Tramite Completado.*\nDias solicitados: {dias}. Su saldo es suficiente (Disponibles: 14). Las fechas han sido agendadas con éxito. Proceso Finalizado."
            actualizar_registro(chat_id, nuevo_estado=3, dato_adicional=f"Vacaciones Aprobadas - {dias} dias")
            bot.reply_to(message, msg_vac_ok, parse_mode="Markdown")
        else:
            msg_vac_error = f"*Tramite Rechazado.*\nDias solicitados: {dias}. Su saldo actual de días es insuficiente (Máximo disponible: 14 días). Proceso Finalizado."
            actualizar_registro(chat_id, nuevo_estado=3, dato_adicional=f"Rechazado por saldo insuficiente - {dias} dias")
            bot.reply_to(message, msg_vac_error, parse_mode="Markdown")

    # ------------------------------------------------------------
    # ESTADO 3: Bloqueo de seguridad (Trámite ya finalizado)
    # ------------------------------------------------------------
    elif estado == 3:
        bot.reply_to(message, f"Hola {nombre_usuario}, tu trámite actual ya se encuentra *CERRADO* en el sistema para evitar modificaciones innecesarias.\n\nSi deseás iniciar un nuevo proceso administrativo, por favor enviá el comando /start.", parse_mode="Markdown")

# ========================================================
# 3. INICIALIZACIÓN CONTINUA
# ========================================================
if __name__ == "__main__":
    print("Bot GLADOS_PROTOTYPE iniciado y escuchando activamente...")
    bot.infinity_polling()