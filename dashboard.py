import streamlit as st
import pandas as pd
import plotly.express as px
import os
import libsql_experimental as libsql
from dotenv import load_dotenv

load_dotenv()
TURSO_URL   = os.getenv("TURSO_URL")
TURSO_TOKEN = os.getenv("TURSO_TOKEN")

st.set_page_config(page_title="Dashboard Bot IA", layout="wide")
st.title("Dashboard — Asistente de Ciencia de Datos")
st.caption("Análisis de conversaciones del bot de Telegram")

@st.cache_data(ttl=30)
def cargar_datos():
    con = libsql.connect("taller-bot", sync_url=TURSO_URL, auth_token=TURSO_TOKEN)
    con.sync()
    rows = con.execute("SELECT * FROM mensajes ORDER BY fecha DESC LIMIT 1000").fetchall()
    cols = ["id","fecha","usuario","user_id","pregunta","respuesta","tokens"]
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=cols)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["hora"]  = df["fecha"].dt.hour
    df["dia"]   = df["fecha"].dt.date
    return df

df = cargar_datos()
if df.empty:
    st.warning("Aún no hay conversaciones.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total mensajes",  len(df))
c2.metric("Usuarios únicos", df["user_id"].nunique())
c3.metric("Tokens usados",   int(df["tokens"].sum()))
c4.metric("Días activos",    df["dia"].nunique())

st.divider()
ca, cb = st.columns(2)
with ca:
    st.subheader("Mensajes por día")
    d = df.groupby("dia").size().reset_index(name="n")
    st.plotly_chart(px.bar(d, x="dia", y="n", color_discrete_sequence=["#1A3A5C"]), use_container_width=True)
with cb:
    st.subheader("Mensajes por hora")
    h = df.groupby("hora").size().reset_index(name="n")
    st.plotly_chart(px.line(h, x="hora", y="n", markers=True, color_discrete_sequence=["#E8A020"]), use_container_width=True)

st.subheader("Usuarios más activos")
top = df.groupby("usuario").size().reset_index(name="n").sort_values("n", ascending=True).tail(10)
st.plotly_chart(px.bar(top, x="n", y="usuario", orientation="h", color_discrete_sequence=["#1A3A5C"]), use_container_width=True)

st.subheader("Últimas conversaciones")
st.dataframe(df[["fecha","usuario","pregunta","respuesta","tokens"]].head(20), use_container_width=True, hide_index=True)

if st.button("Actualizar"):
    st.cache_data.clear()
    st.rerun()
```

---

**`requirements.txt`**
```
python-telegram-bot==20.7
groq==0.4.2
libsql-experimental==0.0.55
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.0.0
python-dotenv==1.0.1
