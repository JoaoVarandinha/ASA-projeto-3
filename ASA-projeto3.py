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
            if i != j and (i, j) not in games_played:
                remaining_games.append((i, j))
    return remaining_games


def minGamesWin(team_id, teams, current_points, remaining_games, max_wins):
    # ---------- PRUNING ----------
    for t in range(1, teams + 1):
        if t == team_id:
            continue
        if current_points[t] > current_points[team_id] + 3 * max_wins[team_id]:
            return -1

    # ---------- BINARY SEARCH ----------
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
    team_games = [(h, v) for h, v in remaining_games if h == team_id or v == team_id]
    if num_wins > len(team_games):
        return False

    prob = LpProblem(f"Team_{team_id}_can_win", LpMinimize)

    # 2 binary variables per game: home win / draw (0,0 = visitor win)
    win_home = {}
    draw = {}
    for h, v in remaining_games:
        win_home[(h, v)] = LpVariable(f"home_{h}_{v}", cat=LpBinary)
        draw[(h, v)] = LpVariable(f"draw_{h}_{v}", cat=LpBinary)
        prob += win_home[(h, v)] + draw[(h, v)] <= 1  # visitor wins if both 0

    # Constraint: team_id wins exactly num_wins
    team_wins_expr = []
    for h, v in team_games:
        if h == team_id:
            team_wins_expr.append(win_home[(h, v)])
        else:
            team_wins_expr.append(1 - win_home[(h, v)] - draw[(h, v)])
    prob += lpSum(team_wins_expr) == num_wins

    # Final points
    final_points = {}
    for t in range(1, teams + 1):
        points = current_points[t]
        for h, v in remaining_games:
            if t == h:
                points += 3 * win_home[(h, v)] + draw[(h, v)]
            elif t == v:
                points += 3 * (1 - win_home[(h, v)] - draw[(h, v)]) + draw[(h, v)]
        final_points[t] = points

    # Constraint: team_id must have at least as many points as everyone else
    for t in range(1, teams + 1):
        if t != team_id:
            prob += final_points[team_id] >= final_points[t]

    # Dummy objective
    prob += lpSum(final_points[t] for t in range(1, teams + 1) if t != team_id)

    prob.solve(PULP_CBC_CMD(msg=0))
    return LpStatus[prob.status] == 'Optimal'


def main():
    teams, games_played, current_points = readInput()
    remaining_games = getRemainingGames(teams, games_played)

    max_wins = [0] * (teams + 1)
    for t in range(1, teams + 1):
        max_wins[t] = sum(1 for h, v in remaining_games if h == t or v == t)

    for team_id in range(1, teams + 1):
        print(minGamesWin(team_id, teams, current_points, remaining_games, max_wins))


main()