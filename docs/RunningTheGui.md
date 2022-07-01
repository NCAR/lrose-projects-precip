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

If you do not want to change the RHI angles, then DO NOT double-click on PrecipRhiUser. Rather, hover the mouse over ```PrecipRhiUser``` in the ```AngleList``` - the list of active angles will show.

If a SYS_IDLE does appear, stop the scan and restart as follows:

* Stop Scan
* Select Schedule you want
* Set Start At to next 12 minute boundary (hit Enter)
* Click Apply
* File -> Save
* Run Scan

The scan will start immediately, and then interrupt at the next 12 minute boundary.

## Changing the list of RHI angles in the PrecipIOP schedule

### Enter angles manually

* Ensure you are in the PrecipIOP schedule (see above)
* Do not do this while PrecipRhiUser is running. Best to do this in PrecipSur1 since that allows plenty of time
* Click on the main RHI tab
* In the RHI list box (left), select PrecipRhiUser
* In the AngleList box (right), double click on PrecipRhiUser
* A window with the current angles will pop up
* Set the angles you want
* If you make a mistake, click on Cancel
* If you are happy, click OK (DON'T do this if you have not made any changes)


The new angle list will take effect the next time PrecipRhiUser runs.



