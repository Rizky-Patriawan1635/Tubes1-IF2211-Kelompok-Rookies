from abc import ABC

from game.models import Board, GameObject


class BaseLogic(ABC):
    def next_move(self, board_bot: GameObject, board: Board) -> (int, int):
        raise NotImplementedError()
