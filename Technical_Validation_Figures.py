"""
The raw data for the External Validation via Benchmarking in the Technical Validation section can be accessed from https://zenodo.org/records/4660133

"""
# === Libraries for formatting ===
import matplotlib.ticker as ticker
import numpy as np
from adjustText import adjust_text
import seaborn as sns
from scipy.stats import pearsonr
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from matplotlib.ticker import ScalarFormatter,MaxNLocator

Title2Name = pd.read_csv('./Data/Title2Name.csv')
Title2Name = dict(zip(Title2Name['Title num'], Title2Name['Title name']))

ContentsOfTitle= pd.read_csv('./Data/Data Records/Data Set1/ContentsOfTitle.csv')
ContentsOfTitle = ContentsOfTitle[ContentsOfTitle['Title']!='All titles']
ContentsOfTitle['Title'] = ContentsOfTitle['Title'].astype(int)

Benchmark_data1 = pd.read_csv('./Data/Technical Validation/Benchmark Data_Figure11B.csv')
Benchmark_data2 = pd.read_csv('./Data/Technical Validation/Benchmark Data_Figure11D.csv')
Benchmark_data3 = pd.read_csv('./Data/Technical Validation/Benchmark Data_Figure11E.csv')

Internal_validation_data1 = pd.read_csv('./Data/Technical Validation/Web_OCR_Content Data_1994_2000.csv')
Internal_validation_data2 = pd.read_csv('./Data/Technical Validation/Web_OCR_Citation Data_1994_2000.csv')


# === Highlighted titles and color mapping ===
highlight_titles = sorted({42, 26, 10, 7, 1, 27, 5, 15, 3, 48, 13, 30, 9, 47}, reverse=True)
color_list = [
    '#377eb8', '#4daf4a', '#e41a1c', '#984ea3', '#ff7f00',
    '#000080', '#a65628', 'skyblue', 'black', '#66c2a5',
    '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854'
]
title2color_highlight = dict(zip(highlight_titles, color_list))

# === Figure 11B ===
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(111)

# === Titles to be explicitly labeled in plot ===
highlight_titles = [42, 26, 10]

# === Accumulate points for correlation computation ===
temp_list1 = []  # Our dataset
temp_list2 = []  # Benchmark dataset
texts = []

# === Loop through all titles (excluding Title 6 and 34) ===
for i in range(1, 51):
    if i != 6 and i != 34:
        # Extract relevant data
        temp_df = ContentsOfTitle[ContentsOfTitle['Title'] == i][['Year', 'Cleaned Text Word Count']]
        temp_df = temp_df[(temp_df['Year'] >= 1994) & (temp_df['Year'] <= 2018)]

        # Set color and transparency
        if i in highlight_titles:
            color = title2color_highlight[i]
            alpha = 1.0
        else:
            color = 'grey'
            alpha = 0.1

        # Plot the final (maximum) word count vs benchmark
        ax.scatter(temp_df['Cleaned Text Word Count'], Benchmark_data1[str(i)],
                   color=color, s=15, alpha=alpha, edgecolors='none')

        # Store values for correlation
        temp_list1.extend(temp_df['Cleaned Text Word Count'])
        temp_list2.extend(Benchmark_data1[str(i)])

        # Label highlighted titles
        if i in highlight_titles:
            texts.append(
                ax.text(temp_df['Cleaned Text Word Count'].max(),
                        Benchmark_data1[str(i)].max(),
                        f'Title {i}: {Title2Name[i]}',
                        fontsize=9, color=color, ha='right')
            )

# Optional: Enable smart label adjustment
# adjust_text(texts, arrowprops=dict(arrowstyle="->", color='gray', lw=0.5))

# === Set axis range (log-log scale) ===
x_min = 10**3
x_max = 10**7
y_min = 10**3
y_max = 10**7
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

# === Reference line (y = x) ===
x_vals = np.linspace(x_min, x_max, 100)
ax.plot(x_vals, x_vals, color='black', linestyle='--', label='y = x')

# === Axis Labels ===
ax.set_xlabel('$W_i$ Million (Data Set 1)', fontsize=20)
ax.set_ylabel('Benchmark $W^{bench}_i$ \nfrom Prior Work (Million)', fontsize=20)

# === Format axis ticks in millions ===
def millions(x, pos):
    return f'{x*1e-6:.0f}'

formatter = ticker.FuncFormatter(millions)
ax.xaxis.set_major_formatter(formatter)
ax.yaxis.set_major_formatter(formatter)

# === Use log-log scale ===
ax.set_xscale('log')
ax.set_yscale('log')

# === Compute and show Pearson correlation ===
r, p = pearsonr(temp_list1, temp_list2)
ax.text(0.45, 0.1, r'$correlation = {:.2f}$'.format(r),
        fontsize=15, weight='bold', transform=ax.transAxes)

# === Save Figure ===
plt.savefig('./Figures/Figure 11B.pdf', dpi=600, bbox_inches='tight')


# === Figure 11C ===
Benchmark_data1.set_index('year', inplace=True)
temp_list = []
ContentsOfTitle.reset_index(drop=True, inplace=True)
for i in range(len(ContentsOfTitle)):
    try:
        temp_year = ContentsOfTitle.loc[i]['Year'].item()
        temp_Title = ContentsOfTitle.loc[i]['Title'].item()
        if temp_Title == 6 or temp_Title == 34:
            temp_list.append(None)
        else:
            temp_word_counts = ContentsOfTitle.loc[i]['Cleaned Text Word Count']
            # Difference: our word count minus benchmark word count
            temp_list.append(temp_word_counts.item() - Benchmark_data1.loc[temp_year][str(temp_Title)].item())
    except:
        temp_list.append(None)

ContentsOfTitle['Wi_diff'] = temp_list

# === Normalize the Difference by Total Words ===
temp_Data1 = ContentsOfTitle.copy()
temp_Data1['Wi_diff/Total Words'] = temp_Data1['Wi_diff'] / temp_Data1['Cleaned Text Word Count']

# === Calculate Title-level Average Difference Ratio ===
temp_df = pd.DataFrame(temp_Data1.groupby('Title')['Wi_diff/Total Words'].mean().sort_values(ascending=False))
temp_df['Title Name'] = temp_df.index.map(Title2Name)

# === Visualization: Swarmplot of Relative Differences ===
# Remove Title 6 and 34 from analysis
filtered_df = temp_df[~temp_df.index.isin([6, 34])].copy()
filtered_df['Title'] = filtered_df.index.astype(str)
filtered_df['x'] = 0  # dummy x for swarmplot

plt.figure(figsize=(3, 3))
ax = plt.subplot(111)

# Plot all titles in gray
sns.swarmplot(data=filtered_df, x='x', y='Wi_diff/Total Words',
              color='gray', dodge=False, size=5, ax=ax, alpha=0.4)

# === Mean Line ===
mean_value = filtered_df['Wi_diff/Total Words'].mean()
ax.axhline(mean_value, linestyle='--', color='gray', linewidth=0.8)
ax.text(0.003, mean_value + 0.01, f"Average = {mean_value:.2f}",
        color='gray', fontsize=9, va='bottom')

# === Highlight Top-3 and Bottom-3 Titles ===
top3 = filtered_df.sort_values(by='Wi_diff/Total Words', ascending=False).head(3)
bottom3 = filtered_df.sort_values(by='Wi_diff/Total Words', ascending=True).head(3)
highlight_df = pd.concat([top3, bottom3]).copy()
highlight_df['x'] = 0
highlight_df.reset_index(drop=True, inplace=True)

# Annotate Highlighted Titles
texts = []
for i, row in highlight_df.iterrows():
    color = title2color_highlight[int(row['Title'])]  # use predefined color map
    ax.scatter(row['x'], row['Wi_diff/Total Words'], color=color, s=20, zorder=3)

    texts.append(
        ax.text(row['x'], row['Wi_diff/Total Words'] + 0.015,
                f"Title {row['Title']} – {row['Title Name']}",
                fontsize=8, color=color)
    )

# Adjust text to avoid overlapping
adjust_text(texts, arrowprops=dict(arrowstyle="->", color='gray', lw=0.5))

# === Final Plot Settings ===
ax.set_xlabel("")
ax.set_ylabel(r"($W_i$ - $W_i^{bench}$) / $W_i$", fontsize=14)
ax.set_xticks([])
ax.set_ylim(0.2, 0.9)
ax.legend().remove()

# === Save Figures ===
plt.savefig('./Figures/Figure 11C.pdf', dpi=600, bbox_inches='tight')

####################
# === Figure 11D ===
# === Initialize plot ===
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(111)

# === Loop through each title and plot its data points ===
for i in range(1, 51):
    if i in [6, 34]:  # Exclude these titles
        continue

    temp_df = Benchmark_data2[
        Benchmark_data2['Title'] == i
    ][['Year', 'Tree_nodes_benchmark', 'Tree_nodes']]
    temp_df = temp_df[(temp_df['Year'] >= 1994) & (temp_df['Year'] <= 2018)]
    
    # Set color and transparency
    color = title2color_highlight.get(int(i), 'grey')
    alpha = 1.0 if i in highlight_titles else 0.1

    # Plot the scatter point for this title
    ax.scatter(temp_df['Tree_nodes'], temp_df['Tree_nodes_benchmark'],
               color=color, s=15, alpha=alpha, edgecolors='none')

    # Add text annotation for selected titles
    if i in [42, 10, 7]:
        ha = 'right'
    elif i in [1, 27]:
        ha = 'left'
    else:
        ha = None

    if ha:
        ax.text(temp_df['Tree_nodes'].max(),
                temp_df['Tree_nodes_benchmark'].max() + 0.05,
                f'Title {i}: {Title2Name[i]}',
                fontsize=9, color=color, ha=ha)

# === Plot diagonal reference line y = x ===
x_min, x_max = 10, 10**6
ax.set_xlim(x_min, x_max)
ax.set_ylim(x_min, x_max)

x_vals = np.linspace(x_min, x_max, 100)
ax.plot(x_vals, x_vals, color='black', linestyle='--', label='y = x')

# === Axis settings ===
ax.set_xlabel('|$N_i$| (Data Set 2)', fontsize=20)
ax.set_ylabel('Benchmark |$N_i$|\nfrom Prior Work', fontsize=20)
ax.set_xscale('log')
ax.set_yscale('log')

# === Display Pearson correlation coefficient ===
r, p = pearsonr(Benchmark_data2['Tree_nodes_benchmark'], Benchmark_data2['Tree_nodes'])
ax.text(0.45, 0.1, r'$correlation = {:.2f}$'.format(r),
        fontsize=15, weight='bold', transform=ax.transAxes)

# === Save figure ===
plt.savefig('./Figures/Figure 11D.pdf', dpi=600, bbox_inches='tight')


####################
# === Figure 11E ===

# === Initialize figure and axis ===
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(111)

# === Define highlighted titles and their colors ===
highlight_titles = [42, 5, 15, 26, 10]
highlight_colors = ['red', 'blue', 'green', 'orange', 'purple']
title2color_highlight = dict(zip(highlight_titles, highlight_colors))

texts = []

# === Plot scatter points for each title ===
for i in range(1, 51):
    if i in [6, 34]:  # Exclude problematic titles
        continue

    temp_df = Benchmark_data3[Benchmark_data3['Title'] == i][['Year', 'Citation Degree_benchmark', 'Citation Degree']]
    temp_df = temp_df[(temp_df['Year'] >= 1994) & (temp_df['Year'] <= 2018)]

    color = title2color_highlight.get(i, 'grey')
    alpha = 1.0 if i in highlight_titles else 0.1

    # Scatter plot of degree values
    ax.scatter(temp_df['Citation Degree'], temp_df['Citation Degree_benchmark'],
               color=color, s=15, alpha=alpha, edgecolors='none')

    # Annotate highlighted titles
    if i in highlight_titles:
        texts.append(
            ax.text(temp_df['Citation Degree'].max(),
                    temp_df['Citation Degree_benchmark'].max() + 0.05,
                    f'Title {i}: {Title2Name[i]}',
                    fontsize=9, color=color, ha='right')
        )

# === Calculate and display correlation coefficient ===
r, p = pearsonr(Benchmark_data3['Citation Degree'], Benchmark_data3['Citation Degree_benchmark'])
ax.text(0.45, 0.1, r'$correlation = {:.2f}$'.format(r),
        fontsize=15, weight='bold', transform=ax.transAxes)

# === Set axis limits and log-log scale ===
x_min, x_max = 1, 10**5
y_min, y_max = 1, 10**5
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_xscale('log')
ax.set_yscale('log')

# === Reference line: y = x ===
x_vals = np.linspace(x_min, x_max, 100)
ax.plot(x_vals, x_vals, color='black', linestyle='--', label='y = x')

# === Set axis labels ===
ax.set_xlabel('Degree (Data Set 3)', fontsize=20)
ax.set_ylabel('Benchmark Degree\nfrom Prior Work', fontsize=20)

# === Save figure ===
plt.savefig('./Figures/Figure 11E.pdf', dpi=600, bbox_inches='tight')


####################
# === Figure 12AB ===

# === Define color for highlighted titles ===
title2color_highlight = {
    9: 'crimson',
    1: 'blue',
    # 34: 'green',  # Excluded
}

# === Define comparison columns: (x_col, y_col, label, label for title) ===
columns_to_plot = [
    ('Cleaned Text Word Count_ocr', 'Cleaned Text Word Count_web', r'$W_i$', 'Cleaned Text Word Count'),
    ('Cleaned Text Unique Word Count_ocr', 'Cleaned Text Unique Word Count_web', r'$V_i$', 'Cleaned Text Unique Word Count')
]

# === Figure 12AB ===
fig, axes = plt.subplots(1, 2, figsize=(8, 4), constrained_layout=True)
axes = axes.flatten()

for i, (x_col, y_col, base_label, title_label) in enumerate(columns_to_plot):
    ax = axes[i]

    # Filter valid nonzero entries
    valid_data = Internal_validation_data1[[x_col, y_col, 'Title']].dropna()
    valid_data = valid_data[(valid_data[x_col] > 0) & (valid_data[y_col] > 0)]

    min_val = valid_data[[x_col, y_col]].min().min()
    max_val = valid_data[[x_col, y_col]].max().max()

    # Scatter all points in gray
    ax.scatter(valid_data[x_col], valid_data[y_col], color='gray', alpha=0.4, s=20)

    # y = x line
    ax.plot([min_val, max_val], [min_val, max_val], linestyle='--', color='black', alpha=0.5)

    # Linear Regression for visual reference
    X_lin = valid_data[[x_col]]
    y_lin = valid_data[y_col]
    model = LinearRegression().fit(X_lin, y_lin)

    # R² for y = x line
    r2_identity = 1 - np.sum((y_lin - X_lin.values.flatten()) ** 2) / np.sum((y_lin - y_lin.mean()) ** 2)

    # Annotate R²
    ax.text(0.05, 0.90,
            r'$R^2_{{y=x}} = {:.2f}$'.format(r2_identity),
            fontsize=13, transform=ax.transAxes)

    # Labels
    ax.set_xlabel(f'{base_label}$^{{\\mathrm{{ocr}}}}$', fontsize=20)
    ax.set_ylabel(f'{base_label}$^{{\\mathrm{{web}}}}$', fontsize=20)
    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)

    # Scientific tick formatting
    ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.xaxis.get_major_formatter().set_scientific(True)
    ax.yaxis.get_major_formatter().set_scientific(True)
    ax.xaxis.get_major_formatter().set_powerlimits((0, 0))
    ax.yaxis.get_major_formatter().set_powerlimits((0, 0))

# Remove legend
handles, labels = ax.get_legend_handles_labels()
fig.legend(handles, labels, title="Title", loc='center right', bbox_to_anchor=(1.12, 0.5)).remove()

# Save
plt.savefig('./Figures/Figure 12AB.pdf', dpi=600, bbox_inches='tight')

# === Figure 12CD ===
# Step 1: Filter valid citation data
temp_df = Internal_validation_data2.dropna(subset=['Citation OCR', 'Citation Web'])
temp_df = temp_df[(temp_df['Citation OCR'] > 0) & (temp_df['Citation Web'] > 0)]

# Step 2: Log-transform and regression
X_log = np.log(temp_df[['Citation OCR']])
y_log = np.log(temp_df['Citation Web'])
model = LinearRegression().fit(X_log, y_log)
y_pred = model.predict(X_log)

# Step 3: Regression statistics
slope = model.coef_[0]
n = len(X_log)
residual_std = np.sqrt(np.sum((y_log - y_pred) ** 2) / (n - 2))
x_std = np.std(X_log.values.flatten())
std_slope = residual_std / (x_std * np.sqrt(n))

# Step 4: R² and RMSE for identity line
y_true = np.log(temp_df['Citation Web'].values)
y_pred_identity = np.log(temp_df['Citation OCR'].values)
r2_identity = 1 - np.sum((y_true - y_pred_identity) ** 2) / np.sum((y_true - y_true.mean()) ** 2)

# Step 5: Plotting
fig, axes = plt.subplots(1, 2, figsize=(8, 4), constrained_layout=True)
ax1, ax2 = axes

# Panel 1: Scatterplot
sns.scatterplot(data=temp_df, x='Citation OCR', y='Citation Web', ax=ax1,
                color='gray', alpha=0.5)

min_val = temp_df[['Citation OCR', 'Citation Web']].min().min()
max_val = temp_df[['Citation OCR', 'Citation Web']].max().max()
ax1.plot([min_val, max_val], [min_val, max_val], linestyle='--', color='black', alpha=0.6)

ax1.set_xlim(min_val, max_val)
ax1.set_ylim(min_val, max_val)
ax1.set_xlabel('$Edge\\ weight^{ocr}$', fontsize=20)
ax1.set_ylabel('$Edge\\ weight^{web}$', fontsize=20)

# R² annotation
ax1.text(0.05, 0.90, r'$R^2_{{y=x}} = {:.2f}$'.format(r2_identity), fontsize=12, transform=ax1.transAxes)

# Scientific ticks
ax1.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
ax1.xaxis.get_major_formatter().set_scientific(True)
ax1.yaxis.get_major_formatter().set_scientific(True)
ax1.xaxis.get_major_formatter().set_powerlimits((0, 0))
ax1.yaxis.get_major_formatter().set_powerlimits((0, 0))

# --- Match tick spacing on both axes ---
ax1.xaxis.set_major_locator(MaxNLocator(nbins=7))
ax1.yaxis.set_major_locator(MaxNLocator(nbins=7))

# Panel 2: Histogram of citation difference
ax2.hist(temp_df['diff'], bins=100, color='steelblue', edgecolor='black', alpha=0.7)
ax2.set_xlabel(r'$\Delta$ $Edge\ weight$', fontsize=20)
ax2.set_ylabel('Frequency', fontsize=20)

# Optional: scientific tick for histogram x-axis (if diff values large)
ax2.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
ax2.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
ax2.xaxis.get_major_formatter().set_scientific(True)
ax2.yaxis.get_major_formatter().set_scientific(True)
ax2.xaxis.get_major_formatter().set_powerlimits((0, 0))
ax2.yaxis.get_major_formatter().set_powerlimits((0, 0))

# Panel 2: Histogram of citation difference
ax2.hist(temp_df['diff'], bins=100, color='steelblue', edgecolor='black', alpha=0.7)
ax2.set_xlabel(r'$\Delta$ $Edge\ weight$', fontsize=20)
ax2.set_ylabel('Frequency', fontsize=20)

# --- x-axis formatter with ×10^x notation at the top ---
from matplotlib.ticker import ScalarFormatter
formatter = ScalarFormatter(useMathText=True)
formatter.set_scientific(True)
formatter.set_powerlimits((0, 0))  # Force scientific
formatter.set_useOffset(True)      # Show ×10^x on top
ax2.xaxis.set_major_formatter(formatter)

# Save
plt.savefig('./Figures/Figure 12CD.pdf', dpi=600, bbox_inches='tight')