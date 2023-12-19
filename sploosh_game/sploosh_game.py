import random
from .variables import board_size, ship_sizes, empty, hit, miss, revealed_ship, ship

class SplooshGame:
    def __init__(self):
        self.board = [[empty for _ in range(board_size)] for _ in range(board_size)]
        self.ships = self.place_ships()

    def place_ships(self):
        ships = []
        ship_representation = 's'  # Internal representation for ships
        for size in ship_sizes:
            while True:
                direction = random.choice(['horizontal', 'vertical'])
                if direction == 'horizontal':
                    x = random.randint(0, board_size - 1)
                    y = random.randint(0, board_size - size)
                    positions = [(x, y + i) for i in range(size)]
                else:
                    x = random.randint(0, board_size - size)
                    y = random.randint(0, board_size - 1)
                    positions = [(x + i, y) for i in range(size)]

                if all(self.board[x][y] == empty for x, y in positions):
                    ships.extend(positions)
                    for x, y in positions:
                        self.board[x][y] = ship_representation  # Use ship_representation for ships
                    break
        return ships

    def print_board(self):
        numbers = ' '.join([f"{i + 1}\uFE0F\u20E3" for i in range(board_size)])  # Numbers with emojis
        header = f"#️⃣{numbers}"  # Header with the numbers
        rows = [f"{chr(65 + i)} {' '.join('🟦' if cell == 's' else cell for cell in self.board[i])}" for i in range(board_size)]
        return f"{header}\n" + '\n'.join(rows)

    def is_valid_coordinate(self, x, y):
        return 0 <= x < board_size and 0 <= y < board_size

    def shoot(self, x, y):
        
        if not self.is_valid_coordinate(x, y):
            return False, "Invalid coordinates. Try again."

        if self.board[x][y] == empty:
            self.board[x][y] = miss
            return True, "Sploosh!💦"
        elif self.board[x][y] == 's':  # Check against the internal ship representation
            self.board[x][y] = hit
            self.ships.remove((x, y))
            if not self.ships:
                return False, f"You've already shot here. Try another coordinate."
            return True, "Hit!💥"
        else:
            return False, "You've already shot here . Try another coordinate."

    def reveal_ships(self):
        for x in range(board_size):
            for y in range(board_size):
                if self.board[x][y] == 's':  # Check against the internal ship representation
                    self.board[x][y] = revealed_ship
    def get_total_prize(self, shots_left):
        total_hits = sum(row.count(hit) for row in self.board)
        prize_per_hit = 10  # 10 rupees per hit

        if total_hits == 0:
            return 0  # If no hits, return 0 rupees

        if not self.ships:  # All ships destroyed
            if shots_left == 0:
                shots_left = 1  # If shots left is 0, consider it as 1 shot
            return total_hits * prize_per_hit * shots_left

        return total_hits * prize_per_hit  # If ships remain, calculate only for hits

        
    def print_ship_positions(self):
        ship_positions = []

        for x in range(board_size):
            for y in range(board_size):
                if self.board[x][y] == ship:
                    ship_positions.append(f"{chr(65 + x)}{y + 1}")

        print(",".join(ship_positions))
