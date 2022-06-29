# Running the CIDD display for PRECIP

## Introduction

The NCAR-based data for the PRECIP displays resides on a server at EOL in Boulder.

You can access that data for display purposes, using either CIDD or Jazz.

## Preparation - CIDD

CIDD currently only runs under LINUX, so you will need to install it.

See the [CIDD installation instructions](https://github.com/NCAR/lrose-core/blob/master/docs/build/CIDD_build.linux.md)

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

