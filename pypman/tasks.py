from . taskABC import TaskABC
import logging
import warnings
import sys
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PythonNodeTask(TaskABC):
    def __init__(self, **kwargs):
        super().__init__()
        if TaskABC.project == 'none':
            log.error('Project name (!=none) required for node and python ve.')
            sys.exit(1)
        if TaskABC.task.fname == 'node':
            self.setEnvShell('node', **kwargs)
            self.setCmd('node')
        else:
            self.setEnvShell('python', **kwargs)
            self.setCmd('python')
        log.debug('FNAME %s' % TaskABC.task.fname)
        log.debug('Class init successful: %s' % self.__class__.__name__)

    def setEnvShell(self, ve_type, **kwargs):
        self._envShell = super().prepareEnvShell(ve_type, **kwargs)

    def setCmd(self, fnamePrefix):
        # this works too: replace 'super()' by 'self'
        self._cmd = super().veAcCmd(fnamePrefix)


class GlobalTask(TaskABC):
    def __init__(self, **kwargs):
        super().__init__()
        self.setEnvShell()
        self.setCmd()
        log.debug('Class init successful: %s' % self.__class__.__name__)

    def setEnvShell(self):
        self._envShell = {}
        if TaskABC.project != 'none':
            self._envShell['path_pd'] = TaskABC.project.rootPath

    def setCmd(self):
        self._cmd = super().task.cmd
