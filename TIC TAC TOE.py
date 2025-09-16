import random

def display_board(board):
    
    print('   |   |')
    print(f' {board[7]} | {board[8]} | {board[9]} ')
    print('   |   |')
    print('-----------')
    print('   |   |')
    print(f' {board[4]} | {board[5]} | {board[6]} ')
    print('   |   |')
    print('-----------')
    print('   |   |')
    print(f' {board[1]} | {board[2]} | {board[3]} ')
    print('   |   |')

def player_input():
    marker = ''
    while marker not in ['X', 'O']:
        marker = input('Player 1, X or O: ').upper()
    if marker == 'X':
        return ('X', 'O')
    else:
        return ('O', 'X')

def place_marker(board, marker, position):
    board[position] = marker

def win_check(board, mark):
    return ((board[1] == board[2] == board[3] == mark) or
            (board[4] == board[5] == board[6] == mark) or
            (board[7] == board[8] == board[9] == mark) or
            (board[1] == board[4] == board[7] == mark) or
            (board[2] == board[5] == board[8] == mark) or
            (board[3] == board[6] == board[9] == mark) or
            (board[1] == board[5] == board[9] == mark) or
            (board[7] == board[5] == board[3] == mark))

def choose_first():
    return 'Player1' if random.randint(0, 1) == 0 else 'Player2'

def space_check(board, position):
    return board[position] == ' '

def full_board_check(board):
    for i in range(1, 10):
        if space_check(board,i):
            return False
    return True

def player_choice(board):
    position = 0
    while True:
        try:
            position = int(input('Choose your position (1-9): '))
            if position in range(1, 10):
                if space_check(board, position):
                    return position
                else:
                    print("That position is already taken. Choose another.")
            else:
                print("Invalid position. Choose a number between 1 and 9.")
        except ValueError:
            print("Please enter a valid number (1-9).")


def replay():
    choice = input('Play again? (Y/N): ').upper()
    return choice == 'Y'


print('Welcome to tic tac toe')

print('The table will be looking like this and will be used like a numpad to fill the users given choice')
print('7 | 8 | 9')
print('4 | 5 | 6')
print('1 | 2 | 3')
print('Please fill according to this sequence')


while True:
    
    the_board = [' '] * 10
    player1_marker, player2_marker = player_input()
    turn = choose_first()
    print(turn + " will go first")

    play_game = input('Ready to play? (Y/N): ').lower()
    game_on = play_game == 'y'

    while game_on:
        if turn == 'Player1':
            display_board(the_board)
            position = player_choice(the_board)
            place_marker(the_board, player1_marker, position)

            if win_check(the_board, player1_marker):
                display_board(the_board)
                print('Player 1 has won')
                game_on = False
            else:
                if full_board_check(the_board):
                    display_board(the_board)
                    print('tie')
                    game_on = False
                else:
                    turn = 'Player2'

        else:  
            display_board(the_board)
            position = player_choice(the_board)
            place_marker(the_board, player2_marker, position)

            if win_check(the_board, player2_marker):
                display_board(the_board)
                print('Player 2 has won')
                game_on = False
            else:
                if full_board_check(the_board):
                    display_board(the_board)
                    print('tie')
                    game_on = False
                else:
                    turn = 'Player1'

    if not replay():
        print("Thanks for playing")
        break

                    























