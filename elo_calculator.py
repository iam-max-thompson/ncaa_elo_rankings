import pandas as pd
import numpy as np
from collections import Counter


df = pd.read_excel("ncaa_raw.xlsx")

print(df.head())

# Create a Counter to count player1 appearances
player_counter = Counter()


player_ratings = {}


# Iterate through the DataFrame rows and update player ratings
for index, row in df.iterrows():
    player1 = row["player1"]
    player2 = row["player2"]
    score1 = row["score1"]
    score2 = row["score2"]
    score1_difference = score1 - score2

    # Increment the count for player1
    player_counter[player1] += 1
    player_counter[player2] += 1

    max_games_played = 3

    # Check if players have ratings, and if not, initialize them to a default rating (e.g., 1000)
    if player1 not in player_ratings:
        player_ratings[player1] = 0
    if player2 not in player_ratings:
        player_ratings[player2] = 0

    expected_score1_difference = round(
        player_ratings[player1] - player_ratings[player2], 3
    )

    postgame_difference = abs(round(score1_difference - expected_score1_difference, 3))

    adjustment = round(
        # -0.381 + 1.33x + -0.0433x^2 + 4.86E-04x^3
        #      -0.0725 + 1.04x + -0.0303x^2 + 2.85E-04x^3
        -0.0725
        + (1.04 * postgame_difference)
        + -0.0303 * (postgame_difference**2)
        + 0.000285 * (postgame_difference**3),
        2,
    )

    if postgame_difference > 31:
        adjustment = 12

    # adjusting based on game number (not relevant yet):
    #  adjustment = adjustment * (
    #      (14 - player_counter[player1] - player_counter[player2]) / 12
    #  )
    # if the score difference is BIGGER than expected, player1 covered the spread
    if score1_difference - expected_score1_difference > 0:
        player1_adjustment = adjustment
        player2_adjustment = -adjustment
    # otherwise, they didn't and player2 covered the spread
    else:
        player1_adjustment = -adjustment
        player2_adjustment = adjustment

    # Update player ratings in the dictionary
    player_ratings[player1] = player_ratings[player1] + player1_adjustment
    player_ratings[player2] = player_ratings[player2] + player2_adjustment
    print(
        f"""{player1} had a rating advantage of {expected_score1_difference} over {player2}.
they scored a scoredifference of {score1_difference} which meant a performance of {round(score1_difference - expected_score1_difference,1)},
which means that the player1 adjustment was {player1_adjustment}
----------------------"""
    )


# Create a new DataFrame to store player ratings
ratings_df = pd.DataFrame(
    {"Player": list(player_ratings.keys()), "Rating": list(player_ratings.values())}
)

# Sort the DataFrame by rating in descending order
ratings_df = ratings_df.sort_values(by="Rating", ascending=False)

# Reset the index of the DataFrame
ratings_df.reset_index(drop=True, inplace=True)


# scaling to have mean of 0 and STDEV of 5
ratings_df["Rating"] = round(
    (
        (ratings_df["Rating"] - np.mean(ratings_df["Rating"]))
        / (np.std(ratings_df["Rating"]))
    )
    * 5,
    1,
)


# Print the final Elo ratings for players
print(ratings_df)
