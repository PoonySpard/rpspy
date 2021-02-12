"""contains:

Classes
-------
RockPaperScissors
    handles generating rock, paper, scissors objects
GameSequenceError
    raised when RockPaperScissors modules are called out of order
"""


from random import choice as randomChoice
from functools import total_ordering
from constants import Moves


@total_ordering
class RockPaperScissors(object):
    """Class representing rock paper scissors games. Can be subclassed and adapted to any variation.

    Attributes
    ----------
    WIN, LOSS, DRAW : int
        class constants, represent game outcomes
    YES, NO : str
        class constants, lowercase, input in any case for yes or no
    RED_TEXT, WHITE_TEXT : str
        class constants, ANSI escape codes for colored text
    Moves : enum
        contains move constants, i.e. RockPaperScissors.Moves.ROCK, PAPER, and SCISSORS
    verbs : dict
        tuples of (winner, loser) as keys for verbs describing their interaction
    moveInputs : dict
        uppercase string input in any case as keys for the move that input corresponds to
    moveStrings : dict
        move constants as keys for corresponding strings
    hierarchy :
        move constants as keys for lists of moves that move beats
    gameState : str
        the current stage the round is in
    gameOutcome : str or None
        relates the current round's outcome from the player's perspective, None if game is unresolved
    _playerMove: str or None
        move the player made in the current round, None if no move yet
    _compMove: str or None
        move the computer made in the current round, None if no move yet
    round: int
        represents both current round and how many rounds have been played
    _record: list
        stores round outcomes in order

    Class Usage
    -----------
    Very simple usage:
        Execute containing module as __main__ to play rock, paper, scissors.
    Simple usage:
        Construct instances of the class and then call them
            to create and play games of rock, paper, scissors.
    Custom usage:
        Follow general flow of playGame method in custom code, adapt as needed.
            For example:
                - Simulate bias for certain moves by changing compMove to a different move
                    some % of the time between begin and resolve.
                    i.e rps = RockPaperScissors()
                        rps.begin
                        rps.compMove = rps.Move.ROCK if random.randint(0, 5) > 3
                        rps.resolve
                    ...etc.
                - Create a ui for the game with TKinter, pickle instances of the class to save
                    and allow merging saves by adding the instances together with +.
                - Allow competitive simultaneous play of multiple games at once
                    via a website and determine who won more rounds with comparison operators.
        Use CustomRockPaperScissors to easily add new moves to the game!
            see CustomRockPaperScissors docstring and Rock, Paper, Scissors, Lizard, Spock in customrps.py
    """
    WIN, LOSS, DRAW = 0, 1, 2
    YES, NO = "y", "n"
    RED_TEXT, WHITE_TEXT = "\033[91m", "\033[0m"

    def __init__(self):
        """Creates a rock paper scissors game and prepares for the first round."""
        self.Moves = Moves
        self.moveStrings = {move: move.name.lower() for move in Moves}
        self.moveInputs = {move.name[0].upper(): move for move in Moves}
        self.hierarchy = {
            Moves.ROCK: [Moves.SCISSORS],
            Moves.PAPER: [Moves.ROCK],
            Moves.SCISSORS: [Moves.PAPER]
        }
        self.verbs = {
            (Moves.ROCK, Moves.SCISSORS): "crushes",
            (Moves.PAPER, Moves.ROCK): "covers",
            (Moves.SCISSORS, Moves.PAPER): "cuts"
        }
        self.gameState = "initial"
        self.gameOutcome = None
        self._playerMove = None
        self._compMove = None
        self.round = 1
        self._record = []

    def __call__(self):
        """Enables calling an instance of the class to play it."""
        self.playGame()

    def __str__(self):
        """Returns a readable description of this object for users."""
        return f"{self.gameName} game object, Stage: {self.gameState}, Record: {self.record}"

    def __repr__(self):
        """Returns a concise and explicit description of this object for debugging."""
        return (f"{self.__class__.__name__}"
                + str((self.gameState, self.round, self._record,
                       self._playerMove, self._compMove, self.gameOutcome)))

    def __bool__(self):
        """Class instances are truthy only when player hasn't gone yet in round.

        Useful in loops that query for user input for custom implementations.
        """
        return self._playerMove is not None

    def __add__(self, addend):
        """Allows for adding two games together to create one with combined records.

        Does not work with different classes.
        """
        if addend.__class__ != self.__class__:
            raise TypeError(f"unsupported operand type(s) for +: {type(self)} and {type(addend)}")
        addGame = self.__class__()
        addGame.round = self.round + addend.round - 1
        addGame._record = self._record + addend._record
        return addGame

    def __eq__(self, compareTo):
        """Defines equality (==) for this class according to player wins.

        Only this and __lt__ are required to define all comparison operator behavior
        with @total_ordering decorator.
        """
        return self._record.count(self.WIN) == compareTo._record.count(self.WIN)

    def __lt__(self, compareTo):
        """Defines less than (<) for this class according to player wins.

        Only this and __eq__ are required to define all comparison operator behavior
        with @total_ordering decorator.
        """
        return self._record.count(self.WIN) < compareTo._record.count(self.WIN)

    def playGame(self):
        """Handles basic game logic if customization isn't required, allows indefinite playing."""
        while "restart" not in locals() or restart:
            self.begin()
            self.resolve()
            self.getWinner()
            print(self.record)
            self.reset()
            restart = self.playAgain()

    def begin(self):
        """Begins the game by displaying instructions and processing player and computer moves."""
        if self.gameState != "initial":
            raise GameSequenceError("This round has already begun!")
        self.gameState = "begun"
        self.displayInstructions()
        self.getCompMove()
        self.getMove()
        self.gameState = "moved"

    def resolve(self):
        """Resolves the current game by setting the outcome and adding it to the record."""
        if self.gameState != "moved" and self.gameOutcome is None:
            raise GameSequenceError("The players haven't gone yet!")
        if self._playerMove == self._compMove:
            self.gameOutcome = self.DRAW
        elif self._compMove in self.hierarchy[self._playerMove]:
            self.gameOutcome = self.WIN
        else:
            self.gameOutcome = self.LOSS
        if self.gameState == "moved":
            self.gameState = "resolved"
            self._record.append(self.gameOutcome)

    def getWinner(self):
        """Prints what moves were chosen and who won the game."""
        if self.gameState != "resolved":
            raise GameSequenceError("The round hasn't been resolved yet!")
        ifWin = self.gameOutcome == self.WIN
        ifLoss = self.gameOutcome == self.LOSS
        print(
            f"The computer chose {self.compMove} and the player chose {self.playerMove}.\n"
            f"{self.verbify()}"
            + (
                "The computer wins!" if ifLoss
                else "The player wins!" if ifWin
                else "It's a draw!"
             )
        )

    @property
    def record(self):
        """string containing current record from all rounds from player's perspective."""
        return (f"Current record: "
                f"W: {self._record.count(self.WIN)} "
                f"L: {self._record.count(self.LOSS)} "
                f"D: {self._record.count(self.DRAW)} "
                f"Rounds: {self.round}"
                )

    def reset(self):
        """Resets all class attributes to allow playing again or quitting game in progress."""
        self.gameState = "initial"
        self.gameOutcome = None
        self._playerMove = None
        self._compMove = None
        self.round += 1

    def getMove(self):
        """Receives user input and validates, queries for further input if invalid, stores move."""
        if self._playerMove is not None:
            raise GameSequenceError("Player has already gone!")
        while "move" not in locals():
            move = input().upper()
            if move not in self.moveInputs.keys():
                self.displaySimpleInstructions()
                del move
        self._playerMove = self.moveInputs[move]

    @property
    def playerMove(self):
        """Current player move as an appropriate string"""
        if self._playerMove is None:
            raise GameSequenceError("The player hasn't gone yet!")
        return self.showMove(self._playerMove)

    @playerMove.setter
    def playerMove(self, newMove):
        """Allows for directly setting the player's move in custom implementations."""
        self._playerMove = newMove

    def getCompMove(self):
        """Pseudo-randomly generates a computer move and stores it as _compMove"""
        if self._compMove is not None:
            raise GameSequenceError("Computer has already gone!")
        self._compMove = randomChoice([move for move in self.Moves])

    @property
    def compMove(self):
        """Current computer move as an appropriate string"""
        if self._compMove is None:
            raise GameSequenceError("The computer hasn't gone yet!")
        return self.showMove(self._compMove)

    @compMove.setter
    def compMove(self, newMove):
        """Allows for directly setting the computer's move in custom implementations."""
        self._compMove = newMove

    def showMove(self, move):
        """Converts moves into readable strings for output."""
        return self.moveStrings[move]

    def verbify(self):
        """If relevant, returns current moves, verb that describes their interaction, and new line as a string."""
        if self.gameOutcome == self.WIN:
            verbified = (
                f"{self.playerMove.capitalize()} " 
                f"{self.verbs[self._playerMove, self._compMove]} " 
                f"{self.compMove}.\n"
            )
        elif self.gameOutcome == self.LOSS:
            verbified = (
                f"{self.compMove.capitalize()} "
                f"{self.verbs[self._compMove, self._playerMove]} "
                f"{self.playerMove}.\n"
            )
        else:
            verbified = ""
        return verbified

    def playAgain(self):
        """Queries player and returns True if player wishes to play again."""
        yesOrNo = input(
            f"Play again {self.YES}/{self.NO}?\n"
        ).lower()
        while yesOrNo not in (self.YES, self.NO):
            yesOrNo = input(
                self.RED_TEXT
                + f"That wasn't {self.YES} or {self.NO}, "
                f"{self.YES}/{self.NO}?\n"
                + self.WHITE_TEXT
            ).lower()
        return yesOrNo == self.YES

    def displayInstructions(self):
        """Displays instructions for the user"""
        moves = self.commaOr(self.moveList)
        print(f"Welcome to {self.gameName}!\n"
              f"{self.verbString}.\n"
              f"Type {self.gameOptions} for {moves}.\n"
              f"Then, press Enter.\n"
              "The computer will go simultaneously and a winner shall be decided!")

    def displaySimpleInstructions(self):
        """"Displays simpler instructions for confused users."""
        print("I'm sorry, were the instructions too complicated?\n"
              "Let's try again...\n"
              f"ME COMPUTER, WE PLAY {self.gameName.upper()}.\n"
              f"YOU ENTER {self.gameOptions.upper()}!")

    @property
    def verbString(self):
        """String containing all interactions between moves."""
        verbStrings = []
        for winner, losers in self.hierarchy.items():
            flattenedLosers = ""
            for loser in losers:
                flattenedLosers += f" {self.verbs[(winner, loser)]} {self.moveStrings[loser]},"
            flattenedLosers += "\b"
            verbStrings.append((self.moveStrings[winner].capitalize(), flattenedLosers))
        verbStrings = ["".join((winner, losers)) for winner, losers in verbStrings]
        return ";\n".join(verbStrings)

    @property
    def gameOptions(self):
        """A string containing all possible player inputs for the current game."""
        return self.commaOr(self.moveInputs.keys())

    @property
    def moveList(self):
        """A list containing the capitalized strings representing the moves in the current game."""
        return [move.capitalize() for move in self.moveStrings.values()]

    @property
    def gameName(self):
        """A capitalized string containing the name of the current game based on possible moves."""
        return self.commaOr(self.moveList, addOr=False)

    @staticmethod
    def commaOr(iterable, addOr=True):
        """Takes iterable, returns a string with commas and one or if addOr."""
        commadify = [str(x) for x in iterable]
        if addOr:
            orAdded = (", or " if addOr else "") + commadify.pop(-1)
            commadified = ", ".join(commadify) + orAdded
        else:
            commadified = ", ".join(commadify)
        return commadified


class GameSequenceError(Exception):
    """Raised when a game method is called out of sequence."""
