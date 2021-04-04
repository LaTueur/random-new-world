import regex
import os
import apply_script as pdx_parser
import codecs
from shared_functions import *

history_path = "history/cultures"
path = os.path.join(game_path, history_path)
mod_path = "../Random New World Innovations"
out_path = os.path.join(mod_path, history_path)

for file in os.listdir(path):
    write_output(out_path, file, "20.3.30 = {}")