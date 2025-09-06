import relex
import re


def checkFile(handle, fileName):
    """
    Check if a file exists.
    Args:
        handle: Device handle.
        fileName: File to check.
    Returns:
        result: "ok" if file exists, "fail" otherwise.
    """
    cmd_output = relex.command(handle, "ls -lart", "\$")
    output = {}
    if re.search(fileName, cmd_output):
        output["result"] = "ok"
    else:
        output["result"] = "fail"
    return output
