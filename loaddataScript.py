#!/usr/bin/env python3

import os
import subprocess

for el in os.listdir("jsons"):
    if os.path.isdir("jsons/"):
        command_splitted = "python3 manage.py loaddata jsons/{}".format(
            el).split()
        subprocess.Popen(command_splitted).communicate()
