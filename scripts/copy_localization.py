import regex
import os
import apply_script as pdx_parser
import codecs
base_folders = ("../Random New World", "../Random New World Holy Sites")
languages = ("french", "german", "spanish", "simp_chinese", "russian", "korean")

for folder in base_folders:
    path = os.path.join(folder, "localization/english")
    for file in os.listdir(path):
        english = open(os.path.join(path, file)).read()
        for lang in languages:
            new_lang = english.replace("l_english", f"l_{lang}")
            new_file = file.replace("l_english", f"l_{lang}")
            new_path = os.path.join(folder, f"localization/{lang}")
            output_file = open(os.path.join(new_path, new_file), "w")
            output_file.write(new_lang)
            output_file.close()

