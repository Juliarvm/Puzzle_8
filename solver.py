from collections import deque
import heapq
import math

GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0]

MOVES = {
    0: [1, 3],
    1: [0, 2, 4],
    2: [1, 5],
    3: [0, 4, 6],
    4: [1, 3, 5, 7],
    5: [2, 4, 8],
    6: [3, 7],
    7: [4, 6, 8],
    8: [5, 7]
}

def index_to_move(i1, i2):
    diff = i2 - i1
    if diff == -3: return "up"
    if diff == 3: return "down"
    if diff == -1: return "left"
    if diff == 1: return "right"

def manhattan(state):
    distance = 0
    for i, tile in enumerate(state):
        if tile == 0:
            continue
        goal_index = GOAL.index(tile)
        distance += abs(i // 3 - goal_index // 3) + abs(i % 3 - goal_index % 3)
    return distance

def euclidean(state):
    distance = 0
    for i, tile in enumerate(state):
        if tile == 0:
            continue
        goal_index = GOAL.index(tile)
        dx = (i % 3) - (goal_index % 3)
        dy = (i // 3) - (goal_index // 3)
        distance += math.sqrt(dx*dx + dy*dy)
    return distance

def apply_move(state, move):
    state = list(state)
    zero_index = state.index(0)

    if move == "up" and zero_index >= 3:
        swap_with = zero_index - 3
    elif move == "down" and zero_index <= 5:
        swap_with = zero_index + 3
    elif move == "left" and zero_index % 3 != 0:
        swap_with = zero_index - 1
    elif move == "right" and zero_index % 3 != 2:
        swap_with = zero_index + 1
    else:
        return state

    state[zero_index], state[swap_with] = state[swap_with], state[zero_index]
    return state

def reconstruct_path(start_flat, path):
    states = [start_flat]
    current = start_flat[:]
    for move in path:
        current = apply_move(current, move)
        states.append(current[:])
    return [to_grid(state) for state in states]

def to_grid(state):
    return [state[i:i+3] for i in range(0, 9, 3)]

def resolucao(start_state, algoritmo="A*", heuristica="Manhattan"):
    flat_start = sum(start_state, []) 
    start = tuple(flat_start)
    visited = set()
    g_score = {start: 0}
    if heuristica is None:
        heuristica = "Manhattan"

    if heuristica.lower() == "euclidiana":
        h_func = euclidean
    else:
        h_func = manhattan

    h_start = h_func(start)

    if algoritmo == "Largura":
        frontier = deque([(start, [])])
    else:
        frontier = []
        priority = h_start if algoritmo == "Busca Gulosa" else g_score[start] + h_start
        heapq.heappush(frontier, (priority, start, []))

    while frontier:
        if algoritmo == "Largura":
            state, path = frontier.popleft()
        else:
            _, state, path = heapq.heappop(frontier)

        if list(state) == GOAL:
            return reconstruct_path(flat_start, path)

        visited.add(state)
        zero_index = state.index(0)

        for neighbor in MOVES[zero_index]:
            new_state = list(state)
            new_state[zero_index], new_state[neighbor] = new_state[neighbor], new_state[zero_index]
            new_tuple = tuple(new_state)

            if new_tuple in visited:
                continue

            move = index_to_move(zero_index, neighbor)
            new_path = path + [move]

            if algoritmo == "Largura":
                frontier.append((new_tuple, new_path))
            else:
                g = g_score[state] + 1
                h = h_func(new_tuple)
                g_score[new_tuple] = g
                priority = h if algoritmo == "Busca Gulosa" else g + h
                heapq.heappush(frontier, (priority, new_tuple, new_path))

    return []