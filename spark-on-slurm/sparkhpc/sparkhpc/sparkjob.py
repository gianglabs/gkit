#
# 
# Running spark clusters on batch scheduling systems
#
# Author: Rok Roskar, ETH Zuerich, 2016
#
#
from __future__ import print_function
import subprocess
import time
import re
import signal 
import os
import json
import glob
import shlex
import sys
from importlib import resources
import logging
import signal


try: 
    get_ipython()
    IPYTHON=True
    from IPython.display import display, HTML
except NameError: 
    IPYTHON=False

class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# try to figure out which scheduler we have
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def get_scheduler():
    if which('bjobs') is not None: 
        scheduler = 'lsf'
    elif which('squeue') is not None: 
        scheduler = 'slurm'
    else:
        scheduler = None
        logger.warn('No suitable scheduler found')

    return scheduler

slaves_template = "{spark_home}/bin/spark-class org.apache.spark.deploy.worker.Worker --cores {cores_per_executor} {master_url}"


def _resolve_spark_home(explicit_spark_home=None):
    if explicit_spark_home and os.path.exists(explicit_spark_home):
        return explicit_spark_home

    env_spark_home = os.environ.get('SPARK_HOME')
    if env_spark_home and os.path.exists(env_spark_home):
        return env_spark_home

    try:
        import pyspark
        pyspark_module = os.path.dirname(pyspark.__file__)
        
        # Check if pyspark has jars directory (typical for pip/conda/pixi installations)
        if os.path.exists(os.path.join(pyspark_module, 'jars')):
            return pyspark_module
        
        # For traditional Spark distributions, try to find the root
        # pyspark is at /path/to/spark/python/pyspark or /path/to/spark/lib/python/pyspark
        # Try going up to find a directory with bin/spark-submit and jars/
        site_packages = os.path.dirname(pyspark_module)
        python_lib = os.path.dirname(site_packages)
        lib_dir = os.path.dirname(python_lib)
        conda_env_root = os.path.dirname(lib_dir)
        
        # Check if environment root has spark binaries
        if os.path.exists(os.path.join(conda_env_root, 'bin', 'spark-submit')):
            if os.path.exists(os.path.join(conda_env_root, 'jars')):
                return conda_env_root
            if os.path.exists(os.path.join(conda_env_root, 'bin', 'spark-class')):
                return conda_env_root
        
        # Fallback: check parent directory (for non-standard layouts)
        parent = os.path.dirname(conda_env_root)
        if os.path.exists(os.path.join(parent, 'bin', 'spark-submit')):
            return parent
            
    except Exception as e:
        pass

    return os.path.join(os.path.expanduser('~'), 'spark')

def get_launch_commands(scheduler):
    if scheduler == 'slurm':
        master_launch_command = '{0}'
        slaves_launch_command = 'srun ' + slaves_template
    elif scheduler == 'lsf':
        master_launch_command = '{0}'
        slaves_launch_command = 'mpirun --npernode 1 ' + slaves_template

    return master_launch_command, slaves_launch_command

home_dir = os.path.expanduser('~')

# set up logging

LOG_LEVEL = 'DEBUG' if os.environ.get('SPARKHPC_DEBUG', False) == '1' else 'INFO'
logging.basicConfig(level=getattr(logging,LOG_LEVEL))
logger = logging.getLogger('sparkhpc.sparkjob')


class SparkJob(object): 
    """
    Generic SparkJob class

    To implement other schedulers, you must simply extend this class 
    and define some class variables: 

    * `_peek_command` (command to get stdout of current job)
    * `_submit_command` (command to submit a job to the scheduler)
    * `_job_regex` (regex to get the job ID from return string of submit command)
    * `_kill_command` (scheduler command to kill a job)
    * `_get_current_jobs` (scheduler command to return jobid, status, jobname one job per line)
    

    See the LSFSparkJob class for an example.
    """

    table_header = """
                    <th>Job ID</th>
                    <th>Number of cores</th>
                    <th>Status</th>
                    <th>Spark UI</th>
                    <th>Spark URL</th>
                    """

    def __init__(self, 
                clusterid=None,
                jobid=None,
                ncores=4,
                cores_per_executor=1, 
                walltime='00:30',
                memory_per_core=2000, 
                memory_per_executor=None,
                jobname='sparkcluster',  
                template=None,
                extra_scheduler_options="", 
                config_dir=None, 
                spark_home=None,
                master_log_dir=None,
                master_log_filename='spark_master.out',
                scheduler=None,
                partition=None):
        """
        Creates a SparkJob
        
        Parameters:

        clusterid: int
            if a spark cluster is already running, initialize this SparkJob with its metadata
        jobid: int
            same as `clusterid` but using directly the scheduler job ID
        ncores: int
            number of cores to request
        walltime: string
            walltime in `HH:MM` format as a string
        memory_per_core: int
            memory to request per core from the scheduler in MB
        memory_per_executor: int
            memory to give to each spark executor (i.e. the jvm part) in MB
            If using pyspark and python workers need a lot of memory, 
            this should be less than `memory_per_core` * `ncores`.
        jobname: string
            name for the job - only used for the scheduler
        template: file path
            custom template to use for job submission
        extra_scheduler_options: string
            A string with custom options for the scheduler
        config_dir: directory path
            path to spark configuration directory
        spark_home: 
            path to spark directory; default is the `SPARK_HOME` environment variable, 
            and if it is not set it defaults to `~/spark`
        master_log_dir:
            path to directory; default is {spark_home}/logs
        master_log_filename:
            Name of the file that the Spark master's output will be written 
            to under {master_log_dir}; default is spark_master.out
        scheduler: string
            specify manually which scheduler you want to use; 
            usually the automatic determination will work fine so this should not be used
        partition: string
            SLURM partition to submit the job to (e.g., 'gpu', 'cpu', 'long', etc.)

        Example usage:
        

            from sparkhpc.sparkjob import sparkjob
            import findspark 
            findspark.init() # this sets up the paths required to find spark libraries
            import pyspark

            sj = sparkjob(ncores=10)

            sj.wait_to_start()

            sc = pyspark.SparkContext(master=sj.master_url())

            sc.parallelize(...)
        """
        if clusterid is not None:
            sjs = self.current_clusters()
            if clusterid < len(sjs): 
                jobid = sjs[clusterid].jobid
            else: 
                raise RuntimeError('cluster %d does not exist'%clusterid)

        # try to load JSON data for the job
        if jobid is not None: 
            jobid = str(jobid)
            try: 
                with open(os.path.join(home_dir, '.sparkhpc%s'%jobid)) as f:
                    self.prop_dict = json.load(f)
            except Exception as e: 
                raise(e)

        else:
            if spark_home is None: 
                spark_home = _resolve_spark_home()

            if memory_per_executor is None: 
                memory_per_executor = memory_per_core * cores_per_executor

            # save the properties in a dictionary
            self.prop_dict = {'ncores': ncores,
                              'cores_per_executor': cores_per_executor,
                              'walltime': walltime,
                              'template': template,
                              'memory_per_core': memory_per_core,
                              'memory_per_executor': memory_per_executor,
                              'config_dir': config_dir,
                              'jobname': jobname,
                              'jobid': jobid,
                              'status': None,
                              'spark_home': spark_home,
                              'master_log_dir': master_log_dir,
                              'master_log_filename': master_log_filename,
                              'scheduler': scheduler,
                              'workdir': os.getcwd(),
                              'extra_scheduler_options': extra_scheduler_options,
                              'partition': partition
                              }

        signal.signal(signal.SIGINT, self._sigint_handler)

    def _repr_html_(self): 
        table_header = "<tr>"+self.table_header+"</tr>"
        return table_header + self._to_string()


    def _to_string(self): 
        if IPYTHON:
            row = """
                    <td>{jobid}</td>
                    <td>{ncores}</td>
                    <td>{status}</td>
                    <td><a target="_blank" href="{ui}">{ui}</a></td>
                    <td>{url}</td>
                  """
            
        else:
            row = "Job id: {jobid}\nNumber of cores: {ncores}\nStatus: {status}\nSpark UI: {ui}\nSpark URL: {url}"

        return row.format(jobid=self.jobid, ncores=self.ncores, status=self.status, ui=self.master_ui(), url=self.master_url())


    def __getattr__(self, val): 
        if val in self.prop_dict: 
            return self.prop_dict[val]
        else: 
            raise AttributeError('%s not an attribute of this SparkJob'%val)

    def master_url(self): 
        """Get the URL of the Spark master"""
        return self._master_url(self.jobid)


    def master_ui(self): 
        """Get the UI address of the Spark master"""
        return self._master_ui(self.jobid)


    def _dump_to_json(self):
        """Write the data to recreate this SparkJob to a JSON file"""

        filename = os.path.join(home_dir, '.sparkhpc%s'%self.jobid)
        with open(filename, 'w') as fp:
            json.dump(self.prop_dict, fp)


    def wait_to_start(self, timeout=60):
        """Wait for the job to start or until timeout, whichever comes first"""

        if self.status != 'submitted':
            self.submit()

        timein = time.time()
        while(True): 
            if self.job_started(): 
                break
            time.sleep(1)


    def _peek(self): 
        """helper function to get the job output; needs to be overriden by subclasses"""
        pass


    def _get_master(self, jobid, regex = None, timeout=60):
        """Retrieve the spark master address for jobid"""

        if self._job_started(jobid): 
            timein = time.time()
            while time.time() - timein < timeout:
                job_peek = self._peek()
                logger.debug('job_peek = %s'%job_peek)

                master_url = re.findall(regex, job_peek)
                if len(master_url) > 0: 
                    break
                else:
                    time.sleep(0.5)
        
            if len(master_url) == 0: 
                raise RuntimeError('Unable to obtain information about Spark master -- are you sure it is running?')
            else:
                return master_url[0]
        else: 
            #logger.info('Job does not seem to be running')
            return None


    def _master_url(self, jobid, timeout=60): 
        """Retrieve the spark master address for jobid"""
        return self._get_master(jobid, regex='(spark://\S+:\d{4})',timeout=timeout)


    def _master_ui(self, jobid, timeout=60): 
        """Retrieve the web UI address for jobid"""
        return self._get_master(jobid, regex='(http://\S+:\d{4})',timeout=timeout)


    def submit(self): 
        """Write job file to current working directory and submit to the scheduler"""

        # check that the user has setup the java environment
        if 'JAVA_HOME' not in os.environ:
            raise RuntimeError('JAVA_HOME not set - please set it to the location of your java installation')

        if self.jobid is not None: 
            raise RuntimeError("This SparkJob instance has already submitted a job; you must create a separate instance for a new job")

        if self.template is None: 
            template_file = templates[self.__class__]
            # Try to get template from package resources first (for installed packages)
            try:
                template_str = resources.files('sparkhpc').joinpath('templates').joinpath(template_file).read_text()
            except (FileNotFoundError, TypeError, AttributeError):
                # Fallback for development versions: use file path relative to this module
                template_dir = os.path.join(os.path.dirname(__file__), 'templates')
                template_path = os.path.join(template_dir, template_file)
                with open(template_path) as f:
                    template_str = f.read()
        else : 
            with open(self.template) as template_file: 
                template_str = template_file.read()

        # Construct partition directive
        partition_directive = ""
        if self.partition:
            partition_directive = "#SBATCH -p {partition}".format(partition=self.partition)

        job = template_str.format(walltime=self.walltime, 
                                  ncores=self.ncores, 
                                  cores_per_executor=self.cores_per_executor,
                                  number_of_executors=int(self.ncores/self.cores_per_executor),
                                  memory_per_core=self.memory_per_core, 
                                  memory_per_executor=self.memory_per_executor,
                                  jobname=self.jobname, 
                                  spark_home=self.spark_home,
                                  master_log_dir=self.master_log_dir,
                                  master_log_filename=self.master_log_filename,
                                  extra_scheduler_options=self.extra_scheduler_options,
                                  partition=partition_directive)

        with open('job', 'w') as jobfile: 
            jobfile.write(job)

        self.prop_dict['jobid'] = self._submit_job('job')
        self.prop_dict['status'] = 'submitted'
        self._dump_to_json()

        sjs = self.current_clusters()
        clusterid = len(sjs)-1
        logger.info('Submitted cluster %d'%(clusterid))
        
        return clusterid

    @classmethod
    def _submit_job(cls, jobfile): 
        """Submits the jobfile and returns the job ID"""

        job_submit = subprocess.check_output(cls._submit_command%jobfile, shell=True).decode()

        logger.info(job_submit)
        try: 
            jobid = re.findall(cls._job_regex, job_submit)[0]
            logger.debug('found jobid = %s from submission output'%jobid)
        except Exception as e: 
            logger.error('Job submission failed or jobid invalid')
            raise e
        return jobid


    def stop(self): 
        """Stop the current job"""
        self._stop(self.jobid)
        self.prop_dict['status'] = 'stopped'


    @classmethod
    def _stop(cls, jobid):
        out = subprocess.check_output([cls._kill_command, jobid], stderr=subprocess.STDOUT).decode()
        logger.info(out)


    def job_started(self): 
        """Check whether the job is running already or not"""
        started = self._job_started(self.jobid)
        if started: 
            self.prop_dict['status'] = 'running'
            self._dump_to_json()
        return started


    @classmethod 
    def _job_started(cls, jobid): 
        command = shlex.split(cls._get_current_jobs)
        logger.debug('job status command: ' + cls._get_current_jobs)
        stat = subprocess.check_output(command).decode().split('\n')
        logger.debug('get_current_jobs: ' + '\n'.join(stat))
        
        running = False

        for line in stat:
            logger.debug('line: ' + ' '.join(line.split()))
            if len(line.split()) > 0:
                if line.split()[-1] == jobid:
                    try: 
                        running = 'RUN' in line.split()[1]
                    except IndexError: 
                        pass
        return running


    @classmethod
    def current_clusters(cls):
        """Determine which Spark clusters are currently running or in the queue"""
        
        # set up the command to query the scheduler for current jobs
        command = shlex.split(cls._get_current_jobs)
        
        # retrieve all the known job metadata files
        sparkjob_files = glob.glob(os.path.join(os.path.expanduser('~'),'.sparkhpc*'))
        sparkjob_files.sort()
        logger.debug('sparkjob files found: ' + '\n'.join(sparkjob_files))

        # get all the running job IDs from the scheduler
        jobs = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
        jobids = set([s.split()[2] for s in jobs.split('\n')[1:-1]])

        # generate SparkJob instances from the collected job IDs that have a metadata file
        sjs = []
        for fname in sparkjob_files: 
            jobid = os.path.basename(fname)[9:]
            if jobid in jobids: 
                sjs.append(cls(jobid=jobid))
        
        return sjs


    def show_clusters(self): 
        sjs = self.current_clusters()

        if len(sjs) == 0: 
            logger.info('No Spark clusters found')

        else:
            if IPYTHON:
                table_header = "<tr><td>ClusterID</td>"+self.table_header+"</tr>"
                table_rows = ""
                for i,sj in enumerate(sjs):
                    table_rows += "<tr>"+"<td>%s</td>"%i+sj._to_string()+"</tr>"
                display(HTML(table_header+table_rows))
            else: 
                for i,sj in enumerate(sjs): 
                    print('----- Cluster %d -----'%i)
                    print(sj._to_string())

    def start_spark(self,
                    spark_conf=None, 
                    executor_memory=None,
                    profiling=False, 
                    graphframes_package='graphframes:graphframes:0.3.0-spark2.0-s_2.11', 
                    extra_conf = None):
        """Launch a SparkContext 
        
        Parameters

        spark_conf: path
            path to a spark configuration directory
        executor_memory: string
            executor memory in java memory string format, e.g. '4G'
            If `None`, `memory_per_executor` is used. 
        profiling: boolean
            whether to turn on python profiling or not
        graphframes_package: string
            which graphframes to load - if it isn't found, spark will attempt to download it
        extra_conf: dict
            additional configuration options
        """

        if graphframes_package:
            os.environ['PYSPARK_SUBMIT_ARGS'] = "--packages {graphframes_package} pyspark-shell"\
                                                .format(graphframes_package=graphframes_package)
        else:
            os.environ['PYSPARK_SUBMIT_ARGS'] = "pyspark-shell"
        
        if 'SPARK_HOME' not in os.environ:
            os.environ['SPARK_HOME'] = _resolve_spark_home(self.spark_home)

        if spark_conf is None:
            spark_conf = os.path.join(os.environ['SPARK_HOME'], 'conf')

        os.environ['SPARK_CONF_DIR'] = os.path.realpath(spark_conf)

        os.environ['PYSPARK_PYTHON'] = sys.executable

        try:
            from pyspark import SparkContext, SparkConf
        except ImportError:
            try:
                import findspark
                findspark.init()
                from pyspark import SparkContext, SparkConf
            except ImportError:
                raise ImportError("Unable to find pyspark -- are you sure SPARK_HOME is set?")

        conf = SparkConf()

        conf.set('spark.driver.maxResultSize', '0')

        if executor_memory is None: 
            executor_memory = '%dM'%self.memory_per_executor

        conf.set('spark.executor.memory', executor_memory)

        if profiling: 
            conf.set('spark.python.profile', 'true')
        else:
            conf.set('spark.python.profile', 'false')
        
        if extra_conf is not None: 
            for k,v in extra_conf.items(): 
                conf.set(k,v)

        sc = SparkContext(master=self.master_url(), conf=conf)

        return sc    

    def _sigint_handler(self, signal, frame): 
        """Handle ctrl-c from the user"""
        self.stop()
        sys.exit(0)


def start_cluster(memory, 
                  cores_per_executor=1, 
                  timeout=30, 
                  spark_home=None, 
                  master_log_dir=None, 
                  master_log_filename='spark_master.out'):
    """
    Start the spark cluster

    This is the script used to launch spark on the compute resources
    assigned by the scheduler. 

    Parameters

    memory: string
        memory specified using java memory format
    timeout: int
        time in seconds to wait for the master to respond
    spark_home: directory path
        path to base spark installation
    master_log_dir: directory path
        path to directory where the spark master process writes 
        its stdout/stderr to a file name spark_master.out
    master_log_filename: string
        name of the file to write Spark master's output to.
    """

    scheduler = get_scheduler()
    master_launch_command, slaves_launch_command = get_launch_commands(scheduler)

    if spark_home is None:
        spark_home = _resolve_spark_home()
    spark_sbin = spark_home + '/sbin'

    os.environ['SPARK_EXECUTOR_MEMORY'] = '%s'%memory
    os.environ['SPARK_WORKER_MEMORY'] = '%s'%memory
    os.environ['SPARK_NO_DAEMONIZE'] = '1'

    env = os.environ
    
    # Start the master
    master_script = os.path.join(spark_sbin, 'start-master.sh')

    if scheduler=='slurm':
        # the master will start on the first host but gethostbyname doesn't always work, 
        # e.g. if using salloc 
        nodelist = subprocess.check_output(shlex.split('srun hostname -f')).decode().split('\n')[:-1]
        nodelist.sort()
        master_host=nodelist[0].split('.')[0]
    else:
        import socket
        master_host=socket.gethostbyname(socket.gethostname())
    
    os.environ['SPARK_MASTER_HOST'] = master_host
    if os.path.exists(master_script):
        master_command = master_launch_command.format(master_script)
    else:
        master_command = '{spark_home}/bin/spark-class org.apache.spark.deploy.master.Master --host {master_host}'\
            .format(spark_home=spark_home, master_host=master_host)

    logger.info('master command: ' + master_command)

    if (not master_log_dir) or (master_log_dir == 'None'):
        master_log_dir = os.environ.get('SLURM_SUBMIT_DIR', os.getcwd())

    if not os.path.exists(master_log_dir):
        os.makedirs(master_log_dir)

    master_log = os.path.join(master_log_dir,master_log_filename)
    logger.info('Logging spark master process output to:'+master_log)
    outfile = open(master_log, 'w+')
    master = subprocess.Popen(shlex.split(master_command), stdout=outfile, stderr=subprocess.STDOUT)

    started = False
    start_time = time.time()
    while not started: 
        with open(master_log,'r') as f: 
            log = f.read()
        try : 
            master_url, master_webui = re.findall('(spark://\S+:\d{4}|http://\S+:\d{4})', log)
            started = True
        except ValueError: 
            if time.time() - start_time < timeout:
                time.sleep(.5)
                pass
            else:
                stop_script = '{spark_sbin}/stop-master.sh'.format(spark_sbin=spark_sbin)
                if os.path.exists(stop_script):
                    subprocess.call(stop_script)
                else:
                    master.terminate()
                raise RuntimeError('Spark master appears to not be starting -- check the logs at: %s'%master_log)

    logger.info('['+bc.OKGREEN+'start_cluster] '+bc.ENDC+'master running at %s'%master_url)
    logger.info('['+bc.OKGREEN+'start_cluster] '+bc.ENDC+'master UI available at %s'%master_webui)

    sys.stdout.flush()
    slaves_command = slaves_launch_command.format(spark_home=spark_home, master_url=master_url, cores_per_executor=cores_per_executor)
    logger.info('slaves command: ' + slaves_command)
    p = subprocess.Popen(slaves_command, env = env, shell=True)
    p.wait()

    outfile.close()


from .lsfsparkjob import LSFSparkJob
from .slurmsparkjob import SLURMSparkJob

templates = {LSFSparkJob: 'sparkjob.lsf.template', SLURMSparkJob: 'sparkjob.slurm.template'}
_sparkjob_registry = {'lsf': LSFSparkJob, 'slurm': SLURMSparkJob}

def _sparkjob_factory(scheduler): 
    """Return the correct class for the given scheduler"""

    if scheduler in _sparkjob_registry:
        return _sparkjob_registry[scheduler]
    elif scheduler is None: 
        pass
    else: 
        raise RuntimeError('Scheduler %s not supported'%scheduler)


sparkjob = _sparkjob_factory(get_scheduler())
