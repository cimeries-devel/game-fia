import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 600, 800
RADIUS = 30
LINE_WIDTH = 5
COLOR_BACKGROUND = (255, 255, 255)
COLOR_LINES = (0, 0, 0)
COLOR_PLAYER = (200, 0, 0)
COLOR_AI = (0, 200, 0)
COLOR_EMPTY = (240, 240, 240)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Group 3")

VERTICES = [
    (WIDTH // 2 - 150, 100), (WIDTH // 2, 100), (WIDTH // 2 + 150, 100),
    (WIDTH // 2 - 150, 300), (WIDTH // 2, 300),
    (WIDTH // 2, 500), (WIDTH // 2 + 150, 500),
    (WIDTH // 2 - 150, 700), (WIDTH // 2, 700), (WIDTH // 2 + 150, 700)
]

CONNECTIONS = [
    (0, 1), (1, 2),
    (1, 4),
    (3, 4), (4, 5), (5, 6),
    (4, 8),
    (7, 8), (8, 9)
]

board = [-1] * len(VERTICES)
PLAYER_TURN = 0
AI_TURN = 1
turn = PLAYER_TURN
game_over = False
player_pieces = 0
ai_pieces = 0
selected_piece = None


def draw_board():
    screen.fill(COLOR_BACKGROUND)
    for conn in CONNECTIONS:
        pygame.draw.line(screen, COLOR_LINES, VERTICES[conn[0]], VERTICES[conn[1]], LINE_WIDTH)
    for i, pos in enumerate(VERTICES):
        if board[i] == -1:
            pygame.draw.circle(screen, COLOR_EMPTY, pos, RADIUS)
        elif board[i] == 0:
            pygame.draw.circle(screen, COLOR_PLAYER, pos, RADIUS)
        elif board[i] == 1:
            pygame.draw.circle(screen, COLOR_AI, pos, RADIUS)


def get_clicked_vertex(pos):
    for i, vertex in enumerate(VERTICES):
        if math.dist(pos, vertex) <= RADIUS:
            return i
    return None


def is_winner(player):
    return (
        all(board[i] == player for i in [0, 1, 2]) or
        all(board[i] == player for i in [7, 8, 9])
    )


def evaluate():
    if is_winner(1):
        return 10
    elif is_winner(0):
        return -10
    return 0


def minimax(depth, maximizing):
    score = evaluate()
    if score == 10 or score == -10:
        return score
    if all(b != -1 for b in board):
        return 0

    if maximizing:
        max_eval = -math.inf
        for i in range(len(board)):
            if board[i] == -1:
                board[i] = 1
                eval = minimax(depth - 1, False)
                board[i] = -1
                max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = math.inf
        for i in range(len(board)):
            if board[i] == -1:
                board[i] = 0
                eval = minimax(depth - 1, True)
                board[i] = -1
                min_eval = min(min_eval, eval)
        return min_eval


def ai_move():
    global ai_pieces
    best_move = None
    best_score = -math.inf

    for i in range(len(board)):
        if board[i] == -1:
            board[i] = 1
            score = minimax(3, False)
            board[i] = -1
            if score > best_score:
                best_score = score
                best_move = i

    if best_move is not None:
        if ai_pieces < 3:
            board[best_move] = 1
            ai_pieces += 1
        else:
            for j in range(len(board)):
                if board[j] == 1:
                    for conn in CONNECTIONS:
                        if conn[0] == j and conn[1] == best_move:
                            board[j] = -1
                            board[best_move] = 1
                            return


while True:
    draw_board()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if not game_over:
            if turn == PLAYER_TURN and event.type == pygame.MOUSEBUTTONDOWN:
                clicked_vertex = get_clicked_vertex(event.pos)
                if clicked_vertex is not None:
                    if player_pieces < 3 and board[clicked_vertex] == -1:
                        board[clicked_vertex] = 0
                        player_pieces += 1
                        if is_winner(0):
                            print("Player wins!")
                            game_over = True
                        else:
                            turn = AI_TURN
                    elif player_pieces == 3:
                        if selected_piece is None and board[clicked_vertex] == 0:
                            selected_piece = clicked_vertex
                        elif selected_piece is not None and board[clicked_vertex] == -1:
                            for conn in CONNECTIONS:
                                if (conn[0] == selected_piece and conn[1] == clicked_vertex) or \
                                (conn[1] == selected_piece and conn[0] == clicked_vertex):
                                    board[selected_piece] = -1
                                    board[clicked_vertex] = 0
                                    selected_piece = None
                                    if is_winner(0):
                                        print("Player wins!")
                                        game_over = True
                                    else:
                                        turn = AI_TURN
                                    break

            if turn == AI_TURN and not game_over:
                ai_move()
                if is_winner(1):
                    print("AI wins!")
                    game_over = True
                else:
                    turn = PLAYER_TURN
