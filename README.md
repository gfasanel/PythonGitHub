PythonGitHub
============

Information on using runTrianglePlot.py exclusion limit plot:

if you take the combinedModel.out out file from LandS you can use the shell script make_list.sh I made to create the individual limit.txt that go into directories such as multileptons_v0.
There will be about 67 directory (66 corresponding the the 0.1 BR increments and 1 for the benchmark point)


To create all the directories execute,

seq 0 66 | xargs -n 1 sh -c 'mkdir multileptons_v$0'

Then run,

./make_list.sh  list.txt

At this point you'll have 67 directories filled with limit.txt file in each one of the corresponding different BR combination (tW, bH, and bZ) order, which you can see
in the list.txt file what order it is in. The make_list.sh file will cat your combinedModel.out so make sure its in the same directory as the make_list.sh script. I used the
limits_multi_higgs_15apr13_10pc directory to put all this in (after you have a look at mine as an example you can delete the multilepton_v directories)

The python script that actually makes the triangle exclusion plot is runTrianglePlot.py (this is the version I used to make mine the original one is plot_triangle.py just so that you now)

the plotter will use the file ascii/bprime_theory_orginal.ascii to theory intersection with the CLs limits.

to run the triangle plotter execute,
./runTrianglePlot.py -l 'limits_multi_higgs_15apr13_10pc/multileptons_v*' -t ascii/bprime_theory.ascii

-l 'limits_multi_higgs_15apr13_10pc/multileptons_v*'  tells it where to get the limit.txt file it reads i and extracts the expected, observed and the 1 and 2 sigma CL values.
you do -t ascii/bprime_theory.ascii since originally this script was set up for t' and so you're not using the tprime_theory.ascii file.

One thing you might have to change is the mass ranges and plot ranges. The script will print out to the terminal the table used in the analysis. It will show 3 plots (after you hit enter
one after another)

To change mass range go to the function find_intersection(limits_, theory_)

this line,

for key in range(500,850,50):

last argument is the by how much you'd like to increment step from 500 to 800.

To change the ranges show in the plot go to makeTrianglePlot function and can change  setMin = 450, setMax=800 to what you need.
