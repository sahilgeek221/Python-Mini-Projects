import random


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
            print("\n-- Reshuffling the deck --")
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


class Chips:
    def __init__(self, total=100):
        self.total = total
        self.bet = 0

    def win_bet(self):
        self.total += self.bet

    def lose_bet(self):
        self.total -= self.bet


def take_bet(chips):
    while True:
        try:
            print(f"\nYou currently have {chips.total} chips.")
            bet = int(input("Enter your bet: "))
            if bet > chips.total:
                print(f"You can't bet more than {chips.total} chips.")
            elif bet <= 0:
                print("Bet must be more than 0.")
            else:
                chips.bet = bet
                break
        except ValueError:
            print("Invalid input. Please enter a number.")

def hit(deck, hand):
    hand.add_card(deck.deal())

def hit_or_stand(deck, hand):
    while True:
        choice = input("Do you want to Hit or Stand? (h/s): ").strip().lower()
        if choice == 'h':
            hit(deck, hand)
            return True
        elif choice == 's':
            print("Player stands. Dealer's turn.")
            return False
        else:
            print("Invalid input. Please enter 'h' or 's'.")

def show_some(player, dealer):
    print("\nDealer's Hand:")
    print(" <Hidden card>")
    print(f" {dealer.cards[1]}")
    print("\nPlayer's Hand:")
    for card in player.cards:
        print(f" {card}")
    print(f"Value: {player.value}")

def show_all(player, dealer):
    print("\nDealer's Hand:")
    for card in dealer.cards:
        print(f" {card}")
    print(f"Value: {dealer.value}")

    print("\nPlayer's Hand:")
    for card in player.cards:
        print(f" {card}")
    print(f"Value: {player.value}")


def player_busts(chips):
    print("Player busts   Dealer wins.")
    chips.lose_bet()

def player_wins(chips):
    print("Player wins  ")
    chips.win_bet()

def dealer_busts(chips):
    print("Dealer busts   Player wins.")
    chips.win_bet()

def dealer_wins(chips):
    print("Dealer wins  ")
    chips.lose_bet()

def push():
    print("It's a tie   Push.")


def play_blackjack():
    print("Welcome to Blackjack")
    player_chips = Chips()
    deck = Deck()

    while True:
        player_hand = Hand()
        dealer_hand = Hand()

        
        for _ in range(2):
            player_hand.add_card(deck.deal())
            dealer_hand.add_card(deck.deal())

        
        take_bet(player_chips)

        
        show_some(player_hand, dealer_hand)

        
        playing = True
        while playing:
            playing = hit_or_stand(deck, player_hand)
            show_some(player_hand, dealer_hand)

            if player_hand.value > 21:
                player_busts(player_chips)
                break

        
        if player_hand.value <= 21:
            while dealer_hand.value < 17:
                hit(deck, dealer_hand)

            show_all(player_hand, dealer_hand)

            
            if dealer_hand.value > 21:
                dealer_busts(player_chips)
            elif dealer_hand.value > player_hand.value:
                dealer_wins(player_chips)
            elif dealer_hand.value < player_hand.value:
                player_wins(player_chips)
            else:
                push()
        

        print(f"\nChips total: {player_chips.total}")

        if player_chips.total <= 0:
            print("No money left. Game over.")
            break


        
        while True:
            again = input("\nPlay another round? (y/n): ").strip().lower()
            if again in ('y', 'n'):
                break
            print("Invalid input. Please enter 'y' to continue or 'n' to quit.")

        if again == 'n':
            print("Thanks for playing Blackjack")
            break



if __name__ == "__main__":
    play_blackjack()
