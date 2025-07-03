'''
This module includes all functions needed to construct and validate hierarchical trees
from parsed legal structures and text data:

- is_valid_tree: checks if a directed graph is a tree
- safe_add_edge: safely adds parent–child edges while maintaining tree constraints
- build_hierarchy: builds node-level trees from section–item parsed tuples
- extract_elements_to_dataframe: flattens nested tree-like dictionaries to a DataFrame
- build_high_level_hierarchy: combines high-level structure (e.g., Subtitle → Chapter) with section trees
- visualize_tree: visualizes the tree structure with color-coded nodes and a legend

These functions support merging structures like:
Title → Subtitle → Division → Part → Chapter → Subchapter → Section  
and node-level trees like: section → subsection → item → subitem → subsubitem → subsubsubitem
'''

import networkx as nx
import matplotlib.pyplot as plt
import re
from collections import defaultdict, deque
import pandas as pd
import pickle
from matplotlib.patches import Patch

# ========== Function to Check if a Graph is a Tree ==========
def is_valid_tree(graph):
    """
    Check if a directed graph is a tree.
    A tree must be connected and acyclic with a single root.
    """
    if not nx.is_tree(graph):
        return False
    root_nodes = [n for n in graph.nodes if graph.in_degree(n) == 0]
    return len(root_nodes) == 1

# ========== Function to Add Edge and Validate Tree ==========
def safe_add_edge(graph, parent, child):
    """
    Add an edge to the graph and check if it remains a tree.
    If adding the edge breaks the tree structure, it is reverted.
    """
    graph.add_edge(parent, child)
    if not is_valid_tree(graph):
        graph.remove_edge(parent, child)

# ========== Hierarchy Constants ==========
HIERARCHY_ORDER_dict = {
    "section": 1,
    "subsection": 2,
    "item": 3,
    "subitem": 4,
    "subsubitem": 5,
    "subsubsubitem": 6
}
HIERARCHY_ORDER = list(HIERARCHY_ORDER_dict.keys())

# ========== Build Hierarchy from Parsed Entries ==========
def build_hierarchy(entries):
    """
    Constructs a hierarchical tree allowing skipped intermediate levels.
    Each entry is a tuple: (indent, class_name, label, text)
    """
    graph = nx.DiGraph()
    stack = {level: None for level in HIERARCHY_ORDER}  # Track last seen node by level

    for indent, class_name, label, text in entries:
        if class_name not in HIERARCHY_ORDER:
            raise ValueError(f"Invalid class name: {class_name}. Expected one of {HIERARCHY_ORDER}")

        base_label = re.sub(r"\\. ", "_", label.strip())

        # Find the nearest valid parent
        parent_hierarchy = None
        class_idx = HIERARCHY_ORDER.index(class_name)
        for higher_idx in range(class_idx - 1, -1, -1):
            candidate = stack[HIERARCHY_ORDER[higher_idx]]
            if candidate is not None:
                parent_hierarchy = candidate
                break

        unique_label = f"{parent_hierarchy}_{class_name}_{base_label}" if parent_hierarchy else f"{class_name}_{base_label}"

        graph.add_node(
            unique_label,
            class_name=class_name,
            label=label,
            text=text
        )

        if parent_hierarchy:
            graph.add_edge(parent_hierarchy, unique_label)

        stack[class_name] = unique_label
        for lower_level in HIERARCHY_ORDER[class_idx + 1:]:
            stack[lower_level] = None  # Reset lower levels

    return graph

# ========== Flatten Nested Dictionary to DataFrame ==========
def extract_elements_to_dataframe(nested_data):
    """
    Flattens the nested legal structure into a 2-column DataFrame:
    - Column 1: Element (e.g., CHAPTER 3)
    - Column 2: Title (e.g., POWERS)
    """
    rows = []

    def recurse(data):
        if isinstance(data, list):
            for section in data:
                if '—' in section:
                    left, right = section.split('—', 1)
                else:
                    left, right = section, ''
                left_clean = left.replace('.', '').strip().upper()
                rows.append((left_clean, right.strip()))
        elif isinstance(data, dict):
            for key, value in data.items():
                if '—' in key:
                    left, right = key.split('—', 1)
                else:
                    left, right = key, ''
                left_clean = left.replace('.', '').strip().upper()
                rows.append((left_clean, right.strip()))
                recurse(value)

    recurse(nested_data)
    return pd.DataFrame(rows, columns=['Element', 'Title'])

# ========== Combine High-Level & Chapter Structures into One Tree ==========
def build_high_level_hierarchy(high_structure, chapter_structure, title_num):
    """
    Builds a combined tree using high-level hierarchy and chapter-based section structure.
    """
    G = nx.DiGraph()
    root = f"Title {title_num}"
    G.add_node(root)

    # Step 1: Build tree from high_structure
    def add_edges_from_structure(current_dict, parent):
        for key, val in current_dict.items():
            node = key.strip()
            safe_add_edge(G, parent, node)
            if isinstance(val, dict):
                add_edges_from_structure(val, node)

    add_edges_from_structure(high_structure, root)

    # Step 2: Attach sections from chapter_structure under chapter/subchapter nodes
    def attach_chapter_structure(chap_struct):
        for chapter_key, content in chap_struct.items():
            chapter_node = chapter_key.strip()
            if not G.has_node(chapter_node):
                continue  # only attach to nodes from high_structure

            if isinstance(content, dict):
                for subkey, subval in content.items():
                    if subkey == "SectionList":
                        for section_entry in subval:
                            section_node = re.sub(r"\. ", "_", section_entry.split('—')[0].strip().lower())
                            safe_add_edge(G, chapter_node, section_node)
                    elif isinstance(subval, dict):
                        # e.g., subkey is a SUBCHAPTER and contains its own SectionList
                        subchapter_node = subkey.strip()
                        safe_add_edge(G, chapter_node, subchapter_node)
                        if "SectionList" in subval:
                            for section_entry in subval["SectionList"]:
                                section_node = re.sub(r"\. ", "_", section_entry.split('—')[0].strip().lower())
                                safe_add_edge(G, subchapter_node, section_node)
                    elif isinstance(subval, list):
                        subchapter_node = subkey.strip()
                        safe_add_edge(G, chapter_node, subchapter_node)
                        for section_entry in subval:
                            section_node = re.sub(r"\. ", "_", section_entry.split('—')[0].strip().lower())
                            safe_add_edge(G, subchapter_node, section_node)

    attach_chapter_structure(chapter_structure)
    return G

def visualize_tree(tree_graph, filename="tree_structure", label = True):
    """
    Visualizes the tree structure using networkx and matplotlib, with color-coded nodes and a legend.

    Args:
        tree_graph (nx.DiGraph): The directed graph representing the tree structure.
        filename (str): The file name to save the visualization.
    """
    try:
        # Use Graphviz hierarchical layout if available
        pos = nx.nx_pydot.graphviz_layout(tree_graph, prog="dot")
    except ImportError:
        print("Warning: Graphviz is not installed. Falling back to spring_layout.")
        pos = nx.spring_layout(tree_graph, seed=42, k=0.5)

    # Classify node types and assign colors
    color_map = []
    for node in tree_graph.nodes():
        node_lower = node.lower()
        if 'subtitle' in node_lower:
            color_map.append('brown')
        elif 'title' in node_lower:
            color_map.append('black')
        elif 'subitem' in node_lower:
            color_map.append('grey')
        elif 'item' in node_lower:
            color_map.append('lightgrey')
        elif 'subsection' in node_lower:
            color_map.append('lightblue')
        elif 'section' in node_lower:
            color_map.append('blue')
        elif 'subchapter' in node_lower:
            color_map.append('green')
        elif 'chapter' in node_lower:
            color_map.append('red')
        elif 'subpart' in node_lower:
            color_map.append('orange')
        elif 'part' in node_lower:
            color_map.append('yellow')
        else:
            color_map.append('grey')  # default for undefined node types

    # Plot settings
    plt.figure(figsize=(14, 10))
    nx.draw(
        tree_graph,
        pos,
        with_labels=False,
        font_size = 4,
        node_size=100,
        node_color=color_map,
        edge_color="gray",
        arrowsize=10
    )

    # Define legend
    legend_elements = [
        Patch(facecolor='black', label='Title'),
        Patch(facecolor='red', label='Chapter'),
        Patch(facecolor='green', label='Subchapter'),
        Patch(facecolor='blue', label='Section (§)'),
        Patch(facecolor='lightblue', label='Subsection (lower capital)'),
        Patch(facecolor='lightgrey', label='Item (number)'),
        Patch(facecolor='grey', label='Below subitem level (upper capital)')
    ]
    #plt.legend(handles=legend_elements, loc='best', fontsize=20)
    for node, (x, y) in pos.items():
        if 'title' in node.lower():
          plt.text(x, y+20, node, fontsize=25, fontweight="bold", rotation=0, ha="center", va="center")

    if label:

      # Get current axes
      ax = plt.gca()

      # Draw rotated labels
      for node, (x, y) in pos.items():
          ax.text(
              x, y, node,
              fontsize=8,
              rotation=30,
              ha="center",
              va="center"
      )

    # Save and show
    plt.savefig(filename, bbox_inches="tight", dpi = 600)
    plt.show()

def clean_graph_labels(tree_graph):
    mapping = {}
    for node in tree_graph.nodes():
        if '–' in node or '—' in node:
            new_node = node.replace('–', '-').replace('—', '-')
            mapping[node] = new_node
    if mapping:
        nx.relabel_nodes(tree_graph, mapping, copy=False)
    return tree_graph