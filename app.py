import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from collections import Counter

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Fecha", "Emoción", "Comentario"])

emojis = {
    "Feliz 😊": "😊",
    "Triste 😢": "😢",
    "Ansioso 😰": "😰",
    "Estresado 😫": "😫",
    "Motivado 💪": "💪",
    "Cansado 😴": "😴",
    "En calma 🧘": "🧘"
}

# Consejos personalizados
consejos_por_emocion = {
    "Feliz 😊": [
        "¡Qué bien que te sientes feliz! Comparte tu alegría con alguien cercano.",
        "Aprovecha tu buen ánimo para hacer algo que te apasione."
    ],
    "Triste 😢": [
        "Está bien sentir tristeza, date permiso para expresarla.",
        "Habla con un amigo o familiar de confianza.",
        "Realiza actividades que te relajen, como escuchar música suave."
    ],
    "Ansioso 😰": [
        "Practica respiraciones profundas para calmar la ansiedad.",
        "Evita la cafeína y el exceso de pantallas.",
        "Realiza una caminata corta para despejar la mente."
    ],
    "Estresado 😫": [
        "Tómate breves descansos durante el día.",
        "Prioriza tus tareas y establece metas pequeñas.",
        "Haz ejercicios de relajación o meditación."
    ],
    "Motivado 💪": [
        "Aprovecha esta motivación para avanzar en tus proyectos.",
        "Establece objetivos claros y celebra cada logro."
    ],
    "Cansado 😴": [
        "Intenta descansar y dormir lo suficiente.",
        "Evita actividades muy demandantes hasta que recuperes energía."
    ],
    "En calma 🧘": [
        "Mantén esta tranquilidad con prácticas regulares de mindfulness.",
        "Aprovecha para planificar tu día con claridad."
    ]
}

st.title("📱 Seguimiento Emocional para Estudiantes")

tab1, tab2, tab3 = st.tabs(["Registrar Emoción", "Consejos", "Resultados"])

with tab1:
    st.header("📝 Registro diario de tu estado emocional")

    fecha = st.date_input("Selecciona la fecha", value=datetime.date.today())

    emocion = st.selectbox("¿Cómo te sientes hoy?", list(emojis.keys()))
    comentario = st.text_area("¿Quieres agregar algún comentario? (opcional)", max_chars=200)

    if st.button("Guardar registro"):
        nuevo = {
            "Fecha": pd.to_datetime(fecha),
            "Emoción": emocion,
            "Comentario": comentario
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([nuevo])], ignore_index=True)
        st.success("¡Registro guardado!")

with tab2:
    st.header("💡 Consejos personalizados para ti")

    emocion_actual = st.selectbox("Selecciona la emoción para ver consejos", list(emojis.keys()))

    st.markdown("### Consejos para cuando te sientes " + emocion_actual)
    for c in consejos_por_emocion.get(emocion_actual, []):
        st.markdown(f"- {c}")

    st.markdown("---")
    st.subheader("📞 Solicita ayuda profesional")

    with st.form("form_ayuda"):
        nombre = st.text_input("Nombre")
        email = st.text_input("Correo electrónico")
        motivo = st.text_area("¿Por qué necesitas ayuda?")

        enviar = st.form_submit_button("Enviar solicitud")

        if enviar:
            if nombre.strip() == "" or email.strip() == "" or motivo.strip() == "":
                st.error("Por favor, completa todos los campos para enviar la solicitud.")
            else:
                # Aquí podrías integrar un backend o API para enviar datos.
                st.success(f"Gracias {nombre}, tu solicitud ha sido recibida. Un profesional se contactará contigo pronto.")
                # Limpiar formulario (opcional)
                st.experimental_rerun()

with tab3:
    st.header("📅 Resumen emocional y calendario")

    if st.session_state.data.empty:
        st.info("No hay datos registrados todavía.")
    else:
        df = st.session_state.data.copy()
        df["Fecha"] = pd.to_datetime(df["Fecha"])

        fecha_min = df["Fecha"].min()
        fecha_max = df["Fecha"].max()

        rango_fecha = st.date_input(
            "Selecciona rango de fechas para visualizar",
            value=(fecha_min.date(), fecha_max.date()),
            min_value=fecha_min.date(),
            max_value=fecha_max.date(),
            key="rango_fechas"
        )

        if rango_fecha and len(rango_fecha) == 2:
            inicio, fin = pd.to_datetime(rango_fecha[0]), pd.to_datetime(rango_fecha[1])
            df_rango = df[(df["Fecha"] >= inicio) & (df["Fecha"] <= fin)]

            if df_rango.empty:
                st.warning("No hay registros en el rango seleccionado.")
            else:
                conteo_emociones = df_rango["Emoción"].value_counts().reset_index()
                conteo_emociones.columns = ["Emoción", "Frecuencia"]
                conteo_emociones["Emoji"] = conteo_emociones["Emoción"].map(emojis)

                fig = px.bar(
                    conteo_emociones,
                    x="Emoción",
                    y="Frecuencia",
                    text="Emoji",
                    color="Emoción",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                    title="Frecuencia de emociones"
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(yaxis_title="Cantidad", xaxis_title="Emoción", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### Calendario emocional")

                resumen_dia = df_rango.groupby("Fecha")["Emoción"].apply(lambda x: Counter(x).most_common(1)[0][0]).reset_index()
                resumen_dia["Emoji"] = resumen_dia["Emoción"].map(emojis)

                meses = resumen_dia["Fecha"].dt.to_period("M").unique()

                for mes in meses:
                    st.markdown(f"#### {mes.strftime('%B %Y')}")
                    dias_mes = pd.date_range(start=mes.start_time, end=mes.end_time, freq='D')

                    primer_dia_semana = dias_mes[0].weekday()  # 0=Lun, ... 6=Dom
                    total_dias = primer_dia_semana + len(dias_mes)
                    num_semanas = (total_dias + 6) // 7

                    tabla = [["" for _ in range(7)] for _ in range(num_semanas)]

                    for idx, dia in enumerate(dias_mes):
                        fila = (primer_dia_semana + idx) // 7
                        col = (primer_dia_semana + idx) % 7
                        emoji = resumen_dia.loc[resumen_dia["Fecha"] == dia, "Emoji"]
                        if not emoji.empty:
                            tabla[fila][col] = emoji.values[0]
                        else:
                            tabla[fila][col] = str(dia.day)

                    df_cal = pd.DataFrame(tabla, columns=["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"])

                    st.table(df_cal.style.set_properties(**{'font-size': '24px', 'text-align': 'center'}))
