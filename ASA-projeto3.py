import sys

def readInput():
    data = sys.stdin.read().strip.split('\n')
    if not data or not data[0].strip():
        return None, None
    
    num_teams, num_games_played = map(int, data[0].split())

    teams = num_teams
    games_played = {}
    current_points = [0] * teams

    for i in range(1, num_games_played + 1):
        home, visitor, result = map(int, data[i].split())
        games_played[(home, visitor)] = result

        if result == 1:
            current_points[home - 1] += 1
            current_points[visitor - 1] += 1
        elif result == home:
            current_points[home - 1] += 3
        elif result == visitor:
            current_points[visitor - 1] += 3
    
    return teams, games_played, current_points

def getRemainingGames(teams, games_played):
    remaining_games = []

    for i in range(1, teams + 1):
        for j in range(1, teams + 1):
            if i != j and (i,j) not in games_played:
                remaining_games.append((i, j))

    return remaining_games

def main():
    teams, games_played, current_ponits = readInput()

    if teams is None:
        return
    
    remaining_games = getRemainingGames(teams, games_played)