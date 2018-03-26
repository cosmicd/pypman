import logging.config
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def profileTime(func, args, kw_args):
    import cProfile
    import pstats
# The following 2 methods did not work for me. they were
# to be used in cProfile.Profile()
# timer=time.clock() # it has different meaning on linux and windows
# timer=time.perf_counter() # does include time elapsed during sleep and is system-wide
# timer=time.process_time() # EXCLUDE sleep time; sum of the system and user CPU time of the current process'''
    prf = cProfile.Profile()
    prf.enable()
    func(*args, **kw_args)
    prf.disable()
    # s = io.StringIO()
    sortby = 'cumulative'
    with open('profstats.txt', 'w') as flw:
        pst = pstats.Stats(prf, stream=flw)
        pst.strip_dirs()
        pst.sort_stats(sortby)
        pst.print_stats()  # write to human readable flw
        # pst.print_callees()
        # pst.print_callers()
        # this file dump is used by gprof2dot in task py.prf.gprof2dot***
        pst.dump_stats('dumpstats')


def profileTimeLine(func, args, kw_args):
    from line_profiler import LineProfiler
    prf = LineProfiler(func)
    # from . import util; prf.add_function(util.loadYml) # you may add more functions
    prf.enable()
    func(*args, **kw_args)
    prf.disable()
    prf.dump_stats('lpstats')
    with open('lineprofstats.txt', 'w') as flw:
        prf.print_stats(flw)
