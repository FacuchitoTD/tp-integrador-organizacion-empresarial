# GLADOS_PROTOTYPE — Sistema Automatizado de Gestión de Procesos

Este proyecto corresponde al **Trabajo Práctico Integrador (TPI)** para la cátedra **Organización Empresarial** de la **Tecnicatura Universitaria en Programación a Distancia (TUPaD - UTN)**.

Consiste en un chatbot administrativo desarrollado en Python, integrado con la API de Telegram, diseñado para automatizar dos flujos de negocio críticos bajo un modelo estricto de máquina de estados y persistencia en una base de datos relacional local (SQLite).

---

## Características Principales

- **Persistencia Real:** Motor embebido SQLite 3 (`Glados.db`) para el seguimiento exacto de las sesiones entre reinicios.
- **Máquina de Estados Finita (FSM):** Control estricto de 4 estados discretos que impide saltos de pasos indebidos.
- **Gestión del Camino Infeliz:** Validación exhaustiva de tipos de datos ante respuestas erróneas del usuario en todos los estados.
- **Dos Trámites Administrativos con Reglas de Negocio:**
  - *Trámite 101 — Rendición de Gastos:* Evaluación de montos con bifurcación automática (aprobación inmediata ≤ $50.000 vs. auditoría manual).
  - *Trámite 202 — Solicitud de Vacaciones:* Validación de saldo de días disponibles (máximo 14 días simulados).
- **Bloqueo de Seguridad:** Una vez finalizado el proceso, el Estado 3 blinda el registro para resguardar la integridad de los datos.
- **Coherencia BPMN 2.0:** La lógica del bot responde fielmente al diagrama de procesos modelado con carriles, compuertas y eventos.

---

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Una cuenta de Telegram y un bot creado a través de [@BotFather](https://t.me/BotFather)

---

## Instalación y Configuración

**1. Clonar el repositorio:**

```bash
git clone https://github.com/FacuchitoTD/tp-integrador-organizacion-empresarial.git
cd tp-integrador-organizacion-empresarial
```

**2. Crear y activar un entorno virtual (recomendado):**

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows
```

**3. Instalar la dependencia:**

```bash
pip install pyTelegramBotAPI
```

**4. Configurar el TOKEN del bot:**

Abrí el archivo `bot_telegram.py` y reemplazá el valor de `TOKEN` con el token que te proveyó @BotFather:

```python
TOKEN = "TU_TOKEN_AQUI"
```

**5. Ejecutar el bot:**

```bash
python bot_telegram.py
```

Si el bot inició correctamente, verás en la terminal:

```
Bot GLADOS_PROTOTYPE iniciado y escuchando activamente...
```

---

## Estructura del Proyecto

```
tp-integrador-organizacion-empresarial/
│
├── bot_telegram.py        # Script principal del bot
├── Glados.db              # Base de datos SQLite (se genera automáticamente al primer uso)
└── README.md              # Este archivo
```

---

## Uso

Una vez el bot esté corriendo, abrí Telegram y buscá tu bot. Los comandos disponibles son:

| Comando / Entrada | Acción |
|---|---|
| `/start` | Inicializa o reinicia el proceso. Resetea el estado en la BD y muestra el menú. |
| `101` | Selecciona el trámite de Rendición de Gastos. |
| `202` | Selecciona el trámite de Solicitud de Vacaciones. |
| *(monto entero)* | En el trámite 101, ingresa el monto a rendir (ej: `45000`). |
| *(cantidad de días)* | En el trámite 202, ingresa los días solicitados (ej: `7`). |

---

## Máquina de Estados

El bot opera con 4 estados persistidos en la base de datos:

| Estado | Nombre | Descripción |
|---|---|---|
| `0` | INICIO | Menú principal. Aguarda selección de trámite (101 o 202). |
| `1` | RENDICIÓN DE GASTOS | Aguarda el monto. Aplica regla de negocio: ≤ $50.000 aprueba automáticamente, > $50.000 deriva a auditoría. |
| `2` | SOLICITUD DE VACACIONES | Aguarda cantidad de días. Aplica regla: ≤ 14 días aprueba, > 14 días rechaza por saldo insuficiente. |
| `3` | TRÁMITE CERRADO | Estado terminal. Bloquea el registro. Solo se sale vía `/start`. |

---

## Base de Datos

El archivo `Glados.db` se crea automáticamente en el mismo directorio al primer uso. Contiene una única tabla:

**Tabla `tramites`:**

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER PRIMARY KEY | `chat_id` del usuario en Telegram. |
| `nombre` | TEXT | Nombre de pila del usuario. |
| `estado` | INTEGER | Estado actual en la máquina de estados (0 a 3). |
| `tipo_tramite` | TEXT | Trámite seleccionado (`Rendicion de Gastos` / `Solicitud de Vacaciones`). |
| `dato_adicional` | TEXT | Resolución final del trámite (resultado de la regla de negocio aplicada). |

---

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.x |
| API de Mensajería | Telegram Bot API (pyTelegramBotAPI) |
| Base de Datos | SQLite 3 (módulo `sqlite3` — stdlib) |
| Despliegue | Local / cualquier servidor con Python |

---

## Integrantes del Equipo

| Nombre | Rol | GitHub |
|---|---|---|
| Facundo López | Desarrollador Técnico | [@FacuchitoTD](https://github.com/FacuchitoTD) |
| Leonel Leandro Quiroga | Documentación | [@leo15deluxe](https://github.com/leo15deluxe) |

TUPaD UTN — Organización Empresarial — Cohorte Marzo 2026
