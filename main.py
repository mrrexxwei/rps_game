import random

class Player:
    pass
    #[write your code here] the constructor has name and score two attributes
    def __init__(self):
        pass

    #[write your code here] the method return random value from the three options
    def choose(self):
        pass

    #[write your code here] increase the score by 1
    def increment_score(self):
        pass


class Game:
    #[write your code here] constructor has two players as attributes
    def __init__(self):
        pass

    #[write your code here] evaluate two choices for winner
    def determine_winner(self, choice1, choice2):
        pass

    def play(self):
        pass
        #[write your code here] make chooses for two players

        #[write your code here] determine the winner
        
        #[write your code here] write the info to game.txt


if __name__=="__main__":
    player_name = input("Enter your name: ")
    player1 = Player(player_name)
    player2 = Player("computer")
    game = Game(player1, player2)
    game.play()