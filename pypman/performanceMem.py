import logging.config
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def profileMemVsLine(func, args, kw_args):
    # profiles line by line memory useage
    # requires activation of ve.
    # Also, wrap profile function with "@profile"; need "from memory_profiler import profile"
    func(*args, **kw_args)


def profileMemVsTime(func, args, kw_args):
    # profiles memory useage as a function of time of the current or other process
    # requires activation of ve.
    import pylab as pl
    import numpy as np
    from memory_profiler import memory_usage
    # log.info(memory_usage(-1,interval=.2, timeout=1))# memprof current process (-1) interpretter
    dt = 0.2
    timeout = 0
    mem = memory_usage(
        (func, (*args,), {**kw_args}), interval=dt, timeout=timeout)
    # import pdb; pdb.set_trace() # then execute this in ipython:  memory_usage((func, (*args,), {**kw_args}),interval=.2, timeout=1)
    """
    Plot memory usage of a numeric computation using numpy and scipy
    """
    log.info(mem)

    x = np.linspace(0, len(mem) * dt, len(mem))
    log.info(x)
    pl.fill_between(x, mem)

    pl.xlabel('time')
    pl.ylabel('Memory consumption (in MB)')
    # pl.show()
    pl.ylim([60, 65])
    pl.savefig('atmp.png')
    log.info('here we are')


def graphMemProfile(func, args, kw_args):
    import objgraph
    # objgraph.show_most_common_types()
    objgraph.show_growth()
    func(*args, **kw_args)
    objgraph.show_growth()
    import random
    str(objgraph.show_chain(objgraph.find_backref_chain(
        random.choice(objgraph.by_type('staticmethod')), objgraph.is_proper_module), filename='chain.png'))
    #objgraph.show_refs([func(*args,**kw_args)], filename='refs.png')
    #objgraph.show_backrefs([func(*args,**kw_args)], filename='backrefs.png')

    #import pdb; pdb.set_trace()
    objgraph.show_growth()


def traceMemAlloc(func, args, kw_args):
    import tracemalloc
    tracemalloc.start()
    func(*args, **kw_args)
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    log.info("[ Top 10 ]")
    for stat in top_stats[:10]:
        log.info(stat)


def objectSize():
    from decimal import Decimal
    mist = [1, 1., Decimal(1.), '', 'a', 'ab', u'ab', (), (1,), (1, 3), set(), set(
        [1]), set([1, 2]), {}, dict(a=1), dict(a=1, b=2)]
    # log.info(len(mist))
    with open('objsizes.txt', 'w') as flw:

        for elm in mist:
            # flw.write(str(type(elm))+'=')
            # flw.write(str(sys.getsizeof(elm))+'\n')
            log.info(totalSize(elm, verbose=True))
    dictio = dict(a=1, b=2, c=3, d=[4, 5, 6, 7], e='a string of chars')
    log.info('Complex object size: ')
    log.info(totalSize(dictio, verbose=True))

# from: https://code.activestate.com/recipes/577504/


def totalSize(o, handlers={}, verbose=False):
    from sys import getsizeof, stderr
    from itertools import chain
    from collections import deque

    """ Returns the approximate memory footprint an object and all of its contents.

        Automatically finds the contents of the following builtin containers and
        their subclasses:  tuple, list, deque, dict, set and frozenset.
        To search other containers, add handlers to iterate over their contents:

            handlers = {SomeContainerClass: iter,
                        OtherContainerClass: OtherContainerClass.get_elements}

    """

    def dict_handler(d): return chain.from_iterable(d.items())
    all_handlers = {tuple: iter,
                    list: iter,
                    deque: iter,
                    dict: dict_handler,
                    set: iter,
                    frozenset: iter,
                    }
    all_handlers.update(handlers)     # user handlers take precedence
    seen = set()                      # track which object id's have already been seen
    # estimate sizeof object without __sizeof__
    default_size = getsizeof(0)

    def sizeof(o):
        if id(o) in seen:       # do not double count the same object
            return 0
        seen.add(id(o))
        s = getsizeof(o, default_size)

        if verbose:
            log.info(s, type(o), repr(o), file=stderr)

        for typ, handler in all_handlers.items():
            if isinstance(o, typ):
                s += sum(map(sizeof, handler(o)))
                break
        return s

    return sizeof(o)
