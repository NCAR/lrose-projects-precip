# Running the GUI for different scan strategies

## Switching between schedules

There are 2 main schedules for PRECIP:

* PrecipIOP
* PrecipUnattended

### (a) Switching from Unattended to IOP

* Wait until you are in PrecipSur2
* Stop Scan
* File -> Open -> scan-you-want.json
* File -> Save As -> default.json
* Schedule -> Select PrecipIOP
* Set Start At to next 12 minute boundary (hit Enter)
* Click Apply
* File -> Save
* Run Scan

The scan will start immediately, and then interrupt at the next 12 minute boundary.

### (b) Switching from IOP to Unattended

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

### (a) Enter angles manually

* Ensure you are in the PrecipIOP schedule (see above)
* Do not do this while PrecipRhiUser is running. Best to do this in PrecipSur1 since that allows plenty of time
* Click on the main RHI tab
* In the RHI list box (left), select PrecipRhiUser
* In the AngleList box (right), double click on PrecipRhiUser
* A window with the current angles will pop up
* Set the angles you want. You can either type them in, or use the Fill with Equal Angle option.
* You should enter 12 RHI angles.
* If you make a mistake, click on Cancel
* If you are happy, click OK (DON'T do this if you have not made any changes)

The new angle list will take effect the next time PrecipRhiUser runs.

### (b) Read in a file with the desired angles

* Ensure you are in the PrecipIOP schedule (see above)
* Do not do this while PrecipRhiUser is running. Best to do this in PrecipSur1 since that allows plenty of time
* File -> Open -> scan-you-want.json
* File -> Save As -> default.json

The new angle list will take effect the next time PrecipRhiUser runs.

## Angle lists for PrecipRhiUser, by file name:

### east.json:

                10,
                20,
                37,
                52,
                67,
                110,
                120,
                130,
                145,
                155,
                165,
                175

### full360.json

                15,
                345,
                330,
                298,
                255,
                240,
                211,
                197,
                168,
                153,
                125,
                113

### initiation.json

                211,
                203,
                195,
                189,
                177,
                171,
                125,
                113,
                107,
                95,
                80,
                67.5

### north.json

                290,
                300,
                310,
                320,
                330,
                340,
                350,
                10,
                20,
                37,
                52,
                67

### northeast.json

                320,
                330,
                340,
                350,
                10,
                20,
                37,
                52,
                67,
                110,
                120,
                130

### northwest.json

                240,
                255,
                290,
                300,
                310,
                320,
                330,
                340,
                350,
                010,
                020,
                037

### south.json

                255,
                240,
                215,
                205,
                195,
                175,
                165,
                155,
                145,
                130,
                120,
                110

### southeast.json

                215,
                205,
                195,
                175,
                165,
                155,
                145,
                130,
                120,
                110,
                67,
                52

### southwest.json

                310,
                300,
                290,
                255,
                240,
                215,
                205,
                195,
                175,
                165,
                155,
                145

### west.json

                350,
                340,
                330,
                320,
                310,
                300,
                290,
                255,
                240,
                215,
                205,
                195
