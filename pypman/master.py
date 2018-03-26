import os
import collections
# import pypman.util
# from . util import Util
# from pypman.util import Util
from . import util
from . taskABC import TaskABC as Tabc
from . tasks import PythonNodeTask,GlobalTask
import logging
import warnings
import time

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler()) 

#######################################
# memory-profile: uncomment when testing efficiency  
# from memory_profiler import profile
# @profile
#######################################

def master(taskAlias,**kwargs):   
    '''   The main function '''    

    Tabc.pypmanConfigPath= os.path.join(os.getcwd(), 'pypman')
    logging.captureWarnings(True)
    log.info('Welcome to pypman!')    
    log.info('Current dir: %s'%os.getcwd())
    log.info('PYPMAN_CONFIG_PATH:%s'%Tabc.pypmanConfigPath)                               
 
    mapClasses={'gb':GlobalTask,'python':PythonNodeTask,'node':PythonNodeTask} 
    file=os.path.join(Tabc.pypmanConfigPath,'pypman.yml')
    log.info('Master config file: %s'%file)     
    Tabc.masterConfig=util.loadYml(file) 
    processInfo = collections.namedtuple('processInfo', 'process tname')
    processInfoList=[]
    targetHosts=Tabc.masterConfig['targetHosts']
    for thost in  targetHosts:   
        Tabc.setHost(thost)         
        log.debug(Tabc.host) 
        Tabc.setProject(taskAlias)
        log.debug(Tabc.project)        
        tList=Tabc.taskList(taskAlias)
        log.info('Task list %s' %tList)   
        for tname in tList:
            Tabc.setTask(tname) 
            log.info('Running task:%s'%tname) 
            executer={}  
            if Tabc.task.fname=="node" or Tabc.task.fname=="python":                 
                executer=mapClasses[Tabc.task.fname](**kwargs)
            else:
                executer=mapClasses["gb"](**kwargs) # global task  
            log.info('executing task %s on host %s '%(tname,Tabc.host.cfg['name']))
            if Tabc.task.synch:
                executer.execute_task() # tasks are executed in series (when user interaction is needed or when one task depends on the other)
            else:                   
                processInfoList.append(processInfo(executer.execute_task(),tname))#asynch exec; tasks are executed in parallel
    if not Tabc.task.synch:
        i=0        
        while processInfoList: 
            i=i+1
            log.debug('i= %s'%i)
            j=0
            for pinf in processInfoList:
                j=j+1
                log.debug('j=%s'%j)
                rcd = pinf.process.poll()
                log.debug(rcd)
                if rcd is None: # No process is done, wait a bit and check again.           
                    log.info('running task %s and buffering output.'%pinf.tname)
                    time.sleep(0.5)# too small or too large is not good; optimize case by case                  
                else: # Process finished.
                    log.info('%s %s'%(pinf.tname,pinf.process.stdout.read().decode('utf-8')))
                    log.info('Task %s is done.'%pinf.tname)
                    processInfoList.remove(pinf)
                    break
    return  