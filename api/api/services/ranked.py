def compute_elo(team, other):
    a_players = team.get_players()
    b_players = other.get_players()

    team_a_elo = sum([player.elo for player in a_players]) / len(a_players)
    team_b_elo = sum([player.elo for player in b_players]) / len(b_players)

    if team_a_elo < 2100:
        k_a = 32
    elif team_a_elo < 2400:
        k_a = 24
    else:
        k_a = 16

    e_a = 1 / (1 + (10 ** ((team_b_elo - team_a_elo) / 400)))
    a_win_rating = k_a * (1 - e_a)
    a_loose_rating = k_a * (0 - e_a)
    return int(round(a_win_rating)), abs(int(round(a_loose_rating)))
