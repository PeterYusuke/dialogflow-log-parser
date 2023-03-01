from pyhocon.config_tree import ConfigTree
from pyhocon.converter import HOCONConverter
from .dict_logic import ResponseDictLogic


class BaseHoconLogic():
    def __init__(self) -> None:
        pass

    def hocon_to_dict(self, hocon: ConfigTree):
        import json
        json_string = HOCONConverter.to_json(hocon)
        return json.loads(json_string)

    def has_messages(self, hocon: ConfigTree):
        messages = hocon \
            .get('result', ConfigTree()) \
            .get('fulfillment', ConfigTree()) \
            .get('messages', None)
        return messages is not None

    def has_parameters(self, hocon: ConfigTree):
        parameters = hocon \
            .get('result', ConfigTree()) \
            .get('parameters', None)
        return parameters is not None

    def has_data(self, hocon: ConfigTree):
        messages = hocon \
            .get('result', ConfigTree()) \
            .get('fulfillment', ConfigTree()) \
            .get('data', None)
        return messages is not None


class ResponseHoconLogic(BaseHoconLogic):
    def __init__(self) -> None:
        super().__init__()

    def hocon_to_dict(self, hocon: ConfigTree):
        modified_hocon = self.modify_hocon(hocon)
        response = super().hocon_to_dict(modified_hocon)
        return ResponseDictLogic().modify_dict(response)

    def modify_hocon(self, hocon: ConfigTree):
        if self.has_messages(hocon):
            hocon['result']['fulfillment']['messages'] \
                = self.get_messages_value(hocon)

        if self.has_parameters(hocon):
            hocon['result']['parameters'] \
                = self.get_parameter_obj(hocon['result']['parameters'])

        if self.has_data(hocon):
            hocon['result']['fulfillment']['data'] \
                = self.get_data_value(hocon)

        return hocon

    def get_messages_value(self, conf: ConfigTree):
        messages_list = []
        for message in conf['result']['fulfillment']['messages']:
            if message.get('payload', False):
                messages_list.append(self.get_payload_obj(message))
            elif message.get('speech', False):
                messages_list.append(self.get_message_obj(message))
            else:
                messages_list.append(message)
        return messages_list

    def get_data_value(self, conf: ConfigTree):
        data_list = []
        for data in conf['result']['fulfillment']['data']:
            data_list.append(self.get_data_obj(data))
        return data_list

    def get_data_obj(self, hocon):
        '''
        dataの中身を取得する
        '''

        field = hocon.get('fields')[0]
        key = field.get('key')
        value = field.get('value')
        fields_value = self.get_field_value(value)
        hocon = ConfigTree({key: fields_value})

        return hocon

    def get_payload_obj(self, hocon):
        '''
        payloadの中身を取得する
        '''

        field = hocon['payload'].get('fields')[0]
        key = field.get('key')
        value = field.get('value')
        fields_value = self.get_field_value(value)
        hocon['payload'] = ConfigTree({key: fields_value})

        if hocon.get('type', False) is not False:
            hocon['type'] = self.get_type_value(hocon['type'])

        return hocon

    def get_type_value(self, type_hocon: ConfigTree):
        return self.get_inside_value(type_hocon)

    def get_message_obj(self, message_hocon: ConfigTree):
        key = 'speech'
        string_value = message_hocon.get(key).get('string_value')
        message_hocon[key] = string_value
        if message_hocon.get('type', False):
            message_hocon['type'] = self.get_type_value(message_hocon['type'])

        return message_hocon

    def get_inside_value(self, value_hocon: ConfigTree):
        if value_hocon.get('string_value', False) is not False:
            return value_hocon['string_value']
        if value_hocon.get('number_value', False) is not False:
            return value_hocon['number_value']
        if value_hocon.get('list_value', False) is not False:
            return self.get_inside_list_value(value_hocon['list_value'])
        if value_hocon.get('struct_value', False) is not False:
            return self.get_struct_value(value_hocon['struct_value'])
        return None

    def get_inside_list_value(self, list_value_hocon: ConfigTree):
        values = []
        if list_value_hocon.get('values', False) is False:
            return []
        for value in list_value_hocon['values']:
            values.append(self.get_inside_value(value))
        return values

    def get_parameter_obj(self, parameter_hocon: ConfigTree):
        result = []
        if parameter_hocon.get('fields', False) == False:
            return result

        fields = parameter_hocon['fields']
        for field in fields:
            key = field.get('key')
            value = self.get_inside_value(field.get('value'))
            result.append(ConfigTree({key: value}))
        return result

    def get_field_value(self, field_value_hocon: ConfigTree):
        '''
        fieldの中身をConfigTreeに変換する
        '''
        result = ''
        if field_value_hocon.get('list_value', False):
            list_value = []
            for value in field_value_hocon['list_value']['values']:
                list_value.append(self.get_field_value(value))
            else:
                return list_value
        elif field_value_hocon.get('struct_value', False):
            return self.get_struct_value(field_value_hocon['struct_value'])
        elif field_value_hocon.get('string_value'):
            return field_value_hocon['string_value']
        return result

    def get_field_key_value(self, field_hocon: ConfigTree):
        '''
        fieldの中身を展開する
        '''
        key = field_hocon.get('key')
        value = self.get_field_value(field_hocon.get('value'))
        return {'key': key, 'value': value}

    def get_struct_value(self, struct_value_hocon: ConfigTree):
        """
        struct_valueの中身を展開する
        """
        values = ConfigTree()
        for field in struct_value_hocon.get('fields', []):
            values.put(**self.get_field_key_value(field))
        return values
