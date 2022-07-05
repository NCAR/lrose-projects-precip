# Running the Jazz display for PRECIP

## Introduction

The NCAR-based data for the PRECIP displays resides on a server at EOL in Boulder.

You can access that data for display purposes, using either CIDD or Jazz.

Jazz is a Java-based display supported by the Research Applications Laboratory (RAL) at NCAR.

See the Jazz main page at:

* [https://projects.ral.ucar.edu/jazz/](https://projects.ral.ucar.edu/jazz/)

## Installing Java

You will need to install the latest OpenJdk version to run Jazz.

Open JDK vesion 18 is available from:

* [https://jdk.java.net/18/](https://jdk.java.net/18/)

### Installing OpenJDK on Windows:

The following video shows how to install OpenJDK 18 on Windows:

* [https://www.youtube.com/watch?v=DSwGFXjB8U8](https://www.youtube.com/watch?v=DSwGFXjB8U8)

### Installing OpenJDK on Linux or Mac

Download the ```tar.gz``` file from:

* [https://jdk.java.net/18/](https://jdk.java.net/18/)

Untar this in a ```java``` subdirectory of your home directory.

In this example we are downloading ```openjdk-18.0.1.1```.

```
  mkdir ~/java
  cd ~/java
  tar xvfz ~/Downloads/openjdk-18.0.1.1_linux-x64_bin.tar.gz
```  

Then, in your environment, set JAVA_HOME:

```
  setenv JAVA_HOME ~/java/jdk-18.0.1.1
```

or:

```
  export JAVA_HOME=$HOME/java/jdk-18.0.1.1
```

And add ```$JAVA_HOME/bin``` to your path.

Then you should be able to run:

```
  which java
```

and get the response:

```
  /home/user/java/jdk-18.0.1.1/bin/java
```

## Downloading jazz and the jazz .xml parameter files

Put these in ```~/jazz```.

From the Jazz web page:

* [https://projects.ral.ucar.edu/jazz/](https://projects.ral.ucar.edu/jazz/)

download ```jazz.zip```, and follow the instructions on unzipping it.

```
  mkdir ~/jazz
  cd ~/jazz
  unzip ~/Downloads/jazz.zip
```

Then download the Jazz .xml parameter files from:

* [jazz4precip.xml](https://raw.githubusercontent.com/NCAR/lrose-projects-precip/main/projDir/display/params/jazz4precip.xml)
* [jazz4spol.xml](https://raw.githubusercontent.com/NCAR/lrose-projects-precip/main/projDir/display/params/jazz4spol.xml)

## Running jazz

Run the start script. On Linux or Mac, this will be:

```
  cd ~/jazz
  chmod +x runJazz.sh
  ./runJazz.sh
```

Jazz will start, and request that you select a parameter file.

The following 2 setups are available:

* ```jazz4precip.xml```: integrated data sets including satellite, models, radar
* ```jazz4spol.xml```: S-Pol-centric display in km coords

BTW - if you go to 'Realtime' - i.e. the current time - using the time controller at the bottom, you will need to click on a time in the time slider to get the data to retrieve and display correctly.

      