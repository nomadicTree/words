import streamlit as st


def select_item(items: list, key: str, label: str):
    """
    Generic selection helper that:
    - stores only PKs in session_state (safe across reloads)
    - rebuilds selected object from PK each run
    - handles stale PKs (when filters change after reload)
    - keeps query params in sync with the selection
    """

    if not items:
        st.warning(f"No options available for {label}.")
        return None

    # Build lookup maps
    pk_map = {item.pk: item for item in items}
    name_map = {item.name: item for item in items}

    session_key = f"selected_{key}_pk"
    query_value = st.query_params.get(key)

    # --- Sync query -> session ---
    if query_value and query_value in name_map:
        # URL value points to a valid item
        st.session_state[session_key] = name_map[query_value].pk

    elif session_key not in st.session_state:
        # No session yet -> initialise with the first item
        st.session_state[session_key] = items[0].pk

    # Resolve the PK we want to select
    selected_pk = st.session_state[session_key]

    # --- Handle stale PKs (hot reload or parent filter changed) ---
    if selected_pk not in pk_map:
        # If the previously selected item no longer exists under the new filter:
        st.session_state[session_key] = items[0].pk
        selected_obj = items[0]
    else:
        selected_obj = pk_map[selected_pk]

    # --- Render the selectbox ---
    selected_from_widget = st.selectbox(
        label,
        items,
        index=items.index(selected_obj),
        format_func=lambda i: i.name,
    )

    # --- Sync session -> query ---
    if query_value != selected_from_widget.name:
        st.session_state[session_key] = selected_from_widget.pk
        st.query_params[key] = selected_from_widget.name
        st.rerun()

    return selected_from_widget
