import streamlit as st
import random
import time

st.set_page_config(page_title="Quiz Agnew MAX", layout="wide")

st.title("🎮 Quiz — Tensión y conducta (Agnew)")

TIEMPO_PREGUNTA = 25

modo = st.sidebar.selectbox("Modo pantalla", ["Juego", "Ranking (proyector)"])

# -----------------------------
# ESTADO
# -----------------------------
if "equipos" not in st.session_state:
    st.session_state.equipos = {f"Grupo {i}": 0 for i in range(1, 11)}

if "pregunta_actual" not in st.session_state:
    st.session_state.pregunta_actual = 0

if "inicio_pregunta" not in st.session_state:
    st.session_state.inicio_pregunta = None

if "respondido" not in st.session_state:
    st.session_state.respondido = False

if "grupo" not in st.session_state:
    st.session_state.grupo = None

if "juego_iniciado" not in st.session_state:
    st.session_state.juego_iniciado = False

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
    ("¿Quién escribió Hamlet?", ["Shakespeare", "Cervantes", "Dante"], "Shakespeare"),
    ("¿Velocidad de la luz?", ["300.000 km/s", "150.000", "1.000.000"], "300.000 km/s"),
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
# SELECCIÓN GRUPO
# -----------------------------
grupo = st.selectbox("Selecciona tu grupo", list(st.session_state.equipos.keys()))

if st.button("🚀 Comenzar juego"):
    st.session_state.grupo = grupo
    st.session_state.juego_iniciado = True
    st.session_state.inicio_pregunta = time.time()

if not st.session_state.juego_iniciado:
    st.stop()

grupo = st.session_state.grupo

# -----------------------------
# FIN DEL JUEGO
# -----------------------------
if st.session_state.pregunta_actual >= len(st.session_state.lista_preguntas):

    st.header("🏁 FIN DEL JUEGO")

    ranking_real = sorted(st.session_state.equipos.items(), key=lambda x: x[1], reverse=True)

    for g, _ in ranking_real:
        if g != grupo:
            ganador = g
            break

    st.success(f"🏆 Ganador: {ganador}")
    st.bar_chart(dict(ranking_real))
    st.stop()

# -----------------------------
# PREGUNTA
# -----------------------------
texto, opciones, correcta = st.session_state.lista_preguntas[st.session_state.pregunta_actual]

st.subheader(f"Pregunta {st.session_state.pregunta_actual + 1}")
st.write(texto)

respuesta = st.radio("Elige una opción", opciones, key=f"radio_{st.session_state.pregunta_actual}")

# -----------------------------
# TIMER VISUAL
# -----------------------------
tiempo_restante = TIEMPO_PREGUNTA - int(time.time() - st.session_state.inicio_pregunta)
tiempo_restante = max(0, tiempo_restante)

st.progress(1 - (tiempo_restante / TIEMPO_PREGUNTA))
st.write(f"⏱️ {tiempo_restante} segundos")

# -----------------------------
# RESPUESTA
# -----------------------------
if not st.session_state.respondido:

    if st.button("Responder"):

        st.session_state.respondido = True

        if respuesta == correcta:

            puntos = 10
            st.session_state.equipos[grupo] += puntos
            st.success(f"✔️ Correcto +{puntos}")

            # -----------------------------
            # SIMULACIÓN DE OTROS GRUPOS
            # -----------------------------
            for g in st.session_state.equipos:
                if g != grupo:
                    if random.random() < 0.6:
                        st.session_state.equipos[g] += random.randint(5, 12)
                    elif random.random() < 0.2:
                        st.session_state.equipos[g] = max(0, st.session_state.equipos[g] - random.randint(1, 5))

            # -----------------------------
            # EVENTOS (TENSIÓN PROGRESIVA)
            # -----------------------------
            progreso = st.session_state.pregunta_actual / len(st.session_state.lista_preguntas)

            if random.random() < (0.2 + progreso * 0.5):

                evento = random.choice(["pierde", "robo", "delay"])

                if evento == "pierde":
                    perdida = random.randint(5, 15)
                    st.session_state.equipos[grupo] = max(0, st.session_state.equipos[grupo] - perdida)
                    st.warning(f"⚠️ Error inesperado: -{perdida} puntos")

                elif evento == "robo":
                    otros = [g for g in st.session_state.equipos if g != grupo]
                    objetivo = random.choice(otros)

                    if st.session_state.equipos[objetivo] > 0:
                        robo = min(random.randint(5, 10), st.session_state.equipos[objetivo])
                        st.session_state.equipos[objetivo] -= robo
                        st.session_state.equipos[grupo] += robo
                        st.warning(f"🕵️ Has robado {robo} puntos a {objetivo}")
                    else:
                        st.info(f"🕵️ Intento de robo fallido: {objetivo} sin puntos")

                elif evento == "delay":
                    st.info("⏳ Validando respuesta...")
                    time.sleep(2)
                    st.success("✔️ Confirmado")

            # -----------------------------
            # FEEDBACK POSICIÓN
            # -----------------------------
            ranking_actual = sorted(
                st.session_state.equipos.items(),
                key=lambda x: x[1],
                reverse=True
            )

            posicion = [g for g, _ in ranking_actual].index(grupo) + 1

            if posicion == 1:
                st.success("🔥 Vas en 1ª posición")
            elif posicion <= 3:
                st.info(f"📈 Vas en posición {posicion}")
            else:
                st.warning(f"📉 Has bajado a la posición {posicion}")

            # -----------------------------
            # CASTIGO AL LÍDER
            # -----------------------------
            if posicion == 1 and random.random() < 0.3:
                perdida = random.randint(5, 10)
                st.session_state.equipos[grupo] = max(0, st.session_state.equipos[grupo] - perdida)
                st.warning(f"⚠️ ATENCIÓN: -{perdida} puntos por robo de otro grupo")

        else:
            st.error("Incorrecto")

# -----------------------------
# SIGUIENTE
# -----------------------------
if st.session_state.respondido:

    if st.button("➡️ Siguiente pregunta"):

        st.session_state.pregunta_actual += 1
        st.session_state.inicio_pregunta = time.time()
        st.session_state.respondido = False

        st.rerun()

# -----------------------------
# CLASIFICACIÓN
# -----------------------------
st.subheader("🏆 Clasificación")
st.bar_chart(ranking)
