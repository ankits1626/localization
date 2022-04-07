import pandas as pd
import os

def get_translated_string(translated_csv_file, english_value):
    translated_value = english_value
    if '.xlsx' in translated_csv_file:
        translated_dataframe = pd.read_excel(translated_csv_file)
    else:
        translated_dataframe = pd.read_csv(translated_csv_file)

    rslt_df = translated_dataframe.loc[translated_dataframe['Translations Required'] == english_value]
    # translated_dataframe[translated_dataframe['Translations Required'].str.contains(string_value, na = False)].iloc[0]['Russian']
    if not rslt_df.empty:
        translated_value = translated_dataframe[translated_dataframe['Translations Required'] == english_value].iloc[0]['Russian']
        print('here')
        # rslt_df = translated_dataframe.loc[translated_dataframe['Translations Required'] == english_value]
    else:
        return  None

    return translated_value

def create_string_file(source_code_directory, extracted_string_file, translated_csv_file, output_values_file):
    strings_dataframe = pd.read_csv(extracted_string_file)
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
                    translated_value = get_translated_string(
                            translated_csv_file,
                            strings_array[current_string_array_key][current_string_array_item]
                        )
                    if translated_value:
                        xml = xml + string_array_item_line_components[0] + '<item>{}</item>\n'.format(
                            translated_value
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
                    string_value = get_translated_string(
                        translated_csv_file,
                        string_key
                        # strings.get(string_key, string_key),
                    )
                    if string_value:
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
                    item_value = get_translated_string(
                        translated_csv_file,
                        plurals[current_plural_key][item_key],
                    )

                    if item_value:
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


        if language == 'en':
            d_file_name = 'en-strings.xml'
            file_name = 'app/src/main/res/values/strings.xml'
        else:
            d_file_name = '{}-strings.xml'.format(language)
            file_name = 'app/src/main/res/values-{}/strings.xml'.format(language)
        with open("{}".format(output_values_file), "w") as text_file:
            # f = open(os.path.join(source_code_directory, file_name), "w")
            text_file.write(xml)
            text_file.close()
        print('here')


if __name__ == '__main__':
    create_string_file(
        '/Users/rewardz/Documents/code/2021Oct28TrendMicro',
        'trend_micro_extracted_strings_3.csv',
        'Android_russian_part2_updated.csv',
        'values-ru_updated.xml'
    )