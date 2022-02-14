import regex
import os
import apply_script as pdx_parser
import codecs

game_path = "C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game" # Can be mod path too

comment_pattern = regex.compile(r"(#)[^\n]*")

def write_output(path, file, text):
    if type(text) == list:
        parsed_file = text
    elif file.endswith("txt"):
        temporary_output_file = open(os.path.join(path, file), "w")
        temporary_output_file.write(text)
        temporary_output_file.close()
        parsed_file = pdx_parser.parse_file(os.path.join(path, file))
    
    if file.endswith("txt"):
        byte_text = bytes(pdx_parser.reconstruct(parsed_file).encode())
    else:
        byte_text = bytes(text.encode())
    output_file = open(os.path.join(path, file), "wb")
    output_file.write(codecs.BOM_UTF8)
    output_file.write(byte_text)
    output_file.close()

def dumpfiles(path, ending = ".txt"):
    full_text = ""
    for file in os.listdir(path):
        if file.endswith(ending):
            full_text += read_with_removed_comments(path, file)
    return(full_text)

def join_files(path, ending):
    full_list = []
    for file in os.listdir(path):
        if file.endswith(ending):
            full_list += pdx_parser.parse_file(os.path.join(path, file))
    return(full_list)

def read_with_removed_comments(path, file):
    file_content = open(os.path.join(path, file)).read()
    return(comment_pattern.sub("", file_content))
