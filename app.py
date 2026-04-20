import streamlit as st
import random
import time

st.set_page_config(page_title="Quiz Agnew MAX", layout="wide")

st.title("🎮 Quiz — Tensión y conducta (Agnew)")

# -----------------------------
# CONFIG
# -----------------------------
TIEMPO_PREGUNTA = 25

modo = st.sidebar.selectbox("Modo pantalla", ["Juego", "Ranking (proyector)"])

# -----------------------------
# ESTADO GLOBAL
# -----------------------------
if "equipos" not in st.session_state:
    st.session_state.equipos = {f"Grupo {i}": 0 for i in range(1, 11)}

if "bloqueados" not in st.session_state:
    st.session_state.bloqueados = []

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = 0

if "inicio_pregunta" not in st.session_state:
    st.session_state.inicio_pregunta = time.time()

if "respondido" not in st.session_state:
    st.session_state.respondido = False

if "evento_hecho" not in st.session_state:
    st.session_state.evento_hecho = False

if "respuesta_tiempo" not in st.session_state:
    st.session_state.respuesta_tiempo = None

if "no_suma" not in st.session_state:
    st.session_state.no_suma = None

# -----------------------------
# PREGUNTAS
# -----------------------------
preguntas = [
    ("¿Quién desarrolló la anomia moderna?", ["Durkheim", "Merton", "Agnew"], "Merton"),
    ("¿Capital de Canadá?", ["Toronto", "Ottawa", "Vancouver"], "Ottawa"),
    ("¿Año caída del Muro de Berlín?", ["1989", "1991", "1985"], "1989"),
    ("¿Elemento Fe?", ["Hierro", "Flúor", "Fósforo"], "Hierro"),
    ("¿Autor de 'La riqueza de las naciones'?", ["Smith", "Marx", "Keynes"], "Smith"),
    ("¿Planeta más grande?", ["Saturno", "Júpiter", "Neptuno"], "Júpiter"),
    ("¿Río más largo?", ["Amazonas", "Nilo", "Yangtsé"], "Amazonas"),
    ("¿Idioma oficial de Suiza?", ["1", "3", "4"], "4"),
    ("¿Pintor Guernica?", ["Dalí", "Picasso", "Miró"], "Picasso"),
    ("¿Capital de Turquía?", ["Estambul", "Ankara", "Izmir"], "Ankara"),
    ("¿País más grande?", ["China", "EEUU", "Rusia"], "Rusia"),
]

if "lista_preguntas" not in st.session_state:
    st.session_state.lista_preguntas = random.sample(preguntas, len(preguntas))

# -----------------------------
# RANKING
# -----------------------------
ranking = dict(sorted(st.session_state.equipos.items(), key=lambda x: x[1], reverse=True))

# -----------------------------
# MODO PROYECTOR
# -----------------------------
if modo == "Ranking (proyector)":
    st.header("🏆 CLASIFICACIÓN")
    st.bar_chart(ranking)
    st.stop()

# -----------------------------
# MODO JUEGO
# -----------------------------
grupo = st.selectbox("Selecciona tu grupo", list(st.session_state.equipos.keys()))

# -----------------------------
# FIN DEL JUEGO
# -----------------------------
if st.session_state.pregunta_actual >= len(st.session_state.lista_preguntas):
    st.header("🏁 FIN DEL JUEGO")
    ganador = max(st.session_state.equipos, key=st.session_state.equipos.get)
    st.success(f"🏆 Ganador: {ganador}")
    st.bar_chart(ranking)
    st.stop()

# -----------------------------
# PREGUNTA ACTUAL
# -----------------------------
p = st.session_state.lista_preguntas[st.session_state.pregunta_actual]
texto, opciones, correcta = p

st.subheader(f"Pregunta {st.session_state.pregunta_actual + 1}")
st.write(texto)

respuesta = st.radio("Elige una opción", opciones)

# -----------------------------
# TIMER
# -----------------------------
tiempo_actual = time.time()
tiempo_restante = TIEMPO_PREGUNTA - int(tiempo_actual - st.session_state.inicio_pregunta)
st.write(f"⏱️ {max(tiempo_restante,0)} segundos")

# -----------------------------
# RESPONDER
# -----------------------------
if not st.session_state.respondido:

    if st.button("Responder"):

        st.session_state.respondido = True
        st.session_state.respuesta_tiempo = tiempo_actual - st.session_state.inicio_pregunta

        if grupo in st.session_state.bloqueados:
            st.warning("⛔ Grupo bloqueado")

        else:
            if respuesta == correcta:

                puntos = 10

                if st.session_state.respuesta_tiempo < 5:
                    puntos += 5
                    st.info("⚡ Bonus rapidez +5")

                if st.session_state.no_suma == grupo:
                    st.info("✔️ Respuesta correcta… pero +0 puntos")
                    st.session_state.no_suma = None
                else:
                    st.session_state.equipos[grupo] += puntos
                    st.success(f"✔️ +{puntos} puntos")

            else:
                st.error("Incorrecto")

# -----------------------------
# EVENTOS
# -----------------------------
if st.session_state.respondido and not st.session_state.evento_hecho:

    if random.random() < 0.4:

        equipos = st.session_state.equipos
        ordenados = sorted(equipos.items(), key=lambda x: x[1], reverse=True)

        lider = ordenados[0][0]
        ultimo = ordenados[-1][0]

        evento = random.choice([
            "mitad",
            "robo",
            "bloqueo",
            "no_suma",
            "bonus_ultimo",
            "castigo_global"
        ])

        if evento == "mitad":
            perdida = equipos[lider] // 2
            equipos[lider] -= perdida
            st.error(f"💥 {lider} pierde {perdida} puntos")

        elif evento == "robo":
            origen, destino = random.sample(list(equipos.keys()), 2)
            robo = min(20, equipos[origen])
            equipos[origen] -= robo
            equipos[destino] += robo
            st.warning(f"🕵️ {destino} roba {robo} puntos a {origen}")

        elif evento == "bloqueo":
            st.session_state.bloqueados.append(grupo)
            st.warning(f"⛔ {grupo} no puntuará en la siguiente")

        elif evento == "no_suma":
            st.session_state.no_suma = grupo
            st.warning(f"⚠️ {grupo} acertará pero no sumará")

        elif evento == "bonus_ultimo":
            equipos[ultimo] += 15
            st.success(f"🎁 {ultimo} gana +15 puntos")

        elif evento == "castigo_global":
            for g in equipos:
                equipos[g] = max(0, equipos[g] - 5)
            st.error("🌪 Todos pierden 5 puntos")

    st.session_state.evento_hecho = True

# -----------------------------
# SIGUIENTE
# -----------------------------
if st.session_state.respondido:
    if st.button("➡️ Siguiente pregunta"):

        st.session_state.pregunta_actual += 1
        st.session_state.inicio_pregunta = time.time()

        st.session_state.respondido = False
        st.session_state.evento_hecho = False
        st.session_state.bloqueados = []

        st.rerun()

# -----------------------------
# CLASIFICACIÓN
# -----------------------------
st.subheader("🏆 Clasificación")
st.bar_chart(ranking)
