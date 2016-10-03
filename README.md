# Auscope-ErrorFinder
Scripts that will read the log and summary files for Auscope experiments,
To run the script, type 
```
python errorFinder.py"
```

in a terminal. The script will then ask the user to input the name of the experiment and the station code.

The script goes through the log looking for specific errors and finds the relavnt scans from the SUM file. I have uploaded two example logs and their corresponding SUM files for some test runs.
It currently only looks for windstows and slewing errors but it can be easily modified to look for any other errors. I recommend sticking with the modular approach. Your additions should take the form of a function/method which can be called from the main function.

Things to do:
- [ ] Include exceptions for bad user inputs. (If user inputs make no sense)
- [x] Include exceptions for IO errors. (Files could not be found)
- [ ] Add scp functionality to download the log
- [ ] Find missed scans.
