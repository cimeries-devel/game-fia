import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 800
RADIUS = 30
LINE_WIDTH = 5

COLOR_BACKGROUND = (240, 240, 240)
COLOR_LINES = (0, 0, 0)
COLOR_PLAYER = (200, 0, 0)
COLOR_AI = (0, 200, 0)
COLOR_EMPTY = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Alinea en la I")

nodes = {
    0: {'pos': (WIDTH // 2 - 150, 100)},
    1: {'pos': (WIDTH // 2, 100)},
    2: {'pos': (WIDTH // 2 + 150, 100)},
    3: {'pos': (WIDTH // 2 - 150, 300)},
    4: {'pos': (WIDTH // 2, 300)},
    5: {'pos': (WIDTH // 2, 500)},
    6: {'pos': (WIDTH // 2 + 150, 500)},
    7: {'pos': (WIDTH // 2 - 150, 700)},
    8: {'pos': (WIDTH // 2, 700)},
    9: {'pos': (WIDTH // 2 + 150, 700)}
}

# Definir las conexiones (aristas) entre los nodos
edges = [
    (0, 1), (1, 2),       # Conexiones horizontales superiores
    (1, 4),               # Conexión vertical del centro superior
    (3, 4), (4, 5),       # Conexiones en la parte media
    (5, 6),               # Conexión horizontal inferior en la parte media
    (4, 8),               # Conexión vertical del centro inferior
    (7, 8), (8, 9)        # Conexiones horizontales inferiores
]

# Crear el grafo como un diccionario de listas de adyacencia
graph = {node: [] for node in nodes}
for edge in edges:
    a, b = edge
    graph[a].append(b)
    graph[b].append(a)
# Estado inicial del tablero (-1: vacío, 0: jugador, 1: IA)
board = {node: -1 for node in nodes}

PLAYER_TURN = 0
AI_TURN = 1
turn = PLAYER_TURN
game_over = False
placing_phase = True
selected_piece = None
player_pieces = 0
ai_pieces = 0


def draw_board():
    screen.fill(COLOR_BACKGROUND)
    for edge in edges:
        a, b = edge
        pygame.draw.line(screen, COLOR_LINES, nodes[a]['pos'], nodes[b]['pos'], LINE_WIDTH)
    for node in nodes:
        pos = nodes[node]['pos']
        state = board[node]
        if state == -1:
            color = COLOR_EMPTY
        elif state == 0:
            color = COLOR_PLAYER
        else:
            color = COLOR_AI
        pygame.draw.circle(screen, color, pos, RADIUS)


def get_clicked_node(pos):
    for node in nodes:
        node_pos = nodes[node]['pos']
        distance = ((pos[0] - node_pos[0]) ** 2 + (pos[1] - node_pos[1]) ** 2) ** 0.5
        if distance <= RADIUS:
            return node
    return None


def is_winner(player):
    top_row = [0, 1, 2]
    bottom_row = [7, 8, 9]
    return all(board[node] == player for node in top_row) or all(board[node] == player for node in bottom_row)


def valid_moves(node):
    return [neighbor for neighbor in graph[node] if board[neighbor] == -1]


def has_valid_moves(player):
    for node in board:
        if board[node] == player:
            if valid_moves(node):
                return True
    return False


def heuristic():
    # Contar fichas alineadas
    ia_aligned = sum(1 for node in [0, 1, 2] if board[node] == 1)
    player_aligned = sum(1 for node in [7, 8, 9] if board[node] == 0)

    # Contar movimientos disponibles
    ia_moves = sum(len(valid_moves(node)) for node in board if board[node] == 1)
    player_moves = sum(len(valid_moves(node)) for node in board if board[node] == 0)

    # Contar fichas bloqueadas
    ia_blocked = sum(1 for node in board if board[node] == 1 and not valid_moves(node))
    player_blocked = sum(1 for node in board if board[node] == 0 and not valid_moves(node))

    # Calcular puntaje
    score = (10 * ia_aligned - 10 * player_aligned +
             3 * ia_moves - 3 * player_moves -
             5 * ia_blocked + 5 * player_blocked)
    return score


def minimax(depth, maximizing):
    if depth == 0 or is_winner(1) or is_winner(0):
        return heuristic()
    if maximizing:
        max_eval = float('-inf')
        for node in board:
            if board[node] == 1:
                for move in valid_moves(node):
                    board[node], board[move] = -1, 1
                    eval = minimax(depth - 1, False)
                    board[move], board[node] = -1, 1
                    max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for node in board:
            if board[node] == 0:
                for move in valid_moves(node):
                    board[node], board[move] = -1, 0
                    eval = minimax(depth - 1, True)
                    board[move], board[node] = -1, 0
                    min_eval = min(min_eval, eval)
        return min_eval


def ai_place_piece():
    global ai_pieces
    best_score = float('-inf')
    best_move = None
    for node in board:
        if board[node] == -1:
            board[node] = 1
            score = minimax(3, False)
            board[node] = -1
            if score > best_score:
                best_score = score
                best_move = node
    if best_move is not None:
        board[best_move] = 1
        ai_pieces += 1


def ai_move():
    best_score = float('-inf')
    best_move = None
    for node in board:
        if board[node] == 1:
            for move in valid_moves(node):
                board[node], board[move] = -1, 1
                score = minimax(3, False)
                board[move], board[node] = -1, 1
                if score > best_score:
                    best_score = score
                    best_move = (node, move)
    if best_move is not None:
        from_node, to_node = best_move
        board[from_node], board[to_node] = -1, 1
        print(f"IA mueve de {from_node} a {to_node}")


while True:
    draw_board()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_over:
            if placing_phase:
                if turn == PLAYER_TURN:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        clicked_node = get_clicked_node(event.pos)
                        if clicked_node is not None and board[clicked_node] == -1:
                            board[clicked_node] = 0
                            player_pieces += 1
                            if player_pieces == 3 and ai_pieces == 3:
                                placing_phase = False
                            turn = AI_TURN
                elif turn == AI_TURN:
                    ai_place_piece()
                    if player_pieces == 3 and ai_pieces == 3:
                        placing_phase = False
                    turn = PLAYER_TURN
            else:
                if turn == PLAYER_TURN:
                    if not has_valid_moves(0):
                        print("Jugador no tiene movimientos válidos. Turno perdido.")
                        turn = AI_TURN
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        clicked_node = get_clicked_node(event.pos)
                        if clicked_node is not None:
                            if selected_piece is None and board[clicked_node] == 0:
                                selected_piece = clicked_node
                            elif selected_piece is not None and board[clicked_node] == -1:
                                if clicked_node in graph[selected_piece]:
                                    board[selected_piece], board[clicked_node] = -1, 0
                                    selected_piece = None
                                    if is_winner(0):
                                        print("¡Jugador gana!")
                                        game_over = True
                                    else:
                                        turn = AI_TURN
                elif turn == AI_TURN:
                    if not has_valid_moves(1):
                        print("IA no tiene movimientos válidos. Turno perdido.")
                        turn = PLAYER_TURN
                    else:
                        ai_move()
                        if is_winner(1):
                            print("¡IA gana!")
                            game_over = True
                        else:
                            turn = PLAYER_TURN
