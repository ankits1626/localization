import os
import numpy as np
import pandas as pd
from builtins import any as b_any
import requests
import shutil
import pandas as pd
from math import isnan

from extract import get_string_file_path_in_project


def get_google_translate(strings_dataframe, target_key, target_language_code, google_translate_key):
    rslt_df = strings_dataframe.loc[strings_dataframe['keys'] == target_key]
    if not rslt_df.empty:
        if isinstance(rslt_df.iloc[0].en, str):
            existing_known_val = rslt_df.iloc[0].en
        else:
            existing_known_val = rslt_df.iloc[0].fillna('')[3:][0]
        text = existing_known_val
        if isinstance(text, str):
            text = text.strip('";').strip('"')
        else:
            return '"{}";'.format(text)
    else:
        return '"";'
    print('<<<<< can call call google api for this {}'.format(text))
    if target_language_code == 'ar' and len(google_translate_key) > 0 and len(text) > 0:
        response = requests.get('https://translation.googleapis.com/language/translate/v2?key'
                                '{key}&q={t}&target={l}'.format(
            key=google_translate_key,
            t=text.strip().strip('"'),
            l=target_language_code
        )
        )
        if response.ok:
            return '"{}";'.format(response.json()['data']['translations'][0]['translatedText'])
        else:
            return '"{}";'.format(text)
    else:
        return '"{}";'.format(text)


def clean_value_before_putting_back(to_value, from_value):
    if not isinstance(to_value, str):
        return ''
    to_value = to_value.replace('“', '"')
    to_value = to_value.replace('”', '"')

    if to_value == '"";':
        return from_value
    to_value = to_value.replace('""', '"')
    if to_value.endswith(';";'):
        to_value = to_value.replace(';";', '";')
    if to_value.endswith('"";') and not (to_value.endswith('\\"";')):
        to_value = to_value.replace('"";', '";')
    return to_value


def create_missing_file(strings_dataframe, language, string_file_path):
    if not language == 'Base':
        print('------------  we have to create {l} file for {f}'.format(l=language, f=string_file_path))
        file_name = string_file_path.split('/')[-1]
        directory_path =  '/'.join(string_file_path.split('/')[:-1])
        print('****  directory {l} file for {f}\n\n'.format(l=directory_path, f=file_name))
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        else:
            print('already exist')
        base_path = '/'.join(string_file_path.split('/')[:-2])
        existing_lproj_dirs = [x for x in os.listdir(base_path) if '.lproj' in x]
        existing_lang_files = [x for x in existing_lproj_dirs if os.path.exists(os.path.join(base_path, x, file_name))]
        if len (existing_lang_files) > 0:
            existing_keys =set([])
            temp_missing_string_file = "temp_{l}_{n}".format(l= language, n = file_name)
            temp_missing_string_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                temp_missing_string_file
            )
            lines = []
            with open(temp_missing_string_file, 'w') as f:
                for file in existing_lang_files:
                    with open(os.path.join(base_path, file, file_name), 'r') as string_file:
                        for line in string_file:
                            if line.startswith('"'):
                                name, var = line.partition("=")[::2]
                                if not (name in list(existing_keys)):
                                    lines.append('%s= %s;\n' % (name, '""'))
                                    f.write('%s= %s;\n\n' % (name, '""'))
                                    existing_keys.add(name)
                                else:
                                    print('already there')
                                # f.write('%s= %s;\n' % (name, '""'))
                            else:

                                if line not in lines:
                                    lines.append('%s' % line)
                                    f.write('%s' % line)

                shutil.move(
                    temp_missing_string_file,
                    string_file_path
                )
            print('------------  finished creating {l} file for {f}'.format(l=language, f=string_file_path))
        else:
            print('<<<<<<<<<<<just create an empty file')



def put_back_strings_to_ios_project(project_directory_path, strings_csv_path, google_translate_key):
    print('<<<<<<<<<< putting back strings')
    strings_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        strings_csv_path
    )
    if '.xlsx' in strings_csv_path:
        strings_dataframe = pd.read_excel(strings_csv_path)
    else:
        strings_dataframe = pd.read_csv(strings_csv_path)
    for file_name in strings_dataframe.files.unique():
        #     file_name = 'Flabuless/Layouts/Apps Specific/BenefitSt Fit/Profile/Profile.strings'
        for language in strings_dataframe.loc[0].keys()[3:]:
            file0_dataframe = strings_dataframe[strings_dataframe.files == file_name]
            language_dataframe = file0_dataframe[['keys', language]]
            type(language_dataframe)
            language_dict = {}
            for index, row in language_dataframe.iterrows():
                language_dict[row[0]] = row[1]

            string_file_path = get_string_file_path_in_project(
                project_directory_path,
                file_name,
                language,
            )

            #         print(language_dict.keys())
            all_keys = []
            temp_string_file = "temp_strings_file.strings"
            temp_string_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                temp_string_file
            )
            if not os.path.isfile(string_file_path):
                create_missing_file(
                    strings_dataframe,
                    language,
                    string_file_path
                )
            print('here')
            if os.path.isfile(string_file_path):
                with open(string_file_path, 'r') as string_file:
                    with open(temp_string_file, 'w') as f:
                        for line in string_file:
                            if line.strip() == '";' or line.strip() == '= ";':
                                print('<<<<<<< empty line')
                            else:
                                if line.startswith('"'):
                                    name, var = line.partition("=")[::2]
                                    all_keys.append(name)

                                    val = language_dict.get(name.strip(), '')
                                    val = clean_value_before_putting_back(
                                        to_value= val,
                                        from_value=var.strip(),
                                    )
                                    if val == '':
                                        val = get_google_translate(
                                            strings_dataframe,
                                            name.strip(),
                                            language,
                                            google_translate_key
                                        )

                                    if not (val == var.strip()):
                                        print('value changed for language {l} from {f} to {t}'.format(
                                            l=language,
                                            f=var.strip(),
                                            t=val
                                        )
                                        )

                                    f.write('%s= %s\n' % (name, val))

                                else:
                                    f.write('%s' % line)

                shutil.move(
                    temp_string_file,
                    string_file_path
                )
            else:
                hello = []
                print('************ still missing  we have to create {l} file for {f}\n\n'.format(l=language, f=string_file_path))


if __name__ == '__main__':
    # google key=AIzaSyAuwuFNTEYvgYYhdUvYIBKTlsfLO7-1GNQ
    put_back_strings_to_ios_project(
        '/Users/rewardz/Documents/code/2022Jan9Skor_Nominations',
        'skor_arabic_20220127.xlsx',
        '=AIzaSyAuwuFNTEYvgYYhdUvYIBKTlsfLO7-1GNQ'
    )
