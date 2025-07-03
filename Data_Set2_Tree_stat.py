import math
from collections import Counter, defaultdict
import networkx as nx
import pandas as pd

def analyze_tree(G):

  root = [node for node in G.nodes if G.in_degree(node) == 0][0]
  print(root)

  depths = nx.shortest_path_length(G, source=root)
  total_depth = sum(depths.values())
  average_depth = total_depth / G.number_of_nodes()
  max_depth = max(depths.values())

  depth_counts = defaultdict(int)
  for node, depth in depths.items():
      depth_counts[depth] += 1
  total_breadth = sum(depth_counts.values())
  average_breadth = total_breadth / (max_depth + 1)
  max_breadth = max(depth_counts.values())

  leaf_nodes = [node for node in G.nodes if G.out_degree(node) == 0]
  num_leaf_nodes = len(leaf_nodes)


  branching_factors = [G.out_degree(node) for node in G.nodes if G.out_degree(node) > 0]
  average_branching_factor = sum(branching_factors) / len(branching_factors)
  variance = sum((x - sum(branching_factors) / len(branching_factors)) ** 2 for x in branching_factors) / len(branching_factors)

  return {
      'number of nodes': G.number_of_nodes(),
      'max_depth': max_depth,
      'average_depth': average_depth,
      'max_breadth': max_breadth,
      'average_breadth': average_breadth,
      'number of leaft nodes': num_leaf_nodes,
      'average_branching_factors': average_branching_factor,
      'variance_branching_factors': variance
      }

# Load the graph from a GML file
year = 1994
title_num = 3
gml_path = f'./Data/Data Records/Data Set2/Entire tree/{year}/title_{title_num:02d}.gml'
Entire_Tree = nx.read_gml(gml_path)

print(f"Loaded tree with {len(Entire_Tree.nodes())} nodes and {len(Entire_Tree.edges())} edges from {gml_path}")

# Analyze the tree structure
tree_stats = analyze_tree(Entire_Tree)
print(tree_stats)

Tree_stats_df = pd.read_csv('./Data/Data Records/Data Set2/Tree_stats.csv', index_col=0)


import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text

# 2x2 subplot configuration
fig, axs = plt.subplots(2, 2, figsize=(18, 12), constrained_layout=True)
axs = axs.flatten()  # flatten to use as 1D indexable list
texts_dict = {}  # To hold text annotations for adjust_text

# Labels for panel annotations (A), (B), (C), (D)
panel_labels = ['(A)', '(B)', '(C)', '(D)']

# Define the us_code_groups dictionary
us_code_groups = {
    "Government Structure": [
        "General Provisions",
        "The Congress",
        "The President",
        "Flag and Seal, Seat of Government, and the States",
        "Government Organization and Employees",
        "Census",
        "Patriotic Societies and Observances",
        "Public Printing and Documents"
    ],
    "National Defense": [
        "Armed Forces",
        "Coast Guard",
        "National Guard",
        "Navy",
        "War and National Defense",
        "Foreign Relations and Intercourse",
        "Pay and Allowances of the Uniformed Services",
        "Veterans Benefits",
        "Territories and Insular Possessions"
    ],
    "Economy": [
        "Surety Bonds",
        "Bankruptcy",
        "Banks and Banking",
        "Commerce and Trade",
        "Customs Duties",
        "Internal Revenue Code",
        "Money and Finance",
        "Railroads",
        "Shipping",
        "Highways",
        "Transportation",
        "Telecommunications",
        'Patents',
        "Public Contracts",
        "Public Buildings, Property, and Works",
        "Public Lands",
        "Mineral Lands and Mining",
        "Navigation and Navigable Waters",
        "Postal Service"
    ],
    "Society": [
        "Agriculture",
        "Aliens and National and Citizenship",
        "Arbitration",
        "Conservation",
        "Copyrights",
        "Crimes and Criminal Procedure",
        "Education",
        "Food and Drugs",
        "Hospitals and Asylums",
        "Intoxicating Liquors",
        "Judiciary and Judicial Procedure",
        "Labor",
        "Indians",
        "The Public Health and Welfare"
    ]
}

# Define the colors for each group
group_colors = {
    "Government Structure": "skyblue",  # Sky blue
    "Economy": "purple",
    "Society": "green",
    "National Defense": "orange"
}


# Iterate over 4 groups and corresponding subplot axes
for idx, (key, ax) in enumerate(zip(us_code_groups.keys(), axs)):
    texts = []
    temp_titles = Tree_stats_df[Tree_stats_df['Group']==key]['Title'].unique()

    for title in temp_titles:
        if title != 6 and title != 34:
            try:
                subset = Tree_stats_df[Tree_stats_df['Title'] == title]
                title_name = subset['Title Name'].iloc[-1]

                assigned_color = group_colors.get(key, 'black')

                ax.plot(subset['Average_Breadth'], subset['Average_Depth'],
                        lw=1, color=assigned_color)
                ax.scatter(subset['Average_Breadth'].iloc[-1],
                           subset['Average_Depth'].iloc[-1],
                           marker='o', color=assigned_color)

                x = subset['Average_Breadth'].iloc[-1]
                y = subset['Average_Depth'].iloc[-1]
                txt = ax.text(x, y, title_name,
                              fontsize=14,
                              ha='left', va='bottom',
                              color=assigned_color)
                texts.append(txt)
            except:
                pass

    # Set labels and titles for each subplot
    ax.set_xlabel('Average Breadth', fontsize=14)
    ax.set_ylabel('Average Depth', fontsize=14)
    ax.text(0.99, 0.01, key,
      transform=ax.transAxes,
      fontsize=40,
      color=group_colors[key],
      ha='right', va='bottom')

    # Add panel labels (A), (B), (C), (D) in the top-right corner
    ax.text(0.08, 0.98, panel_labels[idx],
            transform=ax.transAxes,
            fontsize=20,
            color='black',
            ha='right', va='top', fontweight='bold')  # Adjust position as needed

    texts_dict[key] = texts
    ax.set_xlabel('Average Breadth', fontsize=25)
    ax.set_ylabel('Average Depth', fontsize=25)

# Adjust all texts after plotting to avoid overlaps
for idx, (key, ax) in enumerate(zip(us_code_groups.keys(), axs)):
    adjust_text(
        texts_dict[key],
        ax=ax,
        arrowprops=dict(arrowstyle="->", color='gray', lw=1.5, alpha=0.5),
        expand_text=(1.05, 1.2),
        expand_points=(1.2, 1.4),
        force_text=(0.3, 0.3),
        force_points=(0.3, 0.3),
        lim=500,
        only_move={'points': 'y', 'text': 'xy'}
    )

# Layout and save
plt.savefig('./Figures/Figure 8.pdf', dpi=600, bbox_inches='tight')


# Iterate over 4 groups and corresponding subplot axes
for idx, (key, ax) in enumerate(zip(us_code_groups.keys(), axs)):
    texts = []
    temp_titles = Tree_stats_df[Tree_stats_df['Group']==key]['Title'].unique()

    for title in temp_titles:
        if title != 6 and title != 34:
            try:
                subset = Tree_stats_df[Tree_stats_df['Title'] == title]
                title_name = subset['Title Name'].iloc[-1]

                assigned_color = group_colors.get(key, 'black')

                ax.plot(subset['Average_Breadth'], subset['Average_Depth'],
                        lw=1, color=assigned_color)
                ax.scatter(subset['Average_Breadth'].iloc[-1],
                           subset['Average_Depth'].iloc[-1],
                           marker='o', color=assigned_color)

                x = subset['Average_Breadth'].iloc[-1]
                y = subset['Average_Depth'].iloc[-1]
                txt = ax.text(x, y, title_name,
                              fontsize=14,
                              ha='left', va='bottom',
                              color=assigned_color)
                texts.append(txt)
            except:
                pass

    # Set labels and titles for each subplot
    ax.set_xlabel('Average Breadth', fontsize=14)
    ax.set_ylabel('Average Depth', fontsize=14)
    ax.text(0.99, 0.01, key,
      transform=ax.transAxes,
      fontsize=40,
      color=group_colors[key],
      ha='right', va='bottom')

    # Add panel labels (A), (B), (C), (D) in the top-right corner
    ax.text(0.08, 0.98, panel_labels[idx],
            transform=ax.transAxes,
            fontsize=20,
            color='black',
            ha='right', va='top', fontweight='bold')  # Adjust position as needed

    texts_dict[key] = texts
    ax.set_xlabel('Average Breadth(log)', fontsize=25)
    ax.set_ylabel('Average Depth', fontsize=25)
    ax.set_xscale('log')

# Adjust all texts after plotting to avoid overlaps
for idx, (key, ax) in enumerate(zip(us_code_groups.keys(), axs)):
    adjust_text(
        texts_dict[key],
        ax=ax,
        arrowprops=dict(arrowstyle="->", color='gray', lw=1.5, alpha=0.5),
        expand_text=(1.05, 1.2),
        expand_points=(1.2, 1.4),
        force_text=(0.3, 0.3),
        force_points=(0.3, 0.3),
        lim=500,
        only_move={'points': 'y', 'text': 'xy'}
    )
plt.savefig('./Figures/Figure S19.pdf', dpi=600, bbox_inches='tight')