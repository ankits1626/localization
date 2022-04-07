import os
import numpy as np
import pandas as pd
from builtins import any as b_any
import requests
import shutil


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


def get_file_id(string_file_path):
    # test_string_file = '/Users/rewardz/Documents/code/2020Aug6Flab/Flabuless/Layouts/Common UI/zh-Hans.lproj/Profile.strings'
    clean_file = string_file_path.split('/')
    del clean_file[-2]
    clean_file = os.path.join(*clean_file)
    return clean_file


def get_file_id(string_file_path):
    # test_string_file = '/Users/rewardz/Documents/code/2020Aug6Flab/Flabuless/Layouts/Common UI/zh-Hans.lproj/Profile.strings'
    clean_file = string_file_path.split('/')
    del clean_file[-2]
    clean_file = os.path.join(*clean_file)
    return clean_file


def get_all_files_and_languages_in_project(project_directory):
    string_files = traverse_directory(1, project_directory)
    file_ids = set([])
    languages = set([])

    for string_file in string_files:
        file_id = get_file_id(string_file.replace(project_directory, ''))
        file_ids.add(file_id)
        language = string_file.split('/')[-2].split('.')[0]
        languages.add(language)
    languages = list(languages)
    languages.remove('en')
    languages.insert(0, 'en')
    if ('hi' in languages):
        languages.remove('hi')
        languages.insert(1, 'hi')
    file_ids = list(file_ids)
    languages = ['en', 'vi', 'ms', 'th', 'ru', 'zh-Hans', 'ar', 'id']
    return file_ids, languages


# hi.lproj
def get_string_file_path_in_project(project_path, file_id, language_code):
    file_path = file_id.split('/')
    file_path.insert(-1, '{}.lproj'.format(language_code))
    file_path = '/'.join(file_path)
    return os.path.join(project_path, file_path)


def get_all_keys_from_string_file(project_directory, string_file, languages):
    all_keys = set([])
    for language in languages:
        string_file_path = get_string_file_path_in_project(project_directory, string_file, language)
        myvars = {}
        if os.path.isfile(string_file_path):
            with open(string_file_path) as myfile:
                for line in myfile:
                    if line.startswith('"') and len(line) > 0:
                        name, var = line.partition("=")[::2]
                        myvars[name.strip()] = var
                    all_keys.update(list(myvars.keys()))
    return all_keys


def get_all_strings_from_string_file_for_language(project_directory, string_file, language, keys):
    string_file_path = get_string_file_path_in_project(project_directory, string_file, language)
    myvars = {}
    if os.path.isfile(string_file_path):
        with open(string_file_path) as myfile:
            for line in myfile:
                if line.startswith('"') and not (line == '";') and len(line) > 0:
                    name, var = line.partition("=")[::2]
                    if name.strip() == '"Hrs"' and language == 'hi':
                        print('value for {l} is {v}'.format(l=language, v=var))
                    if not var.strip().endswith('";'):
                        myvars[name.strip()] = var.strip() + '";'
                    else:
                        myvars[name.strip()] = var.strip()

        vals = []
        for key in keys:
            vals.append(myvars.get(key, ''))
        return vals
    else:
        return [''] * len(keys)


def get_all_string_for_file(project_directory, file, languages, keys):
    print('file is {}'.format(file))
    all_strings = {
        'files': [file] * len(keys),
        'keys': list(keys)
    }
    for language in languages:
        all_strings[language] = get_all_strings_from_string_file_for_language(
            project_directory,
            file,
            language,
            keys
        )
    return all_strings


def parse_all_strings_from_project(project_directory):
    file_ids, languages = get_all_files_and_languages_in_project(project_directory)
    parsed_strings_frames = []
    for file in file_ids:
        keys = get_all_keys_from_string_file(
            project_directory,
            file,
            languages
        )
        parsed_strings_frames.append(
            pd.DataFrame(
                get_all_string_for_file(
                    project_directory,
                    file,
                    languages,
                    keys
                )
            )
        )

    return pd.concat(parsed_strings_frames)


def export_strings_to_csv(project_directory, csv_file_name):
    df = parse_all_strings_from_project(project_directory)
    p = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        csv_file_name
    )
    if '.xlsx' in p:
        df.to_excel(r'{}'.format(p))
    else:
        df.to_csv(r'{}'.format(p))


if __name__ == '__main__':
    export_strings_to_csv(
        '/Users/rewardz/Documents/code/2022Jan9Skor_Nominations',
        'skor_arabic_20220127.xlsx',
    )
