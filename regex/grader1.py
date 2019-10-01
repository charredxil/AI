#!/usr/bin/python3
#
# Regular expression grader
# New series

import sys, re, os, subprocess
# To do:
# 1.  Done: Indenting appropriately
# 2.  If there are no user defined test cases, should print out a passed all list
# 3.  Possibly consolidate all timeout, et. al. errors
# 4.  If syntax error, don't repeat the check for further tests

def indent(text, amt):
  return " "*amt + ("\n" + " "*amt).join(text.splitlines())


def updatePassed(dctPassed, reNum, regExp):
  if not reNum in dctPassed: dctPassed[reNum] = {}
  if not regExp in dctPassed[reNum]: dctPassed[reNum][regExp] = 0
  dctPassed[reNum][regExp] += 1
  


def testScript(script, testCases, testSum, scriptSum, tragic, passed):
  for reNum in testCases:
    errNum, rx, actOut, errOut, rxStr = getRegExpFromScript(script, reNum)
    # Uncomment next line to see what the test is on (for debugging purposes)
#    print ("{} got a regexp for reNum {}: {}".format(script, reNum, rxStr))
    passedTheseTests = True

    if errNum:
      details = "" if errNum!=6 else ": {}".format(rx)
      print ("{}: regex {} invalid with error code {}{}".format(script, reNum, errNum, details))
      if actOut: print ("  Actual out:\n{}".format(indent(actOut, 4)))
      if errOut: print ("  Error msg:\n{}".format(indent(errOut, 4)))
      if not script in tragic: tragic[script] = {}
      tragic[script][reNum] = errNum

      if errNum==-1:   # Syntax error should not be rechecked
        for reNum2 in testCases:
          tragic[script][reNum2] = -1
        return 
      continue

    # in this case we have to test the regexp
    testCase = testCases[reNum]
    # either a list of string (from command line), dictionary (for findAll), or list of two lists (for string test)

    if type(testCase)==dict:
      for test in testCase:
        testExpected = testCase[test]
        res = [x.group(0) for x in rx.finditer(test)]
#        res = rx.findall(test)
        if res != testExpected:
          passedTheseTests = False
          if script not in scriptSum: scriptSum[script] = set()
          scriptSum[script].add(reNum)
          testSumIdx = "{}:{}".format(reNum, test)
          if testSumIdx not in testSum: testSum[testSumIdx] = set()
          testSum[testSumIdx].add(script)
      if passedTheseTests: updatePassed(passed, reNum, rxStr)
#      if passedTheseTests:
#        if not reNum in passed: passed[reNum] = set()
#        passed[reNum].add(rxStr)
      continue

    if type(testCase[0])!=str:
      for test in testCase[0]:
        if not rx.search(test):
          passedTheseTests = False
          if script not in scriptSum: scriptSum[script] = set()
          scriptSum[script].add(reNum)
          testSumIdx = "{}:{}".format(reNum, test)
          if testSumIdx not in testSum: testSum[testSumIdx] = set()
          testSum[testSumIdx].add(script)
      for test in testCase[1]:
        if rx.search(test):
          passedTheseTests = False
          if script not in scriptSum: scriptSum[script] = set()
          scriptSum[script].add(reNum)
          testSumIdx = "{}:{}".format(reNum, test)
          if testSumIdx not in testSum: testSum[testSumIdx] = set()
          testSum[testSumIdx].add(script)
      if passedTheseTests: updatePassed(passed, reNum, rxStr)
#      if passedTheseTests:
#        if not reNum in passed: passed[reNum] = set()
#        passed[reNum].add(rxStr)
      continue

    for test in testCase:    # it's a list of strings, which outcome is not specified
#      res = rx.findall(test)
      res = [x.group(0) for x in rx.finditer(test)]
      testSumIdx = "{}:{}".format(reNum, test)
      if testSumIdx not in testSum: testSum[testSumIdx] = []
      pairFound = False
      for idx, pair in enumerate(testSum[testSumIdx]):
        if pair[0] == res:
          pairFound = True
          testSum[testSumIdx][idx][1].add(script)
          break
      if not pairFound:
        testSum[testSumIdx].append([res, {script}])
    if passedTheseTests: updatePassed(passed, reNum, rxStr)
#    if not reNum in passed: passed[reNum] = set()
#    passed[reNum].add(rxStr)


def parseCmdArgs():
  # returns: list of files, index of integers in [31,40]
  defaults = {
    31: [["0", "100", "101"], ["1", "1000", "1010", "10", "11", "0101", "0\n100"]],
    32: [["", "1", "0", "01", "10", "1010", "111", "000"], ["100x", "100\n001", "x100", "10,01"]],
    33: [["0", "10", "100", "110", "1000", "1010"], ["1", "11", "101", "111", "1001"]],
    34: {"The fort was defended": ["defended"],
         "Suzie saw seashells\nby the seashore": ["Suzie", "seashells", "seashore"]},
    35: [["0", "10", "100", "110", "1000", "1010"], ["1", "11", "101", "111", "1001", "010"]],
    36: [["110", "1100", "1110", "10110", "11100", "01101", "110110"], ["0", "21100", "1", "110x", "01", "011", "110\n11100"]],
    37: [["..", "ab", "x\ny", "0123", "xy\nz"], [".", "Hello", "My\nname\nis\nSam."]],
    38: [["123-54-6789",
          "542781963",
          "542  786163",
          "542 - 78-1063"],
         ["123--45-6789",
          "12-345-6789",
          "junk123-98-7654"]],

    39: {"He would have landed in Madrid\nhad it not been landlocked": ["He would", "had"]},
    40: [["0", "1", "00", "11", "101", "0100", "10011", "010100", "1001011", "010011000"], ["10", "01", "011", "1010", "10010"]],
    41: {"The problem with kittens\nis they grow up to become CATS.": ["problem", "kittens", "CATS"]},
    42: [["a", "010", "987\n65432", "even\nme"], ["", "23", "even\nqwert", ".hello"]],
    43: [["0", "11", "10", "010", "0100010"], ["", "1", "100", "00", "1100\n000", "1110\n1111"]],
    44: [["", "0", "1", "00", "01", "10", "11", "00100", "010101", "100001001011"],
         ["110", "0110", "1110", "01011001010"]],
    45: [['.'*27+'ox......xo'+'.'*27, 'X'*64, 'x.O'*20+'x..o'],
         ['?'*100, '@'*64, 'o'*63+"\\", "x"*64+"\nInvalid"]],
    46: [['xxoo.xxxo', 'xoxoooo.', '.xxxxxxx', 'OOOOO.OO'], ['xoxoxoox', '........', 'oxx..oox']],
    47: [['..o..o..', 'XOOOO..O', 'o...ooxx', 'OOOO....', 'xx....xx'], ['ooo...oo', 'xxxxxxxx', 'OO.XX.OO']], 
    48: [["c", "a", "bac", "bcacb", "bbbacc"], ["", "aa", "bcacba"]],
    49: [["aa", "bccb", "abcabc", "cbacabaabbcc"], ["", "a", "abcacba", "cbabacabc", "bbccacbbccb", "aab."]],
    50: [["11", "2002", "102102", "201210110022"], ["", "1", "1021201", "201012102", "001122", "112."]],

    51: [['b'+'a'*10+'c', 'd'+'e'*11+'f', 'g'+"\n"*10+ 'h'], ['j'+'k'*9+'m']],
    52: {"Aa lava is found in Hawaii.": ['Aa', 'ava', 'awa', 'ii'],
         "The eerie footstool spun slowly.": ['eerie', 'ootstoo', 'lowl']},
    53: {"I heard a really funny joke.": ['really', 'funny'],
         "He went on a fool's errand to Mississippi.": ['fool', 'errand', 'Mississippi']},
    54: {"Aa lava is found in Hawaii.": ['Aa', 'lava', 'Hawaii'],
         "The eerie footstool spun slowly.": ['eerie', 'footstool', 'slowly']},
    55: [["0", "1", "00", "11", "101", "000", "1001", "0100", "10011", "00111010"],
         ["", "01", "10", "100", "101\n111", "111000", "101010"]],
    56: {"cat in the hat": [],
         "Catnip is Cathys favorite": ['Catnip', 'Cathys'],
         "The sun would scathe the cattle": ['scathe', 'cattle']},
    57: [["0", "1", "00", "11", "101", "0100", "10011", "010100", "1001011", "010011000"], ["10", "01", "011", "1010", "10010"]],
    58: [["0", "1", "00", "11", "101", "0100", "10011", "010100", "1001011", "010011000"], ["10", "01", "011", "1010", "10010"]],
    59: {"One can acclimatize to the atmosphere in time": ["One", "acclimatize", "atmosphere"],
         "I'ts eerie that they aggregate when they are alone.": ["aggregate", "are", "alone"]},
    60: [["", "0", "1", "00", "01", "10", "11", "00100", "101010", "110100100001"],
         ["011", "0110", "0111", "01010011010"]],
    }

  args = sys.argv[1:]
  if not args: return [], defaults, False
  intLst = findIdxs(args, "^[3-5][0-9]$|^60$")
  if not intLst: return args, defaults, False

  userDefinedTests = False
  fspec = args[:min(intLst)]
  testCases = {}
  for ix, idx in enumerate(intLst):
    idx = int(idx)
    reNum = args[idx]
    if (ix==len(intLst)-1 and idx==len(args)-1) or (ix<len(intLst)-1 and int(intLst[ix+1])==idx+1):
      testCases[reNum] = defaults[int(reNum)]
    elif ix==len(intLst)-1:
      testCases[reNum] = args[idx+1:]
      userDefinedTests = True
    else:
      testCases[reNum] = args[idx+1:int(intLst[ix+1])]
      userDefinedTests = False
  return fspec, testCases, userDefinedTests


def findIdxs(lst, pattern):
  # returns the indeces where the rgex matches, else []
  return [i for i, v in enumerate(lst) if re.search(pattern, v)]



def findScripts(*fileSpec):
  # find all files in the durrent directory, subject to *filespec
  # After retrieving all files in the form of *.py
  # applies each of fileSpec fo the set of remaining scripts
  fileSpec = ["[.]py", "-^(contest|mod|grader|valid)"] + [*fileSpec]

  mypath = os.getcwd()
  for (dirpath, dirnames, filenames) in os.walk(mypath):
    #  filenames = {*filenames}
    break

  for spec in fileSpec:
    if not spec: continue
    if spec[0]=="-": filenames = {f for f in filenames if not re.search(spec[1:], f, re.I)}
    else:            filenames = {f for f in filenames if     re.search(spec,     f, re.I)}

  return filenames


def getRegExpFromScript(script, reNum):
  # errType: -1 for syntax, -2 for timeout, -3 for other script error,
  # -4 for no output, -5 for regexp not found, -6 for invalid regexp
  errType = 0
  actOut, errOut, timedOut = getScriptResults(script, ["{}".format(reNum)])

  if errOut and (errOut + actOut).find("SyntaxError")>-1: return -1, "", actOut, errOut, ""
  if timedOut == True:
#    print("actOut:\n{}".format(indent(actOut, 2)))
#    print("errOut:\n{}".format(indent(errOut, 2)))
#    exit()
    return -2, "", actOut, errOut, ""
  if errOut and (errOut + actOut).find("Traceback")>-1:   return -3, "", actOut, errOut, ""

#  if errOut.find("Traceback")>-1: return -3, "", actOut, errOut, ""

  if errOut:
    print ("script: {}; reNum: {}; timedOut: {}\nerrOut: {}".format(script, reNum, timedOut, errOut))
    exit()

  if not actOut: return -4, "", "", "", ""  
  match = re.search("^.*(\\s|:|^)/(.*)/([ism]*)[^/]*$", actOut, re.S)
  if not match: return -5, None, actOut, errOut, ""
#  print(match)
  rx = match.group(2)
  try:
    optDct = {"i": re.I, "s": re.S, "m": re.M}
    opt = sum(optDct[op] for op in set(match.group(3))) if match.group(3) else 0
    if opt: rex = re.compile(rx, opt)
    else:   rex = re.compile(rx)
  except Exception as exc:
    return -6, rx, actOut, "{}".format(exc), ""

  reTxt = "/{}/{}".format(rx, match.group(3))
  if reNum <= 40 and rx.find("(")>-1:   return -7, rx, actOut, "", reTxt  # we don't know about parens in the first 10 probs
  if reNum <= 50 and rx.find("\\1")>-1: return -7, rx, actOut, "", reTxt  # we don't know backreferences till problem 51
  if reNum <= 55 and rx.find("(?")>-1:  return -7, rx, actOut, "", reTxt  # we don't know lookarounds till problem 55
  if reNum == 57 and rx.find("(?<=")<0: return -7, rx, actOut, "", reTxt  # must use lookbehind
  if reNum == 58 and rx.find("(?=")<0:  return -7, rx, actOut, "", reTxt  # must use lookahead
  if reNum == 60 and rx.find("(?!")<0:  return -7, rx, actOut, "", reTxt  # should use negative lookahead

  return 0, rex, actOut, errOut, reTxt



def getScriptResults(script, lstArgs):
  tmOut   = 1  # 1 second is ample
  myargs = [ '"{}"'.format(sys.executable), "-u", '"{}"'.format(script)] + lstArgs
  timedOut = False

  if os.name == "posix":
    try:
      xcmd = "timeout {} {}".format(tmOut, " ".join(myargs + ["2>&1"]))
      x = subprocess.check_output(xcmd, shell=True)
    except Exception as exc:        # should be a subprocess.CalledProcessError exception
      errOut    = "{}".format(exc)
      actualOut = exc.stdout.decode()     # exc.stderr is not known
      if re.search("exit status 124$", "{}".format(exc)): timedOut = True
#      print("errOut:\n{}".   format(indent(errOut, 2)))
#      print("actualOut:\n{}".format(indent(actualOut, 2)))
#      exit()


#      timedOut  = True
#      print("errOut:\n{}".   format(indent(errOut, 2)))
#      print("actualOut:\n{}".format(indent(actualOut, 2)))
#      exit()
    else:
      errOut    = ""
      actualOut = x.decode()

  else:
    OUTFILE, ERRFILE = "out.txt", "err.txt"
    if os.path.isfile(OUTFILE): os.remove(OUTFILE)
    if os.path.isfile(ERRFILE): os.remove(ERRFILE)
    myargs += [ ">{}".format(OUTFILE), "2>{}".format(ERRFILE) ]


    po = subprocess.Popen ( " ".join(myargs), shell=True )
    try:
      po.wait(float(tmOut))
    except subprocess.TimeoutExpired:
      timedOut = True
      print ("Initiating TASKKILL of {}".format(po.pid))
      pok = subprocess.Popen("TASKKILL /F /PID {} /T".format(po.pid))
      pok.wait(20)    # waiting for TASKKILL to finish
    errOut    = open("err.txt", "r").read().strip() if os.path.isfile("err.txt") else ""
    actualOut = open("out.txt", "r").read().strip() if os.path.isfile("out.txt") else ""
  
  return actualOut, errOut, timedOut



fspec, testCases, userDefinedTestsP = parseCmdArgs()
scriptLst = findScripts(*fspec)
testCases = {tc:testCases[tc] for tc in testCases if tc in {*range(31,61)}}

#print ("Ready to do some work")


def DictvkToList(dct):
  return ["{}:{}".format(dct[k],k) for k in dct]

testSum =   {}   # {reNum:  {failedScript}}
scriptSum = {}   # {script: {failedReNum}
tragic  =   {}   # {script: {reNum: errorNum}
passed  =   {}   # {reNum:  {regex: count}} 

for script in scriptLst:
#  print("About to test script {}".format(script))
  testScript(script, testCases, testSum, scriptSum, tragic, passed)



# standard test summary: print which scripts have failed, by individual test
for test in sorted([*testSum]):
  if type(testSum[test])==set:
    print ("Test {} failed by: {}".format(test, testSum[test]))

# regular expressions that appear to pass each test.
for reNum in sorted([*passed]):
  if passed[reNum]:
#    print("\nPassed all tests for regular expression {}:\n{}".format(reNum, indent("\n".join(sorted([*passed[reNum]])), 2)))
    print("\nPassed all tests for regular expression {}:\n{}".format(reNum, indent("\n".join(sorted(DictvkToList(passed[reNum]))), 2)))


# user test results
for test in testSum:
  if type(testSum[test])==set: continue
  print ("\nTest {} results:\n".format(test))
  for pair in testSum[test]:
    print ("  Result {} by: {}".format(pair[0], pair[1]))


if scriptSum: print("\nFailures:")
for script in scriptSum:
  print ("  {} on: {}".format(script, sorted([*scriptSum[script]])))


# these are the tragedies
# Tragedies are indexed by script
#   Values are dictionary indexed by regExp #: error
if len(tragic): print("\nTragedies:")
for trag in tragic:
  inverted = {v: {k for k in tragic[trag].keys() if tragic[trag][k]==v} for v in tragic[trag].values()}
  if len(inverted)==1:
    print ("  {} had error {} on problem {}".format(trag, [*inverted][0], sorted([*tragic[trag].keys()])))
  else:
    print ("  {} had the following errors:".format(trag))
    for errNum in inverted:
      print("    Error {} on problem {}".format(errNum, inverted[errNum]))





if not userDefinedTestsP:
  passedAll = scriptLst - {*scriptSum} - {*tragic}
  print ("\nPassed all: {}".format(sorted([*passedAll])))
  
