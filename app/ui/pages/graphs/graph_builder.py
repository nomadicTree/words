import networkx as nx
from streamlit_agraph import Node, Edge


def build_graph(df_words, df_rels):
    # build networkx graph for degree + components
    G = nx.Graph()
    G.add_nodes_from(df_words["word_id"])
    for _, row in df_rels.iterrows():
        G.add_edge(int(row["a"]), int(row["b"]))

    # component map
    components = list(nx.connected_components(G))
    comp_map = {}
    for idx, comp in enumerate(components):
        for n in comp:
            comp_map[n] = idx

    # colour function
    def pastel(i):
        import random

        random.seed(i + 77)
        r = random.randint(120, 220)
        g = random.randint(120, 220)
        b = random.randint(120, 220)
        return f"rgb({r},{g},{b})"

    # build nodes
    nodes = []
    for _, row in df_words.iterrows():
        wid = int(row["word_id"])
        degree = G.degree[wid]
        size = 10 + min(degree * 2, 30)

        nodes.append(
            Node(
                id=str(wid),
                label=row["word"],
                size=size,
                color=pastel(comp_map.get(wid, 0)),
                title=f"Degree: {degree}",
            )
        )

    # build edges
    edges = [
        Edge(
            source=str(int(row["a"])),
            target=str(int(row["b"])),
            color="#BBBBBB",
            width=1,
        )
        for _, row in df_rels.iterrows()
    ]

    return nodes, edges
