import json

def calculate_score(data):
    # getting the scores from the data
    bitcoin_score = data.get("bitcoin_score", 0.0)
    crypto_score = data.get("crypto_score", 0.0)
    politics_score = data.get("politics_score", 0.0)
    war_macro_score = data.get("war_macro_score", 0.0)
    # calculating the final score with the given weights
    final_score = (0.4 * bitcoin_score) + (0.3 * crypto_score) + (0.15 * politics_score) + (0.15 * war_macro_score)
    return final_score
