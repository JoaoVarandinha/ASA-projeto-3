import sys
from pulp import *

def readInput():
    data = sys.stdin.read().strip().split('\n')
    if not data or not data[0].strip():
        return None, None, None
    
    num_teams, num_games_played = map(int, data[0].split())

    games_played = {}
    current_points = [0] * (num_teams + 1)

    for i in range(1, num_games_played + 1):
        home, visitor, result = map(int, data[i].split())
        games_played[(home, visitor)] = result

        if result == 0:
            current_points[home] += 1
            current_points[visitor] += 1
        elif result == home:
            current_points[home] += 3
        elif result == visitor:
            current_points[visitor] += 3
    
    return num_teams, games_played, current_points

def getRemainingGames(teams, games_played):
    remaining_games = []

    for i in range(1, teams + 1):
        for j in range(1, teams + 1):
            if i != j and (i,j) not in games_played:
                remaining_games.append((i, j))

    return remaining_games

def minGamesWin(team_id,teams, games_played, current_points, remaining_games):

    # Calculate the maximum number of games the team can still win
    max_wins = sum(1 for (home, visitor) in remaining_games if home == team_id or visitor == team_id)

    left, right = 0, max_wins
    best_num_wins = -1

    while left <= right:
        middle = (left + right) // 2
        if teamCanWinWithWins(team_id, teams, games_played, current_points, remaining_games, middle):
            best_num_wins = middle
            right = middle - 1
        else:
            left = middle + 1

    return best_num_wins  


def teamCanWinWithWins(team_id, teams, games_played, current_points, remaining_games, num_wins):
    # Create the LP problem
    prob = LpProblem(f"Team_{team_id}_can_win", LpMinimize)

    # Variables for game outcomes (home wins, visitor wins, draw)
    win = {}
    draw = {}

    for (home, visitor) in remaining_games:
        win[(home, visitor)] = LpVariable(f"win_home_{home}_{visitor}", cat = LpBinary)
        draw[(home, visitor)] = LpVariable(f"draw_{home}_{visitor}", cat = LpBinary)

        # Each game has exactly one outcome
        prob += win[(home, visitor)] + draw[(home, visitor)] <= 1

    # The team (team_id) must achieve exactly num_wins in the remaining games
    team_wins = lpSum([win[(home, visitor)] for (home, visitor) in remaining_games if home == team_id] +
                      [(1 - win[(home, visitor)] - draw[(home, visitor)]) for (home, visitor) in remaining_games if visitor == team_id])
    prob += team_wins >= num_wins

    # Calculate final points for each team
    final_team_points = {}

    for t in range(1, teams + 1):
        points = current_points[t]

        for (home, visitor) in remaining_games:
            if home == t:
                points += 3 * win[(home, visitor)] + draw[(home, visitor)]
            elif visitor == t:
                points += 3 * (1- win[(home, visitor)] - draw[(home, visitor)]) + draw[(home, visitor)]

        final_team_points[t] = points
    
    for t in range(1, teams + 1):
        if team_id != t:
            prob += final_team_points[team_id] >= final_team_points[t]

    # Minimize points of other teams (favorable scenario)
    #prob += lpSum([final_team_points[t] for t in range(1, teams + 1) if t != team_id])

    prob.solve(PULP_CBC_CMD(msg=0))

    # Check if the solution is optimal (feasible)
    return LpStatus[prob.status] == 'Optimal'



def main():
    teams, games_played, current_points = readInput()

    if teams is None:
        return
    
    remaining_games = getRemainingGames(teams, games_played)

    for team_id in range(1, teams + 1):
        result = minGamesWin(team_id, teams, games_played, current_points, remaining_games)
        print(result)

