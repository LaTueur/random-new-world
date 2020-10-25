import regex
import os

rule_block_pattern = regex.compile(r"(\w+)\s*=\s*{(((?:\w+\s*=\s*{(?3)}|[^{}])*))}")
if_block_pattern = regex.compile(r"\s(?:if|else_if)\s*=\s*{\s*limit\s*=\s*{\s*(\w+)\s*=\s*(\w+)\s*}\s*value\s*=\s*([\w\.]+)\s*}")
comment_pattern = regex.compile(r"(#)[^\n]*")

def read_with_removed_comments(path, file):
    file_content = open(os.path.join(path, file)).read()
    return(comment_pattern.sub("", file_content))

rules_raw = read_with_removed_comments(".", "brave_new_world_game_rules_script_values.txt")
rules = rule_block_pattern.findall(rules_raw)

output = ""

for rule in rules:
    ifs = if_block_pattern.findall(rule[1])

    output += f"""{rule[0]} = {{
    switch = {{
        trigger = {ifs[0][0]}\n"""
    
    for i in ifs:
        output += f"\t\t{i[1]} = {{ value = {i[2]} }}\n"
    
    output += "\t}\n}\n"


output_file = open(os.path.join("../common/script_values", "brave_new_world_game_rules_script_values.txt"), "w")
output_file.write(output)
output_file.close()
