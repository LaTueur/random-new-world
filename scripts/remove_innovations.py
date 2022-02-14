import regex
import os
import apply_script as pdx_parser
import codecs
from shared_functions import *

innovation_path = "common/culture/innovations"
path = os.path.join(game_path, innovation_path)
mod_path = "../Random New World"
effects_path = "common/scripted_effects"
out_path = os.path.join(mod_path, effects_path)
file_name = "rnw_generated_innovation_scripted_effects.txt"

text = "rnw_remove_innovations_from_culture_effect = {\n"
for innovation in filter(lambda x: x[0] != "@", map(lambda x: x[0], join_files(path, "txt"))):
    text += f"if = {{ limit = {{ has_innovation = {innovation} }} remove_innovation = {innovation} }} "
text += "}"

write_output(out_path, file_name, text)