"""
This script parses and constructs hierarchical tree structures from U.S. Code legal text for a given Title and Year.

It performs the following steps:
- parse_section_structure: extracts section–subsection–item level hierarchies from raw text
- parse_high_structure: extracts high-level legal structure (Subtitle → Division → Part → Subpart → Chapter → Subchapter)
- parse_chapter_structure: extracts chapter–subchapter–section layout
- build_hierarchy: constructs fine-grained node-level trees from parsed section entries
- build_high_level_hierarchy: constructs a top-down hierarchy and attaches sections to chapter/subchapter nodes
- merge: combines high-level and low-level trees into a unified structure (Entire_Tree)

These functions support both:
- High-level hierarchies: Title → Subtitle → Division → Part → Chapter → Subchapter → Section  
- Low-level hierarchies: section → subsection → item → subitem → subsubitem → subsubsubitem

Note:
- For titles where PART appears under CHAPTER (instead of above), use `parse_chapter_structure_low`.
- Final tree visualization can be performed via `tf.visualize_tree` in Google Colab.
"""

import parsing_functions as pf  # Custom module for text parsing functions
import tree_functions as tf     # Custom module for tree building and visualization
import pandas as pd
import networkx as nx
import re

year = 1994
title_num = 3
## Structure Parsing
with open(f'./Data/US_govinfo/{year}/TITLE_{title_num}.txt', 'r', encoding='utf-8') as f:
    text = f.read()

structure_result = pf.parse_section_structure(text,debug = False)
structure_result = pf.Fixing_misparsed_context(structure_result)

# Tree 
high_structure = pf.parse_high_structure(text)
chapter_structure = pf.parse_chapter_structure(text)
high_level_hierarchy = tf.build_high_level_hierarchy(high_structure, chapter_structure, title_num = title_num)  ## This builds the high-level hierarchy from the parsed structure

chapter_df = tf.extract_elements_to_dataframe(chapter_structure)
section_structure = pf.parse_section_structure(text)
section_structure = pf.Fixing_misparsed_context(section_structure)
low_level_hierarchy = tf.build_hierarchy(section_structure)  ## This builds the low-level hierarchy from section entries

Entire_Tree = high_level_hierarchy.copy()
for node1 in high_level_hierarchy.nodes:
    if 'section' in node1:
        for edge in low_level_hierarchy.edges():
            if node1.strip().lower() == edge[0].strip().lower():
                temp_subgraph = low_level_hierarchy.subgraph(list(nx.descendants(low_level_hierarchy, edge[0])) + [edge[0]])
                Entire_Tree = nx.compose(Entire_Tree, temp_subgraph)

if not nx.is_tree(Entire_Tree):
    print(f'[{year}-{title_num}] Warning: Final merged tree is not a tree!')

print(len(Entire_Tree.nodes()), len(Entire_Tree.edges()))

