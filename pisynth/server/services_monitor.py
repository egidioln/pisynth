import subprocess
from threading import Thread
import time
import re

PROGRAMS_TO_MONITOR = ['jackd', 'a2jmidid', 'qsynth']


class Monitor(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()

    # Function to check if a program is running
    def is_program_running(self, program_name):
        try:
            output = subprocess.check_output(["pgrep", program_name])
            return len(output.splitlines()) > 0
        except subprocess.CalledProcessError:
            return False

    # Function to start a program
    def start_program(self, program_name):
        if program_name == "jackd":
            self._start_jackd()
        if program_name == "qsynth":
            self._start_qsynth()
        if program_name == "a2jmidid":
            self._start_a2jmidid()
        

    def _start_jackd(self):
        n_device = _get_best_device()
        subprocess.Popen([
            "jackd",
            "-P70",
            "-p16",
            "-t2000",
            "-dalsa",
            f"-dhw:{n_device}",
            "-p128",
            "-n3",
            "-r44100",
            "-s",
        ])


    def _start_qsynth(self):
        subprocess.Popen(["qsynth"])

    def _start_a2jmidid(self):
        subprocess.Popen(["a2jmidid", "-e"])



    # Function to monitor the programs
    def run(self):
        while True:
            for program_name in PROGRAMS_TO_MONITOR:
                if not self.is_program_running(program_name):
                    print(f"{program_name} is not running. Starting...")
                    self.start_program(program_name)

            
            time.sleep(0.5)  # Adjust the interval as needed

def _get_best_device():
    output = subprocess.check_output(['aplay','-l'])
    output = re.findall(b"card (\d+): CODEC", output)
    if output:
        return int(output[0])
    return 0
