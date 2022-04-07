import os
import numpy as np
import pandas as pd
from builtins import any as b_any
import requests


def get_google_translate(text, target_language_code):
    print('<<<<< can call call google api for this {}'.format(text))
    response = requests.get('https://translation.googleapis.com/language/translate/v2?key'
                            '=AIzaSyAuwuFNTEYvgYYhdUvYIBKTlsfLO7-1GNQ&q={t}&target={l}'.format(t=text.strip().strip('"'),
                                                                                               l=target_language_code))
    return 'g"{}"'.format(response.json()['data']['translations'][0]['translatedText'])



def get_all_languages(strings_dictionary):
    languages = set([])
    en_position = -1
    for file_name in strings_dictionary.keys():
        string_file = strings_dictionary[file_name]
        languages = languages.union([*string_file])

    for index, language in enumerate(languages):
        if language == 'en':
            en_position = index
    languages = list(languages)
    languages.insert(0, languages.pop(en_position))
    return languages


def get_all_keys(string_file, languages):
    keys = set([])

    for index, language in enumerate(languages):
        keys = keys.union(set([*string_file.get(language, {})]))
    return keys


def dump_csv(strings_dictionary):
    print('<<<<<<<<< strings_dictionary')
    csv_array = []
    languages = get_all_languages(strings_dictionary)
    header = ['file_name', 'key'] + list(languages)
    csv_array.append(header)
    for file_name in strings_dictionary.keys():
        string_file = strings_dictionary[file_name]
        keys = get_all_keys(string_file, languages)
        for index, key in enumerate(keys):
            row = [file_name]
            # [file_name if index == 0 else '', key]
            for language in languages:
                value = string_file.get(language, {}).get(key, '')
                # if value == '' and language == 'hi':
                #     value = get_google_translate(
                #         string_file.get('en', {}).get(key, ''),
                #         'hi'
                #     )
                row.append(value)
            csv_array.append(row)

    dataframe = pd.DataFrame(csv_array)
    dataframe.to_csv(r"trend_setter_string_files.csv")

    # print(csv)


def parse_string_file(string_file_path):
    language = string_file_path.split('/')[-2].split('.')[0]
    strings = {}
    with open(string_file_path) as myfile:
        for line in myfile:
            if line.startswith('"') and len(line) > 0:
                # print('<<<<< line is ' + line)
                line = line.rstrip(';\n')
                name, var = line.partition("=")[::2]
                strings[name.strip()] = var
    return {language: strings}


def traverse_directory(depth, dir_path):
    exclusion_list = ['Pods', '.git', 'Assets', '.xcdatamodeld', '.xcodeproj', '.plist', '.lock', '.xcassets', '.swift']
    string_files = []
    for item in os.listdir(dir_path):
        if not b_any(x in item for x in exclusion_list):
            s = os.path.join(dir_path, item)
            if os.path.isdir(s):
                # print(('>' * depth) + 'd - {}'.format(s))
                string_files = string_files + traverse_directory(depth + 1, s)
            else:
                if '.strings' in item:
                    string_files.append(s)
                    # print(('*' * depth) + 'f - {}'.format(s))
    return string_files


def export_strings(project_path):
    print('<<<<<<<<< exporting strings')
    string_files_paths = traverse_directory(1, project_path)
    strings_dictionary = {}
    for string_file in string_files_paths:
        parent_directory = string_file.split('/')[-3]
        file_name = string_file.split('/')[-1].split('.')[0]
        # '/'.join(string_file.split('/')[:-2])
        file_name = os.path.join(parent_directory, file_name)
        language = string_file.split('/')[-2].split('.')[0]
        if file_name in strings_dictionary:
            existing_lang_dict = strings_dictionary[file_name]
            lang_dict = parse_string_file(string_file)
            existing_lang_dict[[*lang_dict][0]] = lang_dict[[*lang_dict][0]]
            strings_dictionary[file_name] = existing_lang_dict
        else:
            strings_dictionary[file_name] = parse_string_file(string_file)
    dump_csv(strings_dictionary)
    # parse_string_file('/Users/rewardz/Documents/code/2020Aug6Cerra/SKOR/EditProfileViewStoryboard/zh-Hans.lproj/EditProfileViewStoryboard.strings')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    export_strings('/Users/rewardz/Documents/code/2020Aug6Flab')
