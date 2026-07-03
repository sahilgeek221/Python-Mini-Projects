import pygame
import random
import sys
import os
import time

# --- CORE GAME LOGIC CLASSES ---
suits = ('Hearts', 'Diamonds', 'Spades', 'Clubs')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
values = {'Two':2, 'Three':3, 'Four':4, 'Five': 5, 'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10, 'Jack': 10, 'Queen': 10, 'King': 10, 'Ace': 11 }

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f'{self.rank} of {self.suit}'

class Deck:
    def __init__(self):
        self.build_deck()

    def build_deck(self):
        self.deck = [Card(suit, rank) for suit in suits for rank in ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self):
        if len(self.deck) < 10:  
            print("-- Reshuffling the deck --")
            self.build_deck()
        return self.deck.pop()

class Hand:
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_card(self, card):
        self.cards.append(card)
        self.value += values[card.rank]
        if card.rank == 'Ace':
            self.aces += 1
        self.adjust_for_ace()

    def adjust_for_ace(self):
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1

def calculate_denominations(total_budget):
    if total_budget >= 10000: return [10000, 1000, 500, 100, 50]
    elif total_budget >= 1000: return [1000, 500, 100, 50, 10]
    elif total_budget >= 100: return [100, 25, 10, 5, 1]
    else: return [50, 25, 10, 5, 1]

class Chips:
    def __init__(self, total):
        self.total = total
        self.bet = 0
        self.denominations = calculate_denominations(self.total)
        self.inventory = {d: 0 for d in self.denominations}
        self._breakdown_chips(self.total)

    def _breakdown_chips(self, amount):
        self.inventory = {d: 0 for d in self.denominations}
        remaining = amount
        for i in range(len(self.denominations) - 1, 0, -1): 
            denom = self.denominations[i]
            if remaining >= denom * 5:
                self.inventory[denom] += 5
                remaining -= denom * 5
        for denom in self.denominations:
            if remaining >= denom:
                count = remaining // denom
                self.inventory[denom] += count
                remaining %= denom

    def add_to_bet(self, amount):
        if self.inventory.get(amount, 0) > 0:
            self.inventory[amount] -= 1
            self.bet += amount
            self.total -= amount
            return True
        return False

    def clear_bet(self):
        self.total += self.bet
        self.bet = 0
        self._breakdown_chips(self.total)

    def resolve_bet(self, result):
        if result == 'win':
            self.total += self.bet * 2
        elif result == 'push':
            self.total += self.bet
        self.bet = 0
        self._breakdown_chips(self.total)

class Player:
    def __init__(self, name, budget):
        self.name = name
        self.chips = Chips(budget)
        self.hand = None
        self.status = "playing"
        self.round_result = ""

# --- PYGAME UI CLASSES ---
pygame.init()
font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 16)
title_font = pygame.font.SysFont("arial", 36, bold=True)

class TextBox:
    def __init__(self, x, y, w, h, text='', numeric_only=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (255, 255, 255)
        self.text = text
        self.active = False
        self.numeric_only = numeric_only

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if self.numeric_only and not event.unicode.isnumeric():
                    return
                self.text += event.unicode

    def draw(self, screen):
        color = (200, 255, 200) if self.active else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        txt_surface = font.render(self.text, True, (0, 0, 0))
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))
        
        if self.active:
            if time.time() % 1 > 0.5:
                cursor_x = self.rect.x + 5 + txt_surface.get_width()
                pygame.draw.line(screen, (0, 0, 0), (cursor_x, self.rect.y + 5), (cursor_x, self.rect.y + 35), 2)

# --- GRAPHICS HELPERS ---
WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("Multiplayer Blackjack")

CASINO_GREEN = (35, 120, 65)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

card_positions = {}

def get_anim_pos(card_id, target_x, target_y):
    if card_id not in card_positions:
        card_positions[card_id] = {'x': 100, 'y': 100, 'target_x': target_x, 'target_y': target_y}
    else:
        card_positions[card_id]['target_x'] = target_x
        card_positions[card_id]['target_y'] = target_y
    
    card_positions[card_id]['x'] += (card_positions[card_id]['target_x'] - card_positions[card_id]['x']) * 0.15
    card_positions[card_id]['y'] += (card_positions[card_id]['target_y'] - card_positions[card_id]['y']) * 0.15
    
    return card_positions[card_id]['x'], card_positions[card_id]['y']

def draw_shoe(screen):
    shoe_rect = pygame.Rect(50, 40, 110, 150)
    pygame.draw.rect(screen, (20, 20, 20), shoe_rect, border_radius=10)
    pygame.draw.polygon(screen, (35, 35, 35), [(50, 190), (160, 190), (160, 110), (50, 110)]) 
    pygame.draw.rect(screen, (200, 50, 50), (120, 130, 30, 60), border_radius=5)
    pygame.draw.rect(screen, WHITE, (125, 135, 20, 50), border_radius=3)
    pygame.draw.rect(screen, BLACK, shoe_rect, 3, border_radius=10)

def draw_card(screen, card_name, x, y):
    formatted_name = card_name.replace(' ', '_').lower()
    
    word_to_num = {
        'two': '2', 'three': '3', 'four': '4', 'five': '5', 
        'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10'
    }
    for word, num in word_to_num.items():
        if formatted_name.startswith(word + '_'):
            formatted_name = formatted_name.replace(word, num, 1) 
            break
            
    base_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(base_path, "images", f"{formatted_name}.png")
    
    if not hasattr(draw_card, "missing_printed"):
        draw_card.missing_printed = set()
    
    if os.path.exists(image_path):
        card_img = pygame.image.load(image_path).convert_alpha()
        card_img = pygame.transform.scale(card_img, (100, 145))
        screen.blit(card_img, (x, y))
    else:
        if formatted_name not in draw_card.missing_printed:
            print(f"ERROR: Could not find image at -> {image_path}")
            draw_card.missing_printed.add(formatted_name)
            
        card_rect = pygame.Rect(x, y, 100, 145)
        pygame.draw.rect(screen, WHITE, card_rect)
        pygame.draw.rect(screen, BLACK, card_rect, 2)
        
        if card_name != "Hidden":
            text_color = (200, 0, 0) if "Hearts" in card_name or "Diamonds" in card_name else BLACK
            parts = card_name.split(" ")
            if len(parts) == 3:
                screen.blit(small_font.render(parts[0], True, text_color), (x + 5, y + 5))
                screen.blit(small_font.render(parts[2], True, text_color), (x + 5, y + 25))

def get_chip_color(value):
    colors = {10: (50, 150, 255), 25: (50, 200, 50), 50: (50, 150, 255), 100: (200, 50, 50), 500: (150, 50, 200), 1000: (255, 165, 0), 10000: (50, 50, 50)}
    return colors.get(value, (100, 100, 100))

def draw_chip_button(screen, x, y, value, count):
    color = get_chip_color(value)
    pygame.draw.circle(screen, color, (x, y), 35)
    pygame.draw.circle(screen, WHITE, (x, y), 35, 2)
    val_text = font.render(str(value), True, WHITE)
    screen.blit(val_text, val_text.get_rect(center=(x, y)))
    count_text = small_font.render(f"x{count}", True, GOLD)
    screen.blit(count_text, count_text.get_rect(center=(x, y + 45)))
    return pygame.Rect(x - 35, y - 35, 70, 70)

# --- MAIN LOOP ---
def main():
    clock = pygame.time.Clock()
    state = "HOME"
    next_state = "HOME"
    
    players = []
    current_player_idx = 0
    deck = Deck()
    dealer_hand = None
    payouts_resolved = False
    overall_winner = None
    
    name_box = TextBox(400, 200, 200, 40, "Player 1")
    budget_box = TextBox(400, 270, 200, 40, "10000", numeric_only=True)
    add_player_rect = pygame.Rect(400, 350, 200, 50)
    start_game_rect = pygame.Rect(400, 420, 200, 50)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # --- 1. NON-EVENT GAME LOGIC ---
        if state == "DEALER_TURN":
            while dealer_hand.value < 17:
                dealer_hand.add_card(deck.deal())
            state = "ROUND_OVER"

        if state == "ROUND_OVER" and not payouts_resolved:
            dealer_val = dealer_hand.value
            dealer_busted = dealer_val > 21

            for p in players:
                if p.status == "bankrupt":
                    continue
                    
                pot = p.chips.bet
                if p.status == "busted":
                    p.chips.resolve_bet("lose")
                    p.round_result = f"Dealer takes ${pot} (Bust)"
                elif dealer_busted:
                    p.chips.resolve_bet("win")
                    p.round_result = f"{p.name} wins ${pot * 2}!"
                elif p.hand.value > dealer_val:
                    p.chips.resolve_bet("win")
                    p.round_result = f"{p.name} wins ${pot * 2}!"
                elif p.hand.value < dealer_val:
                    p.chips.resolve_bet("lose")
                    p.round_result = f"Dealer takes ${pot}"
                else:
                    p.chips.resolve_bet("push")
                    p.round_result = "Push - Bet returned"
                
                # Check for bankruptcy right after resolving
                if p.chips.total <= 0:
                    p.round_result += " - BANKRUPT!"
                    p.status = "bankrupt"
                    
            payouts_resolved = True

        # --- 2. EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                can_exit = state in ["HOME", "BETTING", "ROUND_OVER", "GAME_OVER"]
                exit_rect = pygame.Rect(825, HEIGHT - 70, 150, 40)
                if can_exit and exit_rect.collidepoint(mouse_pos):
                    running = False
            
            if state == "HOME":
                name_box.handle_event(event)
                budget_box.handle_event(event)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if add_player_rect.collidepoint(mouse_pos):
                        if budget_box.text != "":
                            budget = int(budget_box.text)
                            players.append(Player(name_box.text, budget))
                            name_box.text = f"Player {len(players) + 1}"
                            
                    if start_game_rect.collidepoint(mouse_pos) and len(players) > 0:
                        state = "TRANSITION"
                        next_state = "BETTING"
                        if len(players) == 1:
                            state = "BETTING"

            elif state == "TRANSITION":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    state = next_state 

            elif state == "BETTING":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    p = players[current_player_idx]
                    
                    start_x = 70
                    for value in reversed(p.chips.denominations):
                        chip_rect = pygame.Rect(start_x - 35, 600 - 35, 70, 70)
                        if chip_rect.collidepoint(mouse_pos):
                            p.chips.add_to_bet(value)
                        start_x += 90
                    
                    clear_rect = pygame.Rect(480, 580, 120, 40)
                    if clear_rect.collidepoint(mouse_pos):
                        p.chips.clear_bet()

                    done_rect = pygame.Rect(620, 580, 140, 40)
                    if done_rect.collidepoint(mouse_pos) and p.chips.bet > 0:
                        current_player_idx += 1
                        
                        # Skip players who are bankrupt
                        while current_player_idx < len(players) and players[current_player_idx].status == "bankrupt":
                            current_player_idx += 1
                            
                        if current_player_idx >= len(players):
                            dealer_hand = Hand()
                            for _ in range(2):
                                dealer_hand.add_card(deck.deal())
                                for player in players:
                                    if player.status != "bankrupt":
                                        player.hand = Hand()
                                        player.hand.add_card(deck.deal())
                            
                            # Find the first active player for the playing phase
                            current_player_idx = 0
                            while current_player_idx < len(players) and players[current_player_idx].status == "bankrupt":
                                current_player_idx += 1
                            
                            active_players = [p for p in players if p.status != "bankrupt"]
                            if len(active_players) > 1:
                                state = "TRANSITION"
                                next_state = "PLAYING"
                            else:
                                state = "PLAYING"
                        else:
                            active_players = [p for p in players if p.status != "bankrupt"]
                            if len(active_players) > 1:
                                state = "TRANSITION"
                                next_state = "BETTING"
                            else:
                                state = "BETTING"

            elif state == "PLAYING":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    current_p = players[current_player_idx]
                    
                    hit_rect = pygame.Rect(300, 530, 100, 40)
                    stand_rect = pygame.Rect(420, 530, 100, 40)
                    
                    if hit_rect.collidepoint(mouse_pos):
                        current_p.hand.add_card(deck.deal())
                        if current_p.hand.value > 21:
                            current_p.status = "busted"
                            state = "BUSTED_WAIT"

                    elif stand_rect.collidepoint(mouse_pos):
                        current_p.status = "stood"
                        current_player_idx += 1
                        
                        # Skip bankrupt players
                        while current_player_idx < len(players) and players[current_player_idx].status == "bankrupt":
                            current_player_idx += 1
                            
                        if current_player_idx >= len(players):
                            state = "DEALER_TURN"
                        else:
                            active_players = [p for p in players if p.status != "bankrupt"]
                            if len(active_players) > 1:
                                state = "TRANSITION"
                                next_state = "PLAYING"
                            else:
                                state = "PLAYING"

            elif state == "BUSTED_WAIT":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    current_player_idx += 1
                    
                    # Skip bankrupt players
                    while current_player_idx < len(players) and players[current_player_idx].status == "bankrupt":
                        current_player_idx += 1
                        
                    if current_player_idx >= len(players):
                        state = "DEALER_TURN"
                    else:
                        active_players = [p for p in players if p.status != "bankrupt"]
                        if len(active_players) > 1:
                            state = "TRANSITION"
                            next_state = "PLAYING"
                        else:
                            state = "PLAYING"
                            
            elif state == "ROUND_OVER":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    exit_rect = pygame.Rect(825, HEIGHT - 70, 150, 40)
                    if not exit_rect.collidepoint(mouse_pos):
                        payouts_resolved = False
                        card_positions.clear() 
                        
                        for p in players:
                            p.hand = None
                            if p.status != "bankrupt":
                                p.status = "playing"
                        dealer_hand = None
                        
                        # Check for ultimate winner
                        active_players = [p for p in players if p.status != "bankrupt"]
                        
                        if len(active_players) == 0:
                            state = "GAME_OVER"
                            overall_winner = None
                        elif len(players) > 1 and len(active_players) == 1:
                            state = "GAME_OVER"
                            overall_winner = active_players[0]
                        else:
                            # Start next round with the first non-bankrupt player
                            current_player_idx = 0
                            while current_player_idx < len(players) and players[current_player_idx].status == "bankrupt":
                                current_player_idx += 1
                                
                            if len(active_players) > 1:
                                state = "TRANSITION"
                                next_state = "BETTING"
                            else:
                                state = "BETTING"
            
            elif state == "GAME_OVER":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    exit_rect = pygame.Rect(825, HEIGHT - 70, 150, 40)
                    if not exit_rect.collidepoint(mouse_pos):
                        # Reset game completely and go home
                        players.clear()
                        name_box.text = "Player 1"
                        state = "HOME"

        # --- 3. DRAWING ---
        SCREEN.fill(CASINO_GREEN)

        if state == "HOME":
            title = title_font.render("Blackjack Setup", True, WHITE)
            SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            
            SCREEN.blit(font.render("Name:", True, WHITE), (300, 205))
            name_box.draw(SCREEN)
            SCREEN.blit(font.render("Money:", True, WHITE), (300, 275))
            budget_box.draw(SCREEN)
            
            pygame.draw.rect(SCREEN, (50, 150, 255), add_player_rect)
            add_txt = font.render("Add Player", True, WHITE)
            SCREEN.blit(add_txt, add_txt.get_rect(center=add_player_rect.center))
            
            pygame.draw.rect(SCREEN, (50, 200, 50) if len(players)>0 else (100,100,100), start_game_rect)
            start_txt = font.render("Start Game", True, WHITE)
            SCREEN.blit(start_txt, start_txt.get_rect(center=start_game_rect.center))
            
            y_offset = 200
            SCREEN.blit(font.render("Joined Players:", True, GOLD), (700, 150))
            for p in players:
                SCREEN.blit(font.render(f"{p.name} - ${p.chips.total}", True, WHITE), (700, y_offset))
                y_offset += 30

        elif state == "TRANSITION":
            target_player = players[current_player_idx].name
            msg = title_font.render(f"Pass the device to {target_player}", True, GOLD)
            sub = font.render("Click anywhere to continue...", True, WHITE)
            SCREEN.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 50))
            SCREEN.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 50))

        elif state == "GAME_OVER":
            if overall_winner:
                msg = title_font.render(f"GAME OVER! {overall_winner.name} wins the game!", True, GOLD)
                sub_msg = font.render(f"Final Balance: ${overall_winner.chips.total}", True, WHITE)
                SCREEN.blit(sub_msg, (WIDTH//2 - sub_msg.get_width()//2, HEIGHT//2 + 10))
            else:
                msg = title_font.render("GAME OVER! Everyone went bankrupt!", True, GOLD)
            
            SCREEN.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 50))
            sub = font.render("Click anywhere to return to Home Screen", True, WHITE)
            SCREEN.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 80))
            
            # Exit Button on Game Over
            exit_rect = pygame.Rect(825, HEIGHT - 70, 150, 40)
            pygame.draw.rect(SCREEN, (200, 50, 50), exit_rect)
            SCREEN.blit(font.render("Exit Game", True, WHITE), exit_rect.move(25, 5))

        elif state in ["BETTING", "PLAYING", "DEALER_TURN", "ROUND_OVER", "BUSTED_WAIT"]:
            current_p = players[current_player_idx] if current_player_idx < len(players) else players[0]
            total_pot = sum(p.chips.bet for p in players)

            # Sidebar
            sidebar_rect = pygame.Rect(800, 0, 200, HEIGHT)
            pygame.draw.rect(SCREEN, (30, 30, 30), sidebar_rect)
            pygame.draw.line(SCREEN, GOLD, (800, 0), (800, HEIGHT), 3)
            SCREEN.blit(font.render("Game Info", True, GOLD), (820, 20))
            
            y_sidebar = 60
            for p in players:
                if p.status == "bankrupt":
                    color = (100, 100, 100) # Grey out bankrupt players
                    SCREEN.blit(small_font.render(f"{p.name}: BANKRUPT", True, color), (810, y_sidebar))
                    y_sidebar += 35
                else:
                    color = (200, 50, 50) if p.status == "busted" else WHITE
                    hand_val = p.hand.value if p.hand else 0
                    SCREEN.blit(small_font.render(f"{p.name}: ${p.chips.total}", True, color), (810, y_sidebar))
                    SCREEN.blit(small_font.render(f"Hand: {hand_val}", True, color), (810, y_sidebar + 20))
                    y_sidebar += 45

            # Helpers Guide
            y_guide = 350
            SCREEN.blit(font.render("Rules & Values", True, GOLD), (810, y_guide))
            rules = ["2-10: Face Value", "J, Q, K: 10", "Ace: 1 or 11", "", "Dealer draws to 16", "stands on 17."]
            y_guide += 35
            for rule in rules:
                SCREEN.blit(small_font.render(rule, True, WHITE), (810, y_guide))
                y_guide += 25

            # Exit Button
            can_exit = state in ["HOME", "BETTING", "ROUND_OVER"]
            exit_rect = pygame.Rect(825, HEIGHT - 70, 150, 40)
            exit_color = (200, 50, 50) if can_exit else (100, 100, 100)
            pygame.draw.rect(SCREEN, exit_color, exit_rect)
            SCREEN.blit(font.render("Exit Game", True, WHITE), exit_rect.move(25, 5))

            # Dealer Area
            pygame.draw.line(SCREEN, GOLD, (0, 250), (800, 250), 3)
            SCREEN.blit(font.render(f"Dealer Area | Total Pot: ${total_pot}", True, WHITE), (20, 10))
            
            draw_shoe(SCREEN)
            
            if dealer_hand:
                for i, card in enumerate(dealer_hand.cards):
                    card_name = "Hidden" if (state in ["PLAYING", "BUSTED_WAIT"] and i == 0) else str(card)
                    cx, cy = get_anim_pos(id(card), 300 + (i * 40), 60) 
                    draw_card(SCREEN, card_name, cx, cy)
                
                if state in ["DEALER_TURN", "ROUND_OVER"]:
                    val_txt = font.render(f"Value: {dealer_hand.value}", True, GOLD)
                    SCREEN.blit(val_txt, (180, 120))

            # Player Area
            if state == "ROUND_OVER":
                msg = title_font.render("Round Over! Click to restart.", True, GOLD)
                SCREEN.blit(msg, (WIDTH//2 - msg.get_width()//2 - 100, 350))
                
                y_res = 420
                for p in players:
                    if p.status == "bankrupt" and "BANKRUPT" not in p.round_result:
                        res_txt = font.render(f"{p.name} is out of money!", True, (150, 150, 150))
                    else:
                        res_txt = font.render(f"Hand: {p.hand.value if p.hand else 0} | {p.round_result}", True, WHITE)
                    SCREEN.blit(res_txt, (200, y_res))
                    y_res += 35
            else:
                SCREEN.blit(title_font.render(f"{current_p.name}'s Turn", True, GOLD), (20, 270))
                SCREEN.blit(font.render(f"Balance: ${current_p.chips.total} | Bet: ${current_p.chips.bet}", True, WHITE), (20, 320))

                if state == "BETTING":
                    start_x = 70
                    for value in reversed(current_p.chips.denominations): 
                        count = current_p.chips.inventory[value]
                        draw_chip_button(SCREEN, start_x, 600, value, count)
                        start_x += 90
                        
                    pygame.draw.rect(SCREEN, (200, 50, 50), pygame.Rect(480, 580, 120, 40))
                    SCREEN.blit(font.render("Clear", True, WHITE), (510, 585))
                    
                    lock_color = (50, 200, 50) if current_p.chips.bet > 0 else (100, 100, 100)
                    pygame.draw.rect(SCREEN, lock_color, pygame.Rect(620, 580, 140, 40))
                    SCREEN.blit(font.render("Lock Bet", True, WHITE), (645, 585))

                elif state in ["PLAYING", "BUSTED_WAIT"]:
                    for i, card in enumerate(current_p.hand.cards):
                        cx, cy = get_anim_pos(id(card), 300 + (i * 40), 360)
                        draw_card(SCREEN, str(card), cx, cy)
                        
                    val_txt = font.render(f"Value: {current_p.hand.value}", True, GOLD)
                    SCREEN.blit(val_txt, (180, 420))
                    
                    if state == "PLAYING":
                        hit_rect = pygame.Rect(300, 530, 100, 40)
                        stand_rect = pygame.Rect(420, 530, 100, 40)
                        pygame.draw.rect(SCREEN, (50, 150, 255), hit_rect)
                        pygame.draw.rect(SCREEN, (200, 50, 50), stand_rect)
                        SCREEN.blit(font.render("Hit", True, WHITE), hit_rect.move(30, 5))
                        SCREEN.blit(font.render("Stand", True, WHITE), stand_rect.move(20, 5))
                    
                    elif state == "BUSTED_WAIT":
                        bust_msg = title_font.render("BUSTED! Click to continue.", True, (200, 50, 50))
                        SCREEN.blit(bust_msg, (300, 530))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()