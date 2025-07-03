import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import LogLocator, LogFormatterMathtext, FuncFormatter
from pylr2 import regress2
import numpy as np
from scipy.optimize import curve_fit

# Function to calculate R-squared
def r_squared(y, y_hat):
    residual_sum_of_squares = np.sum((y - y_hat) ** 2)
    total_sum_of_squares = np.sum((y - np.mean(y)) ** 2)
    return 1 - residual_sum_of_squares / total_sum_of_squares

def zipf_mandelbrot(r, C, b, a):
    return C / (r + b) ** a

def safe_to_int(x):
    try:
        f = float(x)
        if f.is_integer():
            return int(f)
        else:
            return str(x)
    except (ValueError, TypeError):
        return str(x)

years_DS1 = [1926, 1934, 1940, 1946, 1952, 1958, 1964, 1970, 1976, 1982, 1988, 1994, 2000]
years_DS2 = [year for year in range(1994,2024)]

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

# Step 1: Create grid layout
fig, axs = plt.subplots(8, 6, figsize=(20, 20), constrained_layout=True)

# Step 2: Define target titles
titles = [k for k in range(1, 51) if k not in [6, 34]]
titles_text = [f'Title {k}: {Title2Name[k]}' for k in titles]

# Step 3: Loop through subplots
for i, (ax, title, title_text) in enumerate(zip(axs.flat, titles, titles_text)):
    temp_data = Data1.copy()
    temp_data = temp_data[temp_data['Year'] >= 1934]
    temp_data = temp_data[temp_data['Title'] != 'All titles']
    temp_data['Title'] = temp_data['Title'].astype(int)
    temp_df = temp_data[temp_data['Title'] == title].sort_values(by='Year')

    temp_xs = temp_df['Year']
    temp_ys = temp_df['Cleaned Text Word Count']

    ax.plot(temp_xs, temp_ys, color='black')
    ax.axvline(x=1994, color='grey', linestyle='dashed', linewidth=2)
    ax.set_title(title_text, fontsize=10)
    ax.set_xticks([1934, 1980, 2023])

    if i >= 42:
        ax.set_xlabel("Year", fontsize=14)
    if i % 6 == 0:
        ax.set_ylabel('$W_i$', fontsize=14)

    ax.grid(False)

# Step 4: Save or show figure
plt.savefig('./Figures/Figure_S11.pdf', dpi=600, bbox_inches='tight')


# Step 1: Create figure layout
fig, axs = plt.subplots(8, 6, figsize=(20, 20), constrained_layout=True)

# Step 2: Define target titles
titles = [k for k in range(1, 51) if k not in [6, 34]]
titles_text = [f'Title {k}: {Title2Name[k]}' for k in titles]

# Step 3: Loop through and plot each title's unique word count
for i, (ax, title, title_text) in enumerate(zip(axs.flat, titles, titles_text)):
    temp_data = Data1.copy()
    temp_data = temp_data[temp_data['Year'] >= 1934]
    temp_data = temp_data[temp_data['Title'] != 'All titles']
    temp_data['Title'] = temp_data['Title'].astype(int)
    temp_df = temp_data[temp_data['Title'] == title].sort_values(by='Year')

    temp_xs = temp_df['Year']
    temp_ys = temp_df['Cleaned Text Unique Word Count']

    ax.plot(temp_xs, temp_ys, color='black')
    ax.axvline(x=1994, color='grey', linestyle='dashed', linewidth=2)

    ax.set_title(title_text, fontsize=10)
    ax.set_xticks([1934, 1980, 2023])

    if i >= 42:
        ax.set_xlabel("Year", fontsize=14)
    if i % 6 == 0:
        ax.set_ylabel("$V_i$", fontsize=14)

    ax.grid(False)

# Step 4: Save or show
plt.savefig('./Figures/Figure_S12.pdf', dpi=600, bbox_inches='tight')

# Step 1: Create an 8x6 grid for subplots (total: 48 plots)
fig, axs = plt.subplots(8, 6, figsize=(20, 20), constrained_layout=True)

# Step 2: Define titles to include (exclude Title 6 and Title 34)
titles = [k for k in range(1, 51) if k not in [6, 34]]
titles_text = [f'Title {k}: {Title2Name[k]}' for k in titles]

# Step 3: Plot each title's time series in a subplot
for i, (ax, title, title_text) in enumerate(zip(axs.flat, titles, titles_text)):
    # Extract and sort data for the current title
    temp_data = Data1.copy()
    temp_data = temp_data[temp_data['Year']>=1934]
    temp_data = temp_data[temp_data['Title']!='All titles']
    temp_data['Title'] = temp_data['Title'].astype(int)
    temp_df = temp_data[temp_data['Title'] == title].sort_values(by='Year')
    temp_xs = temp_df['Year']
    temp_ys = temp_df['entropies_norm']

    # Main line plot
    ax.plot(temp_xs, temp_ys, color='black')
    ax.axvline(x=1994, color='grey', linestyle='dashed', linewidth=2)

    # Title and ticks
    ax.set_title(title_text, fontsize=10)
    ax.set_xticks([1934, 1980, 2023])

    # Add x-axis label for bottom row only
    if i >= 42:
        ax.set_xlabel("Year", fontsize=14)

    # Add y-axis label for leftmost column only
    if i % 6 == 0:
        ax.set_ylabel(r"$\hat{S}_i$", fontsize=14)

    ax.grid(False)

# Adjust layout to prevent overlapping
plt.savefig('./Figures/Figure_S13.pdf', dpi=600, bbox_inches='tight')




x_label = r"$W_i$"
y_label = r"$V_i$"

# Create an 8x6 grid for subplots
fig, axs = plt.subplots(8, 6, figsize=(20, 20), constrained_layout=True)

# Filter titles to include (exclude Title 6 and 34)
titles = [k for k in range(1, 51) if k not in [6, 34]]
titles_text = [f'Title {k}: {Title2Name[k]}' for k in titles]

for i, (ax, title, title_text) in enumerate(zip(axs.flat, titles, titles_text)):
    # Step 1: Filter data for the given title
    temp_data = Data1.copy()
    temp_data = temp_data[temp_data['Year'] >= 1934]
    temp_data = temp_data[temp_data['Title'] != 'All titles']
    temp_data['Title'] = temp_data['Title'].astype(int)
    x = temp_data[temp_data['Title'] == title]['Cleaned Text Word Count']
    y = temp_data[temp_data['Title'] == title]['Cleaned Text Unique Word Count']

    # Step 2: Remove zero values to avoid log-scale errors
    x = x[(y != 0) & (x != 0)]
    y = y[(y != 0) & (x != 0)]

    # Step 3: Perform regression and calculate fitted line
    results = regress2(np.log10(x), np.log10(y))
    a = results['slope']
    b = results['intercept']
    std_slope = results['std_slope']
    y_hat = x ** a * 10 ** b

    # Step 4: Main plot
    ax.scatter(x, y, color='black', s=10)
    ax.plot(x, y_hat, color='orange', label='Fitted line')
    ax.set_yscale('log')
    ax.set_xscale('log')
    ax.set_title(title_text, fontsize=10)

    if i >= 42:
        ax.set_xlabel(x_label, fontsize=14)
    if i % 6 == 0:
        ax.set_ylabel(y_label, fontsize=14)

    # Annotate slope and R^2
    ax.text(0.05, 0.9, r'$\beta \, = \, {:.2f} \; [ {:.2f} , \; {:.2f} ]$'.format(
        a, a - 1.96 * std_slope, a + 1.96 * std_slope),
        fontsize=12, weight='bold', transform=ax.transAxes)
    ax.text(0.6, 0.2, r'$R^2= {:.2f}$'.format(r_squared(y, y_hat)),
            fontsize=12, weight='bold', transform=ax.transAxes)

    ax.grid(False)

# Adjust layout
plt.savefig('./Figures/Figure_S14.pdf', dpi=600, bbox_inches='tight')




titles = [k for k in range(1, 51) if k not in [6, 34]]

# --- Plot: Year 1934 ---
fig, axs = plt.subplots(8, 6, figsize=(20, 20), constrained_layout=True)
year = 1934

Word_count_df = pd.read_csv('./Data/Word_count_df.csv')

for i, (ax, title_num) in enumerate(zip(axs.flat, titles)):
    temp_data = Word_count_df.copy()
    temp_data = temp_data[temp_data['title']!='All titles']
    temp_data['title'] = temp_data['title'].apply(safe_to_int)
    temp_data = temp_data[(temp_data['title'] == title_num) & (temp_data['year'] == year)].copy()

    y = temp_data['count'].sort_values(ascending=False).values
    x = np.arange(1, len(y) + 1)
    mask = (y != 0) & (x != 0)
    x = x[mask]
    y = y[mask]

    try:
        popt, pcov = curve_fit(zipf_mandelbrot, x, y, p0=[1e5, 1.0, 1.0], maxfev=10000)
        C, b, a = popt
        std_dev = np.sqrt(np.diag(pcov))
        y_hat = zipf_mandelbrot(x, *popt)

        ax.scatter(x, y, color='black', alpha=0.2, s=8)
        ax.plot(x, y_hat, color='orange')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title(f'Title {title_num}: {Title2Name.get(title_num, "Unknown")}', fontsize=10)

        if i >= 42:
            ax.set_xlabel('Rank', fontsize=12)
        if i % 6 == 0:
            ax.set_ylabel('Word Frequency', fontsize=12)

        ci_b_lower, ci_b_upper = b - 1.96 * std_dev[1], b + 1.96 * std_dev[1]
        ci_a_lower, ci_a_upper = a - 1.96 * std_dev[2], a + 1.96 * std_dev[2]
        ax.text(0.05, 0.1, fr'$b = {b:.2f} [{ci_b_lower:.2f}, {ci_b_upper:.2f}]$', fontsize=10, transform=ax.transAxes)
        ax.text(0.05, 0.2, fr'$a = {a:.2f} [{ci_a_lower:.2f}, {ci_a_upper:.2f}]$', fontsize=10, transform=ax.transAxes)
        ax.text(0.6, 0.8, fr'$R^2 = {r_squared(y, y_hat):.2f}$', fontsize=10, transform=ax.transAxes)
        ax.tick_params(labelsize=8)
        ax.grid(False)

    except RuntimeError:
        ax.set_title(f'Title {title_num}: Fit Failed', fontsize=10)
        ax.axis('off')
plt.savefig('./Figures/Figure_S15.pdf', dpi=600, bbox_inches='tight')


# --- Plot: Year 2023 ---
fig, axs = plt.subplots(8, 6, figsize=(20, 20), constrained_layout=True)
year = 2023

for i, (ax, title_num) in enumerate(zip(axs.flat, titles)):
    
    temp_data = Word_count_df.copy()
    temp_data = temp_data[temp_data['title']!='All titles']
    temp_data['title'] = temp_data['title'].apply(safe_to_int)
    temp_data = temp_data[(temp_data['title'] == title_num) & (temp_data['year'] == year)].copy()
    y = temp_data['count'].sort_values(ascending=False).values
    x = np.arange(1, len(y) + 1)
    mask = (y != 0) & (x != 0)
    x = x[mask]
    y = y[mask]

    try:
        popt, pcov = curve_fit(zipf_mandelbrot, x, y, p0=[1e5, 1.0, 1.0], maxfev=10000)
        C, b, a = popt
        std_dev = np.sqrt(np.diag(pcov))
        y_hat = zipf_mandelbrot(x, *popt)

        ax.scatter(x, y, color='black', alpha=0.2, s=8)
        ax.plot(x, y_hat, color='orange')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_title(f'Title {title_num}: {Title2Name.get(title_num, "Unknown")}', fontsize=10)

        if i >= 42:
            ax.set_xlabel('Rank', fontsize=12)
        if i % 6 == 0:
            ax.set_ylabel('Word Frequency', fontsize=12)

        ci_b_lower, ci_b_upper = b - 1.96 * std_dev[1], b + 1.96 * std_dev[1]
        ci_a_lower, ci_a_upper = a - 1.96 * std_dev[2], a + 1.96 * std_dev[2]
        ax.text(0.05, 0.1, fr'$b = {b:.2f} [{ci_b_lower:.2f}, {ci_b_upper:.2f}]$', fontsize=10, transform=ax.transAxes)
        ax.text(0.05, 0.2, fr'$a = {a:.2f} [{ci_a_lower:.2f}, {ci_a_upper:.2f}]$', fontsize=10, transform=ax.transAxes)
        ax.text(0.6, 0.8, fr'$R^2 = {r_squared(y, y_hat):.2f}$', fontsize=10, transform=ax.transAxes)
        ax.tick_params(labelsize=8)
        ax.grid(False)

    except RuntimeError:
        ax.set_title(f'Title {title_num}: Fit Failed', fontsize=10)
        ax.axis('off')

plt.savefig('./Figures/Figure_S16.pdf', dpi=600, bbox_inches='tight')


# Filter titles
titles = [k for k in range(1, 51) if k not in [6, 34]]
titles_text = [f'Title {k}: {Title2Name[k]}' for k in titles]

# Set up figure
fig, axs = plt.subplots(8, 6, figsize=(20, 20), constrained_layout=True)
axs = axs.flatten()

# Prepare data
temp_Data = Data1.copy()
temp_Data = temp_Data[temp_Data['Year'] >= 1934]
temp_Data = temp_Data[temp_Data['Title'] != 'All titles']
temp_Data['Title'] = temp_Data['Title'].astype(int)
temp_min = temp_Data[(temp_Data['Year'] > 1926)]['Scaling_Exponent_Zipf_Mandelbrot_law'].min()
temp_max = temp_Data[(temp_Data['Year'] > 1926)]['Scaling_Exponent_Zipf_Mandelbrot_law'].max()

# Loop through each subplot
for i, (ax, title, title_text) in enumerate(zip(axs, titles, titles_text)):
    temp_data = temp_Data[(temp_Data['Title'] == title) & (temp_Data['Year'] > 1926)].copy()
    if temp_data.empty:
        continue

    sns.lineplot(
        data=temp_data,
        x='Year',
        y='Scaling_Exponent_Zipf_Mandelbrot_law',
        ci=None,
        alpha=1,
        ax=ax,
        marker='o',
        color='black'
    )

    ax.axhline(y=1, color='red', linestyle='dotted', linewidth=1)
    ax.axvline(x=1994, color='black', linestyle='dotted', linewidth=1)

    ax.set_xticks([1934, 1944, 1954, 1964, 1976, 1986, 1994, 2006, 2012, 2018, 2023])
    ax.set_xticklabels([1934, 1944, 1954, 1964, 1976, 1986, 1994, 2006, 2012, 2018, 2023], rotation=90)
    ax.set_ylim(temp_min * 0.9, 1.4)
    ax.set_title(title_text, fontsize=10)

    # Clean up axis labels
    if i < 42:
        ax.set_xlabel('')
    if i % 6 != 0:
        ax.set_ylabel('')

# Shared axis labels
for i in range(42, 48):
    axs[i].set_xlabel('Year', fontsize=12)
for i in range(0, 48, 6):
    axs[i].set_ylabel('Zipf-Mandelbrot Exponent\n($a$)', fontsize=12)

# Final layout
plt.savefig('./Figures/Figure_S17.pdf', dpi=600, bbox_inches='tight')



for title_num in [19]:
    fig, axes = plt.subplots(1, 3, figsize=(12, 3), constrained_layout=True)
    for i, year in enumerate([1964, 1970, 1976]):
        ax = axes[i]
        temp_data = Word_count_df.copy()
        temp_data = temp_data[temp_data['title']!='All titles']
        temp_data['title'] = temp_data['title'].apply(safe_to_int)
        temp_data = temp_data[(temp_data['title'] == title_num) & (temp_data['year'] == year)].copy()
        y = temp_data['count'].sort_values(ascending=False).values
        x = np.arange(1, len(y) + 1)
        x = x[(y != 0) & (x != 0)]
        y = y[(y != 0) & (x != 0)]

        ax.set_yscale('log')
        ax.set_xscale('log')
        ax.set_xlabel('Rank', fontsize=22)
        if i == 0:
            ax.set_ylabel('Word Frequency', fontsize=22)
        ax.tick_params(axis='x', labelsize=12)
        ax.tick_params(axis='y', labelsize=12)

        popt, pcov = curve_fit(zipf_mandelbrot, x, y, p0=[1e5, 1.0, 1.0], maxfev=10000)
        C, b, a = popt
        std_dev = np.sqrt(np.diag(pcov))
        ci_b_lower, ci_b_upper = b - 1.96 * std_dev[1], b + 1.96 * std_dev[1]
        ci_a_lower, ci_a_upper = a - 1.96 * std_dev[2], a + 1.96 * std_dev[2]
        y_hat = zipf_mandelbrot(x, *popt)

        x_min, x_max = np.floor(np.log10(x.min())), np.ceil(np.log10(x.max()))
        y_min, y_max = np.floor(np.log10(y.min())), np.ceil(np.log10(y.max()))
        ax.set_xticks([10 ** j for j in range(int(x_min), int(x_max) + 1)])
        ax.set_yticks([10 ** j for j in range(int(y_min), int(y_max) + 1)])
        ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f'$10^{{{int(np.log10(x))}}}$'))
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda y, _: f'$10^{{{int(np.log10(y))}}}$'))

        ax.scatter(x, y, color='black', alpha=0.2, s=8)
        ax.plot(x, y_hat, color='orange')

        ax.text(0.05, 0.1, fr'$b = {b:.2f} \; [ {ci_b_lower:.2f} , \; {ci_b_upper:.2f} ]$', fontsize=15, weight='bold', transform=ax.transAxes)
        ax.text(0.05, 0.2, fr'$a = {a:.2f} \; [ {ci_a_lower:.2f} , \; {ci_a_upper:.2f} ]$', fontsize=15, weight='bold', transform=ax.transAxes)
        ax.text(0.6, 0.8, fr'$R^2= {r_squared(y, y_hat):.2f}$', fontsize=15, weight='bold', transform=ax.transAxes)
        ax.set_title(f'{year}', fontsize=22)

    plt.suptitle(f'Title {title_num}: {Title2Name[title_num]}', fontsize=22, y=1.1)
    plt.savefig(f'./Figures/Figure_S18A.pdf', dpi=600, bbox_inches='tight')

# === Figure S18b: Exponent over time (Title 19) ===
temp_Data1 = Data1.copy()
temp_Data1 = temp_Data1[temp_Data1['Title'] != 'All titles']
temp_Data1['Title'] = temp_Data1['Title'].astype(int)
temp_Data1 = temp_Data1[(temp_Data1['Year'] > 1926)]
temp_Data1 = temp_Data1[(temp_Data1['Title'] == 19)]

fig = plt.figure(figsize=(6, 4), constrained_layout=True)
ax = plt.subplot(111)

sns.lineplot(
    data=temp_Data1,
    x='Year',
    y='Scaling_Exponent_Zipf_Mandelbrot_law',
    ci=None,
    alpha=1,
    ax=ax,
    marker='o',
    color='red'
)
ax.set_ylabel('Zipf-Mandelbrot Exponent ($a$)', fontsize=14)
ax.set_xlabel('Year', fontsize=14)

ax.axhline(y=1, color='red', linestyle='dotted')
ax.axvline(x=1994, color='black', linestyle='dotted')

ax.set_xticks(years_DS1[1:] + [2006, 2012, 2018, 2023])
ax.set_xticklabels(years_DS1[1:] + [2006, 2012, 2018, 2023], rotation=90)
ax.text(0.01, 0.10, 'Title 19: ' + Title2Name[19],
        fontsize=18,
        transform=ax.transAxes)

highlight_years = [1964, 1970, 1976]
for year in highlight_years:
    y_val = temp_Data1[temp_Data1['Year'] == year]['Scaling_Exponent_Zipf_Mandelbrot_law']
    if not y_val.empty:
        ax.annotate(f'{year}',
                    xy=(year, y_val.values[0]),
                    xytext=(year-5, y_val.values[0]),
                    arrowprops=dict(arrowstyle='->', color='gray'),
                    fontsize=10,
                    ha='center')

plt.savefig('./Figures/Figure_S18B.pdf', dpi=600, bbox_inches='tight')

# === Figure S18c: Top 10 words over time (barplot) ===
temp_Data1 = Word_count_df.copy()
temp_Data1 = temp_Data1[temp_Data1['title']!='All titles']
temp_Data1['title'] = temp_Data1['title'].apply(safe_to_int)

title_num = 19
base_year = 1970
top_words = (
    temp_Data1[(temp_Data1['title'] == title_num) & (temp_Data1['year'] == base_year)]
    .sort_values(by='count', ascending=False)
    .head(10)['word']
    .tolist()
)

years = [1964, 1970, 1976]
data_list = []

for year in years:
    year_df = temp_Data1[
        (temp_Data1['title'] == title_num) &
        (temp_Data1['year'] == year) &
        (temp_Data1['word'].isin(top_words))
    ][['word', 'count']].copy()
    year_df['year'] = str(year)
    data_list.append(year_df)

combined_df = pd.concat(data_list)
combined_df['word'] = pd.Categorical(combined_df['word'], categories=top_words, ordered=True)

plt.figure(figsize=(5, 3), constrained_layout=True)
ax = plt.subplot(111)

sns.barplot(data=combined_df, x='word', y='count', hue='year')
ax.set_ylabel('Frequency', fontsize=18)
ax.set_xlabel('Top 10 word in Title 19', fontsize=18)
ax.legend(title='Year')

plt.setp(ax.get_xticklabels(), rotation=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.savefig('./Figures/Figure_S18C.pdf', dpi=600, bbox_inches='tight')