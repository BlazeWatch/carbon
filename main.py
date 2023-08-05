import os
from ast import literal_eval
from collections import namedtuple

import numpy as np
import streamlit as st
import jinja2
from htmlmin import minify
import addscript
import sqlalchemy as sa
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

engine = sa.create_engine(os.environ.get("DATABASE_URL"))

conn = engine.connect()

day = conn.scalar(sa.text('SELECT MAX(day) FROM public.temp_readings'))

avg = conn.execute(sa.text(f'SELECT AVG(temperature) FROM public.temp_readings WHERE day = {day}')).scalar()

addscript.add_custom_scripts()

st.set_page_config(
    page_title="Fire dashboard",
    layout="wide",
)

df = pd.DataFrame({
    'first column': list(range(1, 4)),
    'second column': list(range(4, 7))
})

cols = st.columns([1, 3, 1])

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)


def render_template(template: str, **kwargs):
    result = templateEnv.get_template(template)
    outputText = result.render(**kwargs)
    st.markdown(minify(outputText), unsafe_allow_html=True)


render_template("css.html")


def fetch_objects(conn, query):
    result_proxy = conn.execute(sa.text(query))

    records = [{column: value for column, value in zip(result_proxy.keys(), r)} for r in result_proxy.fetchall()]

    if records[0]["xy"] is not None:
        for record in records:
            record["xy"] = literal_eval(record["xy"])

    return records


with cols[0]:
    alerts = fetch_objects(conn, 'SELECT * FROM public.fire_alerts ORDER BY event_day DESC LIMIT 5')
    ai_alerts = fetch_objects(conn, 'SELECT * FROM public.ai_fire_alerts ORDER BY day DESC LIMIT 5')

    render_template("alerts.jinja2", alerts=alerts, ai_alerts=ai_alerts)

with cols[1]:
    col1, col2, col3 = st.columns(3)
    col1.metric("Fires", "2")
    col2.metric("AVG Temp", str(round(avg, 1)) + " °F")
    col3.metric("Day", day)
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])

    cols[1].line_chart(chart_data)

    cols[1].header("Hottest zones")
    cols[1].dataframe(
        pd.read_sql_query(f"SELECT * FROM temp_readings WHERE day = {day} ORDER BY temperature DESC LIMIT 20", conn),
        use_container_width=True, hide_index=True)

with cols[2]:
    tweets = fetch_objects(conn, f'SELECT * FROM public.tweets WHERE day = {day} LIMIT 20')

    render_template("tweets.jinja2", tweets=tweets)
