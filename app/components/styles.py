import streamlit as st


def apply_styles():
    st.html(
        """
    <style>
    [data-testid='stHeaderActionElements'] {display: none;}
    .open-link-icon {
        text-decoration: none !important;
        opacity: 0;
        transition: opacity 0.2s;
        cursor: pointer;
    }

    .frayer-title .word-link {
        text-decoration: none !important;
        color: inherit;
        position: relative;
    }

    .frayer-title:hover .open-link-icon {
        opacity: 1;
    }
    </style>
    """
    )


def page_header(title: str = ""):
    st.title("FrayerStore")
    if title:
        st.header(title)
    apply_styles()


def show_markdown_file(file_path: Path, in_container: bool = False):
    md_text = Path(file_path).read_text(encoding="utf-8")
    if in_container:
        with st.container(border=True):
            st.markdown(md_text)
    else:
        st.markdown(md_text)
