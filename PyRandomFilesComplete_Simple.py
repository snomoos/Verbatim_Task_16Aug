from __future__ import print_function

#import the things you will need
import sys
import os
import optparse
import numpy as np

########################Base strings taken from the Scenario file#######
head = """scenario = "Verbatim_Processing_Final";
scenario_type = trials;
no_logfile = false;

# to use trigger from scanner
active_buttons = 2;
button_codes = 2,2;

default_trial_duration = forever;
default_trial_type = first_response;
default_font_size = 90;
default_max_responses = 10;
#default_font_size = 230; # OK for 1024x768 for letters
#default_font_size = 90; # OK for 800x600

default_background_color = 0, 0, 0;   # black background default
default_text_color = 255, 255, 255;   # white text default

$terb = 1;

$duration = 2500; # is good for TR=3.0
$startduration = 9000; # the rest during the get-ready phase
begin;

picture {} default;
"""

taskstart="""
##########Start the task NOW!!! #########
TEMPLATE "NoSound.tem" {
the_duration \t the_code \t the_caption;
$startduration \t "rest" \t "+";
};
TEMPLATE "rest.tem" {
the_responses \t the_caption \t the_code;
1 \t "+" \t "rest";
};
##########Word Set  from Block %i #########
"""

tail = """
# Sophie do not delete ... Use this for the final block
TEMPLATE "rest.tem" {
the_responses	the_caption	the_code;
# end screen
1			    	"+"	 		 "rest";
1			    	"-"	 		 "end";
};
"""

########################Functions to create strings from words#######

def GetLoadString(wavebase):
    """
    load-string = GetLoadString(wavebase)

    wavebase should be the base name of a wav file that you want to play (no path)
    i.e. wavefile (where the file is called wavefile.wav
    """

    string = """sound {
    wavefile {filename = "%s.wav";
    } %s_sound ; } %s;

    """ % (wavebase, wavebase, wavebase)

    #wavebase.wav is the filename
    #wavebase_sound is the wavfile
    #wavebase is the sound
    # --> a little counter intuitive but anyhooms
    return string

def GetBlockStringJohn(blockwords, beepstr, panvals):
    # panval -1.0 is left, 1.0 is right and 0.0 is center
    blockctr = 1
    makeline = lambda x, p: '$duration \t %s_sound \t "%s:%d" \t " " \t %d;' % (x, x, p, p)
    blocksstring = []
    if len(blockwords) != len(panvals):
        print(len(blockwords), len(panvals))
        raise ValueError("blockwords and panvals are different lenghths")

    for thisblock in range(len(blockwords)):
        wordblock = blockwords[thisblock]
        blockpan = panvals[thisblock]
        thisblockstring = ("\n").join([makeline(word, blockpan) for word in wordblock])
        thisreststring = ("\n").join(['$duration \t "rest%i" \t "+";' % wordnum for wordnum in range(len(wordblock))])
        blockstring = """
#################################################
##########Beep and Trigger for Block %i #########
TEMPLATE "Sound.tem" {
the_duration \t soundfile \t the_code \t the_caption;
$duration \t %s \t "%s" \t "+";
};
TEMPLATE "rest.tem" {
the_responses \t the_caption \t the_code;
1 \t "+" \t "rest";
};
##########Word Set  from Block %i #########
TEMPLATE "SoundPan.tem" {
the_duration \t wavefile \t the_code \t the_caption \t thepan;
%s
};

#####REST#########
#The second rest block
TEMPLATE "NoSound.tem" {
the_duration \t the_code \t the_caption;
%s
};
##########End Block %i ##########################
#################################################
""" % (blockctr, beepstr, beepstr, blockctr, thisblockstring, thisreststring, blockctr)
        blockctr += 1
        # print(blockctr)
        blocksstring.append(blockstring)
    # print(blocksstring)
    return ("\n").join(blocksstring)

class genwordfromlist(object):
    def __init__(self, filename):
        self.filename = filename
        self.ParseFile()

    def ParseFile(self):
        with open(self.filename) as X:
            contents = X.readlines()
        self.headercomments = []
        self.header = {}
        self.names = []
        header_items = {"prefix":str, "suffix":str, "nblocks":int, "wordspb":int, "pans":lambda x: [float(t) for t in x.split(",")]}

        for i in contents:
            if i.startswith("!"):
                pair = i.strip().strip("!").split("=")
                assert len(pair) == 2
                tag = pair[0].strip()
                converter = header_items.pop(tag)
                self.header[tag] = converter(pair[1].strip())
            elif i.startswith("#"):
                self.headercomments.append(i.strip())
            else:
                self.names.append(i.strip())
        print(header_items)
        assert len(header_items) == 0
        assert len(self.names) == (self.header["nblocks"] * self.header["wordspb"] * len(self.header["pans"]))
        self.__dict__.update(self.header)


def GetWordBlocks(genlist):
    theseblocks = []
    thesepans = []
    totblocks = 0
    for gen in genlist:
        randomnames = np.random.permutation(gen.names[:]).tolist()
        for thispan in gen.pans:
            for blocks in range(gen.nblocks):
                thisblock = []
                for words in range(gen.wordspb):
                    thisblock.append(randomnames.pop(0))
                thesepans.append(thispan)
                theseblocks.append(thisblock)
                totblocks += 1
        assert len(randomnames) == 0

    randomorder = np.random.permutation(range(totblocks)).tolist()

    return [theseblocks[i] for i in randomorder], [thesepans[i] for i in randomorder]

########################What runs when you run this file!!#######

if __name__ == "__main__":
    #read the folder to use from bash stdin
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option("-o", "--outfilename", dest="outfilename",
                  help="name of the output file", default='')
    parser.add_option("-r", "--randomseed", dest="randomseed", type="int",
                  help="Set the randomseed to 0", default=False)
    parser.add_option("-f", "--filelist", dest="filelist",
                  help="comma seperated list of files to use", default="")

    (options, args) = parser.parse_args()

    if options.randomseed: #set the radom seed to a constant value for repeatability
        np.random.seed(options.randomseed)
    else:# randomize
        np.random.seed()

    files = options.filelist.split(",")
    genlist = [genwordfromlist(i) for i in files]
    basenames = ['a1000ms_1khz']
    for x in genlist: basenames.extend([i for i in x.names])
    basenames = list(set(basenames))
    sep_statements = [GetLoadString(i) for i in basenames]
    loadstrings = ("\n").join(sep_statements)

    blockwords, blockpans = GetWordBlocks(genlist)

    blocksstring = GetBlockStringJohn(blockwords, "a1000ms_1khz", blockpans)

    fullstr = ("\n").join([head, loadstrings, taskstart, blocksstring, tail])

    if options.outfilename == '':
        outf = sys.stdout
        outf.write(fullstr)
    else:
        outf = open(options.outfilename, 'w')
        outf.write(fullstr)
        outf.close()

"""
TEM FILES
~~!~!~~~~~
#Sound.tem
trial {
	trial_duration = $the_duration;
	trial_type = fixed;

	picture { text { caption = $the_caption; }; x = 0; y = 0; };


         sound $soundfile;
         time = 1;


	code = $the_code;
};

#NoSound.tem
trial {
	trial_duration = $the_duration;
	trial_type = fixed;

	picture { text { caption = $the_caption; }; x = 0; y = 0; };
         time = 1;

	code = $the_code;
};

#SoundPan.tem
trial {
	trial_duration = $the_duration;
	trial_type = fixed;

	picture { text { caption = $the_caption; }; x = 0; y = 0; };

         sound {wavefile $wavefile; pan = $thepan;};
         time = 1;


	code = $the_code;
};

#rest.tem
trial {
	trial_duration = forever;
	trial_type = nth_response;
	max_responses = $the_responses;
	terminator_button = 1;

	picture { text { caption = $the_caption; }; x = 0; y = 0; };

	code = $the_code;
};

#Filelists.sh
#To get the file lists $1=filematchstr, $2=outfilenme
ls ${1} | cut -d "." -f 1 > ${2}
"""


"""
probs:
! in params
space in filename
blocks with pans
"""
