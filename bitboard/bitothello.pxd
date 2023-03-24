cdef extern from "<cstdint>" namespace "std":
    ctypedef unsigned long long uint64_t


cdef public class OthelloGameC [object OthelloGameCObject, type OthelloGameCType]:

    # Class variables.
    cdef public int BLACK
    cdef public int WHITE
    cdef public object board
    cdef int _player_clr
    cdef public int turn
    cdef public uint64_t reversible
    cdef public str result
    cdef int _count_player
    cdef int _count_opponent
    cdef int _pass_cnt[2]
    cdef bint _player_auto
    cdef object _strategy_player
    cdef object _strategy_opponent
    cdef object _board_log
    cdef object _board_back

    # Declaration of methods.
    cpdef void play_turn(self, int put_loc)
    cpdef (int, int) update_count(self)
    cpdef bint judge_game(self, int player=?, int opponent=?)
    cpdef void auto_mode(self, bint automode=?)
    cpdef void load_strategy(self, object Strategy)
    cpdef void change_strategy(self, str strategy, bint is_player=?)
    cpdef (bint, bint) process_game(self)
    cpdef list display_board(self)
    cpdef bint undo_turn(self)
    cpdef bint redo_turn(self)
    cpdef int return_turn(self)
    # cpdef (uint64_t, uint64_t, list, list) return_state(self)
    cpdef void load_state(
        self, uint64_t black_board, uint64_t white_board,
        list board_log, list board_back)
