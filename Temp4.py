import sys
from pulp import *

def readInput():
    num_teams, num_games_played = map(int, sys.stdin.readline().split())
    games_played = {}
    current_points = [0] * (num_teams + 1)

    for _ in range(num_games_played):
        home, visitor, result = map(int, sys.stdin.readline().split())
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

def minGamesWin(team_id, teams, current_points, remaining_games, max_wins):
    for t in range(1, teams + 1):
        if t == team_id: continue
        if current_points[t] >= (current_points[team_id] + 3 * max_wins[team_id]):
            return -1
        games_between = [(h, v) for h, v in remaining_games if (h == t or v == t) and (h != team_id and v != team_id)] #Check cause may be stupid
        max_points_t = current_points[t] + 3 * len(games_between)
        if max_points_t < current_points[team_id]:
            continue


    left, right = 0, max_wins[team_id]
    best_num_wins = -1

    while left <= right:
        mid = (left + right) // 2
        if teamCanWinWithWins(team_id, teams, current_points, remaining_games, mid):
            best_num_wins = mid
            right = mid - 1
        else:
            left = mid + 1

    return best_num_wins

def teamCanWinWithWins(team_id, teams, current_points, remaining_games, num_wins):
    # Max possible wins
    team_games = [(h, v) for h, v in remaining_games if h == team_id or v == team_id]
    if num_wins > len(team_games):
        return False

    prob = LpProblem(f"Team_{team_id}_can_win", LpMinimize)

    # Only two binary variables per game: home_win and draw
    win_home = {}
    draw = {}
    for h, v in remaining_games:
        win_home[(h,v)] = LpVariable(f"home_{h}_{v}", cat=LpBinary)
        draw[(h,v)] = LpVariable(f"draw_{h}_{v}", cat=LpBinary)
        # If both are 0 → visitor wins
        prob += win_home[(h,v)] + draw[(h,v)] <= 1

    # The team must win exactly num_wins games
    team_wins = []
    for h, v in team_games:
        if h == team_id:
            team_wins.append(win_home[(h,v)])
        else:  # visitor is the team
            team_wins.append(1 - win_home[(h,v)] - draw[(h,v)])
    prob += lpSum(team_wins) == num_wins

    # Calculate final points for each team
    final_points = {}
    for t in range(1, teams + 1):
        points = current_points[t]
        for h, v in remaining_games:
            if t == h:
                points += 3 * win_home[(h,v)] + 1 * draw[(h,v)]
            elif t == v:
                points += 3 * (1 - win_home[(h,v)] - draw[(h,v)]) + 1 * draw[(h,v)]
        final_points[t] = points

    # Team must tie or beat all other teams
    for t in range(1, teams + 1):
        if t != team_id:
            prob += final_points[team_id] >= final_points[t]

    # Dummy objective
    prob += lpSum([final_points[t] for t in range(1, teams + 1) if t != team_id])

    prob.solve(PULP_CBC_CMD(msg=0))
    return LpStatus[prob.status] == 'Optimal'

def main():
    teams, games_played, current_points = readInput()
    remaining_games = getRemainingGames(teams, games_played)

    max_wins = [0] * (teams + 1)
    # Games involving the team
    for t in range(1, teams + 1):
        team_games = [(h, v) for h, v in remaining_games if h == t or v == t]
        max_wins[t] = len(team_games)

    for team_id in range(1, teams + 1):
        print(minGamesWin(team_id, teams, current_points, remaining_games, max_wins))

main()
