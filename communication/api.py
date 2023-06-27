import subprocess

"""
Expected API Behavior:
    Args:
        1. COMMAND (str):      Command to execute = "GET" || "SET"
        2. TAG (str):          Tag to search for.
        3. VALUE (str):        Value to set. (Dependent on COMMAND being "SET")

    Return:
        {TAG}-{GET,SET}-{VALUE}-{SUCCESS,FAIL}
"""


class API:
    EXECUTABLE = "python3"
    PATH = ""

    def execute(self, executable=None, path=None, *args) -> str:
        """
        Parameters:
            *args (str):        Command line arguments to be passed to the program.

        Optional Parameters:
            executable (str):   How to run the program (e.g., 'python3', 'g++', 'echo', etc.)
            path (str):         Path to the file to run.

        Returns:
            str:                The output of the executed CLI program.
        """
        if executable is None:
            executable = self.EXECUTABLE
        if path is None:
            path = self.PATH

        return self._exec(executable, path, *args)

    def _exec(self, executable: str, path: str, *args) -> str:
        """
        Parameters:
            executable (str):   How to run the program (e.g., 'python3', 'g++', 'echo', etc.)
            path (str):         Path to the file to run.
            *args (str):        Command line arguments to be passed to the program.

        Returns:
            str:                The output of the executed CLI program.
        """
        # Command to execute
        command = [executable, path] + list(args)

        # Run command, capturing STDOUT and STDERR with subprocess.PIPE
        process = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        if process.returncode != 0:
            return f"EXEC ERROR: {process.stderr}"

        return process.stdout

    def get(self, tag: str) -> str:
        """
        Parameters:
            tag (str):          Tag to search for.

        Returns:
            str:                Value returned by Simulator
        """
        return self.execute(self.EXECUTABLE, self.PATH, "GET", str(tag))

    def set(self, tag: str, value: str) -> str:
        """
        Parameters:
            tag (str):          Target Tag.
            value (str):        Value to set.

        Returns:
            str:                Value returned by Simulator.
        """
        return self.execute(self.EXECUTABLE, self.PATH, "SET", str(tag), str(value))
