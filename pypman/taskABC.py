import os
import glob
import sys
import collections
from abc import ABC, abstractmethod
#from fabric.api import local # not using fabric 
import subprocess
from . import util
import logging
import warnings

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TaskABC(ABC):
    # static data
    pypmanConfigPath={}
    masterConfig={}
    def __init__(self):
        super().__init__()
        self._envShell = {}
        self._cmd = {}
    @staticmethod
    def setHost(name):
        alist = name.split('.')  # split name.local/remote
        file = os.path.join(TaskABC.pypmanConfigPath,
                            'hosts', alist[0]+'.yml')
        cfg = util.loadYml(file)
        log.info('Host config file: %s' % file)
        Host = collections.namedtuple('Host', 'cfg fname access')
        TaskABC.host = Host(cfg, alist[0], alist[1])
    @staticmethod
    def setProject(name):
        if len(name) <= 3 and int(name[1:])>=0: # e.g. taskAlias is t0-t99
            projectDir=os.path.basename(os.path.dirname(TaskABC.pypmanConfigPath))
            log.info('Project name: %s' % projectDir)
            Project = collections.namedtuple('Project', 'name rootPath')
            TaskABC.project = Project(projectDir,os.getcwd())
        else:
            # taskAlias is a pypman config task (e.g. aws.iam.ul)
            # will execute a global task without 
            # any link to a project.
            TaskABC.project = 'none' 
    @staticmethod
    def taskList(name):
        tlist = []    
        if len(name) <= 3 and int(name[1:])>=0:
            tname = TaskABC.masterConfig['task'][name]
            if type(tname) == list:
                for name in tname:
                    tlist.append(TaskABC.taskList(name)[0])
            else:
                tlist = TaskABC.taskList(tname)
        else:
            tlist = [name] # if running task directly (e.g. pypman gb.test.t0)
        return tlist

    @staticmethod
    def setTask(name):
        alist = name.split('.')
        synch = 0  # synch/asynch execution of tasks ()
        if alist[0] == 's':
            # tasks are executed in series (when user rinteraction is needed or when one task depends on the other)
            synch = 1
            alist.pop(0)
        [fname, group, name] = alist
        gname = group+name
        file = os.path.join(TaskABC.pypmanConfigPath,
                            'tasks', fname+'.yml')
        log.info('Task config file: %s' % file)
        cfg = util.loadYml(file)
        cmd = cfg[group][name]
        Task = collections.namedtuple(
            'Task', 'cfg name gname fname group cmd synch')
        TaskABC.task = Task(cfg, name, gname, fname, group, cmd, synch)

    @staticmethod
    def prepareEnvShell(ve_type, **kwargs):
        apath = TaskABC.host.cfg['paths']['ve'+ve_type]
        envsh = {}
        envsh['path_pd'] =  os.path.join(TaskABC.project.rootPath,TaskABC.masterConfig[ve_type][0])
        envsh['path_ve'] = os.path.join(
            apath, TaskABC.masterConfig[ve_type][1])
        envsh['version'] = TaskABC.masterConfig[ve_type][2]
        envsh['project_name'] = TaskABC.project.name
        envsh.update(kwargs)
        log.debug('envsh: %s' % envsh)
        #log.debug('node_mod_sl: %s'%envsh['node_mod_sl'])
        return envsh

    def veAcCmd(self, namePrefix):
        if TaskABC.task.group == 've' and TaskABC.task.name not in {'cr', 'rm', 'ac'}:
            # activate ve in this case
            log.warn("activating ve for task group: %s"%TaskABC.task.group)
            file = os.path.join(TaskABC.pypmanConfigPath,
                                'tasks', namePrefix+".yml")
            ve_ac = (util.loadYml(file))['ve']['ac']
            log.info('Intended task launch dir: %s' %
                     self._envShell['path_ve'])
            return ve_ac+' && '+TaskABC.task.cmd
        else:
            # do not activate ve
            log.warn("Global execution for task group: %s"%TaskABC.task.group)
            return TaskABC.task.cmd

    @abstractmethod
    def setCmd(self):
        raise NotImplementedError("Subclasses should implement this!")

    @abstractmethod
    def setEnvShell(self):
        raise NotImplementedError("Subclasses should implement this!")

    def _parseCmdVars(self):
        #cmd=re.sub('[${}]', '',cmd)
        shellvar = 'echo Execution Result: '  # need this just to have nonempty start
        for key, value in self._envShell.items():
            # cmd=self._cmd.replace('${'+key+'}',value)
            if key == 'cmd':  # do not change cmd
                log.debug('cmd type: %s' % type(value))
                # do not change, otherwise commands that have spaces will not work
                value = repr(value)
            log.info("Setting var: %s = %s" % (key, value))
            var = '='.join([key, value])
            shellvar = ' && '.join([shellvar, var])
        cmd = ' && '.join([shellvar, self._cmd])
        log.debug('cmd: %s' % cmd)
        return cmd

    @staticmethod
    def _user_input(ayes, cmd):
        if cmd.find('rm ') >= 0:
            return input('WARN: execute %s? %s for yes: ' % (cmd, ayes))
        else:
            return ayes

    def execute_task(self):
        cmd = self._parseCmdVars()
        log.debug('Executing CMD: %s' % cmd)
        ayes = 'y'
        if self._user_input(ayes, cmd) == ayes:
            # local(cmd) # works if using fabric
            if TaskABC.task.synch:
                log.info('Executing synch task %s' % cmd)
                # execution is synchornous (in series, not parallel).
                subprocess.run(cmd, shell=True,executable='/bin/bash')
            else:
                log.info('Executing Asynch task %s' % cmd)
                proc = subprocess.Popen(
                    cmd, shell=True, executable='/bin/bash',stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                return proc
