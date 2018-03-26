import os
import yaml
import logging.config
import logging


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def loadYml(path):
    log.debug('loading file: %s' % path)
    log.debug('cwd: %s' % os.getcwd())
    with open(path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def initializeLogger(par):
    """Setup logging configuration
    """
    if os.path.exists(par):
        logging.config.dictConfig(loadYml(par))
    else:
        logging.basicConfig(level=par)
        logging.warning('Could not find logging config file: %s' % par)
        log.info('Now using basicConfig for logging with level %s' % par)
