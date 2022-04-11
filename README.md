# lrose-projects-precip

Run-time scripts and parameters for the NCAR/EOL/RSF PRECIP project in Taiwan.

## Server

The EOL component of this will run on the ```cirrus``` server.

## Account

On each server we have an ```rsfdata``` account.

All data management should be performed under this account.

The precip project params and scripts reside under:

```
  ~/git/lrose-projects-precip
```

On the server, you will find the links:

```
  ~/.cshrc -> projDir/system/dotfiles/cshrc
  ~/projDir -> git/lrose-projects-precip/projDir
  ~/projDir/data -> data directory
  ~/projDir/logs -> logs directory
```

```projDir``` is the top level entry point into the scripts and parameters for the project.

If you want to modify the ```.cshrc``` file, do this down in the projDir tree, and check it in.

## Project directory layout

| Directory name | Purpose |
|:-------------- |:------------- |
| alg | Algorithms - e.g. PID, TITAN |
| beamBlock | Running RadxBeamBlock |
| cal | Calibration |
| catalog | Creating images for the catalog |
| control | Controlling what runs |
| data | A link to the data directory |
| dial | MPD |
| display | HawkEye, CIDD, Jazz |
| docs | Documentation |
| ingest | Reading in data, reformatting etc. |
| logs | log files |
| qc | QC operations |
| qpe | For example RadxRate, RadxQpe |
| system | System scripts and parameters |

In most subdirectory, you will find:

| SubDir name | Purpose |
|:-------------- |:------------- |
| params | Parameter files |
| scripts | Scripts for starting processes etc. |

## System level scripts and parameters

The system-level scripts reside in:

```
  ~/projDir/system/scripts
```

These are the main controlling scripts for the project.

All of these ```scripts``` directories are included in the PATH. Therefore if you add a script, and run ```rehash```, that script will be available for use.

Executables and other high level scripts will reside in:

```
  ~/lrose/bin
```

The system-level parameters reside in:

```
  ~/projDir/system/params
```

and this directory includes the following link:

```
  ~/projDir/system/params/project_info
```

which points to the relevation project info for that host.

## Controlling the processes running on a host

### Processes that run all the time

The process list for each host is found in:

```
  ~/projDir/control/proc_list
```

This is a link which points to the process list for the host.

The process list looks something like this:

```
######################################################################
# PRECIP - on hail
######################################################################
# SYSTEM processes
Janitor             logs     start_Janitor.logs        snuff_inst
Scout               primary  start_Scout               kill_Scout
DataMapper          primary  start_DataMapper          kill_DataMapper
######################################################################
# SERVER processes
DsServerMgr         primary  start_inst(no-params)     snuff_inst
DsProxyServer       primary  start_inst(no-params)     snuff_inst
DsMdvServer         manager  start_inst(no-params)     snuff_inst
######################################################################
# Base observations ingest - from LDM
InputWatcher        mrms_conus_plus    start_inst(ingest)  snuff_inst 
Metar2Spdb          ops                start_inst(ingest)  snuff_inst 
LdmDynamic2Static   metar              start_inst(ingest)  snuff_inst
######################################################################
# Interpolate surface data
SurfInterp          ops                start_inst(alg)     snuff_inst
# etc. etc.
######################################################################
```

The 4 columns are as follows:

* Column 1: name of application or script to run
* Column 2: instance of the process
* Column 3: start script for the process
* Column 4: kill script for the process

The start and kill scripts can be actuall script names.

Alternatively they may be macros as follows:

* start_inst(dir): starts the specified application, using the parameter file ```appname.instance``` in the directory ```dir```.
* start_inst(no-params): starts the specified application, without specifying a parameter file
* snuff_inst: kills ```appname.instance```.

### Processes that run at given times - controlled by ```cron```

The cron table for each host is found in:

```
  ~/projDir/control/crontab
```

This is a link which points to the cron table for the host.

These are standard cron tables.

See [geeksforgeeks](https://www.geeksforgeeks.org/crontab-in-linux-with-examples/) for examples.

There are many web pages on writing cron tables.

## Starting and stopping the system

To start the system, run ```start_all```.

This will run ```~/projDir/system/scripts/start_all```.

```start_all``` will in turn do the following:

* start the process mapper: ```procmap```.
* start all of the processes in ```proc_list``` by running ```procmap_list_start```.
* start the auto-restarter: ```procmap_auto_restart```.
* install the cron table by running ```install_crontab```.

```procmap_list_start``` goes through all of the processes in ```proc_list``` and runs their start scipts.

The process_mapper ```procmap``` keeps a registry of all running processes.

All processes listed in the ```proc_list``` register with ```procmap```, generally once every 60 secons.

```procmap_auto_restart``` periodically checks with ```procmap``` to see which processes are running. It checks this against ```proc_list```, and if necessary restarts any missing processes.

To see what is running, type ```ppm```. This is an alias for ```print_procmap -hb -up -status```.

To see what processes are missing, run ```pcheck```. This is an alias for ```procmap_list_check -proc_list $PROJ_DIR/control/proc_list```.

## Keeping track of the data

The main environment variable for the data tree is $DATA_DIR. All data is stored relative to this location.

The ```DataMapper``` process keeps a registry of all data sets stored on the host.

Processes which write data generally register with the ```DataMapper``` after each write.

In addition the ```Scout``` process crawls the tree below $DATA_DIR, accumulating stats on the files and bytes used.

To see the data list type ```pdm```. This is an alias for ```PrintDataMap -all -relt -lreg```.

## Adding a process to the proc_list

When adding a process to run, decide which directory to use.

For example, a process reading in or converting data would go in ```~/projDir/ingest```. Or an algorithm such as ```Titan``` would go in ```~/projDir/alg```.

In the ```params``` subdirectory, add the parameter file. Generally this should be named ```appname.instance```. For example, ```RadxConvert.kftg``` for converting NEXRAD data from the KFTG radar.

If the parameter file is named in this way, you can use ```start_inst``` to start it via ```procmap_list_start``` or ```procmap_auto_restart```.

Such an app would have something like the following in the ```proc_list```:

```
RadxConvert   kftg  start_inst(ingest)     snuff_inst
```

If the app needs its own start script, write that and save it in the ```scripts``` subdirectory.

Then the entry in ```proc_list``` would look like the following:

```
Scout               primary  start_Scout               kill_Scout
```

After adding the entry to ```proc_list```, you can either wait for the app to be started by ```procmap_auto_restart```, or you can use ```start_all``` to go through the proc_list starting all apps that are not already running.

## Adding a script running under cron

To add a script running under cron:

* write the script, add it to the relevant ```scripts``` subdirectory.
* add a cron entry to ```~/projDir/control/crontab```.
* run ```install_crontab```.
* run ```crontab -l``` to check for your cron entry.
* monitor the logs to make sure your script is running.

## Logging and the LogFilter

LogFilter is an application that will read from ```stdin``` and copy what it reads to a log file.

```
Usage: LogFilter -d logdir -p procname [options as below]
options:
       [ -h ] produce this list.
       [ -debug ] print debug messages
       [ -p ] set process name 
       [ -i ] set process instance
       [ -hourly ] set the logs to be placed in hourly files
       [ -single ] create a single log file, not one per day
       [ -t ] interval between time stamp prints (sec)
              defaults to 3600, -1 disables printing
       [ -keepRunningOnError ] keep running if an error occurs
       [ -noLineStamp ] do not time-stamp every line
```

We use LogFilter to read the output from apps running on the system, and write this output neatly to dated subdirectories on the disk.

The two main logging directories are:

```
  ERRORS_LOG_DIR = ~/projDir/logs/errors
  RESTART_LOG_DIR = ~/projDir/logs/restart
```

The ```errors``` directory contains the output from the applications.

The ```restart``` directory contains the output from any restarts performed by ```procmap_auto_restart```.

In the ```crontab``` for each host you will see the following entry:

```
# Build links to log date subdirs
*/5 * * * *   csh -c "start_build_logdir_links" 1> /dev/null 2> /dev/null
```

This runs every 5 minutes, and it create 2 links in the log directories.

```
  yesterday -> points to yesterday's day directory
  today -> points to today's day directory
```

You can use these as shorthand when watching a log file grow.

For example:

```
  tail -f ~/projDir/logs/errors/today/rsync.potsdam_gps_results_to_snow.log
```


