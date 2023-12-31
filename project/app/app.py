import streamlit as st
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import seaborn as sns
import matplotlib.pyplot as plt

# Loading the data
df = pd.read_csv("project/app/games_dataset_clean.csv")
column_order = ['name', 'platform', 'release_year', 'genre(s)', 'score', 'opinion', 'developer', 'publisher', 'summary',
                'multiplayer', 'rating', 'link']
df = df[column_order]

# Page Layout
st.set_page_config(
    page_title="Video Game Data",
    page_icon=":bar_chart:",
    layout="wide",
)

search_term = st.sidebar.text_input("Search for a game by name:")

# Sidebar
st.sidebar.header("Apply filter:")

console = st.sidebar.multiselect(
    "Choose a platform:",
    options=df["platform"].unique(),
    default=df["platform"].unique()
)

year = st.sidebar.multiselect(
    "Choose a year of release:",
    options=df["release_year"].unique(),
    default=df["release_year"].unique()
)

genre = st.sidebar.multiselect(
    "Choose a genre:",
    options=df["genre(s)"].unique(),
    default=df["genre(s)"].unique()
)

df_selection = df.query(
    "(platform == @console) & (release_year == @year) & (`genre(s)` == @genre)"
)

if search_term:
    df_selection = df_selection[df_selection["name"].str.contains(search_term, case=False)]

# Main page
st.title(":video_game: Game Information")
st.markdown("##")

st.dataframe(df_selection)


# Graphs

def generate_genre_distribution():
    st.title(':bar_chart: Distribution of Games by Genre')

    sns.set(style="dark")
    genre_counts = df_selection['genre(s)'].str.split(', ').explode().value_counts()

    plt.figure(figsize=(12, 12))
    sns.barplot(x=genre_counts.values, y=genre_counts.index, orient='h')

    plt.xlabel('Number of Games')
    plt.ylabel('Genre')
    plt.title('Distribution of Games by Genre')

    for i, count in enumerate(genre_counts):
        plt.text(count, i, str(count), ha='left', va='center')

    plt.tight_layout()
    st.pyplot(plt)


if st.button("Show Genre distribution"):
    generate_genre_distribution()


def generate_year_distribution():
    st.title(':bar_chart: Distribution of Games by Release Year')
    release_years = df_selection['release_year'].dropna()

    plt.figure(figsize=(10, 6))
    sns.histplot(release_years, kde=True, bins=26, color='skyblue')

    plt.xlabel("Release Year")
    plt.ylabel("Number of Games")
    plt.title("Distribution of Game Releases Over Time")

    plt.tight_layout()
    st.pyplot(plt)


if st.button("Show Year distribution"):
    generate_year_distribution()


def generate_platform_distribution():
    st.title(':bar_chart: Distribution of Games by Platform')
    platform_counts = df_selection['platform'].value_counts()

    plt.figure(figsize=(12, 6))
    sns.barplot(x=platform_counts.index, y=platform_counts.values)

    plt.xlabel('Platform')
    plt.ylabel('Number of Games')
    plt.title('Distribution of Games by Platform')

    for i, count in enumerate(platform_counts):
        plt.text(i, count, str(count), ha='center', va='bottom')

    plt.xticks(rotation=45)
    plt.yticks([])

    plt.tight_layout()
    st.pyplot(plt, clear_figure=True)


if st.button("Show Platform distribution"):
    generate_platform_distribution()

# Model load

df_nlp = pd.read_csv("project/app/bag_of_words.csv")

count = CountVectorizer()
count_matrix = count.fit_transform(df_nlp['Bag_of_words'])


def recommend(title, df_nlp=df_nlp, count_matrix=count_matrix):
    # Calculate cosine similarity dynamically
    idx = df_nlp[df_nlp['name'] == title].index[0]
    cosine_sim = cosine_similarity(count_matrix[idx], count_matrix).flatten()

    # Get top 10 indices
    top_10_indices = cosine_sim.argsort()[:-11:-1]

    recommended_games = []
    for i in top_10_indices:
        game_name = df_nlp['name'].iloc[i]
        game_platform = df_nlp['platform'].iloc[i]
        recommended_games.append(f"{game_name} ({game_platform})")

    return recommended_games


# Search Bar

st.title(":magic_wand: Game Recommendation App")

game_name = st.text_input("Enter Game Name")

if st.button("Recommend a game !"):
    if game_name:
        result: object = recommend(game_name)
        st.write("Search Result :")
        for jeu in result:
            st.write(jeu)
    else:
        st.write("Please Enter a Game's Name.")
