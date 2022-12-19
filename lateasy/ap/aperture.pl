#!/usr1/local/bin/perl5

#####################
# aperture.pl
#####################
#
#
# Robin Corbet (UMBC), 2012-01-04
#
#
######################

use strict 'subs';
use strict 'refs';

$VERSION = "1.53";

$help = "
aperture.pl 

Typing
\$ aperture.pl -help
will display this help information.

This is a Perl script that generates Fermi LAT light curves using
aperture photometry. This is not an official part of the Fermi
analysis software.

To use the script you can either type:
\$ perl aperture.pl
or
you can make the file executable (e.g. chmod +x aperture.pl) and edit
the first line of this script to point at your local installation of
perl.

The default value of parameters may be optionally taken from a file.
e.g.
\$ aperture.pl -file aperture.par

The script can be run in non-interactive mode where parameter values
will not be prompted for using the \"-batch\" flag. This
can be combined with the \"-file\" option.
e.g.
\$ aperture.pl -batch -file aperture.par

To generate a parameter file use:
\$ aperture.pl -makepar [filename]
If no file name is specififed, a file called \"aperture.par\" will be created.

To use this script you must be set up to run both the Fermi science
tools and HEASOFT.
This script checks the environment variables LHEASOFT, PFILES, and
FERMI_DIR as a check on this.


Among the inputs prompted for are two files:
slist.dat
        This should contain a list of source names and their coordinates
        in the form:
        2FGLJ0240.5+6113 40.1317, 61.2281
        Note that there is _no_ space in the source name.
        i.e. \"2FGLJ0240.5+6113\" rather than \"2FGL J0240.5+6113\"

Source names should not be duplicated because the output files are
constructed from the source names.


plist.dat
        This contains a list of photon files, one file per line.
It is also necessary to provide a single spacecraft (FT2) file.

Several temporary files are created while running this script.
At least most are deleted at the end.


One output file is produced for each source in the slist.dat file.
The file has the name of the source with \"lc_\" prepended and \".out\" appended.
e.g. lc_2FGLJ0240.5+6113.out

Each output file has the format:
Time (MJD), count rate (cts/cm2/s), count-rate based error (cts/cm2/s), bin half width (days), exposure-based error (cts/cm2/s), exposure (cm^2 s)

For many purposes the exposure-based error is recommended.

The count-rate based errors use the prescription of the BaBar
Statistics Working Group.
http://www-cdf.fnal.gov/physics/statistics/notes/pois_eb.txt The
asymmetric errors from this prescription are then \"symmeterized\" to
produce a single number.

Both the exposure-based and count-rate based errors will give non-zero
errors, even if no photons are detected in a time bin.

-version
	Print version number of script then exit.
-batch
	Runs with minimal output and no prompting for inputs.
-makepar [filename]
	Generates a default parameter file with the name [filename]. If no name
	is given the file generated is like_lc.par
-file [filename]
	Reads parameter values from a file with the name [filename].
-start [start time in MJD]
	Specify start time for light curve in Modified Julian Day.
-stop [stop time in MJD]
	Specify end time for light curve in Modified Julian Day.


History:
V1.53	- bug fix (missing routines)
V1.52	- add start and stop command line options
V1.51	- updated help information
V1.5	- Pass 8 support added (default)
V1.42	- correction to flux units in help information
V1.41	- minor changes. Change default energy upper limit to 300 GeV
V1.4	- add Pass7 reprocessed option
V1.31	- add \"-makepar\" option
V1.3	- add \"-batch\" and \"-file\" options
V1.21	- change default to _not_ barycenter times
V1.2	- change to checks on whether needed environment variables are set.
V1.1	- remove calls to sunpos and increase Sun avoidance defaults now that
solar position is given in spacecraft files.
V1.0	- initial release

";

$TRUE = 1;
$FALSE = 0;

$FT2LIST = $FALSE;

$BATCH = $FALSE;

# Default, prompted for parameters
$DEFAULT_BIN_SIZE = 1;
$DEFAULT_ROI = 1;
$DEFAULT_ZENITH_LIMIT = 105;
$DEFAULT_ROCK = 90;
$DEFAULT_BORE = 180;
$DEFAULT_EVENT_CLASS_MIN = 3;
$DEFAULT_SOURCE_LIST = "slist.dat";
$DEFAULT_FT1_LIST = "plist.dat";
$DEFAULT_FT2 = "lat_spacecraft_merged.fits";


#$DEFAULT_IRF_CODE = 4; # P7REP
$DEFAULT_IRF_CODE = 6; # P8

$DEFAULT_SUN_MINIMUM = 5.0;


# Default energy range parameters
$DEFAULT_EMIN = 100;
$DEFAULT_EMAX = 300000;

$DEFAULT_SPECTRAL_INDEX = -2.1;

$DEFAULT_BARYCENTER = $TRUE;

$DEFAULT_PREFIX = "";

$DEFAULT_PARAMETER_FILE = "aperture.par";

$chatter = 2;

$start_time = 0;
$stop_time = 9e99;


print "aperture.pl: V$VERSION (R. Corbet)\n";


# Check command line parameters


$numArgs = $#ARGV + 1;
#if($numArgs > 0){print "$numArgs command-line arguments:\n"};

foreach $argnum (0 .. $#ARGV) {

   print "$ARGV[$argnum]\n";
        if($ARGV[$argnum] =~ /-batch/) {
                print "Batch mode - no parameter prompting\n";
                $BATCH = $TRUE;
                }
        elsif($ARGV[$argnum] =~ /-help|-h|--help/) {
                print $help;
                exit;
        }
	elsif($ARGV[$argnum] =~ /-version/) {
		print "aperture.pl: Version $VERSION\n";
		exit;
	}
	elsif($ARGV[$argnum] =~ /-file/) {
		if($argnum+1 < $numArgs){
			$parameter_filename = $ARGV[$argnum+1];
			print "parameter_filename = $parameter_filename\n";
			set_defaults();
		}
		else{
			print "No input parameter file name given, using default of $DEFAULT_PARAMETER_FILE\n";
			$parameter_filename = $DEFAULT_PARAMETER_FILE;
			set_defaults();
		}

	}
	elsif($ARGV[$argnum] =~ /-makepar/) {
		if($argnum+1 < $numArgs){
			$output_parameter_filename = $ARGV[$argnum+1];
			print "output parameter_filename = $output_parameter_filename\n";
			write_defaults();
		}
		else{
			print "No output parameter file name given, using default of $DEFAULT_PARAMETER_FILE\n";
			$output_parameter_filename = $DEFAULT_PARAMETER_FILE;
			write_defaults();
		}

	}
	elsif($ARGV[$argnum] =~ /-start/) {
		if($argnum+1 < $numArgs){
			$start_time = mjd2met($ARGV[$argnum+1]);
			print "start time = $start_time\n";
		}
		else{
			print "No input start time value given\n";
		}

	}
	elsif($ARGV[$argnum] =~ /-stop/) {
		if($argnum+1 < $numArgs){
			$stop_time = mjd2met($ARGV[$argnum+1]);
			print "stop time = $stop_time\n";
		}
		else{
			print "No input stop time value given\n";
		}

	}
}







# Check if FTOOLS are available

if (!defined($status = $ENV{'LHEASOFT'})  ||  !defined($status = $ENV{'PFILES'})  )
{
    print "\n Error: You need to set up HEASOFT to use this script.\n";
    print " e.g. typically you need to type \"ftools\".\n";
    exit(0);
}

# Check if environment variable FERMI_DIR set
if (!defined($status = $ENV{'FERMI_DIR'} ))
{
    print "\n Error: You need to set up the Fermi Science Tools to use this script.\n";
    print " e.g. typically you need to type \"fermi\".\n";
    exit(0);
}




# Official Fermi directory
$fermi_dir = $ENV{'FERMI_DIR'};


# EXPERIMENT WITH SETTING PFILES TO OTHER DIRECTORY
# WITHIN SCRIPT (useful if running multiple instances of the script
#$ENV{'PFILES'} = $ENV{'HOME'}."/pfiles3".":".$ENV{'PFILES'};



$irf_code = get_value("Which IRFs? (1 = P6_V3, 2 = P6_V11, 3 = P7_V6, 4 = P7REP, 5 = P7REP/newbackground, 6 = P8)", $DEFAULT_IRF_CODE, 1, 6);
if($irf_code == 1){
	$irf_prefix = "P6_V3_";
	$gll_file = "galdiffuse/gll_iem_v02.fit";
	$isotropic_file = "galdiffuse/isotropic_iem_v02.txt";
	$galactic_name = "gal_v02";
	$extra_galactic_name = "eg_v02";
	}
elsif($irf_code == 2){
	$irf_prefix = "P6_V11_";
	$gll_file = "galdiffuse/gll_iem_v02_P6_V11_DIFFUSE.fit";
	$isotropic_file = "galdiffuse/isotropic_iem_v02_P6_V11_DIFFUSE.txt";
	$galactic_name = "gal_v02";
	$extra_galactic_name = "eg_v02";
	}
elsif($irf_code == 3){
	$irf_prefix = "P7_V6_";
	$gll_file = "diffuseModels/gal_2yearp7v6_v0.fits";

# This hardwires in "source" for now. Other alternative would be "clean".
	$isotropic_file = "diffuseModels/iso_p7v6source.txt";


	$galactic_name = "gal_2yearp7v6_v0";
	$extra_galactic_name = "iso_p7v6source";
	}

elsif($irf_code == 4){
	$irf_prefix = "P7REP_";
	$gll_file = "galdiffuse/gll_iem_v05.fits";

# This hardwires in "source" for now. Other alternative would be "clean".
	$isotropic_file = "galdiffuse/iso_source_v05.txt";
	$galactic_name = "gll_iem_v05";
	$extra_galactic_name = "iso_source_v05";
	}


# IRF code is "overloaded" to also specify the fixed versions
# of the background files
elsif($irf_code == 5){
	$irf_prefix = "P7REP_";


	$gll_file = "galdiffuse/gll_iem_v05_rev1.fit";

# This hardwires in "source" for now. Other alternative would be "clean".
	$isotropic_file = "galdiffuse/iso_source_v05_rev1.txt";

	$galactic_name = "gll_iem_v05_rev1";
	$extra_galactic_name = "iso_source_v05";
	}

elsif($irf_code == 6){
	$irf_prefix = "P8R2_";


# Galactic interstellar
	$gll_file = "galdiffuse/gll_iem_v06.fits";


# isotropic
	$isotropic_file = "galdiffuse/iso_P8R2_SOURCE_V6_v06.txt";

	$galactic_name = "gll_iem_v06";
	$extra_galactic_name = "iso_source_v06";
}




else{
	print "Got an invalid IRF code ($irf_code) somehow!\n";
} 



$prefix = get_string("Give any prefix for output file name(s) [optional]", $DEFAULT_PREFIX);



$bary = get_yn("Barycenter light curves?", $DEFAULT_BARYCENTER);

if($bary){
	print "(Barycenter correction. Light curves may be truncated by 60s if needed.)\n";}
else{
	print "(No barycenter correction)\n";
}



# File containing source names and parameters
$source_list = get_file_open("Give source parameter file", *SOURCE_LIST, $DEFAULT_SOURCE_LIST);



# Get names of files which contain lists of the
# photon and spacecraft files to be processed


$ft1_file_list = get_file_open("Give photon file name list", *FT1_LIST, $DEFAULT_FT1_LIST);


# Look for spacecraft files in the current directory.
opendir(DIR, ".");
@files = grep(/_SC00\.fits$/,readdir(DIR));
closedir(DIR);
$files = @files;
print "Number of SC files found = $files\n";

# If there's exactly one spacecraft file in the current directory suggest that as
# default
if($files == 1){
	$ft2_file = get_file("Give spacecraft (FT2) file name", $files[0]);
}
else{
	$ft2_file = get_file("Give spacecraft (FT2) file name", $DEFAULT_FT2);
}

$FT2_FILE_LIST = $FALSE;

$roi_to_use = get_value("Give aperture radius (degrees)", $DEFAULT_ROI, 0, 180);

$roi_inner = get_value("Give inner size of aperture annulus (degrees)", 0, 0, $roi_to_use);


$emin_to_use = get_value("Give Emin (MeV)", $DEFAULT_EMIN, 0, 1E10);


$emax_to_use = get_value("Give Emax (MeV)", $DEFAULT_EMAX, $emin_to_use, 1E10);


$zenith_limit = get_value("Give Zenith limit (degrees)", $DEFAULT_ZENITH_LIMIT, 0, "INDEF");



# Pass 6 and Pass 7 cause gtselect to require different key words.

if($irf_code == 1 || $irf_code == 2){

	$event_class_max = 10; #big value deliberate

	$event_class_min = get_value("Give EVENT_CLASS minimum (use 0 for simulated data)", 
				$DEFAULT_EVENT_CLASS_MIN, 0, 3);

	if($event_class_min == 3 || $event_class_min == 0){
		$irfs = $irf_prefix."DIFFUSE";
		}
	elsif($event_class_min == 2){
		$irfs = $irf_prefix."SOURCE";
		}
	elsif($event_class_min == 1){
		$irfs = $irf_prefix."TRANSIENT";
		}
	else{
		print "event class minimum not allowed\n";
	}

}
elsif($irf_code == 3){
	print "For P7 only SOURCE event class is currently provided\n";
	$event_class_min = 0; 
	$event_class_max = 0;
	$event_class = 2;
	$irfs = "P7SOURCE_V6";

}
elsif($irf_code == 4){
	print ("For P7REP only SOURCE event class is currently provided\n");
	$event_class_min = 0; 
	$event_class_max = 0;
	$event_class = 2;
	$irfs = "P7REP_SOURCE_V15";

}


elsif($irf_code == 5){
	print ("For P7REP only SOURCE event class is currently provided\n");
	$event_class_min = 0; 
	$event_class_max = 0;
	$event_class = 2;

	$irfs = "CALDB";

}

elsif($irf_code == 6){
	print ("For P8 only SOURCE event class is currently provided\n");
	$event_class = 128; 
# clean would be 256


# evtype: 3 = front and back, 1 = front only, 2 = back only.
	$event_type = 3;


	$irfs = "CALDB";

}



else{
	print "Shouldn't be here - got bad value of irf_code ($irf_code)\n";
}




$rock_limit = get_value("Give rock angle limit (degrees)", $DEFAULT_ROCK, -90, 90);


$bore_limit = get_value("Give Bore limit (degrees)", $DEFAULT_BORE, 0, 360);


$spectral_index = get_value("Give spectral index", $DEFAULT_SPECTRAL_INDEX, -100, 100);

if ($spectral_index > 0){
	print "Forcing spectral index to be negative: ";
	$spectral_index = -$spectral_index;
	print "$spectral_index\n";
}

$bin_size = get_value("Give bin size (days)", $DEFAULT_BIN_SIZE, 0, 1e10);
# convert to seconds
$bin_size = $bin_size * 86400;


$sun_minimum = get_value("Give minimum solar distance (degrees)", $DEFAULT_SUN_MINIMUM, 0, 180);

#-------------------------------------


# Start of source loop

print "get sources\n";


while(chomp($line = <SOURCE_LIST>)){

    print "line = $line\n";


# remove any commas
$line =~ s/\,/ /g;


# Need to have at least source name, RA and dec
# in input file


@fields = split(' ', $line);


        $length = @fields;
$source = $fields[0];


# change any plus sign in source name to "p"
# to avoid FTOOLS problems (may be better way to work
# around this!)

# First store raw form of source name

$src = $source;

$source =~ s/\+/p/g;


$ra = $fields[1];
$dec = $fields[2];


# Optionally may have region size and energy
# range (-ve values mean use values set above)
# fields are: 
# aperture size
# low E
# high E
# also, values must be positive to be used.

    $roi = $roi_to_use;
    $emin = $emin_to_use;
    $emax = $emax_to_use;



# This bit is klunky/nasty.

print "field length = $length\n";


    if($length >= 4){
	if($fields[3] > 0) {$roi = $fields[3]};
}

    if($length >= 5){
	if($fields[4] > 0) {$emin = $fields[4]};
}

    if($length >= 6){
	if($fields[5] > 0) {$emax = $fields[5]};
}






print "START OF NEW SOURCE\n";

    $base = $prefix . $source;


print "base = $base, RA = $ra, dec = $dec\n";
# kludge
if ($ra > 360) {
	$ra = $ra - 360;
}


if ($ra > 360 || $ra < 0){
	die "Invalid RA\n";
}


if ($dec > 90 || $dec < -90){
	die "Invalid dec\n";
}




############################################################################################
# Construct commands and execute


# spacecraft files should be sorted but they weren't sometimes
# uncomment the lines below if the problem recurs
#$command = "fsort  infile=\"$ft2_file\[1\]\" columns=START method=\"heap\"";
#    doit($command);




$ft1_file = make_temp("eventfile0.fits");
$ft1_file_0 = make_temp("eventfile0.0.fits");
$eventfile2 = make_temp("eventfile2.fits");
$temp2 = make_temp("temp2.fits");
$temp3 = make_temp("temp3.fits");


# Combine all photon files together

if($irf_code == 6){
$command = "gtselect chatter=$chatter zmax=180 emin=$emin_to_use emax=$emax_to_use infile=\"\@$ft1_file_list\" outfile=\'$ft1_file_0\' ra=$ra dec=$dec rad=$roi evclass=$event_class evtype=$event_type tmin=0 tmax=0";
    doit($command);
}

elsif($irf_code >= 3 && $irf_code <= 5){
$command = "gtselect chatter=$chatter zmax=180 emin=$emin_to_use emax=$emax_to_use infile=\"\@$ft1_file_list\" outfile=\'$ft1_file_0\' ra=$ra dec=$dec rad=$roi evclass=$event_class evclsmin=$event_class_min evclsmax=$event_class_max tmin=0 tmax=0";
    doit($command);
}
else{
$command = "gtselect chatter=$chatter zmax=180 emin=$emin_to_use emax=$emax_to_use infile=\"\@$ft1_file_list\" outfile=\'$ft1_file_0\' ra=$ra dec=$dec rad=$roi evclsmin=$event_class_min evclsmax=$event_class_max tmin=0 tmax=0";
    doit($command);
}



#if($irf_code == 3 || $irf_code == 4){
#$command = "gtselect zmax=180 emin=$emin_to_use emax=$emax_to_use infile=\"\@$ft1_file_list\" outfile=\'$ft1_file_0\' ra=$ra dec=$dec rad=$roi evclass=$event_class evclsmin=$event_class_min evclsmax=$event_class_max tmin=0 tmax=0";
#    doit($command);
#}
#else{
#$command = "gtselect zmax=180 emin=$emin_to_use emax=$emax_to_use infile=\"\@$ft1_file_list\" outfile=\'$ft1_file_0\' ra=$ra dec=$dec rad=$roi evclsmin=$event_class_min evclsmax=$event_class_max tmin=0 tmax=0";
#    doit($command);
#}

# Apply annulus selection using fselect (gtselect can't do this) if specified

if($roi_inner > 0){
	$command = "fselect $ft1_file_0 $ft1_file  \"circle($ra,$dec,$roi,RA,DEC) &&  !circle($ra,$dec,$roi_inner,RA,DEC)\"";
    		doit($command);	
#die;
}
else{
	$ft1_file = $ft1_file_0;
}



# get TSTART and TSTOP of photon file

$command = "fkeypar \"$ft1_file\[1\]\" TSTART";

    doit($command);

chomp($ph_tstart = `pget fkeypar value`);
print "photon start time = $ph_tstart\n";

$command = "fkeypar \"$ft1_file\[1\]\" TSTOP";

    doit($command);

chomp($ph_tstop = `pget fkeypar value`);
print "photon stop time = $ph_tstop\n";


# get TSTART and TSTOP of S/C file

$command = "fkeypar \"$ft2_file\[1\]\" TSTART";

    doit($command);

chomp($sc_tstart = `pget fkeypar value`);
print "spacecraft start time = $sc_tstart\n";

$command = "fkeypar \"$ft2_file\[1\]\" TSTOP";

    doit($command);

chomp($sc_tstop = `pget fkeypar value`);
print "spacecraft stop time = $sc_tstop\n";


# If we're going to barycenter spacecraft file must cover
# slightly more time range than the photon file


$tstart = $ph_tstart;
$tstop = $ph_tstop;


if($bary){
    if($tstart <= $sc_tstart){
	print "fixing tstart\n";
	$tstart = $sc_tstart + 60.0;
	print "new tstart = $tstart\n";
    }

    if($tstop >= $sc_tstop) {
	print "fixing tstop\n";
	$tstop = $sc_tstop - 60.0;
	print "new tstop = $tstop\n";
    }
}


# allow specification of shorter time range
$tstart = max($start_time, $tstart);
$tstop = min($stop_time, $tstop);


if($irf_code == 6){
$command = "gtselect chatter=$chatter zmax=$zenith_limit emin=$emin emax=$emax infile=\"$ft1_file\" outfile=$temp2 ra=$ra dec=$dec rad=$roi tmin=$tstart tmax=$tstop evclass=$event_class evtype=$event_type";
    doit($command);
}
elsif($irf_code >= 3 && $irf_code <= 5){
$command = "gtselect chatter=$chatter zmax=$zenith_limit emin=$emin emax=$emax infile=\"$ft1_file\" outfile=$temp2 ra=$ra dec=$dec rad=$roi tmin=$tstart tmax=$tstop evclass=$event_class evclsmin=$event_class_min evclsmax=$event_class_max";
    doit($command);
}
else{
$command = "gtselect chatter=$chatter zmax=$zenith_limit emin=$emin emax=$emax infile=\"$ft1_file\" outfile=$temp2 ra=$ra dec=$dec rad=$roi tmin=$tstart tmax=$tstop evclsmin=$event_class_min evclsmax=$event_class_max";
    doit($command);
}

#if($irf_code == 3 || $irf_code == 4){
#$command = "gtselect zmax=$zenith_limit emin=$emin emax=$emax infile=\"$ft1_file\" outfile=$temp2 ra=$ra dec=$dec rad=$roi tmin=$tstart tmax=$tstop evclass=$event_class evclsmin=$event_class_min evclsmax=$event_class_max";
#    doit($command);
#}
#else{
#$command = "gtselect zmax=$zenith_limit emin=$emin emax=$emax infile=\"$ft1_file\" outfile=$temp2 ra=$ra dec=$dec rad=$roi tmin=$tstart tmax=$tstop evclsmin=$event_class_min evclsmax=$event_class_max";
#    doit($command);
#}

# different calls to gtmktime depending on whether sun_minimum is greater than 0
# this was originally to avoid need for installing sun_pos code.
# This should be superceded now Sun coordinates are available in all FT2 files


if($sun_minimum > 0){
	$command = "gtmktime scfile=\"$ft2_file\" filter=\"(DATA_QUAL==1) && ABS(ROCK_ANGLE)<$rock_limit && (LAT_CONFIG==1) && (angsep(RA_ZENITH,DEC_ZENITH,$ra,$dec)\+$roi<$zenith_limit) && (angsep($ra,$dec,RA_SUN,DEC_SUN)>$sun_minimum\+$roi) && (angsep($ra,$dec,RA_SCZ,DEC_SCZ)<$bore_limit)\" roicut=n evfile=\"$temp2\" outfile=\"$temp3\"";
}
else{
	$command = "gtmktime scfile=\"$ft2_file\" filter=\"(DATA_QUAL==1) && ABS(ROCK_ANGLE)<$rock_limit && (LAT_CONFIG==1) && (angsep(RA_ZENITH,DEC_ZENITH,$ra,$dec)\+$roi<$zenith_limit) && (angsep($ra,$dec,RA_SCZ,DEC_SCZ)<$bore_limit)\" roicut=n evfile=\"$temp2\" outfile=\"$temp3\"";
}
    doit($command);



$command = "gtbin algorithm=LC evfile=$temp3 outfile=lc_$base.fits scfile=$ft2_file tbinalg=LIN tstart=$tstart tstop=$tstop dtime=$bin_size";
    doit($command);


$command = "gtexposure infile=\"lc_$base.fits\" scfile=\"$ft2_file\" irfs=\"$irfs\" srcmdl=\"none\" specin=$spectral_index";
	doit($command);


# version based on already using gtselect earlier
if($bary){ bcorrect("lc_$base.fits", $ft2_file, $ra, $dec);}


$counts = "COUNTS";

$command = "fdump prhead=no infile=\"lc_$base.fits[1]\" outfile=\"lc_$base.dmp1\" columns=\"TIME $counts EXPOSURE TIMEDEL\" pagewidth=256 rows=\"-\"";
    doit($command);


# print LIST_FILE "lc_$base.dmp$n\n";

########################################
# remove unncessary files

# remove all files except temp_$base
$command = "rm lc_$base.fits  $temp2  $temp3 $ft1_file";

# remove all files except FITS light curve
#    $command = "rm  temp2_$base  temp3_$base.fits  temp_$base";

    doit($command);


# This file was only created if used annulus
if($roi_inner > 0){
	$command = "rm $ft1_file_0";
    	doit($command);
}


# process fdumped output file to assign time, convert
# counts to rates, and calculate errors in two different ways
# arguments are input and output files

prepare("lc_$base.dmp1", "lc_$base.out");

# rewind photon file list

    seek(FT1_LIST, 0, 0);


# remove initial fdump output
	$command = "rm lc_$base.dmp1";
	doit($command);

}



sub doit{
    print "\n$_[0]\n\n";
    system($_[0]);
}

#######################################
# process the fdumped light curve that comes out of gtbin
# changes times to UT, counts to rates, and two types of error bars
#
# One set is a variety of ways to 
# take asymmetric error bars and symmeterize them
# This suffers from the assume that the observed
# mean is the population mean.
#
# The other assumes that the intrinsic count
# rate is constant and that the "true" error
# should be determined from the mean count rate
# and scale that by the exposure time.

sub prepare{
my $in_file = $_[0];
my $out_file = $_[1];


$mjdref = 51910.0e0 + 7.428703703703703e-4;

open (IN_FILE, "$in_file") ||
               die "Can't open input file\n";

open (OUT_FILE, ">$out_file") ||
               die "Can't open output file\n";


# read through input file to get mean count rate

# skip header
#readhead(IN_FILE);

chomp($line = <IN_FILE>);
chomp($line = <IN_FILE>);
chomp($line = <IN_FILE>);
chomp($line = <IN_FILE>);



my $nobs = 0;
my $meanrate = 0.0;
my $countsum = 0.0;
my $weightsum = 0.0;
my $expsum = 0.0;

while(chomp($line = <IN_FILE>)){
	$command = "rm $to_remove";
	@fields = split(' ', $line);
	$i = $fields[0];
	$time  = $fields[1];
	$counts = $fields[2];
	$exposure = $fields[3];
	$timedel = $fields[4];

        if($exposure > 0.0){
         	$countsum = $countsum + $counts;
         	$expsum = $expsum + $exposure;
         	$nobs = $nobs + 1;
	}
}

$meanrate = $countsum/$expsum;

# second pass
seek(IN_FILE, 0, 0);
#readhead(IN_FILE);
chomp($line = <IN_FILE>);
chomp($line = <IN_FILE>);
chomp($line = <IN_FILE>);
chomp($line = <IN_FILE>);

while(chomp($line = <IN_FILE>)){
	$command = "rm $to_remove";
	@fields = split(' ', $line);
	$i = $fields[0];
	$time  = $fields[1];
	$counts = $fields[2];
	$exposure = $fields[3];
	$timedel = $fields[4];

        if($exposure > 0.0){

      		$popcounts = $meanrate * $exposure;
	        $perr = sqrt($popcounts);

# ERRORS FROM SAMPLE RATE

# use bbar approach, but average asymmetrical error
# bars
      		$cerr1 = 0.5 + sqrt($counts + 0.25);
      		$cerr2 = -0.5 + sqrt($counts + 0.25);

# mean error
       		$meanerr = $cerr1 + $cerr2;
       		$meanerr = $meanerr/2.0;

# rms type error
       		$rmserr = sqrt(($cerr1*$cerr1 + $cerr2*$cerr2)/2.0);

       		$cerr = $rmserr;

      		$rate = $counts/$exposure;
      		$rerr = $cerr/$exposure;
      		$prerr = $perr/$exposure;

      		$time = $time/86400.0;
      		$time = $time + $mjdref;

      		$timedel = $timedel/(2.0 * 86400.0);

      		print OUT_FILE "$time $rate $rerr $timedel $prerr $exposure $counts\n";


	}

}

close(IN_FILE);
close(OUT_FILE);

}




#######################################
# barycenter correction that assumes that length of
# event file was already checked to make sure it's
# shorter than the spacecraft file

sub bcorrect{
my $lc_file = $_[0];
my $ft2_file = $_[1];
my $ra = $_[2]; 
my $dec = $_[3];

my $bc_file = make_temp("temp_temp1");

$command = "gtbary evfile=\"$lc_file\" outfile=\"$bc_file\" scfile=\"$ft2_file\" ra=$ra dec=$dec tcorrect=BARY";
    doit($command);


$command = "rm $lc_file";
    doit($command);

# cp rather than mv. Change to mv (and remove later delete)
# when have more confidence this is working OK
$command = "cp $bc_file $lc_file";
    doit($command);

$command = "rm $bc_file";
    doit($command);

}






# make a temporary filename to use that includes the
# process ID to (hopefully) make it unique
sub make_temp{

#return "/tmp/".$$.$_[00];
	return "tmp_".$$.$_[00];

}

#######################################
# Prompt for and get a file name.
# Check that file exists before accepting its name.
# Usage: $file_name = get_file("String to prompt for name"[, "default name"]);
# The default file name is not required.

sub get_file{

$prompt = $_[0];
$default = $_[1];

$waiting = 1;


if($BATCH){
	$file_name = $default;
	if (open(CHECK, $file_name)){ 
		close(CHECK);
    	}
	else {
        	die "Can't open default file: $file_name\n";
   	}

	return $default;
}

while($waiting){

if ($default){
	print "$prompt [default = $default]\: ";
	}
else{
	print "$prompt\: ";
}

chomp($file_name = <STDIN>);

if($file_name eq "" && $default)
       {$file_name = $default; print "(Using default: \"$default\")\n";}
if (open(CHECK, $file_name)){ 
#	print "opened $file_name\n";
	$waiting = 0;
	close(CHECK);
    }
else {
               print "Can't open file: $file_name\n";
   }
}
	return $file_name;
}

#######################################
# Prompt for and get a file name, then open it.
# This should probably be combined with get_file()
# Check that file exists before accepting its name.
# Usage: $file_name = get_file("String to prompt for name", FILE_HANDLE, [, "default name"]);
# The default file name is not required.

sub get_file_open{

$prompt = $_[0];
$check = $_[1];
$default = $_[2];


if($BATCH){
	$file_name = $default;
	open($check, $file_name);
	return $file_name;
}

$waiting = 1;


while($waiting){

if ($default){
	print "$prompt [default = $default]\: ";
	}
else{
	print "$prompt\: ";
}

chomp($file_name = <STDIN>);

if($file_name eq "" && $default)
       {$file_name = $default; print "(Using default: \"$default\")\n";}
if (open($check, $file_name)){ 
#	print "opened $file_name\n";
	$waiting = 0;
#	close(CHECK);
    }
else {
               print "Can't open file: $file_name\n";
   }
}
return $file_name;
}


############################################################
# Prompt for a Y/N response and return true or false (1 or 0)
# default value is determined by argument
# Usage: $response = get_yn("Prompt", $default);
# $default should be 1, 0, or "INDEF"

sub get_yn{
$prompt = $_[0];
$default = $_[1];

if($BATCH){
	return $default;
}

if($default eq 1){$default_yn = "Y";}
elsif($default eq 0){$default_yn = "N";}
else{print "Bad value of default in get_yn\n";}

$INDEF = "INDEF";


$waiting = 1;



while($waiting){

if($default eq $INDEF){
	print "$prompt [y/n]\: ";
}
else{
	if ($default){
		print "$prompt [y/n; default = y]\: ";
	}
	else{
		print "$prompt [y/n; default = n]\: ";
	}
}

chomp($response = substr(uc(<STDIN>),0,1));

#print "response = $response\n";

#if($response eq "" && ($default != $INDEF))
if($response eq "")
       {$value = $default; print "(Using default: \"$default_yn\")\n"; $waiting = 0;}
# Check response format OK
elsif($response eq "Y"){
#	print "got y\n";
	$value = 1; $waiting = 0;
}
elsif($response eq "N"){
#	print "got n\n";
	$value = 0; $waiting = 0;
}
else {
           print "Response ($response) is not \"y\" or \"n\"\n";
   }
}
	
return $value;

}

sub get_value{

my $prompt = $_[0];
my $default = $_[1];
my $minimum = $_[2];
my $maximum = $_[3];

#print "default = $default, min = $minimum, max = $maximum\n";

if($BATCH){
	return $default;
}

my $INDEF = "INDEF";

my $waiting = 1;


while($waiting){


if ($default eq $INDEF){
	print "$prompt\: ";
	$use_default = 0;
	}
else{
	print "$prompt [default = $default]\: ";
	$use_default = 1;
}


chomp($value = <STDIN>);

if($value eq "" && ($use_default))
#if($value eq "")
       {$value = $default; print "(Using default: \"$default\")\n";}
# Check data range is OK

if(check_value($value, $minimum, $maximum)){
	 	$waiting = 0;
	}

else {
               print "Value ($value) is not in the range $minimum to $maximum\n";
   }
}
return $value;
}




############################################################
# Prompt for and get a string.
# No range check.
# Usage: $value = get_string("String to prompt for value", default)
# If a default is not to be specified, call with value set to 
# the string "INDEF"

sub get_string{

$prompt = $_[0];
$default = $_[1];


if($BATCH){
	return $default;
}

$INDEF = "INDEF";

$waiting = 1;

while($waiting){

if ($default){
	print "$prompt [default = $default]\: ";
	}
else{
	print "$prompt\: ";
}

chomp($value = <STDIN>);
#print "value = $value\n";
if($value eq "" && ($value ne $INDEF))
       {$value = $default; print "(Using default: \"$default\")\n";
	$waiting = 0;}
#       {$value = $default; print "(Using default: \"$default\")\n";}
if($value ne ""){$waiting = 0;}

}
return $value;
}

##########################################
# 
sub check_value{
my $value = shift;
my $minimum = shift;
my $maximum = shift;

my $result = $TRUE;



if($value !~ /[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?/){
	print "$value is not a number!\n";
	$result = $FALSE;
	return $result;
	}
#[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?

if($maximum ne "INDEF"){
	if($value > $maximum){$result = $FALSE;}
	}
if($minimum ne "INDEF"){
	if($value < $minimum){$result = $FALSE;}
	}

return $result;
}
##########################################
# Change default values if specified from a file
# Likely to be most useful if running in "batch" mode
sub set_defaults{

open(PARAMETERS, $parameter_filename) ||
     die "Can't open input parameter file $parameter_filename\n";

while(chomp($par_line = <PARAMETERS>)){

# ignore comment lines
#print "first character:", substr($par_line, 0, 1), "\n";
	if(substr($par_line, 0, 1) ne "\#"){
		@par_fields = split(' ', $par_line);
# blank line OK
		if(@par_fields == 0){
		}		
		elsif((@par_fields == 1 || @par_fields > 2) && $par_fields[0] ne "prefix"){
			print "Invalid number of fields in parameter file, must have exactly 2\n";
			print "$par_line\n";
		}	

		if(@par_fields == 2){
# Yes, this could be done more elegantly!
# convert to upper case
			$par_fields[0] = lc($par_fields[0]);
			if($par_fields[0] eq "ft2") {$DEFAULT_FT2 = $par_fields[1];}
			elsif($par_fields[0] eq "bin_size") {$DEFAULT_BIN_SIZE = $par_fields[1];}
			elsif($par_fields[0] eq "roi") {$DEFAULT_ROI = $par_fields[1];}
			elsif($par_fields[0] eq "zenith_limit") {$DEFAULT_ZENITH_LIMIT = $par_fields[1];}
			elsif($par_fields[0] eq "rock") {$DEFAULT_ROCK = $par_fields[1];}
			elsif($par_fields[0] eq "bore") {$DEFAULT_BORE = $par_fields[1];}
			elsif($par_fields[0] eq "event_class_min") {$DEFAULT_EVENT_CLASS_MIN = $par_fields[1];}
			elsif($par_fields[0] eq "source_list") {$DEFAULT_SOURCE_LIST = $par_fields[1];}
			elsif($par_fields[0] eq "ft1_list") {$DEFAULT_FT1_LIST = $par_fields[1];}
			elsif($par_fields[0] eq "catalog") {$DEFAULT_CATALOG = $par_fields[1];}
			elsif($par_fields[0] eq "pthreshold") {$DEFAULT_PTHRESHOLD = $par_fields[1];}
			elsif($par_fields[0] eq "irf_code") {$DEFAULT_IRF_CODE = $par_fields[1];}
			elsif($par_fields[0] eq "sun_minimum") {$DEFAULT_SUN_MINIMUM = $par_fields[1];}
			elsif($par_fields[0] eq "emin") {$DEFAULT_EMIN = $par_fields[1];}
			elsif($par_fields[0] eq "emax") {$DEFAULT_EMAX = $par_fields[1];}
			elsif($par_fields[0] eq "spectral_index") {$DEFAULT_SPECTRAL_INDEX = $par_fields[1];}
			elsif($par_fields[0] eq "barycenter") {$DEFAULT_BARYCENTER = $par_fields[1];}
			elsif($par_fields[0] eq "prefix") {$DEFAULT_PREFIX = $par_fields[1];}
			else{print "Unrecognized parameter: $par_fields[0]\n";}
		}
#		else{
#			print "Hmmm.... how did I get here?!\n";
#		}
	}	

}
close(PARAMETERS);

}

##########################################
# Write current file defaults to a parameter file
# This can then be edited (if desired) then used as
# future input.

sub write_defaults{

open(PARAMETERS, ">$output_parameter_filename") ||
     die "Can't open output parameter file $output_parameter_filename\n";


print PARAMETERS
"\# Default parameters of the \"bex\" aperture photometry code
\# can be set with a file like this.
\# Use the syntax such as
\# \$ bex -file bex.par
\# This can be most useful when running in \"batch\" mode where parameters
\# are not prompted for.
\# e.g.
\# \$ aperture.pl -batch -file aperture.par

\# for true/false conditions, such as barycenter, 0 is \"false\", and 1 is \"true\".

\# If a parameter is not specified here, then the defaults contained in the script will be used.

\# default spacecraft file to be used if more than one \"SC\" file is found in directory
ft2 $DEFAULT_FT2
\# time bin size in days
bin_size $DEFAULT_BIN_SIZE
\# default aperture radius in degrees
roi $DEFAULT_ROI
zenith_limit $DEFAULT_ZENITH_LIMIT
\# maximum rock angle
rock $DEFAULT_ROCK
\# maximum distance of source from boresight
bore $DEFAULT_BORE
event_class_min $DEFAULT_EVENT_CLASS_MIN
\# file containing list of sources with coordinates
source_list $DEFAULT_SOURCE_LIST
\# file containing list of photon files
ft1_list $DEFAULT_FT1_LIST
\# IRF to use. 4 = Pass7 reprocessed.
irf_code $DEFAULT_IRF_CODE
\# minimum distance from Sun
sun_minimum $DEFAULT_SUN_MINIMUM
\# lower energy bound
emin $DEFAULT_EMIN
\# upper energy bound
emax $DEFAULT_EMAX
\# spectral index - used in exposure calculations
spectral_index $DEFAULT_SPECTRAL_INDEX
\# set barycenter to \"1\" if you don't want to do barycenter correction
barycenter $DEFAULT_BARYCENTER
\# Optional prefix to be added to the output light curve file name
prefix $DEFAULT_PREFIX\n";

close(PARAMETERS);

exit;

}

##########################################
# maximum and minimum functions
# taken from somewhere on web

sub max ($$) { $_[$_[0] < $_[1]] }
sub min ($$) { $_[$_[0] > $_[1]] }

##########################################
# convert MJD to MET
# start and stop times are specified on command line in MJD units
# but science tools use MET

sub mjd2met{
my $value = shift;

# This makes an assumption about UT vs. TT....
$result = ($value - (51910.0 + 7.428703703703703E-4)) * 86400.0;

return($result)
}

