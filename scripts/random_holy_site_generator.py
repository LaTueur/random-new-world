import apply_script as pdx_parser
import os
import codecs

game_path = "C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game" # Can be mod path too
def join_files(path, ending):
    full_list = []
    for file in os.listdir(path):
        if file.endswith(ending):
            full_list += pdx_parser.parse_file(os.path.join(path, file))
    return(full_list)

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

sites = join_files(os.path.join(game_path, "common\\religion\\holy_sites"), "txt")
religions = join_files(os.path.join(game_path, "common\\religion\\religions"), "txt")
localization = "l_english:"
site_infos = []
faith_names = []
new_list = []
new_site_list = []
new_religion_list = []
for religion in religions:
    for element in religion[2]:
        if element[0] == "faiths":
            for faith in element[2]:
                faith_names.append(faith[0])

for site in sites:
    name = site[0]
    for element in site[2]:
        if element[0] == "is_active":
            element[2] = "no"
            break
    else:
        site[2].append(['is_active', '=', 'no'])
    
    has_extra_effect = False
    for element in site[2]:
        if element[0] == "flag":
            has_extra_effect = True
        if element[0] == "county":
            county = element[2]
    
    site_infos.append([name, county])

    for faith in faith_names:
        long_name = f"{name}_{faith}"
        site[0] = long_name
        new_site_list.append(site.copy())
        localization += f'''
 holy_site_{long_name}_name:0 "$holy_site_{name}_name$"'''
        if has_extra_effect:
            localization += f'''
 holy_site_{long_name}_effects:0 "$holy_site_{name}_effects$"'''

for religion in religions:
    for element in religion[2]:
        if element[0] == "faiths":
            for faith in element[2]:
                for felement in faith[2].copy():
                    if felement[0] == "holy_site":
                        faith[2].remove(felement)
                for site in site_infos:
                    faith[2].append(["holy_site", "=", f"{site[0]}_{faith[0]}"])

choose_holy_site = """
rnw_choose_holy_site_effect = {
    random_list = {"""
for site in site_infos:
    choose_holy_site += f"""
        10 = {{
            trigger = {{
                NOT = {{
                    title:{site[1]} = {{
                        is_in_list = choosen_holy_sites
                    }}
                }}
            }}
            rnw_holy_site_choice_modifier = {{
                COUNTY = title:{site[1]}
            }}
            rnw_add_holy_site_effect = {{
                SITE = {site[0]}
                COUNTY = title:{site[1]}
                FAITH = $FAITH$
            }}
        }}"""
choose_holy_site += f"""
    }}
}}
rnw_forward_to_holy_site_choice_effect = {{
    if = {{
        limit = {{
            NOT = {{ exists = religion }}
        }}
        rnw_choose_multiple_holy_site_effect = {{
            FAITH = {faith_names[0]}
        }}
    }}"""

for faith in faith_names:
    choose_holy_site += f"""
    else_if = {{
        limit = {{
            this = faith:{faith}
        }}
        rnw_choose_multiple_holy_site_effect = {{
            FAITH = {faith}
        }}
    }}"""

choose_holy_site += """
}"""

write_output("..\\Random New World Holy Sites\\common\\religion\\holy_sites","rnw_generated_holy_sites.txt", new_site_list)
write_output("..\\Random New World Holy Sites\\common\\religion\\religions","zzz_rnw_generated_religions.txt", religions)
write_output("..\\Random New World Holy Sites\\common\\scripted_effects","zzz_rnw_generated_holy_site_effects.txt", choose_holy_site)
write_output("..\\Random New World Holy Sites\\localization\\english","rnw_generated_holy_sites_l_english.yml", localization)

