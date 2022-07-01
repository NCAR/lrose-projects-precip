# Running the GUI for different scan strategies

## Switching between schedules

There are 2 main schedules for PRECIP:

* PrecipIOP
* PrecipUnattended

### Switching from Unattended to IOP

* Wait until you are in PrecipSur2
* Stop Scan
* File -> Read -> scan-you-want.json
* File -> Save As -> default.json
* Schedule -> Select PrecipIOP
* Set Start At to next 12 minute boundary (hit Enter)
* Click Apply
* Click Save
* Run Scan

### Switching from IOP to Unattended

* Wait until you are in PrecipRhiUser
* Stop Scan
* Schedule -> Select PrecipUnattended
* Set Start At to next 12 minute boundary (hit Enter)
* Click Apply
* File -> Save
* Run Scan

## Recovering from SYS_IDLE insertion

* Stop Scan
* Set Start At to next 12 minute boundary (hit Enter)
* Click Apply
* File -> Save
* Run Scan

