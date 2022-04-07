import os
import pandas as pd

def merge_external_translation_to_extracted_csv(project_path, existing_strings_file, translation_file_path, language_code):
    strings_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        existing_strings_file
    )
    if '.xlsx' in strings_path:
        existing_strings_dataframe = pd.read_excel(strings_path)
    else:
        existing_strings_dataframe = pd.read_csv(strings_path)

    translator_provided_strings = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        existing_strings_file
    )

    if '.xlsx' in translator_provided_strings:
        translator_provided_strings_dataframe = pd.read_excel(translator_provided_strings)
    else:
        translator_provided_strings_dataframe = pd.read_csv(translator_provided_strings)



if __name__ == '__main__':
    merge_external_translation_to_extracted_csv(
        '/Users/rewardz/Documents/code/2021Nov22CerraRussian',
        'russian_new_extracted_spanish_strings.xlsx',
        '/Users/rewardz/Downloads/IOS_russian.csv',
        'ru'
    )
