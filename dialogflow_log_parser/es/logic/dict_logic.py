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
        return None

    def get_contexts_dict(self, contexts: list[dict]) -> dict:
        result = []
        for context in contexts:
            if context.get('parameters', False) is False:
                continue
            
            context_copy = context.copy()

            parameters = []
            fields = context_copy.get('parameters').get('fields',[])
            for field in fields:
                key = field.get('key')
                value = self.get_inside_value(field.get('value'))
                parameters.append({key: value})
            context_copy['parameters'] = parameters
            result.append(context_copy)

        return result
