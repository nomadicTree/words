import streamlit as st


def inject_styles():
    st.html(
        """
    <style>
    .frayer-word {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0;
        padding: 0;    
        font-size: 1.8rem;
        font-weight: 600; /* bold */
    }

    .search-title-block {
    margin-bottom: 0;  
    }

    .search-word {
        font-weight: 600;
        font-size: 1.05rem;          /* slightly larger than body text */
        margin-bottom: 0.1rem;       /* tiny, controlled spacing */
    }

    .search-caption {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0;               /* remove default paragraph spacing */
        margin-bottom: 0;
    }
    """
    )


def page_header(title: str = "") -> None:
    inject_styles()
    if title:
        st.title(title)
        st.divider()
    else:
        st.title("FrayerStore")
