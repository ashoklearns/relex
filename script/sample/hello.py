###############################
#
# Sample Script: Hello, World!
#
###############################
import relex

def Setup():
    #STEP - Sample step 1
    OK("Setup step 1")

    #CLEAN - Sample clean 1
    OK("Setup clean 1")

    #STEP - Sample step 2
    OK("Setup step 2")

    #CLEAN - Sample clean 2
    OK("Setup clean 2")

def Test():
    #STEP - Test Step 1
    INFO("This is a variable i defined in param file: " + param["vars"]["msg"])
    OK("Test step 1")

    #CLEAN - Test Clean 1
    OK("Test clean 1")

    #STEP - Test Step 2
    OK("Hello, World", "TestCase")

    #CLEAN - Test Clean 2
    OK("Test clean 2")

relex.testExec(Setup, Test)