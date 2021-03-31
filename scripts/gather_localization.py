import regex
import os
import apply_script as pdx_parser
import codecs
from shared_functions import *

localization_key_pattern = regex.compile(r"localization_key\s*=\s*(\w+)")
comment_pattern = regex.compile(r"(#)[^\n]*")

custom_loc = dumpfiles("../Random New World/common/customizable_localization")
loc_keys = localization_key_pattern.findall(custom_loc)
output = "l_english:\n"
for loc_key in loc_keys:
    output += f' {loc_key}:0 "{loc_key.replace("rnw_", "").replace("letter_", "").replace("ending_", "")}"\n'

write_output("../Random New World/localization/english", "rnw_new_naming_l_english.yml", output)

