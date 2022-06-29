# Running the CIDD and Jazz displays for PRECIP

## Introduction

The NCAR-based data for the PRECIP displays resides on a server at EOL in Boulder.

You can access that data for display purposes, using either CIDD or Jazz.

## Preparation - CIDD

CIDD currently only runs under LINUX, so you will need to install it.

See the [CIDD installation instructions](https://github.com/NCAR/lrose-core/blob/master/docs/build/CIDD_build.linux.md)

## Preparation - Jazz

Jazz is a Java-based display supported by the Research Applications Laboratory (RAL) at NCAR.

See the Jazz main page at:

* [https://projects.ral.ucar.edu/jazz/](https://projects.ral.ucar.edu/jazz/)

You will need to install the latest OpenJdk version to run Jazz.

Open JDK vesion 18 is available from:

* [https://jdk.java.net/18/](https://jdk.java.net/18/)

The Oracle download page is [here](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html).

The OpenJdk download page is [here](https://openjdk.java.net/install/).

## Running CIDD

1. Make sure you have CIDD in your path. Check this with:

```
  which CIDD
```

2. Download the start script:

```
  wget https://raw.githubusercontent.com/NCAR/lrose-projects-eolbase/master/projDir/display/scripts/start_CIDD.precip
```

3. Make the start script executable:

```
  chmod +x start_CIDD.precip
```

4. Run it:

```
  ./start_CIDD.precip
```

## Running Jazz

1. Make sure you have java installed. Check this with:

```
  which java
  which javaws
```

2. Download the start script:

You can either go to the GitHub site:

```
```

```
  wget https://raw.githubusercontent.com/NCAR/lrose-projects-eolbase/master/projDir/display/scripts/start_Jazz.precip
```

3. Make the start script executable:

```
  chmod +x start_Jazz.precip
```

4. Run it:

```
  ./start_Jazz.precip
```

BTW - if you go to 'Realtime' - i.e. the current time - using the time controller at the bottom, you will need to click on a time in the time slider to get the data to retrieve and display correctly.

      
