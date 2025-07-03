import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import LogLocator, LogFormatterMathtext, FuncFormatter


# Load title name mapping
Title2Name = pd.read_csv('./Data/Title2Name.csv')
Title2Name = dict(zip(Title2Name['Title num'], Title2Name['Title name']))

# Color palette for titles
colors = sns.color_palette("pastel", 50)
Title2Color = {title: colors[i] for i, title in enumerate(range(1, 51))}

# Load main dataset
Data1 = pd.read_csv('./Data/Data Records/Data Set1/ContentsOfTitle.csv')
Data1['Title'] = Data1['Title'].apply(
    lambda x: int(x) if str(x).isdigit() else str(x)
)

# Prepare data for plotting
fig, ax = plt.subplots(figsize=(8, 6), constrained_layout=True)
temp_data = Data1.copy()
temp_data = temp_data[temp_data['Year'] >= 1934]
temp_data = temp_data[temp_data['Title'] != 'All titles']
pivot_df = temp_data.pivot(index='Year', columns='Title', values='Cleaned Text Word Count')

# Stacked area chart
area_plot = pivot_df.plot(kind='area', stacked=True, legend=False, ax=ax)

# Axis labels and limits
ax.set_xlabel('Year', fontsize=25)
ax.set_ylabel('$W_i$ (Millions)', fontsize=25)
ax.set_xlim(1934, 2023)
ax.set_ylim(1, 1000000 * 50)
formatter = FuncFormatter(lambda y, _: f'{int(y / 1000000)}M')
ax.yaxis.set_major_formatter(formatter)

# Add right-side labels
colors = [area.get_facecolor() for area in area_plot.collections]
y_min, y_max = ax.get_ylim()
num_titles = len(Title2Name)
y_positions = [y_min + i * (y_max - y_min) / num_titles for i in range(num_titles)]

for i, (y, color) in enumerate(zip(y_positions, colors)):
    if i + 1 in [6, 34]:
        continue
    if i + 1 in Title2Name.keys():
        rgba_color = color[0]
        ax.text(2023.5, y, f'Title {i + 1}: {Title2Name[i + 1]}',
                va='center', fontsize=9, color=rgba_color)

# Add vertical reference line
plt.axvline(x=1994, linestyle='dashed', color='grey', linewidth=2)

# Add inset plot: total word count over time (log scale)
ax_inset = inset_axes(ax, width="100%", height="100%", loc='upper left',
                      bbox_to_anchor=(0.15, 0.65, 0.3, 0.3), bbox_transform=ax.transAxes)

ax_inset.plot(temp_data.groupby('Year').sum().index,
              temp_data.groupby('Year').sum()['Cleaned Text Word Count'],
              marker='o', color='black', markersize=2)
ax_inset.set_xlim(1925, 2023)
ax_inset.set_yscale('log')
ax_inset.set_xticks([1934, 1980, 2020])
ax_inset.tick_params(axis='both', which='both', labelsize=8)
ax_inset.set_title("$\Sigma_i{W_i}$", fontsize=12)
ax_inset.set_xlabel('')
ax_inset.set_ylabel('')

plt.savefig('./Figures/Figure 3.pdf', dpi=600, bbox_inches='tight')

# Step 1: Create a 2x2 grid of subplots
fig, axs = plt.subplots(2, 2, figsize=(12, 12), constrained_layout=True)

# Target titles and corresponding label texts
titles = [42, 26, 10, 16]
titles_text = [f'Title {i}: {Title2Name[i]}' for i in titles]

# Step 2: Iterate through each subplot and draw main & inset plots
for i, (ax, title, title_text) in enumerate(zip(axs.flat, titles, titles_text)):
    # Filter and sort data by year for the current title
    temp_data = Data1.copy()
    temp_data = temp_data[temp_data['Year']>=1934]
    temp_data = temp_data[temp_data['Title']!='All titles']
    temp_data['Title'] = temp_data['Title'].astype(int)
    
    temp_df = temp_data[temp_data['Title'] == title].sort_values(by='Year')
    temp_xs = temp_df['Year']
    temp_ys = temp_df['Cleaned Text Word Count']

    # === Main Plot ===
    ax.plot(temp_xs, temp_ys, color='black')
    ax.axvline(x=1994, color='grey', linestyle='dashed', linewidth=2)
    ax.set_title(title_text, fontsize=20)
    ax.set_xticks([1934, 1945, 1955, 1965, 1975, 1985, 1995, 2005, 2015, 2023])

    # Format y-axis to show values in millions
    formatter = FuncFormatter(lambda y, _: f'{(y / 1_000_000):.1f} × $10^6$')
    ax.yaxis.set_major_formatter(formatter)

    # Add axis labels to appropriate subplots only
    if i >= 2:  # Bottom row
        ax.set_xlabel("Year", fontsize=25)
    if i % 2 == 0:  # Left column
        ax.set_ylabel('$W_i$', fontsize=25)

    ax.grid(False)

    # === Inset Plot ===
    inset = inset_axes(ax, width="100%", height="100%", loc='upper left',
                       bbox_to_anchor=(0.15, 0.65, 0.3, 0.3), bbox_transform=ax.transAxes)

    inset.plot(temp_xs, temp_ys, color='black', marker='o', linewidth=1, markersize=2)
    inset.axvline(x=1994, color='grey', linestyle='dashed', linewidth=2)
    inset.set_xticks([1934, 1980, 2023])

    # Log-scale on y-axis with scientific formatting
    inset.set_yscale('log')
    inset.yaxis.set_major_locator(LogLocator(base=10.0))
    inset.yaxis.set_major_formatter(LogFormatterMathtext())
    inset.set_title('Log Scale', fontsize=14)
    inset.grid(False)
    inset.tick_params(labelsize=8)

# Step 3: Adjust layout and display the figure
plt.savefig('./Figures/Figure 4.pdf', dpi=600, bbox_inches='tight')

# Step 1: Create constrained layout
fig, axs = plt.subplots(2, 2, figsize=(12, 12), constrained_layout=True)

# Step 2: Define titles and plot labels
titles = [42, 26, 10, 16]
titles_text = ['All titles'] + [f'Title {i}: {Title2Name[i]}' for i in titles[:-1]]

# Step 3: Main and inset plots
for i, (ax, title, title_text) in enumerate(zip(axs.flat, titles, titles_text)):
    if title == 'All titles':
        temp_data = Data1.copy()
        temp_data = temp_data[temp_data['Year'] >= 1934]
        temp_df = temp_data[temp_data['Title'] == title].sort_values(by='Year')
    else:
        temp_data = Data1.copy()
        temp_data = temp_data[temp_data['Year'] >= 1934]
        temp_data = temp_data[temp_data['Title'] != 'All titles']
        temp_data['Title'] = temp_data['Title'].astype(int)
        temp_df = temp_data[temp_data['Title'] == title].sort_values(by='Year')

    temp_xs = temp_df['Year']
    temp_ys = temp_df['entropies_norm']
    ax.plot(temp_xs, temp_ys, color='black')
    ax.axvline(x=1994, color='gray', linestyle='dashed', linewidth=2)
    ax.set_title(title_text, fontsize=20)
    ax.set_xticks([1934, 1945, 1955, 1965, 1975, 1985, 1995, 2005, 2015, 2023])

    if i >= 2:
        ax.set_xlabel("Year", fontsize=25)
    if i == 0:
        ax.set_ylabel(r"$\hat{S}$", fontsize=25)
    else:
        ax.set_ylabel(r"$\hat{S}_i$", fontsize=25)
    ax.grid(False)

    # Inset: unique word count
    if title == 'All titles':
        inset_df = temp_data[temp_data['Title'] == title].sort_values(by='Year')
    else:
        inset_df = temp_data[temp_data['Title'] == title].sort_values(by='Year')

    inset_xs = inset_df['Year']
    inset_ys = inset_df['Cleaned Text Unique Word Count']

    inset = inset_axes(ax, width="100%", height="100%", loc='lower left',
                       bbox_to_anchor=(0.65, 0.6, 0.3, 0.3), bbox_transform=ax.transAxes)
    inset.plot(inset_xs, inset_ys, color='black', marker='o', linewidth=1, markersize=2)
    inset.axvline(x=1994, color='gray', linestyle='dashed', linewidth=2)
    inset.set_yscale('log')
    inset.set_xticks([1934, 1980, 2023])
    inset.set_title('$V_i$', fontsize=14)
    inset.grid(False)
    inset.yaxis.set_major_locator(LogLocator(base=10.0))
    inset.yaxis.set_major_formatter(LogFormatterMathtext())
    inset.tick_params(labelsize=8)

# Step 4: Save or show
plt.savefig('./Figures/Figure 5.pdf', dpi=600, bbox_inches='tight')