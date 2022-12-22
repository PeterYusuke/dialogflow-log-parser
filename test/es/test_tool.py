import os
import json
from unittest import TestCase
from dialogflow_log_parser.es import response_to_dict

BASE_TEST_DATA_DIR = 'test/es/data/'


class MainTest(TestCase):
    maxDiff = None

    BASE_TEST_DATA_DIR = 'test/es/data/'

    def get_conf_file(self, file_name):
        file_dir = os.path.join(self.BASE_TEST_DATA_DIR, 'response', file_name)
        with open(file_dir) as f:
            return f.read()

    def get_dest_file(self, file_name):
        file_dir = os.path.join(self.BASE_TEST_DATA_DIR,
                                'destination', file_name)
        with open(file_dir) as f:
            return f.read()

    def test_default(self):
        response = self.get_conf_file('1_default.conf')

        dest = self.get_dest_file('1_default.json')
        response_dict = response_to_dict(response)
        dest_dict = json.loads(dest)

        self.assertDictEqual(response_dict, dest_dict)

    def test_messages_payload(self):
        response = self.get_conf_file('2_message_payload.conf')
        dest = self.get_dest_file('2_message_payload.json')

        response_dict = response_to_dict(response)
        dest_dict = json.loads(dest)

        self.assertDictEqual(response_dict, dest_dict)

    def test_parameters(self):
        response = self.get_conf_file('3_parameters.conf')
        dest = self.get_dest_file('3_parameters.json')

        response_dict = response_to_dict(response)
        dest_dict = json.loads(dest)

        self.assertDictEqual(response_dict, dest_dict)

    def test_contexts(self):
        response = self.get_conf_file('4_contexts.conf')
        dest = self.get_dest_file('4_contexts.json')

        response_dict = response_to_dict(response)
        dest_dict = json.loads(dest)

        self.assertDictEqual(response_dict, dest_dict)

    def test_parameter_list(self):
        response = self.get_conf_file('5_parameter_list.conf')
        dest = self.get_dest_file('5_parameter_list.json')

        response_dict = response_to_dict(response)
        dest_dict = json.loads(dest)

        self.assertDictEqual(response_dict, dest_dict)

    def test_multi_parameter_list(self):
        response = self.get_conf_file('6_multi_parameter_list.conf')
        dest = self.get_dest_file('6_multi_parameter_list.json')

        response_dict = response_to_dict(response)
        dest_dict = json.loads(dest)

        self.assertDictEqual(response_dict, dest_dict)

    def test_data_key(self):
        response = self.get_conf_file('7_data_key.conf')
        dest = self.get_dest_file('7_data_key.json')

        response_dict = response_to_dict(response)
        dest_dict = json.loads(dest)

        self.assertDictEqual(response_dict, dest_dict)
