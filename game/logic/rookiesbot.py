import random, math
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

'''
point diamond merah = 2
Gameobject: DiamondGameObject, BotGameObject, DiamondButtonGameObject, TeleportGameObject
'''

class MyBot(BaseLogic):
    def __init__(self):
        # Inisialisasi arah pergerakan (kanan, bawah, kiri, atas)
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def isDiamondAvailable(self, board: Board):
        """
        Mengecek apakah ada diamond biru (point=1) di papan permainan.
        Return True jika ada minimal 1 diamond biru, False jika tidak ada.
        """
        diamond = sum(1 for obj in board.game_objects if obj.type == "DiamondGameObject" and obj.properties.points == 1)
        return diamond > 0

    def isRedAvailable(self, board: Board):
        """
        Mengecek apakah ada diamond merah (point=2) di papan permainan.
        Return True jika ada minimal 1 diamond merah, False jika tidak ada.
        """
        red = sum(1 for obj in board.game_objects if obj.type == "DiamondGameObject" and obj.properties.points == 2)
        return red > 0

    def getRedPos(self, board: Board):
        """
        Mendapatkan posisi diamond merah pertama yang ditemukan di papan.
        Return posisi diamond merah atau None jika tidak ditemukan.
        """
        for obj in board.game_objects:
            if obj.type == "DiamondGameObject" and obj.properties.points == 2:
                return obj.position

    def goTo(self, a: Position, b: Position):
        """
        Menghitung arah langkah (delta_x, delta_y) dari posisi a ke posisi b.
        """
        return get_direction(a.x, a.y, b.x, b.y)

    def countDistance(self, a: Position, b: Position):
        """
        Menghitung jarak Manhattan (abs(x) + abs(y)) antara dua posisi.
        """
        return abs(b.x - a.x) + abs(b.y - a.y)

    def getClosestDiamondPos(self, board: Board, me: GameObject):
        """
        Mencari posisi diamond biru terdekat dari posisi bot.
        Return posisi diamond biru terdekat, atau None jika tidak ada.
        """
        diamonds = [obj for obj in board.game_objects if obj.type == "DiamondGameObject" and obj.properties.points == 1]
        closest = min(diamonds, key=lambda d: self.countDistance(me.position, d.position), default=None)
        return closest.position if closest else None

    def getClosestRedPos(self, board: Board, me: GameObject):
        """
        Mencari posisi diamond merah terdekat dari posisi bot.
        Return posisi diamond merah terdekat, atau None jika tidak ada.
        """
        reds = [obj for obj in board.game_objects if obj.type == "DiamondGameObject" and obj.properties.points == 2]
        closest = min(reds, key=lambda r: self.countDistance(me.position, r.position), default=None)
        return closest.position if closest else None

    def getClosestTeleportPos(self, board: Board, me: GameObject):
        """
        Mencari posisi teleport terdekat dari posisi bot.
        Return posisi teleport terdekat, atau None jika tidak ada.
        """
        teleports = [obj.position for obj in board.game_objects if obj.type == "TeleportGameObject"]
        return min(teleports, key=lambda t: self.countDistance(me.position, t)) if teleports else None

    def isCloseBase(self, a: Position, b: Position):
        """
        Mengecek apakah jarak antara posisi a dan posisi b (biasanya base) <= 8.
        """
        return self.countDistance(a, b) <= 8

    def isHomeWithPortal(self, board: Board, me: GameObject):
        """
        Mengecek apakah lebih efisien untuk menuju base dengan bantuan portal.
        Return True jika menggunakan portal lebih cepat, False jika tidak.
        """
        base = me.properties.base
        teleports = [obj for obj in board.game_objects if obj.type == "TeleportGameObject"]
        if len(teleports) < 2:
            return False
        t1, t2 = sorted(teleports, key=lambda t: self.countDistance(me.position, t.position))
        return (self.countDistance(me.position, t1.position) + self.countDistance(t2.position, base)) < self.countDistance(me.position, base)

    def isBetterPortalDiamond(self, usPos: Position, board: Board, me: GameObject):
        """
        Mengecek apakah menggunakan portal akan lebih cepat mencapai diamond biru dibanding langsung menuju diamond biru.
        Return True jika lewat portal lebih cepat, False jika tidak.
        """
        teleports = [obj for obj in board.game_objects if obj.type == "TeleportGameObject"]
        if len(teleports) < 2:
            return False
        t1, t2 = sorted(teleports, key=lambda t: self.countDistance(me.position, t.position))
        dPos1 = self.getClosestDiamondPos(board, me)
        dPos2 = self.getClosestDiamondPos(board, t2)
        if dPos1 and dPos2:
            jTot = self.countDistance(usPos, t1.position) + self.countDistance(t2.position, dPos2)
            return self.countDistance(usPos, dPos1) > jTot
        return False

    def checkDiamondReset(self, mePosition: Position, board: Board):
        """
        Mengecek apakah ada DiamondButton di sekitar bot (jarak 1 langkah).
        Jika ada, kembalikan posisi tombol tersebut agar bisa diaktifkan.
        Jika tidak ada, kembalikan posisi bot.
        """
        buttons = [obj for obj in board.game_objects if obj.type == "DiamondButtonGameObject"]
        for button in buttons:
            if abs(mePosition.x - button.position.x) + abs(mePosition.y - button.position.y) == 1:
                return button.position
        return mePosition

    def next_move(self, board_bot: GameObject, board: Board):
        """
        Fungsi utama untuk menentukan langkah bot di setiap tick permainan.
        Memutuskan apakah akan mengambil diamond, pulang ke base, lewat portal, 
        atau mengaktifkan tombol diamond reset, berdasarkan strategi greedy.
        """
        usPos = board_bot.position
        base = board_bot.properties.base
        tPos1 = self.getClosestTeleportPos(board, board_bot)
        positionButton = self.checkDiamondReset(usPos, board)
        time = math.floor(board_bot.properties.milliseconds_left / 1000)

        print("waktu", time)
        print("Jarak ke base", self.countDistance(usPos, base))
        print("POSISI KITA", usPos)

        if self.isDiamondAvailable(board):
            bluePos = self.getClosestDiamondPos(board, board_bot)

        if self.isRedAvailable(board):
            redPos = self.getClosestRedPos(board, board_bot)

        if positionButton != usPos:
            delta_x, delta_y = self.goTo(usPos, positionButton)
        elif time >= 15:
            if board_bot.properties.diamonds == 5:
                print("Balik ke base (5)")
                if self.isHomeWithPortal(board, board_bot) and usPos != tPos1:
                    print("Lewat portal lebih cepat")
                    delta_x, delta_y = self.goTo(usPos, tPos1)
                else:
                    print("Langsung tanpa portal")
                    delta_x, delta_y = self.goTo(usPos, base)
            elif board_bot.properties.diamonds >= 3 and self.isCloseBase(usPos, base):
                if self.isRedAvailable(board) and self.isDiamondAvailable(board):
                    if self.countDistance(usPos, redPos) < 3 and board_bot.properties.diamonds < 4:
                        print("pengen balik ke base tapi ada merah deket banget")
                        delta_x, delta_y = self.goTo(usPos, redPos)
                    elif self.countDistance(usPos, bluePos) < 3:
                        print("pengen balik ke base tapi ada biru deket banget")
                        delta_x, delta_y = self.goTo(usPos, bluePos)
                    else:
                        print("Deket base dan ada diamond di invent")
                        if self.isHomeWithPortal(board, board_bot) and usPos != tPos1:
                            print("Lewat portal lebih cepat")
                            delta_x, delta_y = self.goTo(usPos, tPos1)
                        else:
                            print("Langsung tanpa portal")
                            delta_x, delta_y = self.goTo(usPos, base)
                else:
                    print("Deket base dan ada diamond di invent")
                    if self.isHomeWithPortal(board, board_bot) and usPos != tPos1:
                        print("Lewat portal lebih cepat")
                        delta_x, delta_y = self.goTo(usPos, tPos1)
                    else:
                        print("Langsung tanpa portal")
                        delta_x, delta_y = self.goTo(usPos, base)
            elif board_bot.properties.diamonds <= 3:
                if self.isDiamondAvailable(board) and self.isRedAvailable(board):
                    if self.isBetterPortalDiamond(usPos, board, board_bot) and usPos != tPos1:
                        print("Via portal lebih bagus!")
                        delta_x, delta_y = self.goTo(usPos, tPos1)
                    elif self.countDistance(usPos, bluePos) < self.countDistance(usPos, redPos):
                        delta_x, delta_y = self.goTo(usPos, bluePos)
                        print("Prior Biru")
                    else:
                        delta_x, delta_y = self.goTo(usPos, redPos)
                        print("Prior Merah")
                elif self.isDiamondAvailable(board):
                    delta_x, delta_y = self.goTo(usPos, bluePos)
                    print("Sisa biru")
                else:
                    delta_x, delta_y = self.goTo(usPos, redPos)
                    print("Sisa merah")
            else:
                if self.isDiamondAvailable(board):
                    delta_x, delta_y = self.goTo(usPos, bluePos)
                    print("Diamond ada 4 paksa ambil biru")
                else:
                    print("Diamond ada 4 tapi gk ada biru, balik")
                    if self.isHomeWithPortal(board, board_bot) and usPos != tPos1:
                        print("Lewat portal lebih cepat")
                        delta_x, delta_y = self.goTo(usPos, tPos1)
                    else:
                        print("Langsung tanpa portal")
                        delta_x, delta_y = self.goTo(usPos, base)
        else:
            if board_bot.properties.diamonds > 0:
                print("Waktu dikit dan ada diamond, balik ke base")
                if self.isHomeWithPortal(board, board_bot) and usPos != tPos1:
                    print("Lewat portal lebih cepat")
                    delta_x, delta_y = self.goTo(usPos, tPos1)
                else:
                    print("Langsung tanpa portal")
                    delta_x, delta_y = self.goTo(usPos, base)
            else:
                if self.isDiamondAvailable(board) and self.isRedAvailable(board):
                    if self.countDistance(usPos, bluePos) < self.countDistance(usPos, redPos):
                        delta_x, delta_y = self.goTo(usPos, bluePos)
                        print("Prior biru waktu dikit")
                    else:
                        delta_x, delta_y = self.goTo(usPos, redPos)
                        print("Prior Merah waktu dikit")
                elif self.isDiamondAvailable(board):
                    delta_x, delta_y = self.goTo(usPos, bluePos)
                    print("Sisa biru waktu dikit")
                else:
                    delta_x, delta_y = self.goTo(usPos, redPos)
                    print("Sisa merah waktu dikit")
        return delta_x, delta_y
