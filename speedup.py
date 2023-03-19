from line_profiler import LineProfiler
import timeit

import Cython

# x()
# y()
# print(timeit.timeit("x()", globals=globals(), number=500000))
# print(timeit.timeit("y()", globals=globals(), number=500000))


# if __name__ == '__main__':
#     prf = LineProfiler()                                                                                         
#     prf.add_function(y)                                                                                            
#     prf.runcall(y)                                                                                            
#     prf.print_stats()
