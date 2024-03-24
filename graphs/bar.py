import altair as alt
import streamlit as st

color_palette = ["#e07a5f", "#3d405b", "#81b29a", "#f2cc8f", "#f4f1de"]


@st.cache_resource
def grouped_bar(data, y_field, y_title):
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('senario:N', title=None, axis=alt.Axis(
            labels=False), sort=['baseline', 'RCP45', 'RCP85']),
        y=alt.Y(y_field, title=y_title),
        color=alt.Color('senario:N', scale=alt.Scale(
            range=color_palette), sort=['baseline', 'RCP45', 'RCP85']),
        column=alt.Column(
            'return_period:O',
            title="Return Period",
            header=alt.Header(labelOrient='bottom',
                              titleOrient='bottom', labelPadding=10),
        ),
    ).properties(
        width=100,
        height=300
    )

    st.altair_chart(chart, theme="streamlit", use_container_width=False)


def bar(df, y_field, x_field, y_axis_name=None, x_axis_name=None):
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(x_field, title=x_axis_name),
        y=alt.Y(y_field, title=y_axis_name),
        color=alt.Color(x_field, scale=alt.Scale(range=color_palette))
    ).properties(
        width=600,
        height=400
    )

    st.altair_chart(chart, theme="streamlit", use_container_width=False)
