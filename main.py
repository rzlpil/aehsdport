import streamlit as st

pages = {
    "Menu": [
        st.Page("aehsdport.py", title="A/E HSD at Port"),
        st.Page("memfo.py", title="M/E MFO"),
    ]
}

pg = st.navigation(pages)
pg.run()
