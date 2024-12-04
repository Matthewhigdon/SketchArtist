import time


class Round:
    def __init__(self, round_number, duration=60):
        """
        Initialize a single round.

        :param round_number: The number of the current round.
        :param duration: Duration of the round in seconds.
        """
        self.round_number = round_number
        self.duration = duration
        self.remaining_time = duration
        self.is_active = False

    def start(self):
        """
        Start the round and track the time.
        """
        print(f"Starting Round {self.round_number}")
        self.is_active = True
        start_time = time.time()

        while self.remaining_time > 0:
            elapsed_time = time.time() - start_time
            self.remaining_time = self.duration - int(elapsed_time)

            if self.remaining_time <= 0:
                self.remaining_time = 0
                self.is_active = False
                print(f"Round {self.round_number} ended!")
                break

            # Simulate waiting or perform other tasks
            time.sleep(1)  # Simulate 1-second ticks for simplicity
            print(f"Round {self.round_number}: {self.remaining_time} seconds left")

    def reset(self):
        """
        Reset the round for replay.
        """
        self.remaining_time = self.duration
        self.is_active = False


class Game:
    def __init__(self, total_rounds=5, round_duration=60):
        """
        Initialize the game with a series of rounds.

        :param total_rounds: Total number of rounds in the game.
        :param round_duration: Duration of each round in seconds.
        """
        self.total_rounds = total_rounds
        self.round_duration = round_duration
        self.current_round = 0
        self.rounds = [Round(i + 1, round_duration) for i in range(total_rounds)]

    def start(self):
        """
        Start the game and iterate through the rounds.
        """
        print("Starting the game!")
        for round_instance in self.rounds:
            self.current_round = round_instance.round_number
            round_instance.start()

            # Placeholder: Perform any inter-round logic here
            print(f"Intermission after Round {self.current_round}\n")

        print("Game over! Thanks for playing.")


if __name__ == "__main__":
    # Create and start the game
    game = Game(total_rounds=5, round_duration=60)
    game.start()
