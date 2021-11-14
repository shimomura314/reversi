"""
オセロアプリを起動するためのファイル．
    - bitbord : オセロの手続きを設定
    - display : GUIを設定
    - strategy : CPUの戦略を定義
"""

import wx

from bitboard import OthelloGame
from display import MyFrame
from strategy import Strategy

if __name__ == "__main__":
    game = OthelloGame()
    game.load_strategy(Strategy)

    application = wx.App()
    frame = MyFrame(title="Othello Game", othello=game)

    frame.Center()
    frame.Show()
    application.MainLoop()
    wx.Exit()
