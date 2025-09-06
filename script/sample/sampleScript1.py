import relex

def testSetup():
    #STEP - Sample step 1
    output = connect(vm1, "ssh")
    if output["result"] == "ok":
        OK("Success in connecting to vm1")
    else:
        FAIL("Failure in connecting to vm1")
    vm1h = output["session"]
    output = connect(vm2, "ssh")
    if output["result"] == "ok":
        OK("Success in connecting to vm2")
    else:
        FAIL("Failure in connecting to vm2")
    vm2h = output["session"]
    OK("Setup step 1")

    #CLEAN - Sample clean 1
    output = close(vm1h)
    if output["result"] == "ok":
        OK("Success in closing vm1")
    else:
        FAIL("Failure in closing vm1")
    output = close(vm2h)
    if output["result"] == "ok":
        OK("Success in closing vm2")
    else:
        FAIL("Failure in closing vm2")
    OK("Setup clean 1")

    #STEP - Sample step 2
    OK("Setup step 2")

    #CLEAN - Sample clean 2
    OK("Setup clean 2")

def Test1():
    #STEP - Test Step 1
    print(param["vars"]["x"])
    output = lib("func", "checkFile", vm1h, "bashrc")
    if output["result"] == "ok":
        OK("File bashrc exists in vm1")
    else:
        FAIL("File bashrc does not exist in vm1")
    OK("Test 1, step 1", "TestCase")

    #CLEAN - Test Clean 1
    OK("Test 1, clean 1")

def Test2():
    #STEP - Test Step 1
    print(param["vars"]["x"])
    output = command(vm2h, "ls -lart", "\$")
    if re.search("bashrc" , output):
        OK("File bashrc exists in vm2")
    else:
        FAIL("File bashrc does not exist in vm2")
    OK("Test 2, step 1")

    #CLEAN - Test Clean 1
    OK("Test 2, clean 1")

    #STEP - Test Step 2
    output = command(vm2h, "pwd", "\$")
    if not re.search("command" , output):
        OK("pwd command executed successfully in vm2","TestCase")
    else:
        FAIL("pwd command thrown an error in vm2")
    OK("Test 2, step 2")

    #CLEAN - Test Clean 1
    OK("Test 2, clean 2")

relex.testExec(testSetup, Test1, Test2)