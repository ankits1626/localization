import pandas as pd
import os
import requests

def get_goole_translated_value(english_value, google_translate_key, target_language_code):
    response = requests.get('https://translation.googleapis.com/language/translate/v2?key'
                            '{key}&q={t}&target={l}'.format(
        key=google_translate_key,
        t=english_value,
        l=target_language_code
    )
    )
    if response.ok:
        return response.json()['data']['translations'][0]['translatedText']
    else:
        return ''

def prepare_google_translated_version(source_code_directory, strings_csv_path, google_translate_key, language_code):
    strings_csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        strings_csv_path
    )
    if '.xlsx' in strings_csv_path:
        strings_dataframe = pd.read_excel(strings_csv_path)
    else:
        strings_dataframe = pd.read_csv(strings_csv_path)
    # print(strings_dataframe)
    # languages = strings_dataframe.loc[0].keys()[1:]
    languages = ['values']

    for language in languages:
        print('<<<<<<<<<<<<<<< start for language {l}'.format(l=language))
        strings = {}
        strings_array = {}
        plurals = {}
        # file0_dataframe = strings_dataframe[strings_dataframe.files == file_name]
        language_dict = {}
        language_dataframe = strings_dataframe[['keys', language]]
        seperator = '-->>'
        xml = '<?xml version="1.0" encoding="utf-8"?>' + '\n'
        xml = xml + '<resources xmlns:tools="http://schemas.android.com/tools" tools:ignore="ExtraTranslation">' + '\n'
        for index, row in language_dataframe.iterrows():
            key = row['keys']
            components_key = key.split(seperator)
            if 'plurals' == components_key[0]:
                existing_plural_map = plurals.get(components_key[1], {})
                existing_plural_map[components_key[2]] = row[language]
                plurals[components_key[1]] = existing_plural_map

            if 'string-array' == components_key[0]:
                existing_string_array = strings_array.get(components_key[1], [])
                existing_string_array.append(row[language])
                strings_array[components_key[1]] = existing_string_array

            if 'string' == components_key[0]:
                # components_key[1] == 'not_available'
                strings[components_key[1]] = row[language]
                # xml_row = '    <string name="{k}">{v}</string>'.format(k=components_key[1], v=row[language])
                # xml = xml + xml_row + '\n'

            # value = row[language]
            language_dict[row[0]] = row[1]
        xml = xml + '</resources>'
        print('<<<<<<<<<<<<<<< end for language {l}'.format(l=language))
        xml = ''
        xml_string_file_path = os.path.join(source_code_directory,
                                            'app/src/main/res/{v}/strings.xml'.format(v=language))
        elements = ['<string', '']
        # is_dealing_plural = False
        current_plural_key = None
        current_string_array_key = None
        current_string_array_item = -1
        with open(xml_string_file_path, "r") as xml_file:
            for line in xml_file.readlines():
                # print(line)
                if '<string-array' in line:
                    current_string_array_item = 0
                    string_array_components = line.split('string-array name="')
                    current_string_array_key = string_array_components[1].split('"')[0]
                    xml = xml + line
                elif '<item>' in line and current_string_array_key:
                    # <item>Singapore Citizen</item>
                    string_array_item_line_components = line.split('<item>')
                    xml = xml + string_array_item_line_components[0] + '<item>{}</item>\n'.format(
                        get_goole_translated_value(
                            strings_array[current_string_array_key][current_string_array_item],
                            google_translate_key,
                            language_code
                        )
                    )
                    current_string_array_item = current_string_array_item + 1
                    pass
                elif '</string-array>' in line:
                    xml = xml + line
                    current_string_array_key = None
                    current_string_array_item = -1
                elif '<string name' in line:
                    print(line)
                    if '<string name=' in line:
                        string_line_components = line.split('<string name="')
                    if '<string name =' in line:
                        string_line_components = line.split('<string name ="')
                    string_key = string_line_components[1].split('">')[0]
                    string_value = get_goole_translated_value(
                        strings[string_key],
                        google_translate_key,
                        language_code
                    )
                    if isinstance(string_value, str):
                        xml = xml + string_line_components[
                            0] + '<string name="' + string_key + '">' + string_value + '</string>\n'
                    else:
                        xml = xml + line
                elif '<plurals' in line:
                    l_components = line.split('<plurals name="')
                    current_plural_key = l_components[1].split('"')[0]
                    xml = xml + line
                    print(line)
                elif '<item quantity' in line and current_plural_key:
                    # parse items
                    item_line_components = line.split('<item quantity="')
                    item_key = item_line_components[1].split('">')[0]
                    item_value = get_goole_translated_value(
                        plurals[current_plural_key][item_key],
                        google_translate_key,
                        language_code
                    )
                    xml = xml + item_line_components[
                        0] + '<item quantity="' + item_key + '">' + item_value + '</item>\n'
                    print(line)
                elif '</plurals>' in line:
                    xml = xml + line
                    current_plural_key = None
                    print(line)
                else:
                    xml = xml + line
        print('here')

        # xml = '<?xml version="1.0" encoding="utf-8"?>' + '\n'
        # xml = xml + '<resources xmlns:tools="http://schemas.android.com/tools" tools:ignore="ExtraTranslation">' + '\n'
        # for key in language_dict.keys():
        #     # <string name="hint_search">Search</string>
        #     # print(language_dict[key])
        #     if (not isinstance(language_dict[key], str)) and math.isnan(language_dict[key]):
        #         string_value = ""
        #     else:
        #         string_value = language_dict[key]
        #     # string_value = html.escape(string_value, quote=False)
        #     string_value = string_value.replace('&', '&amp;')
        #     # string_value = string_value.encode(encoding="ascii", errors="xmlcharrefreplace")
        #     # string_value = string_value.decode()
        #     row = '    <string name="{k}">{v}</string>'.format(k=key, v=string_value)
        #     xml = xml + row + '\n'
        # xml = xml + '</resources>'
        # print(xml)

        # xml_string_file_path = os.path.join(source_code_directory, 'app/src/main/res/values-de/strings.xml')
        # print(xml_string_file_path)
        if language == 'en':
            d_file_name = 'en-strings.xml'
            file_name = 'app/src/main/res/values/strings.xml'
        else:
            d_file_name = '{}-strings.xml'.format(language)
            file_name = 'app/src/main/res/values-{}/strings.xml'.format(language)
        with open("values-{}.xml".format(language_code), "w") as text_file:
            # f = open(os.path.join(source_code_directory, file_name), "w")
            text_file.write(xml)
            text_file.close()
        print('here')

if __name__ == '__main__':
    prepare_google_translated_version(
        '/Users/rewardz/Documents/code/2021Sep14_Skor_Android',
        'csv_android_new_extracted_spanish_strings.csv',
        '=AIzaSyAuwuFNTEYvgYYhdUvYIBKTlsfLO7-1GNQ',
        'ar',
    )