import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from htmlBuilder.attributes import Class
from htmlBuilder.tags import *
import jinja2
import htmlmin
from htmlmin import minify
import addscipt

addscipt.add_analytics_tag()

st.set_page_config(
    page_title="My Dashboard",
    layout="wide",
)

df = pd.DataFrame({
    'first column': list(range(1, 4)),
    'second column': list(range(4, 7))
})

cols = st.columns([1, 3, 1])

with cols[0]:
    array = [
        {'ai_reported': 32, 'event_day': 19, 'notification_day': 13, 'xy': [12, 1]},
        {'ai_reported': 11, 'event_day': 17, 'notification_day': 13, 'xy': [11, 1]},
        {'ai_reported': 32, 'event_day': 16, 'notification_day': 13, 'xy': [3, 1]},
        {'ai_reported': 14, 'event_day': 14, 'notification_day': 13, 'xy': [1, 1]},
        {'ai_reported': 52, 'event_day': 11, 'notification_day': 13, 'xy': [23, 1]},
    ]

    # st.markdown(
    #     Section(
    #         [],
    #         [
    #             Div([Class(f"tw-{tweet['ai_reported']}")],
    #                 Div([],
    #                     H5([],
    #                        f"**Event on:** {tweet['event_day']}"
    #                        ),
    #                     )
    #                 ) for tweet in array],
    #     ).render(),
    #     unsafe_allow_html=True
    # )

    for idx, item in enumerate(array):
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
    col2.metric("AVG Temp", "80 °F")
    col3.metric("Day", "2")
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])

    cols[1].line_chart(chart_data)

    cols[1].dataframe(df, use_container_width=True)

with cols[2]:
    tweets = [
        {"day": 4, "xy": [12, 1], "content": "A cat", "score": 0.7},
        {"day": 5, "xy": [11, 1], "content": "A dog", "score": 0.3},
        {"day": 6, "xy": [3, 1], "content": "An owl", "score": 0.2},
        {"day": 7, "xy": [1, 1], "content": "A bird", "score": 0.1},
        {"day": 8, "xy": [23, 1], "content": "A fish", "score": 0.0},
        {"day": 10, "xy": [23, 1], "content": "A Fly", "score": 0.5},
        {"day": 11, "xy": [23, 1], "content": "A Bish", "score": 0.3},
        {"day": 12, "xy": [23, 1], "content": "A Lion", "score": 0.2},
        {"day": 13, "xy": [23, 1], "content": "A Wolf", "score": 0.1},
        {"day": 14, "xy": [23, 1], "content": "A Fox", "score": 0.0}
    ]
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "template.html"
    template = templateEnv.get_template("tweets.jinja2")
    outputText = template.render(tweets=tweets)
    st.markdown(minify(outputText), unsafe_allow_html=True)

# cols[2].dataframe(df, use_container_width=True)
