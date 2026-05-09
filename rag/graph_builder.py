import json
import logging
from pathlib import Path

import networkx as nx

from config import PROCESSED_DIR

logger = logging.getLogger(__name__)

GRAPH_PATH = PROCESSED_DIR / "knowledge_graph.json"


def build_knowledge_graph() -> nx.Graph:
    chunks_path = PROCESSED_DIR / "all_chunks.json"
    if not chunks_path.exists():
        return nx.Graph()

    data = json.loads(chunks_path.read_text())
    G = nx.Graph()

    doc_groups = {}
    for c in data:
        sf = c.get("source_file", "unknown")
        doc_groups.setdefault(sf, []).append(c)

    for doc_name, chunks in doc_groups.items():
        first = chunks[0]
        agency = first.get("agency", "")
        location = first.get("incident_location", "")
        date = first.get("incident_date", "")
        title = first.get("title", doc_name)
        chunk_type = first.get("chunk_type", "")

        G.add_node(doc_name, type="document", title=title, agency=agency,
                    location=location, date=date, chunk_type=chunk_type,
                    chunks=len(chunks))

        if agency and agency != "Unknown":
            G.add_node(agency, type="agency")
            G.add_edge(doc_name, agency, relation="reported_by")

        if location and location not in ("Unknown", "N/A", ""):
            G.add_node(location, type="location")
            G.add_edge(doc_name, location, relation="occurred_at")

        if date and date not in ("Unknown", "N/A", ""):
            G.add_node(date, type="date")
            G.add_edge(doc_name, date, relation="reported_on")

    docs = list(doc_groups.keys())
    for i in range(len(docs)):
        for j in range(i + 1, len(docs)):
            d1, d2 = docs[i], docs[j]
            c1, c2 = doc_groups[d1][0], doc_groups[d2][0]
            shared = 0
            for key in ("agency", "incident_location", "incident_date"):
                v1, v2 = c1.get(key, ""), c2.get(key, "")
                if v1 and v2 and v1 != "Unknown" and v1 != "N/A" and v1 == v2:
                    shared += 1
            if shared >= 2:
                G.add_edge(d1, d2, relation="shared_context", weight=shared)

    logger.info(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def graph_to_pyvis(G: nx.Graph, output_path: str | None = None) -> str:
    from pyvis.network import Network

    net = Network(height="700px", width="100%", bgcolor="#1a1a2e", font_color="white",
                  select_menu=True, filter_menu=True)

    color_map = {"document": "#00d4ff", "agency": "#ff6b6b", "location": "#51cf66", "date": "#ffd43b"}

    for node, attrs in G.nodes(data=True):
        ntype = attrs.get("type", "document")
        label = attrs.get("title", node) if ntype == "document" else node
        if len(label) > 50:
            label = label[:47] + "..."
        net.add_node(node, label=label, color=color_map.get(ntype, "#ccc"),
                     title=f"{ntype}: {attrs.get('title', node)}",
                     size=15 if ntype == "document" else 10)

    for src, dst, attrs in G.edges(data=True):
        rel = attrs.get("relation", "")
        weight = attrs.get("weight", 1)
        net.add_edge(src, dst, title=rel, value=weight, color="#ffffff30")

    if output_path is None:
        output_path = str(PROCESSED_DIR / "graph.html")
    net.save_graph(output_path)
    logger.info(f"Graph saved to {output_path}")
    return output_path


def get_document_clusters(G: nx.Graph, min_size: int = 2) -> list[list[str]]:
    communities = nx.community.louvain_communities(G, seed=42)
    return [sorted(list(c)) for c in communities if len(c) >= min_size]


def get_node_neighborhood(G: nx.Graph, node_id: str, depth: int = 2) -> dict:
    if node_id not in G:
        return {"error": f"Node {node_id} not found"}

    nodes = set()
    edges = []
    frontier = {node_id}
    for _ in range(depth):
        next_frontier = set()
        for n in frontier:
            for neighbor in G.neighbors(n):
                if neighbor not in nodes:
                    next_frontier.add(neighbor)
                    edges.append((n, neighbor, G.edges[n, neighbor].get("relation", "")))
        nodes.update(frontier)
        frontier = next_frontier
    nodes.update(frontier)

    return {
        "center": node_id,
        "nodes": {n: dict(G.nodes[n]) for n in nodes if n in G},
        "edges": edges,
        "cluster_count": len(nodes),
    }
