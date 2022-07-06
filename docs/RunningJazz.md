# Installing and running the Jazz display for PRECIP

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

The following is a tutorial from PRECIP participants on how to install openJDK 18 on Windows:

* [JazzInstallOnWindows.pdf](./JazzInstallOnWindows.pdf)

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

      
## Using the Jazz GUI

### main_window.png

<img align="center" src="./images/Jazz/main_window.png">

### archive_main_window.png

<img align="center" src="./images/Jazz/archive_main_window.png">


### archive_main_window2.png

<img align="center" src="./images/Jazz/archive_main_window2.png">



### main_menu.png

<img align="center" src="./images/Jazz/main_menu.png">


### file_menu.png

<img align="center" src="./images/Jazz/file_menu.png">

### load_config.png

<img align="center" src="./images/Jazz/load_config.png">




### grid_menu.png

<img align="center" src="./images/Jazz/grid_menu.png">


### grid_table.png

<img align="center" src="./images/Jazz/grid_table.png">


### grids_menu.png

<img align="center" src="./images/Jazz/grids_menu.png">


### features_menu.png

<img align="center" src="./images/Jazz/features_menu.png">


### features_menu2.png

<img align="center" src="./images/Jazz/features_menu2.png">


### draw_rhi.png

<img align="center" src="./images/Jazz/draw_rhi.png">

### measured_rhi.png

<img align="center" src="./images/Jazz/measured_rhi.png">


### reconstructed_rhi.png

<img align="center" src="./images/Jazz/reconstructed_rhi.png">

### maps_menu.png

<img align="center" src="./images/Jazz/maps_menu.png">


### maps_menu2.png

<img align="center" src="./images/Jazz/maps_menu2.png">


### tools_menu.png

<img align="center" src="./images/Jazz/tools_menu.png">


### tools_menu2.png

<img align="center" src="./images/Jazz/tools_menu2.png">


### tools_grids.png

<img align="center" src="./images/Jazz/tools_grids.png">


### vel_field.png

<img align="center" src="./images/Jazz/vel_field.png">


### vel_field_and_menu.png

<img align="center" src="./images/Jazz/vel_field_and_menu.png">


### views_menu.png

<img align="center" src="./images/Jazz/views_menu.png">


### views_menu2.png

<img align="center" src="./images/Jazz/views_menu2.png">


### time_and_anim.png

<img align="center" src="./images/Jazz/time_and_anim.png">


### zoom.png

<img align="center" src="./images/Jazz/zoom.png">


### color_scale_menu.png

<img align="center" src="./images/Jazz/color_scale_menu.png">


### color_scale_editor.png

<img align="center" src="./images/Jazz/color_scale_editor.png">


### customize_features.png

<img align="center" src="./images/Jazz/customize_features.png">


### customize_maps.png

<img align="center" src="./images/Jazz/customize_maps.png">


### inspect.png

<img align="center" src="./images/Jazz/inspect.png">


