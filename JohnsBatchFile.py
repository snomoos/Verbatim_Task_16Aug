import PyRandomFilesComplete_Simple as PRFCS

nn = 100
if __name__ == "__main__":
    #read the folder to use from bash stdin
    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option("-o", "--outfilename", dest="outfilename",
                  help="name of the output file without suffix", default='')
    parser.add_option("-f", "--filelist", dest="filelist",
                  help="comma seperated list of files to use", default="")

    (options, args) = parser.parse_args()
    if options.outfilename == '':
        raise ValueError("No output filename doofus!")

    files = options.filelist.split(",")
    genlist = [PRFCS.genwordfromlist(i) for i in files]
    basenames = ['a1000ms_1khz']
    for x in genlist: basenames.extend([i for i in x.names])
    basenames = list(set(basenames))
    sep_statements = [PRFCS.GetLoadString(i) for i in basenames]
    loadstrings = ("\n").join(sep_statements)

    for i in range(nn):
        PRFCS.np.random.seed(i)
        blockwords, blockpans = PRFCS.GetWordBlocks(genlist)
        blocksstring = PRFCS.GetBlockStringJohn(blockwords, "a1000ms_1khz", blockpans)
        fullstr = ("\n").join([PRFCS.head, loadstrings, PRFCS.taskstart, blocksstring, PRFCS.tail])
        outf = open(options.outfilename+str(i)+".sce", 'w')
        outf.write(fullstr)
        outf.close()
        print(i)
