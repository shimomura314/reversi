import pstats
sts = pstats.Stats('./_trial/matching/matching.prof')
sts.strip_dirs().sort_stats(1).print_stats()