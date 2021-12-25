import pstats
sts = pstats.Stats('./matching/matching.prof')
sts.strip_dirs().sort_stats(0).print_stats()
