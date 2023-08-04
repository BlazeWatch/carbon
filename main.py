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


def fetch_objects(conn, query):
    result_proxy = conn.execute(sa.text(query))

    records = [{column: value for column, value in zip(result_proxy.keys(), r)} for r in result_proxy.fetchall()]

    return records


with cols[0]:
    array = conn.execute(sa.text('SELECT * FROM public.fire_alerts ORDER BY event_day DESC LIMIT 8')).fetchall()
    for idx, row in enumerate(array):
        item = {"ai_reported": -1, "notification_day": row[1], "event_day": row[0], "xy": row[2]}
        with st.container():
            st.markdown("<div style='background-color:#f3f3f3'>", unsafe_allow_html=True)
            st.markdown(f"##### **Event on:** {item['event_day']}")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**AI Reported:** {item['ai_reported']}")
            with col2:
                st.markdown(f"**Notification Day:** {item['notification_day']}")
            st.markdown("</div>", unsafe_allow_html=True)

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
    for record in tweets:
        record["xy"] = literal_eval(record["xy"])
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "template.html"
    template = templateEnv.get_template("tweets.jinja2")
    outputText = template.render(tweets=tweets)
    st.markdown(minify(outputText), unsafe_allow_html=True)
