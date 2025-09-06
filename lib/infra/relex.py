import sys
import inspect
import logging
import testLogger
import testArgs
import datetime
import code
import re
import os
import pexpect
import yaml
import types
import imp

sys.dont_write_bytecode = True

#     Holds counters and messages for test execution reporting.
#     Tracks pass/fail counts, info/debug messages, and test status.
reportVars = types.SimpleNamespace(
    PassCount=0,
    FailCount=0,
    InfoCount=0,
    DebugCount=0,
    TestPassCount=0,
    TestFailCount=0,
    SetupFail=False,
    TestFail=False,
    Message=[],
)

#     Stores properties and counters for test steps.
#     Controls abort/continue behavior on failure.
stepProperty = types.SimpleNamespace(
    AbortOnFail=False,
    ContinueOnFail=False,
    SetupStepCount=0,
    TestStepCount=0,
)

#     Stores global configuration variables for the test run.
#     Includes file paths, log level, and current section.
commonVars = types.SimpleNamespace(
    currentSection=None,
    currentSectionFailFlag=False,
    currentTest=None,
    logfile=None,
    stationfile=None,
    paramfile=None,
    loglevel=None,
    stnmatchlist=[],
    stnbkplist={},
)


def OK(msg, test=False):
    """
    Log a successful test step.
    Increments pass counters and appends a formatted message.
    """
    reportVars.PassCount += 1
    if test == "TestCase":
        reportVars.TestPassCount += 1
    logger.ok(msg)
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    append_msg = time + " - [OK] - " + msg
    reportVars.Message.append(append_msg)


def FAIL(msg):
    """
    Log a failed test step.
    Increments fail counters, sets fail flags, and aborts if needed.
    """
    reportVars.FailCount += 1
    if commonVars.currentSection == "Setup":
        reportVars.SetupFail = True
    else:
        if not reportVars.TestFail:
            reportVars.TestFail = True
            reportVars.TestFailCount += 1
    logger.fail(msg)
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    append_msg = time + " - [FAIL] - " + msg
    reportVars.Message.append(append_msg)
    if stepProperty.AbortOnFail == True:
        INFO("*** Aborting Script on Failure ***")
        reportSummary()
        sys.exit(1)


def ERROR(msg):
    """
    Log an error during test execution.
    Increments fail counters, sets fail flags, and aborts if needed.
    """
    reportVars.FailCount += 1
    if commonVars.currentSection == "Setup":
        reportVars.SetupFail = True
    else:
        if not reportVars.TestFail:
            reportVars.TestFail = True
            reportVars.TestFailCount += 1
    logger.error(msg)
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    append_msg = time + " - [ERROR] - " + msg
    reportVars.Message.append(append_msg)
    if stepProperty.AbortOnFail == True:
        INFO("*** Aborting Script on Failure ***")
        reportSummary()
        sys.exit(1)


def INFO(msg):
    """
    Log an informational message.
    Increments info counter and appends a formatted message.
    """
    reportVars.InfoCount += 1
    logger.info(msg)
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    append_msg = time + " - [INFO] - " + msg
    reportVars.Message.append(append_msg)


def DEBUG(msg):
    """
    Log a debug message.
    Increments debug counter and appends a formatted message.
    """
    reportVars.DebugCount += 1
    logger.debug(msg)
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    append_msg = time + " - [DEBUG] - " + msg
    reportVars.Message.append(append_msg)


def reportSummary():
    """
    Print a summary of all test results and messages.
    Shows pass/fail counts and script status.
    """
    print("\n")
    SummaryReport = "\n".join(reportVars.Message)
    banner = "Execution Summary"
    print("=" * 100)
    print(banner.rjust(70))
    print("=" * 100)
    print(SummaryReport)
    print("=" * 100)
    print("=" * 100)
    print("+" + "-" * (52) + "+")
    msg = "Total Number Of Test Passed = {}".format(reportVars.TestPassCount)
    summaryFormatter(msg)
    msg = "Total Number Of Test Failed = {}".format(reportVars.TestFailCount)
    summaryFormatter(msg)
    if reportVars.FailCount == 0 and reportVars.TestPassCount == 0:
        msg = "Script dont have pass criteria for TestCases!"  # .rjust(35)
    elif reportVars.FailCount == 0:
        msg = "Script has Passed!"  # .rjust(35)
    else:
        if reportVars.SetupFail:
            msg = "Script has Failed in Setup!"
        else:
            msg = "Script has Failed!"  # .rjust(35)
    summaryFormatter(msg)
    print("+" + "-" * (52) + "+")


def summaryFormatter(line):
    """
    Format and print a summary line with fixed width.
    Args:
        line: String to format.
    """
    line = [line[0 + i : 50 + i] for i in range(0, len(line), 50)]
    print("| {0:^{1}} |".format(line[0], 50))


def splitTestRunner(*testlist):
    """
    Run each test function in the provided list.
    Splits test steps, executes them, and logs results.
    Args:
        *testlist: One or more test functions to execute.
    """
    for test in testlist:
        # INFO("+++ Starting Execution Of TestCase +++")
        commonVars.currentSectionFailFlag = False
        testObj = testProc(test)
        testObj.splitTest()
        INFO("+++ Starting Execution Of {} +++".format(commonVars.currentTest))
        stepProperty.TestStepCounter = 0
        testObj.runTestStep()
        testObj.runTestClean()
        # reportVars.TestPassCount+=1
        INFO("+++ Ending Execution Of {} +++".format(commonVars.currentTest))


def execBlock(codeblock):
    """Executes a block of code, handling exceptions."""
    try:
        testblock = "\n".join(
            re.sub(r"^\s{4}", "", sline) for sline in codeblock.split("\n")
        )
        exec(testblock, globals())
    except Exception as exp:
        ERROR(f"Exception Occured - {type(exp).__name__} - {exp}")
        return False
    return True


class splitProc:
    """Base class for splitting and executing steps and cleanups."""

    def __init__(self, src_func):
        self.src_func = src_func
        self.stepList = []
        self.cleanList = []
        self.stepCounter = 0

    def splitStepClean(self):
        srclines = inspect.getsourcelines(self.src_func)[0]  # [1:]
        funcName = srclines.pop(0)
        try:
            functionName = re.search("def\s+(\S+)\(\):", funcName).group(1)
            commonVars.currentTest = functionName
        except:
            pass
        srclines = "".join(srclines)
        testlines = re.split("#STEP.*\n", srclines)
        for line in testlines:
            if line:
                split_lines = re.split("#CLEAN.*\n", line)
                self.stepList.append(split_lines[0])
                self.cleanList.append(split_lines[1] if len(split_lines) > 1 else "")


class setupProc(splitProc):
    """Handles setup steps and cleanup for test execution."""

    def __init__(self, testSetup):
        super().__init__(testSetup)

    def splitSetup(self):
        """
        Split the setup function source code into step and clean blocks.
        Populates setupStepList and setupCleanList.
        """
        super().splitStepClean()

    def runSetupStep(self):
        """Execute setup steps sequentially."""
        reportVars.SetupFail = False
        self.stepCounter = 0
        for codeblock in self.stepList:
            if reportVars.SetupFail:
                break
            self.stepCounter += 1
            if not execBlock(codeblock):
                reportVars.SetupFail = True
                break

    def runSetupClean(self):
        """Execute setup cleanup steps in reverse order."""
        for codeblock in reversed(self.cleanList):
            if self.stepCounter <= 0:
                break
            self.stepCounter -= 1
            execBlock(codeblock)


class testProc(splitProc):
    """Handles splitting and execution of test steps and cleanup."""

    def __init__(self, testFunc):
        super().__init__(testFunc)

    def splitTest(self):
        """
        Split the test function source code into step and clean blocks.
        Populates setupStepList and setupCleanList.
        """
        super().splitStepClean()

    def runTestStep(self):
        """Execute test steps sequentially."""
        commonVars.currentSection = "Test"
        reportVars.TestFail = False
        self.stepCounter = 0
        for codeblock in self.stepList:
            if reportVars.TestFail and not stepProperty.ContinueOnFail:
                break
            self.stepCounter += 1
            if not execBlock(codeblock):
                reportVars.TestFail = True
                if not stepProperty.ContinueOnFail:
                    break

    def runTestClean(self):
        """Execute test cleanup steps in reverse order."""
        for codeblock in reversed(self.cleanList):
            if self.stepCounter <= 0:
                break
            self.stepCounter -= 1
            execBlock(codeblock)


def stationLoader():
    """
    Loads station and parameter data from YAML files.
    Matches parameters to stations and sets up global references.
    Populates backup lists for alternative matches.
    """
    global param
    global station
    global device
    try:
        with open(commonVars.stationfile) as tb_data:
            station_data = yaml.safe_load(tb_data)
        with open(commonVars.paramfile) as pf_data:
            param_data = yaml.safe_load(pf_data)
    except Exception as e:
        ERROR(f"Error loading files: {e}")
        return

    param = param_data
    station = station_data
    commonVars.stnmatchlist = []
    commonVars.stnbkplist = {}

    for paramkey, paramfields in param_data.items():
        if paramkey == "vars":
            continue
        first_match = True
        commonVars.stnbkplist[paramkey] = {}
        for stnkey, stnfields in station_data.items():
            if all(item in stnfields.items() for item in paramfields.items()):
                if stnkey not in commonVars.stnmatchlist:
                    if first_match:
                        globals()[paramkey] = station_data[stnkey]
                        commonVars.stnmatchlist.append(stnkey)
                        first_match = False
                    else:
                        commonVars.stnbkplist[paramkey][stnkey] = {}
                        commonVars.stnbkplist[paramkey][stnkey] = stnfields
        if not first_match:
            DEBUG(
                f"Backup stations for '{paramkey}' are '{list(commonVars.stnbkplist.get(paramkey, []).keys())}'"
            )
            globals()["device"] = paramkey
        else:
            DEBUG(f"No match found for param '{paramkey}'")
    for stn in commonVars.stnmatchlist:
        for paramkey in param_data.keys():
            if paramkey != "vars":
                try:
                    if stn in commonVars.stnbkplist[paramkey]:
                        del commonVars.stnbkplist[paramkey][stn]
                except KeyError:
                    pass


def testExec(Setup, *test):
    """
    Executes the test workflow:
    - Initializes logging and configuration variables.
    - Loads station and parameter data.
    - Runs setup steps and cleans up.
    - Executes test cases if setup succeeds.
    - Prints a summary report.
    Args:
        Setup: Setup function to run before tests.
        *test: One or more test functions to execute.
    """
    # Run the setup function
    arg = testArgs.testArgs()
    commonVars.logfile = arg.logfile
    commonVars.stationfile = arg.station
    commonVars.paramfile = arg.param
    commonVars.loglevel = arg.loglevel
    testLogger.initLogging(logFile=arg.logfile, level=arg.loglevel)
    global logger
    logger = logging.getLogger(__name__)
    logger.info("Log file: {}".format(arg.logfile))
    logger.info("Station file: {}".format(arg.station))
    logger.info("Param file: {}".format(arg.param))
    logger.info("Log level: {}".format(arg.loglevel))
    stationLoader()
    INFO(
        "*** Starting Execution Of Script - {} ***".format(
            os.path.realpath(sys.argv[0])
        )
    )
    setupObj = setupProc(Setup)
    commonVars.currentSection = "Setup"
    setupObj.splitSetup()
    setupObj.runSetupStep()
    if reportVars.SetupFail == False:
        splitTestRunner(*test)
    setupObj.runSetupClean()
    INFO("*** Ending Script Execution ***")
    reportSummary()


def connect(conDev, protocol="ssh"):
    """
    Establish a connection to a device using SSH or Telnet.
    Handles failover to backup devices if connection fails.
    Args:
        conDev: Device dictionary with connection details.
        protocol: Connection protocol ("ssh" or "telnet").
    Returns:
        Dictionary with result status and session handle.
    """
    ip = conDev["ip"]
    port = conDev["port"]
    user = conDev["user"]
    password = conDev["password"]
    output = {}
    output["result"] = "fail"
    output["session"] = None
    if re.match("ssh", protocol, re.I):
        if re.match("linux", conDev["type"], re.I):
            prompt = "\$"
        else:
            prompt = conDev["prompt"]
        conDevSession = connect_ssh(ip, user, password, prompt, port)
        for paramkey in param.keys():
            if paramkey != "vars":
                if globals()[paramkey] == conDev:
                    try:
                        bkp_list_dict = commonVars.stnbkplist[paramkey]
                        bkp_list = list(bkp_list_dict.items())
                    except KeyError:
                        bkp_list = []
                    break
        while conDevSession == "fail":
            with open(os.path.expanduser("~/.REXdevDownList"), "a+") as f:
                f.seek(0)
                content = f.read()
                if not re.search(conDev["name"], content):
                    f.write(conDev["name"] + "\n")
            if not bkp_list:
                return output
            for newconDev in bkp_list:
                for paramkey in param.keys():
                    if paramkey != "vars":
                        if globals()[paramkey] == conDev:
                            conDev = newconDev[1]
                            globals()[paramkey] = conDev
                            bkp_list.remove(newconDev)
                break
            for paramkey in param.keys():
                if paramkey != "vars":
                    for k, v in commonVars.stnbkplist[paramkey].items():
                        if v == conDev:
                            commonVars.stnbkplist[paramkey].pop(k, None)
                            DEBUG(
                                f"Removed {v['name']} from backup list for {paramkey}"
                            )
                            break
            ip = conDev["ip"]
            port = conDev["port"]
            user = conDev["user"]
            password = conDev["password"]
            if re.match("linux", conDev["type"], re.I):
                prompt = "\$"
            else:
                prompt = conDev["prompt"]
            conDevSession = connect_ssh(ip, user, password, prompt, port)
    output["result"] = "ok"
    output["session"] = conDevSession
    station[conDevSession] = conDev
    return output


def connect_ssh(ip, user, password, prompt, port=22, timeout=30):
    """
    Establish an SSH connection using pexpect.
    Handles authentication and prompt matching.
    Args:
        ip: IP address of the device.
        user: Username.
        password: Password.
        prompt: Shell prompt to expect.
        port: SSH port (default 22).
        timeout: Timeout for connection (default 30).
    Returns:
        pexpect handle or "fail" on error.
    """
    spawn_string = "ssh " + user + "@" + ip + " -p " + port
    handle = pexpect.spawn(spawn_string)
    handle.logfile_read = sys.stdout.buffer
    handle.timeout = timeout
    while True:
        if isinstance(prompt, bytes):
            prompt = prompt.decode()
        idx = handle.expect(
            [
                "continue connecting (yes/no)?",
                "password:",
                "Password",
                prompt,
                pexpect.EOF,
                pexpect.TIMEOUT,
            ]
        )
        if idx == 0:
            handle.sendline("yes")
        if 1 <= idx <= 2:
            handle.sendline(password)
        if idx == 3:
            handle.sendline()
            handle.expect(prompt)
            break
        if idx == 4:
            handle = "fail"
            INFO("connection closed unexpectedly for {}".format(ip))
            break
        if idx == 5:
            handle = "fail"
            INFO("Timeout in getting connection for {}".format(ip))
            break
    return handle


def connect_telnet(ip, user, password, prompt, timeout=30):
    """
    Establish a Telnet connection using pexpect.
    Handles authentication and prompt matching.
    Args:
        ip: IP address of the device.
        user: Username.
        password: Password.
        prompt: Shell prompt to expect.
        timeout: Timeout for connection (default 30).
    Returns:
        pexpect handle or "fail" on error.
    """
    spawn_string = "telnet" + " " + ip
    handle = pexpect.spawn(spawn_string)
    handle.logfile_read = sys.stdout
    while True:
        idx = handle.expect(
            [
                "user:",
                "User:",
                "username:",
                "Username:",
                "password:",
                "Password:",
                prompt,
                pexpect.EOF,
                pexpect.TIMEOUT,
            ]
        )
        if 0 <= idx <= 3:
            handle.sendline(user)
        if 4 <= idx <= 5:
            handle.sendline(password)
        if idx == 6:
            handle.sendline()
            handle.expect(prompt)
            break
        if idx == 7:
            handle = "fail"
            INFO("connection closed unexpectedly for (}".format(ip))
            break
        if idx == 8:
            handle = "fail"
            INFO("Timeout in getting connection for {}".format(ip))
            break
    return handle


def command(handle, cmd, prompt="", timeout=30):
    """
    Send a command to the device and capture output.
    Handles prompt matching and timeouts.
    Args:
        handle: pexpect session handle.
        cmd: Command string to send.
        prompt: Expected prompt after command (optional).
        timeout: Timeout for command execution (default 30).
    Returns:
        Command output as string.
    """
    if prompt == "":
        prompt = stepProperty.prompt[handle]
    handle.timeout = timeout
    expect_list = [pexpect.EOF, pexpect.TIMEOUT]
    if isinstance(prompt, str):
        expect_list.append(prompt)
    elif isinstance(prompt, list):
        expect_list = expect_list + prompt
    else:
        INFO("Prompt doesnt match any category!")
    handle.flush()
    handle.sendline(cmd)
    idx = handle.expect(expect_list)
    if idx == 0:
        INFO("connection closed unexpectedly")
        return
    elif idx == 1:
        cmd_output = handle.before
        cmd_output = cmd_output.split("\r\n")
        try:
            cmd_output.pop(0)
        except IndexError:
            cmd_output = "\r\n".join(cmd_output)
        INFO("Timeout in executing command")
        return cmd_output
    else:
        pmt = expect_list[idx]
        cmd_output = handle.before
        cmd_output = cmd_output.decode("utf-8", errors="ignore")
        cmd_output = cmd_output.split("\r\n")
        try:
            cmd_output.pop(0)
            cmd_output.remove(pmt)
        except (IndexError, ValueError):
            pass
        cmd_output = "\r\n".join(cmd_output)
        return cmd_output


def sendCntrl(handle, char):
    """
    Send a control character to the device session.
    Args:
        handle: pexpect session handle.
        char: Control character to send.
    """
    handle.sendControl(char)


def close(handle):
    """
    Close the device session handle.
    Returns a result dictionary indicating success or failure.
    Args:
        handle: pexpect session handle.
    Returns:
        Dictionary with result status.
    """
    output = {}
    output["result"] = "fail"
    try:
        handle.close()
    except Exception as exp:
        ERROR("Exception Occured - " + type(exp).__name__ + " - " + str(exp))
        return output
    output["result"] = "ok"
    return output


def pause():
    """
    Pause execution and open an interactive shell for debugging.
    """
    code.interact(local=globals())


def lib(fnType, fnName, *args, **kwargs):
    """
    Dynamically invoke a function by name with arguments.
    Args:
        fnName: Name of the function to invoke.
        fnType: Identifies the type of function.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
    Returns:
        Result of the invoked function or None on error.
    """
    basepath = os.path.dirname(os.path.abspath(__file__))
    if fnType == "util":
        fnPath = basepath + "/../" + "utility" + "/" + fnName + ".py"
    elif fnType == "wf":
        fnPath = basepath + "/../" + "workflow" + "/" + fnName + ".py"
    elif fnType == "func":
        type = station[args[0]]["type"]
        fnPath = basepath + "/../" + "func" + "/" + type + "/" + fnName + ".py"
    try:
        fnCall = imp.load_source(fnName, fnPath)
    except IOError:
        ERROR("Unable to find function in path - {}".format(fnPath))
        return
    tmpfunc = getattr(fnCall, fnName)
    return tmpfunc(*args, **kwargs)
