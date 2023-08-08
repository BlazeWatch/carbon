import os
import time
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
import plotly.graph_objects as go
import plotly.express as px

load_dotenv()

st.set_page_config(
    page_title="Zaza Monitor",
    layout="wide",
    page_icon="/app/static/iconee.png",
    initial_sidebar_state="collapsed",
)


@st.cache_resource(ttl=20)
def get_conn():
    print("Connecting to database")
    engine = sa.create_engine(os.environ.get("DATABASE_URL"))

    conn = engine.connect()
    print("Connected to database")
    return conn


# addscript.add_custom_scripts()

df = pd.DataFrame({
    'first column': list(range(1, 4)),
    'second column': list(range(4, 7))
})

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)

placeholder = st.empty()
conn = get_conn()


def render_template(template: str, **kwargs):
    result = templateEnv.get_template(template)
    outputText = result.render(**kwargs)
    st.markdown(minify(outputText), unsafe_allow_html=True)


render_template("css.html")


@st.cache_data(ttl=1, show_spinner=False)
def fetch_objects(query):
    print(f"FO: {query}")
    result_proxy = conn.execute(sa.text(query))
    if result_proxy.rowcount == 0:
        return []
    records = [{column: value for column, value in zip(result_proxy.keys(), r)} for r in result_proxy.fetchall()]

    if records[0]["xy"] is not None:
        for record in records:
            record["xy"] = literal_eval(record["xy"])
    return records


@st.cache_data(ttl=60, show_spinner=False)
def fetch_panda_frame(query):
    print(f"PD: {query}")
    return pd.read_sql_query(query, conn)


max_day = conn.scalar(sa.text('SELECT MAX(day) FROM public.temp_readings_production'))

with st.sidebar:
    page = st.radio(
        "What\'s your favorite movie genre",
        ('realtime', 'stats'))
    if page == 'realtime':
        day = st.number_input("Day", min_value=1, max_value=5000, value=max_day)
        if day > max_day:
            day = max_day
        if day == 0:
            day = max_day


def calculate_avg_temperature_per_plot():
    query = 'SELECT xy, AVG(temperature) FROM public.temp_readings_production GROUP BY xy'
    return fetch_objects(query)


def plot_avg_temperature_per_plot():
    # Fetch average temperature per plot
    avg_temperatures = calculate_avg_temperature_per_plot()

    # Prepare data for the chart
    plots = [str(record['xy']) for record in avg_temperatures]
    temperatures = [record['temperature'] for record in avg_temperatures]

    # Create a DataFrame
    df_avg_temperatures = pd.DataFrame({
        'Plot': plots,
        'Avg Temperature': temperatures
    })

    # Plot the chart
    fig = px.bar(df_avg_temperatures, x='Plot', y='Avg Temperature', title='Average Temperature per Plot')
    st.plotly_chart(fig)


if page == 'stats':
    st.markdown("A small tab with some stats about the dataset")

    tweet_count = conn.scalar(sa.text(f'SELECT COUNT(*) FROM public.tweets_production'))
    fire_alert_count = conn.scalar(sa.text(f'SELECT COUNT(*) FROM public.fire_alerts_production'))
    ai_fire_alert_count = conn.scalar(sa.text(f'SELECT COUNT(*) FROM public.ai_fire_alerts'))
    temperature_reading_count = conn.scalar(sa.text(f'SELECT COUNT(*) FROM public.temp_readings_production'))
    avg_temperature = conn.scalar(sa.text(f'SELECT AVG(temperature) FROM public.temp_readings_production'))
    max_temperature = conn.scalar(sa.text(f'SELECT MAX(temperature) FROM public.temp_readings_production'))
    min_temperature = conn.scalar(sa.text(f'SELECT MIN(temperature) FROM public.temp_readings_production'))

    st.table([
        ("Tweet Count", tweet_count),
        ("Fire Alert Count", fire_alert_count),
        ("AI Fire Alert Count", ai_fire_alert_count),
        ("Temperature Reading Count", temperature_reading_count),
        ("Average Temperature", avg_temperature),
        ("Max Temperature", max_temperature),
        ("Min Temperature", min_temperature)
    ])

    df_stats = pd.DataFrame({
        "Category": ["Tweet Count", "Fire Alert Count", "AI Fire Alert Count", "Temperature Reading Count"],
        "Count": [tweet_count, fire_alert_count, ai_fire_alert_count, temperature_reading_count]
    })

    fig = go.Figure(data=go.Bar(x=df_stats["Category"], y=df_stats["Count"]))
    fig.update_layout(yaxis_type="log", title_text="Logarithmic Scale Bar Chart")
    st.plotly_chart(fig)

    plot_avg_temperature_per_plot()

while page != 'stats':
    avg = conn.scalar(sa.text(f'SELECT AVG(temperature) FROM public.temp_readings_production WHERE day = {day}'))
    with placeholder.container():
        cols = st.columns([1, 3, 1])

        with cols[0]:
            alerts = fetch_objects(
                f'SELECT * FROM public.fire_alerts_production WHERE notification_day <= {day} ORDER BY event_day DESC LIMIT 5')
            ai_alerts = fetch_objects(
                f'SELECT * FROM public.ai_fire_alerts WHERE day <= {day} ORDER  BY day DESC LIMIT 5')

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
                fetch_panda_frame(
                    f"SELECT * FROM temp_readings_production WHERE day = {day} ORDER BY temperature DESC LIMIT 20"),
                use_container_width=True, hide_index=True)

        with cols[2]:
            tweets = fetch_objects(f'SELECT * FROM public.tweets_production WHERE day = {day} LIMIT 20')
            render_template("tweets.jinja2", tweets=tweets, day=day)
        print("Reloading")
        time.sleep(4)
