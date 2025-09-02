import logging
import sys
import re


def initLogging(logFile="app.log", level="debug"):
    logger = logging.getLogger()

    # Prevent duplicate handlers in case of multiple calls
    if logger.handlers:
        return

    # Format for logs
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Define custom levels
    logging.OK = 25
    logging.FAIL = 35

    # Register the levels with the logging module
    logging.addLevelName(logging.OK, "OK")
    logging.addLevelName(logging.FAIL, "FAIL")

    def ok(self, message, *args, **kws):
        if self.isEnabledFor(logging.OK):
            self._log(logging.OK, message, args, **kws)

    def fail(self, message, *args, **kws):
        if self.isEnabledFor(logging.FAIL):
            self._log(logging.FAIL, message, args, **kws)

    logging.Logger.ok = ok
    logging.Logger.fail = fail
    logMethods = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "ok": logging.OK,
        "warning": logging.WARNING,
        "fail": logging.FAIL,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    logger.setLevel(logMethods[level])
    # Console handler (output to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler (output to file)
    file_handler = open(logFile, "a", buffering=1)
    file_handler = logging.StreamHandler(file_handler)
    file_handler.setFormatter(formatter)

    # Add handlers to the root logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


    ansi_escape = re.compile(
    rb'''
    \x1B\[ [0-?]* [ -/]* [@-~]      |
    \x1B\] .*? (?:\x07|\x1B\\)      |
    \x1B[@-Z\\-_]                   |  
    \r                                
    ''',
    re.VERBOSE,
    )
    # Tee logger to log both to terminal and file
    class teeLogger:
        def __init__(self, logFile):
            self.terminal = sys.stdout.buffer
            self.log = open(logFile, "ab")
            self.buffer = self

        def write(self, message):
            if isinstance(message, str):
                data = message.encode()
            else:
                data = message
            clean_data = ansi_escape.sub(b'', data)
            self.terminal.write(data)
            self.terminal.flush()
            self.log.write(clean_data)
            self.log.flush()

        def flush(self):
            self.terminal.flush()
            self.log.flush()

        def close(self):
            self.log.close()
    sys.stdout= teeLogger(logFile)