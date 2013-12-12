#!/usr/bin/env python

#hardcoded conditions
doOneColour = True
brStepSize  = 0.1
#
def banner():
        print '''
        +--------------------------------------------------------------
        |
        | plot_triangle.py
        |
        |     finds the intersection between the limits.txt and the theoretical
        |     also does multiple files at once with * wildcard, to find triangle
        |     plot
        |  
        | usage: 
        |    ./plot_triangle.py -l 'foldernames_*' -n 'append_name_to_save'
        |         -h for more help
        |         where foldernames are multiple files that contain limits.txt
        |
        |   
        | author: Michael Luk, 05 mar 13
        |
        +--------------------------------------------------------------
            '''
banner()
_legend = "[plotTriangle:]"        

#####################
#
# options
#
######################
from optparse import OptionParser
add_help_option = "./plot_triangle.py -ACTION [other options]"

parser = OptionParser(add_help_option)

parser.add_option("-f", "--file", dest="filename", default='limits.txt', 
		  help="filename/location of limits.txt")


parser.add_option("-l", "--list-of-files", dest="listoffiles", default='limits.txt', 
		  help="list of folders to make plot with: use wildcard * to indicate multiple directories")

parser.add_option("-n", "--name", dest="name", default='combined', 
		  help="name to append to savefile")


parser.add_option("-t", "--theory", dest="theoryfile", default='tprime_theory.ascii',
		  help="filename/ location of limits.txt")


parser.add_option("-c", "--channel", dest="channelname", default='',
		  help="channel name to add to the plot")


print _legend, 'parsing command line options...',
(options, args) = parser.parse_args()
print 'done'

limitFileName   = options.filename
theoryFileName  = options.theoryfile
filelist        = options.listoffiles
appendName      = options.name
channelName     = options.channelname

print "limitFileName ", limitFileName, "filelist = ", filelist


def find_intersection(limits_, theory_):
	#
        for key in range(500,850,50):
		
		if limits_[key] > theory_[key]:
			if key == 400:
				# too week to set limit
				return 400

			# in here, the xs is too weak to set a limit
			x0 = key - 50
			x1 = key
			
			y0 = limits_[x0]
			y1 = limits_[x1]
			m1 = (y1 - y0)/(x1-x0)
					
			y0p = theory_[x0]
			y1p = theory_[x1]
			m2  = (y1p - y0p)/(x1-x0)

			c1  = y1 - x1*(y1-y0)/(x1-x0)
			c2  = y1p - x1*(y1p-y0p)/(x1-x0)

			return  round(100 * (c2 - c1) / (m1 - m2))/100.

#
def getColumn(_fileName, nthColumn):

	file_  = open(_fileName,'r')	
	_nthColumnDict = {}

	for id,line in enumerate(file_):
		columns = line.split(" ")
		if "#" not in columns[0]:
			_nthColumnDict[round(float(columns[0]))] = float(columns[nthColumn].replace("\n",""))

	file_.close()
	return _nthColumnDict



def makeBRDict(stepSize = 0.1):
	versionCounter = 1
	BRr = range(0,11,int(round(10*stepSize)))
	BRDict = {}
	BRDict[0] = (0.5, 0.25, 0.25)
	for bw_ in BRr:
		for th_ in BRr:
			if (bw_+th_) <= 10:
				tz_ = 10 - bw_ - th_
				BRDict[versionCounter] = (round(bw_*10)/100., round(th_*10)/100., round(tz_*10)/100.)
				#print "("+str(versionCounter)+")","&", bw_/10.,"&", th_/10.,"&",tz_/10.,"\\\\"
				#print "counter", versionCounter
				versionCounter += 1
				
	return BRDict


def getObsExp(_limitFileName,_theoryFileName):
	"""
	# limits
	#
	# mass observed -2sig -1sig median_exp +1sig +2sig
	# -------------------------------------------
	500  0.16199  0.066496  0.092811  0.13588  0.20234  0.29836
	600  0.061975  0.037114  0.050605  0.070805  0.10106  0.1514
	700  0.055545  0.021078  0.029212  0.040897  0.05892  0.081807
	800  0.037912  0.014379  0.018497  0.02588  0.03716  0.051418
	900  0.020186  0.0098627  0.012963  0.018153  0.025971  0.03707
	1000  0.015139  0.006412  0.0089664  0.012829  0.018184  0.024917
	1100  0.017633  0.00587  0.0081242  0.01173  0.017775  0.024946
	1200  0.011271  0.0048906  0.0065896  0.0091507  0.013666  0.018503
	1300  0.013483  0.0045915  0.0063618  0.0093912  0.013811  0.019741
	1400  0.0095263  0.0038711  0.0053808  0.0078363  0.011378  0.015583
	1500  0.011826  0.0034208  0.0047425  0.0069339  0.010048  0.014563
	"""

	observedDict = getColumn(_limitFileName,2)
	twoSigmaDownDict = getColumn(_limitFileName,4)
	oneSigmaDownDict = getColumn(_limitFileName,6)
	expectedDict = getColumn(_limitFileName,8)
	oneSigmaUpDict = getColumn(_limitFileName,10)
	twoSigmaUpDict = getColumn(_limitFileName,12)

	theoryDict   = getColumn(_theoryFileName,1)

	
	# find the intersection points
	observed = find_intersection(observedDict, theoryDict)
	expected = find_intersection(expectedDict, theoryDict)
	two_sigma_down = find_intersection(twoSigmaDownDict, theoryDict)
	two_sigma_up = find_intersection(twoSigmaUpDict, theoryDict)
	one_sigma_down = find_intersection(oneSigmaDownDict, theoryDict)
	one_sigma_up = find_intersection(oneSigmaUpDict, theoryDict)
	return observed, two_sigma_down,one_sigma_down, expected, one_sigma_up, two_sigma_up



import array
from tdrStyle import *
from ROOT import *

def makeTrianglePlot(_versions,_limits,z_axis_name,plot_name,two_sigma_up = {}, two_sigma_down = {}, one_sigma_up = {}, one_sigma_down = {}, plotDifference = False, setMin = 450, setMax=800): 
	setTDRStyle()
	a = sqrt(3)/ 2
	
	gr2d = TGraph2D()
	Mlow_high = -999
	Mlow_low  = 9999

	counter = -1
	for key in sorted(_versions.keys()):
		counter += 1
				
		bW   = (_versions[key])[0]
		tH   = (_versions[key])[1]
		Mlow = _limits[key]

		if tH == 1:
			tH = 0.9999
			# fix infinite issue later
			
		if Mlow_high < one_sigma_down[key]: 
			Mlow_high = one_sigma_down[key] # will set the max of the z axis to the -2sigam, which is highest mass limit
		if Mlow_low > one_sigma_up[key]:
			Mlow_low = one_sigma_up[key]
		
		# fnd x-y coordinates to plot
		y = bW;
		m=(y-(1-tH)/2)/(1-tH)/a;
		x = (tH-0.333)*a+m*(1-tH)/2;
		gr2d.SetPoint(counter,x,y,Mlow);
		tZ=1-bW-tH;

	c1 = TCanvas("c1","Graph Draw Options",5000,4000,650,600);
	c1.SetGrid();
	c1.GetFrame().SetFillColor(42);
	c1.GetFrame().SetLineColor(kWhite);
	
	c1.SetRightMargin(0.2);
	c1.SetLeftMargin(0.08);
	c1.SetTopMargin(0.16);
	c1.SetBottomMargin(0.16);
	
	#
	# draw the graph with axis, contineous line, and put a * at each point                 
	#
	
	if doOneColour:
		#color=(gROOT.GetListOfColors().At(100));
		#color.SetRGB(1,0,0);
		#color=(gROOT.GetListOfColors().At(99));
		#color.SetRGB(1,0.3,0.3);
		#color=(gROOT.GetListOfColors().At(98));
		#color.SetRGB(1,0.5,0.5);
		#color=(gROOT.GetListOfColors().At(97));
		#color.SetRGB(1,0.6,0.6);
		#color=(gROOT.GetListOfColors().At(96));
		#color.SetRGB(1,0.65,0.65);
		#color=(gROOT.GetListOfColors().At(95));  
		#color.SetRGB(1,0.7,0.7);
		#color=(gROOT.GetListOfColors().At(94));
		#color.SetRGB(1,0.75,0.75);
		#color=(gROOT.GetListOfColors().At(93));
		#color.SetRGB(1,0.8,0.8);
		#color=(gROOT.GetListOfColors().At(92));
		#color.SetRGB(1,0.85,0.85);
		#color=(gROOT.GetListOfColors().At(91));
		#color.SetRGB(1,0.9,0.9);
		#color=(gROOT.GetListOfColors().At(90));		


		# [CC]
		color=(gROOT.GetListOfColors().At(100));
                color.SetRGB(1,0.05,0.05);
                color=(gROOT.GetListOfColors().At(99));
                color.SetRGB(1,0.1,0.1);
                color=(gROOT.GetListOfColors().At(98));
                color.SetRGB(1,0.15,0.15);
                color=(gROOT.GetListOfColors().At(97));
                color.SetRGB(1,0.20,0.20);
                color=(gROOT.GetListOfColors().At(96));
                color.SetRGB(1,0.25,0.25);
                color=(gROOT.GetListOfColors().At(95));
                color.SetRGB(1,0.30,0.30);
                color=(gROOT.GetListOfColors().At(94));
                color.SetRGB(1,0.35,0.35);
                color=(gROOT.GetListOfColors().At(93));
                color.SetRGB(1,0.40,0.40);
                color=(gROOT.GetListOfColors().At(92));
                color.SetRGB(1,0.45,0.45);
                color=(gROOT.GetListOfColors().At(91));
                color.SetRGB(1,0.50,0.50);
                color=(gROOT.GetListOfColors().At(90));
		color.SetRGB(1,0.55,0.55);
		color=(gROOT.GetListOfColors().At(89));
                color.SetRGB(1,0.60,0.60);
                color=(gROOT.GetListOfColors().At(88));
                color.SetRGB(1,0.65,0.65);
                color=(gROOT.GetListOfColors().At(87));
                color.SetRGB(1,0.70,0.70);
                color=(gROOT.GetListOfColors().At(86));
                color.SetRGB(1,0.75,0.75);
                color=(gROOT.GetListOfColors().At(85));
                color.SetRGB(1,0.80,0.80);
                color=(gROOT.GetListOfColors().At(84));
                color.SetRGB(1,0.85,0.85);
                color=(gROOT.GetListOfColors().At(83));
                color.SetRGB(1,0.90,0.90);
                color=(gROOT.GetListOfColors().At(82));
                color.SetRGB(1,0.95,0.95);
		color=(gROOT.GetListOfColors().At(81)); #450 mass point		
		color.SetRGB(1,1,1);

		#color_indices=array.array('i',[91, 92, 93, 94, 95, 96, 97, 98, 99, 100]);
		color_indices=array.array('i',[81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]);  

		gStyle.SetPalette(20,color_indices)
	else:
		gStyle.SetPalette(1);

        if plotDifference:
                gr2d.SetMinimum(-(Mlow_high-Mlow_low)/2)
                gr2d.SetMaximum((Mlow_high-Mlow_low)/2)
        else:
		gr2d.SetMinimum(setMin)
		gr2d.SetMaximum(setMax)


	gr2d.SetNpx(400);
	gr2d.SetNpy(400);
	
	
	
	gr2d.Draw("contz A ][");

	t = TLatex();
	t.SetTextAlign(21);
	t.SetTextSize(0.05);

	t.DrawLatex(0,1.06,"B(tW)");
	t.SetTextAlign(23);
	t.DrawLatex(-0.55,-0.08,"B(bZ)");
	t.DrawLatex(0.55,-0.08,"B(bH)");
	
	gr2d.SetTitle("");
	
	bWAxis = TGaxis(0,0.0,0,1,0,1,505);
	bWAxis.SetLabelOffset(999)
	bWAxis.SetLineWidth(1)
	bWAxis.Draw("S");

	tZAxis1 = TGaxis(0.288964,0.4978,-0.577058,0,0,1,505,"-+");
	tZAxis1.SetLabelOffset(999);
	tZAxis1.SetLineWidth(1)
	tZAxis1.Draw("S");

	tHAxis1 = TGaxis(-0.288964,0.49647,0.577062,0,0,1,505,"-+");
	tHAxis1.SetLabelOffset(999);
	tHAxis1.SetLineWidth(1)
	tHAxis1.Draw("S");
	t.SetTextAlign(22);
	
	
	axisline = TLine(-0.575, 0, 0.001, 0.9992)
	axisline . SetLineWidth(3)
	axisline.Draw("SAME")
	
	axisline2 = TLine(-0.575, 0, 0.575, 0)
	axisline2 . SetLineWidth(3)
	axisline2 .Draw("SAME")

	axisline3 = TLine(0.001,0.999, 0.575, 0)
	axisline3 . SetLineWidth(3)
	axisline3 .Draw("SAME")



	t.SetTextSize(0.04);
	t.DrawLatex(0.3183481,0.5115681,"0");
	t.DrawLatex(-0.605,-0.025,"1");
	t.DrawLatex(-0.3183481,0.5115681,"0");
	t.DrawLatex(0.6039,-0.025,"1");


	#bW axis labels
	t.DrawLatex( 0,-0.03,"0");
	t.DrawLatex(-0.05,.2,"0.2");
	t.DrawLatex(-0.05,0.4,"0.4");
	t.DrawLatex(-0.05,0.6,"0.6");
	t.DrawLatex(-0.05,0.8,"0.8");
	t.DrawLatex(-.03,1.01,"1");
	
	c1.SetFrameLineColor(0);
	
	t.SetTextSize(0.045);
	#t.DrawLatex(-0.65,1.15,"CMS preliminary 19.6 fb^{-1}");
	t.SetTextAlign(22);
	t.SetTextAngle(-90);
	

	latex = TLatex()
	latex.SetNDC()
	latex.SetTextSize(0.05)
	latex.SetTextAlign(11);
	latex.DrawLatex(0.03, 0.95, "CMS Preliminary");

	latex2 = TLatex()
	latex2.SetNDC()
	latex2.SetTextSize(0.035)
	latex2.SetTextAlign(31) # align right                                         
	latex2.DrawLatex(0.97, 0.93, "#intLdt=19.5 fb^{-1}, #sqrt{s} = 8 TeV");


	latex3 = TLatex()
	latex3.SetNDC()
	latex3.SetTextSize(0.05)
	#latex3.SetTextAlign(31) # align right                                         
	latex3.DrawLatex(0.035, 0.885, channelName);

	
	t.DrawLatex(0.835,0.5,z_axis_name+" b' Quark Mass Limit (GeV)");
	
        raw_input('press enter to continue...')
        #c1.SaveAs(plot_name+'.pdf')
	#c1.SaveAs(plot_name+'.png')
	

	
	




##############################
#
#  main code
#
#############################
if __name__ == '__main__':
	
        #################################################
	# this works for one filename, one theoryfilename
	#print getObsExp(limitFileName,theoryFileName)
	#################################################

	
	BRVersions =  makeBRDict(stepSize=brStepSize)
	
	observed = {}
	expected = {}
	two_sigma_up = {}
	two_sigma_down = {}
	one_sigma_up = {}
	one_sigma_down = {}

	difference = {} # difference between observed and expected

	file_notused = [True]*67
	import glob,sys
	_files = glob.glob(filelist)
	for key in sorted(BRVersions.keys()):
		for foldername in sorted(_files):
			
			if ("v"+str(key) == foldername[foldername.rindex("v"):]) and (file_notused[key]):
				# get the observed / expected limits
				observed[key],two_sigma_down[key],one_sigma_down[key],expected[key],one_sigma_up[key],two_sigma_up[key] = getObsExp(foldername+'/'+limitFileName,theoryFileName)
				# make the difference
				difference[key] = observed[key]-expected[key]
				
				print '('+str(key)+')',"&", round(BRVersions[key][0]*10.)/10., "&",round(BRVersions[key][1]*10.)/10.,
				print "&",round(BRVersions[key][2]*10.)/10.,"&",str(int(observed[key])),"&",str(int(expected[key]))+" & ["+str(int(one_sigma_up[key]))+","+str(int(one_sigma_down[key]))+"] & ["+str(int(two_sigma_up[key]))+","+str(int(two_sigma_down[key]))+"] \\\\"


				file_notused[key] = False # this ensures that the file is only used once, since we're starting from the smallest


	#####################################################################
	#
	# we now have BRversions, dict with keys label version number, 
	#  bw,th,tz branching ratio
	#   
	# observed and expected limits stored by, the key value....
	#
	#####################################################################
	#print BRVersions 
	#print observed, expected
	
			
	
	##############
	#
	# make the observed / expected limit triangle plots
	#
	# format is: 
	#      makeTrianglePlot(_versions,_limits,z_axis_name,plot_name,two_sigma_up = {}, two_sigma_down = {}, one_sigma_up = {}, one_sigma_down = {}, setMin = 600, setMax=850, plotDifference=False):
	#
	makeTrianglePlot(BRVersions,expected,'Expected','expected_'+appendName,two_sigma_up,two_sigma_down, one_sigma_up, one_sigma_down)
	makeTrianglePlot(BRVersions,observed,'Observed','observed_'+appendName,two_sigma_up,two_sigma_down, one_sigma_up, one_sigma_down)
	makeTrianglePlot(BRVersions,difference,'(Obs. - Exp.)','difference_'+appendName,two_sigma_up,two_sigma_down, one_sigma_up, one_sigma_down,True)




