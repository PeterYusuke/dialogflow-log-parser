class BaseDictLogic():
    def __init__(self) -> None:
        pass


class ResponseDictLogic(BaseDictLogic):
    def modify_dict(self, response: dict) -> dict:

        if response \
            .get('result', {}) \
                .get('contexts', False) is not False:
            response['result']['contexts'] \
                = self.get_contexts_dict(response['result']['contexts'])

        return (response)

    def get_inside_value(self, value: dict):
        if value.get('string_value', False) is not False:
            return value['string_value']
        if value.get('number_value', False) is not False:
            return value['number_value']
        if value.get('list_value', False) is not False:
            return self.get_inside_list_value(value['list_value'])
        if value.get('struct_value', False) is not False:
            return self.get_struct_value(value['struct_value'])
        return None

    def get_struct_value(self, struct_value: list[dict]):
        if struct_value.get('fields', False) is not False:
            fields_list = {}
            fields = struct_value.get('fields')
            for field in fields:
                key = field.get('key')
                value = self.get_inside_value(field.get('value'))
                fields_list[key] = value
            return fields_list
        return None

    def get_inside_list_value(self, list_value: dict):
        values = []
        if list_value.get('values', False) is False:
            return values

        for value in list_value.get('values'):
            values.append(self.get_inside_value(value))
        return values

    def get_contexts_dict(self, contexts: list[dict]) -> dict:
        result = []
        for context in contexts:
            if context.get('parameters', False) is False:
                continue

            context_copy = context.copy()

            parameters = []
            fields = context_copy.get('parameters').get('fields', [])
            for field in fields:
                key = field.get('key')
                value = self.get_inside_value(field.get('value'))
                parameters.append({key: value})
            context_copy['parameters'] = parameters
            result.append(context_copy)

        return result
