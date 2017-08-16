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
default_font_size = 300;
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
$startduration \t "rest" \t "Wait";
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
    makeline = lambda x, p: '$duration \t %s_sound \t "%s" \t " " \t %d;' % (x, x, p)
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

def GetBlockStringSophie(blockwords, beepstr):
    # print("There")
    blockctr = 1
    makeline = lambda x: '$duration \t %s \t "%s" \t "+";' % (x, x)
    blocksstring = []
    for wordblock in blockwords:
        thisblockstring = ("\n").join([makeline(word) for word in wordblock])
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
TEMPLATE "Sound.tem" {
the_duration \t soundfile \t the_code \t the_caption;
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

def GetBlockStringShawna(blockwords, beepstr):
    # print("There")
    blockctr = 1
    def makeline(x, wordnum):
        return """
TEMPLATE "rest.tem" {
the_responses \t the_caption \t the_code;
1 \t "+" \t "rest%i";
};
TEMPLATE "Sound.tem" {
the_duration \t soundfile \t the_code \t the_caption;
$duration \t %s \t "%s" \t "+" ;
};
""" % (wordnum, x, x)

    blocksstring = []
    for wordblock in blockwords:
        thisblockstring = ("\n").join([makeline(wordblock(num), num) for num in range(len(wordblock))])
        blockstring = """
#################################################
##########Beep and Trigger for Block %i #########
%s
##########Word Set  from Block %i #########
%s

#####REST#########
#The second rest block
TEMPLATE "rest.tem" {
the_responses	the_caption	the_code;
%i\t"+"\t"rest";
};

##########End Block %i ##########################
#################################################
""" % (blockctr, makeline(beepstr), blockctr, thisblockstring, len(wordblock), blockctr)
        blockctr += 1
        # print(blockctr)
        blocksstring.append(blockstring)
    # print(blocksstring)
    return ("\n").join(blocksstring)

def GetWordBlocks_initial(wordlists, blockorder, blocklength):
    if len(np.bincount(blockorder)) != len(wordlists):
        raise ValueError

    allblockwords = []
    for i in blockorder:
        thisblockwords = wordlists[i]
        blockwords = np.random.choice(thisblockwords, size=blocklength, replace=False)
        allblockwords.append(blockwords.copy().tolist())
    return allblockwords

def genwordfromlist(listtosee):
    poplist = []
    while True:
        if len(poplist) == 0:
            poplist = np.random.permutation(listtosee).tolist()
        topop = poplist.pop(0)
        yield topop

def GetWordBlocks(genwordslist, blockorder, blocklength):
    if len(np.bincount(blockorder)) != len(genwordslist):
        raise ValueError

    allblockwords = []
    for wordblock in blockorder:
        #allblockwords.append([genwordslist[wordblock].next() for word in range(blocklength)])
        #if running python 3 look at
        allblockwords.append([genwordslist[wordblock].__next__() for word in range(blocklength)])

    return allblockwords

########################What runs when you run this file!!#######

if __name__ == "__main__":
    #read the folder to use from bash stdin
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--folder", dest="folder",
                      help="the folder containing the wave files to choose from ",
                      default="./Verbatim_from_Shawna_and_John/Original_lib_2/")

    parser.add_option("-b", "--blocks", dest="blocks", type="int",
                  help="the number of blocks _per condition_ in the experiment", default=6)
    parser.add_option("-w", "--words", dest="words", type="int",
                  help="the number of words in each block", default=6)
    parser.add_option("-x", "--randomblocks", dest="randomblocks", type="int",
                  help="randomize the order of the blocks", default=False)
    parser.add_option("-z", "--testoutcomes", dest="testoutcomes", type="int",
                  help="test the distribution of outcomes n times", default=False)

    parser.add_option("-r", "--randomseed", dest="randomseed", type="int",
                  help="Set the randomseed to 0", default=False)

    parser.add_option("-o", "--outfilename", dest="outfilename",
                  help="the file you want to output to -- default is stdout", default='')

    parser.add_option("-s", "--shorso", dest="shorso",
                  help="how do you want to format the file -- shawna, sophie or john", default='sophie')

    parser.add_option("-c", "--conditions", dest="conditions",
                    help="a , seperated list of strings that prefix the sounds for each condition", default='')
    parser.add_option("-d", "--setdefaults", dest="setdefaults",
                    help="set basic defaults for EMOT or NEUT trials: overides anything set", default='')
    parser.add_option("-i", "--includeloads", dest="includeloads",
                    help="include load defs in the sce file", default='y')

    parser.add_option("-l", "--justloads", dest="justloads",
                    help="just write out the loads file", type="int", default=0)

    (options, args) = parser.parse_args()



    if options.setdefaults == '':
        pass
    elif options.setdefaults == "EMOT": #emotional impetus task
        options.words = 8
        options.blocks = 6
        options.conditions = "FES:0.0,FC:0.0"
        options.shorso = "john"
        options.randomblocks = True
        options.randomseed = False #do not set a random seed
    elif options.setdefaults == "NEUT": #neutral only task
        options.words = 5
        options.blocks = 6
        options.conditions = "MC:-1.0,MC:0.0,MC:1.0" # Left ear, Right ear, Both ears
        options.shorso = "john"
        options.randomblocks = True
        options.randomseed = False #do not set a random seed
    else:
        raise ValueError("setdefaults setting not valid!!")

    if options.randomseed: #set the radom seed to a constant value for repeatability
        np.random.seed(0)
    else:# randomize
        np.random.seed()


    prefixes = [i.split(":")[0] for i in options.conditions.split(",")]

    nconds = len(prefixes)
    blockorder = [j for i in range(options.blocks) for j in range(nconds)]
    if options.randomblocks:
        blockorder = np.random.permutation(blockorder).tolist()

    thisdir = options.folder
    files = os.listdir(thisdir) #the list of wave files to load (all of them!!)
    #get the base filenames
    basenames = [i[:-4] for i in files if i.endswith(".wav")]
    #get a list of strings each of which loads a wav file ect
    sep_statements = [GetLoadString(i) for i in basenames]
    #cat the load strings with a newline to make a single all-file load string
    loadstrings = ("\n").join(sep_statements)

    #The first type of block
    wordgendict = {}
    for wordtype in list(set(prefixes)):
        wordgendict[wordtype] = genwordfromlist([i for i in basenames if i.startswith(wordtype)])
    wordgenlists = [wordgendict[thisprefix] for thisprefix in prefixes]

    blockwords = GetWordBlocks(wordgenlists, blockorder, options.words)
    if options.outfilename != '':
        for i in blockwords:
            print("~~~~~~~~~~")
            for j in i:
                print(j)

    if options.testoutcomes:
        theseblockwords = []
        for i in range(options.testoutcomes):
            blockwords = GetWordBlocks(wordlists, blockorder, options.words)
            theseblockwords.extend(blockwords)

    if options.shorso == 'john':
        pans = [float(i.split(":")[1]) for i in options.conditions.split(",")]
        panorder = [float(pans[i]) for i in blockorder]
        blocksstring = GetBlockStringJohn(blockwords, "a1000ms_1khz", panorder)
    elif options.shorso == 'sophie':
        blocksstring = GetBlockStringSophie(blockwords, "a1000ms_1khz")
    elif options.shorso == 'shawna':
        blocksstring = GetBlockStringShawna(blockwords, "a1000ms_1khz")
    else:
        raise ValueError("shorso one of shawna, sophie or john")

    fullstr = ("\n").join([head, loadstrings, taskstart, blocksstring, tail])
    #We wanted to jam all the loads into a single file but couldn't seem to work it out
    # if options.includeloads:
    #     if options.includeloads == "y":
    #         fullstr = ("\n").join([head, loadstrings, taskstart, blocksstring, tail])
    #     else:
    #         fullstr = ("\n").join([head, 'include "%s"' % options.includeloads, taskstart, blocksstring, tail])
    # else:
    #     fullstr = ("\n").join([head, taskstart, blocksstring, tail])
    #
    # if options.justloads: fullstr = ("\n").join([loadstrings])

    if options.outfilename == '':
        outf = sys.stdout
        outf.write(fullstr)
    else:
        outf = open(options.outfilename, 'w')
        outf.write(fullstr)
        outf.close()
    #thispref = sys.argv[2]
    #thisnum = int(sys.argv[3])


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
"""
