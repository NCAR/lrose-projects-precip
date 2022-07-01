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
* File -> Save
* Run Scan

The scan will start immediately, and then interrupt at the next 12 minute boundary.

### Switching from IOP to Unattended

* Wait until you are in PrecipRhiUser
* Stop Scan
* Schedule -> Select PrecipUnattended
* Set Start At to next 12 minute boundary (hit Enter)
* Click Apply
* File -> Save
* Run Scan

The scan will start immediately, and then interrupt at the next 12 minute boundary.

## Recovering from SYS_IDLE insertion

Sometimes a SYS_IDLE becomes inserted in the current schedule, and the scan will stop.

This occurs if you inspect the RHI angle list and hit OK instead of Cancel.

If you do not want to change the RHI angles, then do not double-click on PrecipRhiUser. Rather, hover the mouse over ```PrecipRhiUser``` in the ```AngleList``` - the list of active angles will show.

If a SYS_IDLE does appear, stop the scan and restart as follows:

* Stop Scan
* Set Start At to next 12 minute boundary (hit Enter)
* Click Apply
* File -> Save
* Run Scan

