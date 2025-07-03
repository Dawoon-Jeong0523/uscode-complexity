import pandas as pd
import numpy as np
from scipy.stats import sem
import scipy  # Optional additional scipy modules
from pylr2 import regress2
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm, font_manager
from matplotlib.ticker import LogLocator, LogFormatterMathtext, FuncFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from adjustText import adjust_text
import matplotlib.cm as cm
from scipy.optimize import curve_fit
import matplotlib.colors as mcolors

years_DS1 = [1926, 1934, 1940, 1946, 1952, 1958, 1964, 1970, 1976, 1982, 1988, 1994, 2000]
years_DS2 = [year for year in range(1994,2024)]

def safe_to_int(x):
    try:
        f = float(x)
        if f.is_integer():
            return int(f)
        else:
            return str(x)
    except (ValueError, TypeError):
        return str(x)
    
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
        "Public Contracts",
        "Public Buildings, Property, and Works",
        "Public Lands",
        "Mineral Lands and Mining",
        "Navigation and Navigable Waters",
        "Postal Service",
        'Patents'
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

# Function to calculate R-squared
def r_squared(y, y_hat):
    residual_sum_of_squares = np.sum((y - y_hat) ** 2)
    total_sum_of_squares = np.sum((y - np.mean(y)) ** 2)
    return 1 - residual_sum_of_squares / total_sum_of_squares


# --- Define Zipf-Mandelbrot function ---
def zipf_mandelbrot(r, C, b, a):
    return C / (r + b) ** a


# --- Group Colors (predefined) ---
group_colors = {
    "Government Structure": "skyblue",
    "Economy": "purple",
    "Society": "green",
    "National Defense": "orange"
}

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


title_nums = [19, 4]
x_label = r"$W_i$"
y_label = r"$V_i$"

fig, ax = plt.subplots(1, 2, figsize=(8, 4), constrained_layout=True)

for i, title_num in enumerate(title_nums):
    temp_data = Data1.copy()
    temp_data = temp_data[temp_data['Year'] >= 1934]

    # Step 1: Filter data
    x = temp_data[temp_data['Title'] == title_num]['Cleaned Text Word Count']
    y = temp_data[temp_data['Title'] == title_num]['Cleaned Text Unique Word Count']

    # Step 2: Remove zero values
    x = x[(y != 0) & (x != 0)]
    y = y[(y != 0) & (x != 0)]

    # Step 3: Set log scale
    ax[i].set_yscale('log')
    ax[i].set_xscale('log')
    ax[i].set_xlabel(x_label, fontsize=25)
    if i == 0:
        ax[i].set_ylabel(y_label, fontsize=25)
    ax[i].tick_params(axis='x', labelsize=12)
    ax[i].tick_params(axis='y', labelsize=12)
    ax[i].yaxis.set_ticks_position('left')
    ax[i].xaxis.set_ticks_position('bottom')

    # Step 4: Log-log regression
    results = regress2(np.log10(x), np.log10(y))
    a = results['slope']
    b = results['intercept']
    std_slope = results['std_slope']
    y_hat = x ** a * 10 ** b

    # Step 5: Axis ticks (powers of 10)
    x_min, x_max = np.floor(np.log10(x.min())), np.ceil(np.log10(x.max()))
    y_min, y_max = np.floor(np.log10(y.min())), np.ceil(np.log10(y.max()))
    ax[i].set_xticks([10 ** j for j in range(int(x_min), int(x_max) + 1)])
    ax[i].set_yticks([10 ** j for j in range(int(y_min), int(y_max) + 1)])

    # Step 6: Plot
    ax[i].scatter(x, y, color='black')
    ax[i].plot(x, y_hat, color='orange', label='Fitted line')

    # Step 7: Annotations
    ax[i].text(0.05, 0.9, r'$\beta \, = \, {:.2f} \; [ {:.2f} , \; {:.2f} ]$'.format(
        a, a - 1.96 * std_slope, a + 1.96 * std_slope), fontsize=15, weight='bold', transform=ax[i].transAxes)
    ax[i].text(0.6, 0.2, r'$R^2= {:.2f}$'.format(r_squared(y, y_hat)),
               fontsize=15, weight='bold', transform=ax[i].transAxes)

    if title_num == 4:
        ax[i].set_title(f'Title {title_num}: Flag and Seal, ...', fontsize=14)
    else:
        ax[i].set_title(f'Title {title_num}: {Title2Name[title_num]}', fontsize=14)

# Step 8: Save and show
plt.savefig('./Figures/Figure 6ab.pdf', dpi=600, bbox_inches='tight')


# === Step 1: Prepare Data ===
temp_data = Data1.copy()
temp_data = temp_data[temp_data['Year'] >= 1934]
temp_data = temp_data[temp_data['Title'] != 'All titles']
temp_data['Title'] = temp_data['Title'].astype(int)

# Get scaling exponents (one per title)
scaling_exponents = temp_data.drop_duplicates(subset=['Title'])['Scaling_Exponent_Heaps_law'].tolist()

# Get total word count in 2023 and apply log scale
temp_data_2023 = temp_data[temp_data['Year'] == 2023].copy()
word_counts = temp_data_2023.groupby('Title')['Cleaned Text Word Count'].sum().sort_values(ascending=False)
coolwarm_colors = plt.cm.coolwarm(np.linspace(0, 1, len(word_counts)))
Title2Color_size = dict(zip(word_counts.index, coolwarm_colors))
word_counts_log = np.log10(word_counts)

# === Step 2: Normalize color scale ===
min_val = word_counts_log.min()
max_val = word_counts_log.max()
norm = mcolors.Normalize(vmin=min_val, vmax=max_val)
cmap = cm.coolwarm

Title2Color_size = {
    idx: cmap(norm(value))
    for idx, value in word_counts_log.items()
}

# === Step 3: Bin scaling exponents and assign colors ===
bin_centers = np.arange(0.05, 1.05, 0.1)
bin_counts = np.zeros(len(bin_centers), dtype=int)
color_coordinate = {}
title_coordinate = {}

for i, value in enumerate(scaling_exponents):
    if i in [5, 33]:  # Skip problematic titles
        continue
    idx = np.argmin(np.abs(bin_centers - value))
    bin_counts[idx] += 1
    color_coordinate[idx, bin_counts[idx]] = Title2Color_size.get(i + 1, 'black')
    title_coordinate[idx, bin_counts[idx]] = i + 1

# === Step 4: Plot stacked squares by bin ===
plt.figure(figsize=(6, 9), constrained_layout=True)
box_size = 0.1

for idx, center in enumerate(bin_centers):
    for j in range(1, bin_counts[idx] + 1):
        plt.fill_betweenx(
            [j * box_size - box_size, j * box_size],
            center - box_size / 2, center + box_size / 2,
            color=color_coordinate.get((idx, j), 'gray'),
            edgecolor='black'
        )
        plt.text(center, j * box_size - box_size / 2, str(title_coordinate.get((idx, j), '')),
                 ha='center', va='center', fontsize=8, color='white', fontweight='bold')

plt.xlim(0, 1)
plt.xticks(np.arange(0, 1.1, 0.1), fontsize=12)
plt.ylim(0, np.max(bin_counts) * box_size + box_size)
ax = plt.gca()
ax.set_yticks([0, 0.5, 1, 1.5, 2, 2.5, 3])
ax.set_yticklabels([0, 5, 10, 15, 20, 25, 30], fontsize=12)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.xlabel("Scaling Exponents", fontsize=20)
plt.ylabel("Frequency", fontsize=20)

# === Step 5: Add colorbar legend ===
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

fig = plt.gcf()
ax = plt.gca()
cbar = fig.colorbar(sm, ax=ax, pad = 0.01, orientation= 'horizontal', location = 'bottom')
cbar.set_label('Number of words (log scale, year 2023)', fontsize=15)
cbar.ax.tick_params(labelsize=12)
plt.savefig(f'./Figures/Figure 6c.pdf', dpi=600, bbox_inches='tight')


# --- Define Zipf-Mandelbrot function ---
def zipf_mandelbrot(r, C, b, a):
    return C / (r + b) ** a

# --- Group Colors (predefined) ---
group_colors = {
    "Government Structure": "skyblue",
    "Economy": "purple",
    "Society": "green",
    "National Defense": "orange"
}

# --- Group Mapping (title2group, Title2color_group assumed) ---
title2group = {}
for group, titles in us_code_groups.items():
    for title in titles:
        title2group[title] = group
Title2color_group = {title: group_colors[title2group[title]] for title in title2group}

# --- Load word frequency data ---
Word_count_df = pd.read_csv('./Data/Word_count_df.csv')
Word_count_df['title'] = Word_count_df['title'].apply(lambda x: int(x) if str(x).isdigit() else str(x))

# --- Prepare subset of Data1 ---
temp_Data1 = Data1.copy()
temp_Data1 = temp_Data1[temp_Data1['Year'] >= 1934]
temp_Data1 = temp_Data1[temp_Data1['Title'] != 'All titles']
temp_Data1['Title'] = temp_Data1['Title'].astype(int)
temp_Data1 = temp_Data1[~temp_Data1['Title'].isin([6, 34])]

# --- Create subplots ---
fig, axs = plt.subplots(2, 2, figsize=(14, 12), constrained_layout=True)

# === (1) All Titles in 2023 ===
ax = axs[0, 0]
year = 2023
temp_data = Word_count_df.copy()
temp_data = temp_data[(temp_data['year'] == year) & (temp_data['title'] == 'All titles')]
y = temp_data['count'].sort_values(ascending=False).values
x = np.arange(1, len(y)+1)
x, y = x[y != 0], y[y != 0]
popt, pcov = curve_fit(zipf_mandelbrot, x, y, p0=[1e5, 1.0, 1.0], maxfev=10000)
C, b, a = popt
std_dev = np.sqrt(np.diag(pcov))
ci_b_lower, ci_b_upper = b - 1.96 * std_dev[1], b + 1.96 * std_dev[1]
ci_a_lower, ci_a_upper = a - 1.96 * std_dev[2], a + 1.96 * std_dev[2]
y_hat = zipf_mandelbrot(x, *popt)

ax.set_xscale('log'); ax.set_yscale('log')
ax.scatter(x, y, color='black', alpha=0.2, s=8)
ax.plot(x, y_hat, color='orange')
ax.set_title('All Titles (2023)', fontsize=20)
ax.set_xlabel('Rank', fontsize=20); ax.set_ylabel('Word Frequency', fontsize=20)
ax.text(0.05, 0.1, rf'$b = {b:.2f} \; [ {ci_b_lower:.2f} , \; {ci_b_upper:.2f} ]$', fontsize=20, weight='bold', transform=ax.transAxes)
ax.text(0.05, 0.2, rf'$a = {a:.2f} \; [ {ci_a_lower:.2f} , \; {ci_a_upper:.2f} ]$', fontsize=20, weight='bold', transform=ax.transAxes)
ax.text(0.05, 0.3, rf'$R^2= {r_squared(y, y_hat):.2f}$', fontsize=20, weight='bold', transform=ax.transAxes)

# Inset: a vs β
inset_ax = inset_axes(ax, width="30%", height="30%", loc='upper right', bbox_to_anchor=(-0.05, -0.05, 1, 1), bbox_transform=ax.transAxes)
sns.regplot(data=temp_Data1, x='Scaling_Exponent_Heaps_law', y='Scaling_Exponent_Zipf_Mandelbrot_law', scatter=False, ax=inset_ax, color='gray')
sns.scatterplot(data=temp_Data1, x='Scaling_Exponent_Heaps_law', y='Scaling_Exponent_Zipf_Mandelbrot_law', hue='Group', palette=group_colors, ax=inset_ax, legend=False)
inset_ax.set_title(r'$a$ vs. $\beta$', fontsize=10)
inset_ax.set_xlabel(r'$\beta$', fontsize=10)
inset_ax.set_ylabel(r'$a$', fontsize=10)
inset_ax.tick_params(axis='both', labelsize=8)

# === (2) Title 19 ===
ax = axs[0, 1]
title_num = 19
temp_data = Word_count_df.copy()
temp_data = temp_data[temp_data['title']!='All titles']
temp_data['title'] = temp_data['title'].apply(safe_to_int)
temp_data = temp_data[(temp_data['year']==year) & (temp_data['title']==title_num)]
y = temp_data['count'].sort_values(ascending=False).values
x = np.arange(1, len(y)+1)
x, y = x[y != 0], y[y != 0]
popt, pcov = curve_fit(zipf_mandelbrot, x, y, p0=[1e5, 1.0, 1.0], maxfev=10000)
C, b, a = popt
std_dev = np.sqrt(np.diag(pcov))
y_hat = zipf_mandelbrot(x, *popt)
ax.set_xscale('log'); ax.set_yscale('log')
ax.scatter(x, y, color='black', alpha=0.2, s=8)
ax.plot(x, y_hat, color='orange')
ax.set_title(f'Title {title_num}: {Title2Name[title_num]}', fontsize=20)
ax.set_xlabel('Rank', fontsize=20); ax.set_ylabel('Word Frequency', fontsize=20)
ax.text(0.05, 0.1, rf'$b = {b:.2f} \; [ {b - 1.96 * std_dev[1]:.2f} , \; {b + 1.96 * std_dev[1]:.2f} ]$', fontsize=20, weight='bold', transform=ax.transAxes)
ax.text(0.05, 0.2, rf'$a = {a:.2f} \; [ {a - 1.96 * std_dev[2]:.2f} , \; {a + 1.96 * std_dev[2]:.2f} ]$', fontsize=20, weight='bold', transform=ax.transAxes)
ax.text(0.6, 0.8, rf'$R^2= {r_squared(y, y_hat):.2f}$', fontsize=20, weight='bold', transform=ax.transAxes)

# === (3) Title 4 ===
ax = axs[1, 0]
title_num = 4
temp_data = Word_count_df.copy()
temp_data = temp_data[temp_data['title']!='All titles']
temp_data['title'] = temp_data['title'].apply(safe_to_int)
temp_data = temp_data[(temp_data['year']==year) & (temp_data['title']==title_num)]
y = temp_data['count'].sort_values(ascending=False).values
x = np.arange(1, len(y)+1)
x, y = x[y != 0], y[y != 0]
popt, pcov = curve_fit(zipf_mandelbrot, x, y, p0=[1e5, 1.0, 1.0], maxfev=10000)
C, b, a = popt
std_dev = np.sqrt(np.diag(pcov))
y_hat = zipf_mandelbrot(x, *popt)
ax.set_xscale('log'); ax.set_yscale('log')
ax.scatter(x, y, color='black', alpha=0.2, s=8)
ax.plot(x, y_hat, color='orange')
ax.set_title(f'Title {title_num}: Flag and Seal, ...', fontsize=20)
ax.set_xlabel('Rank', fontsize=20); ax.set_ylabel('Word Frequency', fontsize=20)
ax.text(0.05, 0.1, rf'$b = {b:.2f} \; [ {b - 1.96 * std_dev[1]:.2f} , \; {b + 1.96 * std_dev[1]:.2f} ]$', fontsize=20, weight='bold', transform=ax.transAxes)
ax.text(0.05, 0.2, rf'$a = {a:.2f} \; [ {a - 1.96 * std_dev[2]:.2f} , \; {a + 1.96 * std_dev[2]:.2f} ]$', fontsize=20, weight='bold', transform=ax.transAxes)
ax.text(0.6, 0.8, rf'$R^2= {r_squared(y, y_hat):.2f}$', fontsize=20, weight='bold', transform=ax.transAxes)

# === (4) Exponent over time ===
ax = axs[1, 1]
temp_Data1 = Data1.copy()
temp_Data1 = temp_Data1[temp_Data1['Year'] >= 1934]
temp_Data1 = temp_Data1[temp_Data1['Title'] != 'All titles']
temp_Data1['Title'] = temp_Data1['Title'].astype(int)
temp_Data1 = temp_Data1[~temp_Data1['Title'].isin([6, 34])]
for title in range(1, 51):
    sns.lineplot(data=temp_Data1[temp_Data1['Title'] == title], x='Year', y='Scaling_Exponent_Zipf_Mandelbrot_law',
                 ci=None, color=Title2Color[title], alpha=0.1, ax=ax)
sns.lineplot(data=Data1[Data1['Title'] == 'All titles'], x='Year', y='Scaling_Exponent_Zipf_Mandelbrot_law',
             marker='o', color='black', ax=ax)
ax.axhline(1, color='red', linestyle='dotted')
ax.axvline(1994, color='black', linestyle='dotted')
ax.set_title('Scaling Exponent ($a$) over Time', fontsize=20)
ax.set_xlabel('Year', fontsize=20); ax.set_ylabel('Zipf-Mandelbrot Exponent ($a$)', fontsize=20)
ax.set_xticks(years_DS1[1:] + [2006, 2012, 2018, 2023])
ax.set_xticklabels(years_DS1[1:] + [2006, 2012, 2018, 2023], rotation=90)
ax.legend().set_visible(False)
plt.savefig('./Figures/Figure 7.pdf', dpi=600, bbox_inches='tight')