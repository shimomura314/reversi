cdef extern from "<cstdint>" namespace "std":
    ctypedef unsigned long long uint64_t


cdef public class BitBoardC [object BitBoardCObject, type BitBoardCType]:

    # Class variables.
    cdef public uint64_t BLACK
    cdef public uint64_t WHITE
    cdef public uint64_t INIT_BLACK
    cdef public uint64_t INIT_WHITE

    # Instance variables.
    cdef public uint64_t _black_board
    cdef public uint64_t _white_board

    # Declaration of methods.
    cpdef uint64_t _bit_count(self, uint64_t x)
    cpdef uint64_t _check_surround(self, uint64_t put_loc, uint64_t direction)
    cpdef (uint64_t, uint64_t) simulate_play(
        self, int turn, uint64_t put_loc,
        uint64_t black_board, uint64_t white_board,
        )
    cpdef void update_board(self, uint64_t black_board, uint64_t white_board)
    cpdef (uint64_t, uint64_t) count_disks(
            self, uint64_t black_board, uint64_t white_board)
    cpdef uint64_t reversible_area(
        self, uint64_t turn, uint64_t black_board, uint64_t white_board)
    cpdef bint is_reversible(
        self, uint64_t turn, uint64_t put_loc,
        uint64_t black_board, uint64_t white_board,
        )
    cpdef bint turn_playable(
        self, uint64_t turn, uint64_t black_board, uint64_t white_board)
    cpdef (uint64_t, uint64_t) return_board(self)
    cpdef (uint64_t, uint64_t) return_player_board(self, int turn)
    cpdef load_board(self, uint64_t black_board, uint64_t white_board)
