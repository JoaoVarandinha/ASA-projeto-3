#!/usr/bin/env python3
"""
ASA Project 3: Calculate the minimum number of wins necessary to win the championship
using Linear Programming (PuLP).

The problem consists of determining, for each team, the minimum number of games
they need to win to still be able to win the championship.
"""

import sys
from pulp import LpMinimize, LpMaximize, LpProblem, LpVariable, lpSum, LpStatus, LpInteger, LpBinary
from collections import defaultdict


def read_input():
    data = sys.stdin.read().strip().split('\n')
    # Check if there is valid data (not just empty strings after split)
    if not data or not data[0].strip():
        return None, None, None
    
    # First line: number of teams and games already played
    num_teams, num_games_played = map(int, data[0].split())
    
    # Initialize data structure
    teams = num_teams
    games_played = {}
    current_points = [0] * (teams + 1)  # Index 0 not used, teams indexed from 1 to num_teams
    
    # Read results of games already played
    for i in range(1, num_games_played + 1):
        home, visitor, result = map(int, data[i].split())
        games_played[(home, visitor)] = result
        
        # Update points
        if result == 0:
            # Draw
            current_points[home] += 1
            current_points[visitor] += 1
        elif result == home:
            # Home team won
            current_points[home] += 3
        elif result == visitor:
            # Visiting team won
            current_points[visitor] += 3
    
    return teams, games_played, current_points


def get_remaining_games(teams, games_played):
    remaining = []
    for i in range(1, teams + 1):
        for j in range(1, teams + 1):
            if i != j:
                # Each team plays with each other twice (home and away)
                if (i, j) not in games_played:
                    remaining.append((i, j))
    return remaining


def solve_for_team(team_id, teams, games_played, current_points, remaining_games):

    # Calculate the maximum number of possible wins for the team
    max_wins = sum(1 for (i, j) in remaining_games if i == team_id or j == team_id)
    
    # Binary search to find the minimum number of wins
    left, right = 0, max_wins
    best = -1
    
    while left <= right:
        mid = (left + right) // 2
        if can_win_with_wins(team_id, teams, games_played, current_points, remaining_games, mid):
            best = mid
            right = mid - 1  # Try with fewer wins
        else:
            left = mid + 1  # Needs more wins
    
    return best


def can_win_with_wins(team_id, teams, games_played, current_points, remaining_games, target_wins):

    # Create problem: check if there exists a favorable scenario where the team can win
    # We minimize points of other teams (favorable scenario)
    prob = LpProblem(f"Team_{team_id}_can_win", LpMinimize)
    
    # Decision variables: for each remaining game
    win_home = {}
    win_away = {}
    draw = {}
    
    # Create variables and add constraint: each game has exactly one result
    for (i, j) in remaining_games:
        win_home[(i, j)] = LpVariable(f"win_home_{i}_{j}", cat=LpBinary)
        win_away[(i, j)] = LpVariable(f"win_away_{i}_{j}", cat=LpBinary)
        draw[(i, j)] = LpVariable(f"draw_{i}_{j}", cat=LpBinary)
        prob += win_home[(i, j)] + win_away[(i, j)] + draw[(i, j)] == 1
    
    # Constraint: the team must win exactly target_wins games
    team_wins = lpSum([win_home[(i, j)] for (i, j) in remaining_games if i == team_id] +
                      [win_away[(i, j)] for (i, j) in remaining_games if j == team_id])
    prob += team_wins == target_wins
    
    # Calculate final points of each team
    final_points = {}
    for t in range(1, teams + 1):
        points = current_points[t]
        
        for (i, j) in remaining_games:
            if i == t:
                points += 3 * win_home[(i, j)] + 1 * draw[(i, j)]
            elif j == t:
                points += 3 * win_away[(i, j)] + 1 * draw[(i, j)]
        
        final_points[t] = points
    
    # Add constraints: to win the team must have at least as many points as any other team
    for t in range(1, teams + 1):
        if t != team_id:
            prob += final_points[team_id] >= final_points[t]
    
    # Objective: any objective works, we just want to verify feasibility
    # Minimize points of other teams (favorable scenario)
    prob += lpSum([final_points[t] for t in range(1, teams + 1) if t != team_id])
    
    # Solve the problem
    prob.solve()
    
    # Check if a feasible solution was found
    return LpStatus[prob.status] == 'Optimal'


def main():
    """Main function."""
    teams, games_played, current_points = read_input()
    
    if teams is None:
        return
    
    # Get games yet to be played
    remaining_games = get_remaining_games(teams, games_played)
    
    # Solve for each team
    results = []
    for team_id in range(1, teams + 1):
        min_wins = solve_for_team(team_id, teams, games_played, current_points, remaining_games)
        results.append(min_wins)
    
    # Output
    for result in results:
        print(result)

