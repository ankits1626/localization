import os
import xml.etree.ElementTree as ET
import pandas as pd

import json
import xmltodict
import html
from  xml_helper import etree_to_dict

def get_all_languages(source_code_directory):
    res_path = os.path.join(source_code_directory,
                            'app/src/main/res/')  # '/mydrive/code_lab/android_skor/skor-android/app/src/main/res/'
    values = [x for x in os.listdir(res_path) if 'values' in x]
    languages = []
    for x in values:
        if os.path.isfile(os.path.join(res_path, x, 'strings.xml')):
            languages.append(x.split('values-')[-1] if x != 'values' else 'en')

    return languages


def export_strings_to_stringsfile(project_directory, csv_file_name):
    res_path = os.path.join(project_directory,
                            'app/src/main/res/')  # '/mydrive/code_lab/android_skor/skor-android/app/src/main/res/'
    languages = get_all_languages(project_directory)
    print(languages)
    ignore_list = ['values-it', 'values-es', 'values-de']
    keys = {}
    values = [x for x in os.listdir(res_path) if 'values' in x and x not in ignore_list]
    values.sort()
    # values = ['values']
    language_dump={}
    for value in values:
        strings_file_path = os.path.join(res_path, value, 'strings.xml')
        if os.path.isfile(strings_file_path):
            with open(strings_file_path) as xml_file:
                # data = ' '.join([line.replace('\n', '') for line in xml_file.readlines()])
                data_dict = xmltodict.parse(xml_file.read())
                # xml_dict = etree_to_dict(xml_file.read())

            xml_file.close()


            seperator = '-->>'
            # language_dump = []
            for string_component in data_dict['resources']['string']:
                key  = seperator.join(['string', string_component['@name']])
                values_in_different_languages = language_dump.get(key, {})
                underlined = string_component.get('u', '')
                bold = string_component.get('b', '')
                if len(bold)>0:
                    values_in_different_languages[value] ='<b>{}</b>'.format(bold)
                elif len(underlined)>0:
                    values_in_different_languages[value] ='<u>{}</u>'.format(underlined)
                else:

                    values_in_different_languages[value] = html.unescape(string_component.get('#text', ''))
                language_dump[key] = values_in_different_languages


            for string_component in data_dict['resources']['string-array']:
                for index, item in enumerate(string_component.get('item', [])):
                    key = seperator.join(['string-array', string_component['@name'], '{i}'.format(i=index)])
                    values_in_different_languages = language_dump.get(key, {})
                    values_in_different_languages[value] = item
                    language_dump[key] = values_in_different_languages

            for string_component in data_dict['resources']['plurals']:
                for index, item in enumerate(string_component.get('item', [])):
                    key = seperator.join(['plurals', string_component['@name'], item['@quantity']])
                    values_in_different_languages = language_dump.get(key, {})
                    values_in_different_languages[value] = item['#text']
                    language_dump[key] = values_in_different_languages





    df = pd.DataFrame.from_dict(language_dump)
    df = df.T
    df.index.names=['keys']
    if '.xlsx' in csv_file_name:
        df.to_excel(r'{}'.format(csv_file_name))
    else:
        df.to_csv(r'{}'.format(csv_file_name))


if __name__ == '__main__':
    export_strings_to_stringsfile(
        '/Users/rewardz/Documents/code/2021Oct28TrendMicro',
        'trend_micro_extracted_strings_3.csv'
    )
