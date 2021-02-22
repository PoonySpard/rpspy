"""Contains:

Class
-----
CustomRockPaperScissors
    allows for creation of Rock Paper Scissors derivatives

Function
--------
main
    runs an example of CustomRockPaperScissors:
        Rock, Paper, Scissors, Lizard, Spock

Body
----
if __name__ == "__main__":
    main()

Acknowledgements
----------------
Rock, Paper, Scissors, Lizard, Spock adapted from:
    http://www.samkass.com/theories/RPSSL.html

Rock Paper Scissors Lizard Spock by Sam Kass and Karen Bryla is
licensed under a Creative Commons Attribution-NonCommercial 3.0 Unported License
    https://creativecommons.org/licenses/by-nc/3.0/
 """

from enum import Enum
from rps import RockPaperScissors


class CustomRockPaperScissors(RockPaperScissors):
    """Allows for initializing with different or modified moves.

    Format
    ------
    Each new or modified move is a kwarg of form:
    moveAtt=moveDict
    moveAtt is what the move's attribute will be named.
        - Will always end up uppercase, stored in class attribute enum Moves after generation.
        - Use ROCK, PAPER, or SCISSORS, in any case, to overwrite properties of built-in moves.
        - Use ROCK, PAPER, and/or SCISSORS with a type other than dict to remove them.
        - The name of game will reflect the order moves are defined in,
            define built-in moves with an empty dict to maintain their position.
    moveDict is a dictionary of form: {
        "string" (optional): lowercase string that represents the move, default is lowercase moveAtt
        "inputString" (optional): expected input to use move, default is first letter
        "beats" (optional):
            list of tuples of strings [(move this move beats, verb),(move this move beats, verb)]
        "losesTo" (optional):
            list of tuples of strings [(move this move loses to, verb),(move this move loses to, verb)]
        }
            - Moves will be generated fine with the bare minimum amount of information required.
            - New moves will overwrite other's properties in input order.
            - "losesTo" overwrites "beats" within the same move
            - Built-in move properties are always overwritten by any relevant new values.
            - Values will not be added to built-in move "beats" or "losesTo", they will be replaced.
                Redefine these with desirable old properties included
                ...ideally, just define any new interactions in new moves.
        """

    def __init__(self, **kwargs):
        """Initializes as normal, but calls buildNewMoves to change class attributes if kwargs are used."""
        super().__init__()
        if kwargs:
            self.oldMoveNames = [move.name.upper() for move in self.Moves]
            self.buildNewMoves(**kwargs)
            self.newClass()

    def newClass(self):
        """Sets class name and type to reflect the game an instance represents."""
        self.__name__ = self.__qualname__ = "".join([move.name.capitalize() for move in self.Moves])
        self.__class__ = type(self.__name__, (CustomRockPaperScissors,), self.__dict__)

    def buildNewMoves(self, **kwargs):
        """Redefines class attributes according to kwargs to create a new game."""
        upperKwargs = self.upKwargs(**kwargs)
        oldMoveKwargs = self.processOldMoves(upperKwargs)
        self.Moves = Enum("Moves", " ".join(oldMoveKwargs.keys()))
        enumKwargs = self.oldMoveKwargsToEnums(oldMoveKwargs)
        self.moveStrings = {}
        self.moveInputs = {}
        self.hierarchy = {}
        self.verbs = {}
        for move, moveDict in enumKwargs.items():
            self.moveStrings[move] = moveDict["string"] if "string" in moveDict else move.name.lower()
            moveInput = moveDict["inputString"] if "inputString" in moveDict else move.name[0].upper()
            self.moveInputs[moveInput] = move
            self.processBeats(move, moveDict)
            self.processLosesTo(move, moveDict)
            self.processVerbs(move, moveDict)

    def upKwargs(self, **kwargs):
        """Takes self.oldMoveNames, kwargs, returns uppercase-keyed desired changes without undesired moves."""
        upperKwargs = {}
        for moveAtt, moveDict in kwargs.items():
            if type(moveDict) is not dict and moveAtt.upper() in self.oldMoveNames:
                self.oldMoveNames.remove(moveAtt.upper())
            else:
                moveDictUpper = moveDict
                try:
                    moveDictUpper["beats"] = tuple(
                        ((move.upper(), verb) for move, verb in moveDict["beats"])
                    )
                except KeyError:
                    pass
                try:
                    moveDictUpper["losesTo"] = tuple(
                        ((move.upper(), verb) for move, verb in moveDict["losesTo"])
                    )
                except KeyError:
                    pass
                upperKwargs[moveAtt.upper()] = moveDictUpper
        return upperKwargs

    def processOldMoves(self, upperKwargs):
        """Returns all desired old moves with any missing properties in upperKwargs

        Doesn't overwrite any custom properties for old moves.
        """
        for oldName in self.oldMoveNames:
            if oldName not in upperKwargs:
                upperKwargs[oldName] = {}
            moveDict = upperKwargs[oldName]
            oldMove = self.Moves[oldName]
            if "string" not in moveDict:
                moveDict["string"] = self.moveStrings[oldMove]
            if "inputString" not in moveDict:
                moveDict["inputString"] = {
                    value: key for key, value in self.moveInputs.items()
                }[oldMove]
            if "beats" not in moveDict:
                moveDict["beats"] = tuple((
                    (move.name, self.verbs[(oldMove, move)])
                    for move in self.hierarchy[oldMove]
                    if move.name not in self.noOverwrite(oldName, upperKwargs, "beats")
                ))
            if "losesTo" not in moveDict:
                losesTo = (move for move, losers in self.hierarchy.items() if oldMove in losers)
                moveDict["losesTo"] = tuple((
                    (move.name, self.verbs[(move, oldMove)])
                    for move in losesTo
                    if move.name not in self.noOverwrite(oldName, upperKwargs, "losesTo")
                ))
            upperKwargs[oldName] = moveDict
        return upperKwargs

    def noOverwrite(self, oldName, upperKwargs, key):
        """Returns values to avoid overwriting when redefining keys "beats" or "losesTo"""
        avoidOverwrite = []
        for moveAtt, moveDict in upperKwargs.items():
            try:
                if oldName in [moveName for moveName, verb in moveDict[key]]:
                    avoidOverwrite.append(moveAtt)
            except KeyError:
                pass
        return avoidOverwrite

    def oldMoveKwargsToEnums(self, oldMoveKwargs):
        """Returns upperKwargs modified to contain members of Moves Enum instead of strings"""
        for move in self.Moves:
            oldMoveKwargs[move] = oldMoveKwargs[move.name]
            del oldMoveKwargs[move.name]
            if "beats" in oldMoveKwargs[move]:
                newBeats = []
                for loser, verb in oldMoveKwargs[move]["beats"]:
                    newBeats.append((self.Moves[loser], verb))
                oldMoveKwargs[move]["beats"] = tuple(newBeats)
            if "losesTo" in oldMoveKwargs[move]:
                newLosesTo = []
                for winner, verb in oldMoveKwargs[move]["losesTo"]:
                    newLosesTo.append((self.Moves[winner], verb))
                oldMoveKwargs[move]["losesTo"] = tuple(newLosesTo)
        return oldMoveKwargs

    def processBeats(self, move, moveDict):
        """Processes beats and adds relevant values to hierarchy"""
        if "beats" in moveDict:
            beats = [loser for loser, _ in moveDict["beats"]]
            for loser in beats:
                try:
                    if loser not in self.hierarchy[move]:
                        self.hierarchy[move].append(loser)
                except KeyError:
                    self.hierarchy[move] = [loser]
                if loser in self.hierarchy and move in self.hierarchy[loser]:
                    self.hierarchy[loser].remove(move)

    def processLosesTo(self, move, moveDict):
        """Processes LosesTo and adds relevant moves to hierarchy"""
        if "losesTo" in moveDict:
            losesTo = [winner for winner, _ in moveDict["losesTo"]]
            for winner in losesTo:
                try:
                    if move not in self.hierarchy[winner]:
                        self.hierarchy[winner].append(move)
                except KeyError:
                    self.hierarchy[winner] = [move]
                if move in self.hierarchy and winner in self.hierarchy[move]:
                    self.hierarchy[move].remove(winner)

    def processVerbs(self, move, moveDict):
        """Processes verbs from beats and LosesTo and adds relevant moves to verbs"""
        verbs = []
        if "beats" in moveDict:
            verbs += [((move, loser), verb) for loser, verb in moveDict["beats"]]
        if "losesTo" in moveDict:
            verbs += [((winner, move), verb) for winner, verb in moveDict["losesTo"]]
        for moves, verb in verbs:
            self.verbs[moves] = verb


def main():
    """Instantiates and starts Rock Paper Scissors Lizard Spock."""
    CustomRockPaperScissors(
                        ROCK={},
                        PAPER={},
                        SCISSORS={
                            "inputString": "SC"
                        },
                        LIZARD={
                           "beats": [("spock", "poisons"), ("paper", "eats")],
                           "losesTo": [("scissors", "decapitates"), ("rock", "crushes")]
                        },
                        SPOCK={
                           "inputString": "SP",
                           "beats": [("scissors", "smashes"), ("rock", "vaporizes")],
                           "losesTo": [("paper", "disproves")]
                        }
    )()


if __name__ == "__main__":
    main()
