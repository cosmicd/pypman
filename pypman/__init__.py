import os
import sys
import inspect
import logging
from . import master
from . import util
import coloredlogs
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler()) 
coloredlogs.install(level='WARN', logger=log)
def main():
    """Entry point for the application execution.""" 
##############################################################      
# Not using logging config during development    
    #loggerConfigPath = os.path.join(os.getcwd(), 'pypman', 'logging.yml')
    #util.initializeLogger(loggerConfigPath)  # if config exists OR:
    #util.initializeLogger(logging.DEBUG) # ignore config file
######################################################################
   
    func = master.master
    args = sys.argv[1:2]
    kw_args = dict(args.split('=') for args in sys.argv[2:])
    log.debug(sys.argv)
    log.debug(args)
    log.debug(kw_args)   

    if(len(args) < 1):
        raise SyntaxError(" cli arguments mismatch.\
 Corrent useage: pypman taskName optional-keyword-args")

    try:
        if (('prof', 'time') or ('prof', 'mem')) in kw_args.items():  # if profiling performance
            log.info('executing testCodePerformance...')
            testCodePerformance(func, args, kw_args)
        else:
            log.info('executing master...')
            func(*args, **kw_args)
    except Exception:
        log.exception('APP CRASHED! ')
    log.info('ALL DONE')

###################################################
# check code performance during development phase:


def testCodePerformance(func, args, kw_args):
    # keep import inside the function as this is a dev dependency
    # this function will be removed from prodcution code
    from . import performanceTime as pTime
    from . import performanceMem as pMem
    if kw_args['prof'] == 'time':
        # time profile using cprofile; output is used by gprof2do
        pTime.profileTime(func, args, kw_args)
        # see task: py.prf.gprof2dotpng
        # line by line time profile of a function
        pTime.profileTimeLine(func, args, kw_args)
    else:  
        # use one or more methods below for profiling memory useage
        pMem.objectSize()  # system specific sizes of objects
        # pMem.traceMemAlloc(func,args,kw_args) # memory profile using tracemalloc
        # pMem.profileMemVsTime(func,args,kw_args) # memory useage vs time (uses memory profiler)
        # pMem.profileMemVsLine(func,args,kw_args) # line profile of memory (uses memory profiler)
        # pMem.graphMemProfile(func,args,kw_args) #
