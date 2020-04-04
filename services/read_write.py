import json
import os
import requests
from datetime import date
from datetime import datetime as dt
from pickle import load as load_pickle_file
import urllib.request
"""
python library to facilitate the manipulation of writing to the disk.
"""


def file_is_empty(path):
    """
    a function that check if a file is empty
    :return: True if file is empty
    """
    return os.stat(path).st_size == 0


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (dt, date)):
        return obj.isoformat()
    raise TypeError(f'Type {type(obj)} not serializable')


def read_json(file_to_read):
    file_to_read.seek(0)
    return json.load(file_to_read)


def write_json(path, file_to_write, content):
    if file_is_empty(path):
        data = [content]
    else:
        data = read_json(file_to_write)
        data.append(content)
    with open(path, 'w', encoding='utf8') as file_to_write:
        json.dump(data, file_to_write, indent=4, default=json_serial)


def read_txt(file_to_read, separator):
    return file_to_read.read().split(separator)


def write_txt(file_to_write, content):
    print('txt')
    file_to_write.write(str(content))


def read_pickle(file_to_read):
    return load_pickle_file(file_to_read)


def write_pickle(file_to_write):
    print('t')


class FileManipulation:
    def __init__(self, base_path='.'):
        """
        :param base_path: the root folder where you wanna put your file (if it doesn't exist it's automatically created)
            leave empty for root
        """
        # Constructing the file path from the arguments
        self.base_path = base_path
        # If the root folder doesn't exist, it's automatically created
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    def write_to_disk(self, file_name, file_type, content, root_array_key='default_root'):
        """
        a function that write a file to the disk
        :param file_name: the name of your file
        :param file_type: the extension of your file, supported types: json, txt
        :param content: the content you want to write
        :param root_array_key: this is an optional argument, if the type is json
            we need a root array to store the json object
            example: content={"name": "ash", "age": 26, "car": None}
                    file_object = FileManipulation('local_database/', 'my_database', 'json')
                    file_object.write_to_disk(content, root_array_key='personal_info')
                    output: {"personal_info": [{"name": "ash","age": 26,"car": null}]}
        :return:
        """
        path = f'{self.base_path}/{file_name}.{file_type}'
        with open(path, 'a+', encoding='utf8') as file_to_write:
            if 'json' in file_type:
                write_json(path, file_to_write, content)
            else:
                write_txt(file_to_write, content)
        print(f'You can find the file in {path}')

    def read_file(self, file_name, file_type, separator='\n'):
        path = f'{self.base_path}/{file_name}.{file_type}'
        """
        a function to read a file and return it's content
        :param file_name: the name of your file
        :param file_type: the extension of your file, supported types: json, txt, pickle
        :param separator: the separator to split the file to an array
        :return: an array of data from the file
        """
        if not file_is_empty(path):
            with open(path, 'r', encoding='utf8') as file_to_read:
                if 'json' in file_type:
                    data = read_json(file_to_read)
                elif 'txt' in file_type:
                    data = read_txt(file_to_read, separator)
                elif 'pkl' in file_type:
                    data = read_pickle(file_to_read)
            return data
        else:
            print('No data to read')
            return False

    def download_image(self, image_name, image_url):
        image_data = requests.get(image_url).content
        image_extension = image_url.split('.')[-1]
        with open(f'{self.base_path}/{image_name}.{image_extension}', 'wb') as handler:
            handler.write(image_data)

    def download_pdf(self, pdf_name, pdf_url):
        urllib.request.urlretrieve(pdf_url, f'{self.base_path}/{pdf_name}.pdf')
