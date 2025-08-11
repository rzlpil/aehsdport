import streamlit as st

pages = {
    "Menu": [
        st.Page("aehsd.py", title="A/E HSD"),
        st.Page("memfo.py", title="M/E MFO"),
    ]
}

pg = st.navigation(pages)
pg.run()
