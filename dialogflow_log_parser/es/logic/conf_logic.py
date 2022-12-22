import re
from pyhocon.config_tree import ConfigTree


class BaseConfLogic():
    def __init__(self) -> None:
        pass

    def get_indeices_of_regex(self, config_list: list[str], regex: str):
        '''get the indices that match with regular expression
        '''
        index_list = []
        for index, text in enumerate(config_list):
            if re.match(regex, text):
                index_list.append(index)
        return index_list

    def parse_list_to_hocon(self, conf_list: list[str]) -> ConfigTree:
        """parse list configuration list to Hocon object"""
        from pyhocon.config_parser import ConfigFactory
        return ConfigFactory.parse_string('\n'.join(conf_list))


class ResponseConfLogic(BaseConfLogic):
    def __init__(self) -> None:
        super().__init__()

    def list_to_hocon(self, conf_list: list[str]) -> ConfigTree:
        operations: list[DuplicatedConfLogic] = [
            MessagesConfLogic,
            ValuesConfLogic,
            ContextsConfLogic,
            FieldsConfLogic,
            DataConfLogic,
        ]

        conf_list_result = conf_list

        for operation in operations:
            conf_list_result = operation().modify_conf_list(conf_list_result)

        return self.parse_list_to_hocon(conf_list_result)


class DuplicatedConfLogic():
    def __init__(self) -> None:
        pass

    def modify_conf_list(self, conf_list: list[str]) -> list[str]:
        return conf_list

    def get_indeices_of_regex(self, config_list: list[str], pattern: str):
        '''get the indices that match with regular expression
        '''
        index_list = []
        for index, text in enumerate(config_list):
            if re.match(pattern, text):
                index_list.append(index)
        return index_list

    def get_end_curly_brace_index(self, list, start_index):
        """終わりの}インデックスを取得する"""
        def is_start(text):
            return re.search(r'\s{1,}{', text)

        def is_end(text):
            return re.search(r'\s{1,}}', text)

        curly_brace_stack = []

        current_index = start_index
        while current_index < len(list):
            if is_end(list[current_index]):
                curly_brace_stack.pop()
            if is_start(list[current_index]):
                curly_brace_stack.append('{')

            if len(curly_brace_stack) < 1:
                break
            current_index += 1
        else:
            current_index = -1

        return current_index

    def get_curly_brace_pair_indices(
        self,
        config_list: list,
        start_indices: list[int]
    ) -> list[(int, int)]:
        """
        {}の始まりと終わりのインデックスペアを取得する。
        """
        return [
            (start_index, self.get_end_curly_brace_index(config_list, start_index))
            for start_index in start_indices
        ]

    def replace_edge(
        self,
        list,
        start_index,
        end_index,
        start_pattern,
        start_replace_pattern,
        end_pattern,
        end_repleca_pattern
    ):
        """
        最初と最後のmessagesを処理する
        """
        result_list = list.copy()
        result_list[start_index] = re.sub(
            start_pattern, start_replace_pattern, list[start_index])
        result_list[end_index] = re.sub(
            end_pattern, end_repleca_pattern, list[end_index])

        # {}を追加する
        # インデックスの間違いを無くすため、最後から追加する
        result_list.insert(end_index, ' }')
        result_list.insert(start_index+1, ' {')
        return result_list

    def replace_duplicate_key(
        self,
        list,
        start_end_pairs: list[(int, int)],
        inside_pattern,
        inside_replace_pattern,
        edge_start_pattern,
        edge_start_replece_pattern,
        edge_end_pattern,
        edge_end_replace_pattern
    ):
        """
        複数のキーを処理する
        """
        if len(start_end_pairs) < 1:
            return list

        result_list = list.copy()

        for i in range(1, len(start_end_pairs)):
            # 真ん中はmessagesを取り除くのみ
            inside_start_index = start_end_pairs[i][0]
            result_list[inside_start_index] = re.sub(
                inside_pattern,
                inside_replace_pattern,
                list[inside_start_index]
            )

        # {}を追加する
        # インデックスの間違いを無くすため、最後から追加する
        start_index = start_end_pairs[0][0]
        end_index = start_end_pairs[-1][1]
        result_list = self.replace_edge(
            result_list,
            start_index,
            end_index,
            edge_start_pattern,
            edge_start_replece_pattern,
            edge_end_pattern,
            edge_end_replace_pattern
        )
        return result_list

    def get_continue_start_indices(self, fields_start_end_indices):
        if len(fields_start_end_indices) < 1:
            return []
        copy_indices = fields_start_end_indices.copy()
        result = []
        temp_pairs = [copy_indices.pop(0)]
        while len(copy_indices) > 0:
            fields_end = temp_pairs[-1][1]
            for i, indices in enumerate(copy_indices):
                if fields_end + 1 == indices[0]:
                    temp_pairs.append(copy_indices.pop(i))
                    break
            else:
                # no continus fields
                result.append(temp_pairs)
                temp_pairs = [copy_indices.pop(0)]
        else:
            # end the loop
            result.append(temp_pairs)
        return [item[0][0] for item in result]


class MessagesConfLogic(DuplicatedConfLogic):
    def modify_conf_list(self, conf_list: list[str]) -> list[str]:
        """modify message duplicated list"""
        start_indices = self.get_indeices_of_regex(
            conf_list, pattern=r'\s{1,}messages\s{1,}{')

        start_end_pairs = self.get_curly_brace_pair_indices(
            conf_list, start_indices)

        return self.replace_duplicate_key(
            conf_list,
            start_end_pairs,
            inside_pattern=r'messages(\s{1,}{)',
            inside_replace_pattern='\\1',
            edge_start_pattern=r'(messages)\s{1,}{',
            edge_start_replece_pattern='\\1: [',
            edge_end_pattern=r'(\s{1,})}',
            edge_end_replace_pattern='\\1]'
        )


class ValuesConfLogic(DuplicatedConfLogic):
    START_KEY_PATTERN = r'\s{1,}values\s{1}{'

    def modify_conf_list(self, conf_list: list[str]) -> list[str]:
        """modify values duplicated list"""
        start_indices = self.find_list_value_value_index(conf_list)
        return self.replace_values_key(conf_list, start_indices)

    def find_list_value_value_index(self, conf_list):
        '''
        "list_value->values"のインデックスを取得する
        '''
        result = []
        for i in range(len(conf_list)):
            if re.match(self.START_KEY_PATTERN, conf_list[i]) \
                    and re.match(r'\s{1,}list_value\s{1}{', conf_list[i-1]):
                result.append(i)
        return result

    def replace_values_key(self, conf_list, start_value_indices):
        # get the end curly braces
        # インデックスの変更を防ぐために後ろから実施する
        result = conf_list
        for index in start_value_indices[::-1]:
            start_end_pairs = self.get_end_values_curly_braces(result, index)
            result = self.replace_duplicate_key(
                result,
                start_end_pairs,
                inside_pattern=r'values(\s{1,}{)',
                inside_replace_pattern='\\1',
                edge_start_pattern=r'(values)\s{1,}{',
                edge_start_replece_pattern='\\1: [',
                edge_end_pattern=r'(\s{1,})}',
                edge_end_replace_pattern='\\1]'
            )
        return result

    def get_end_values_curly_braces(self, conf_list, index):
        start_index = index
        result = []
        while re.match(self.START_KEY_PATTERN, conf_list[start_index]):
            end_index = self.get_end_curly_brace_index(conf_list, start_index)
            result.append((start_index, end_index))

            start_index = end_index + 1
        return result


class ContextsConfLogic(DuplicatedConfLogic):
    def modify_conf_list(self, conf_list: list[str]) -> list[str]:
        """modify message duplicated list"""
        start_indices = self.get_indeices_of_regex(
            conf_list, pattern=r'\s{1,}contexts\s{1,}{')

        start_end_pairs = self.get_curly_brace_pair_indices(
            conf_list, start_indices)

        return self.replace_duplicate_key(
            conf_list,
            start_end_pairs,
            inside_pattern=r'contexts(\s{1,}{)',
            inside_replace_pattern='\\1',
            edge_start_pattern=r'(contexts)\s{1,}{',
            edge_start_replece_pattern='\\1: [',
            edge_end_pattern=r'(\s{1,})}',
            edge_end_replace_pattern='\\1]'
        )


class FieldsConfLogic(DuplicatedConfLogic):
    START_KEY_PATTERN = r'\s{1,}fields\s{1,}{'

    def modify_conf_list(self, conf_list: list[str]) -> list[str]:
        """modify fields duplicated list"""
        start_indices = self.get_indeices_of_regex(
            conf_list,
            pattern=self.START_KEY_PATTERN
        )

        start_end_pairs = self.get_curly_brace_pair_indices(
            conf_list,
            start_indices
        )

        start_indices = self.get_continue_start_indices(start_end_pairs)

        result = self.replace_fields_key(conf_list, start_indices)

        return result

    def replace_fields_key(self, conf_list, start_indices):
        result = conf_list

        # インデックスのずれをなくために、最後からループする
        for start_index in start_indices[::-1]:
            start_end_pairs = self.get_fields_start_end_pairs(
                result, start_index)
            result = self.replace_duplicate_key(
                result,
                start_end_pairs,
                inside_pattern=r'fields(\s{1,}{)',
                inside_replace_pattern='\\1',
                edge_start_pattern=r'(fields)\s{1,}{',
                edge_start_replece_pattern='\\1: [',
                edge_end_pattern=r'(\s{1,})}',
                edge_end_replace_pattern='\\1]'
            )
        return result

    def get_fields_start_end_pairs(self, conf_list, start_index):
        start_index = start_index
        result = []
        while re.match(r'\s{1,}fields\s{1,}{', conf_list[start_index]):
            end_index = self.get_end_curly_brace_index(conf_list, start_index)
            result.append((start_index, end_index))
            start_index = end_index + 1
        return result


class DataConfLogic(DuplicatedConfLogic):
    def modify_conf_list(self, conf_list: list[str]) -> list[str]:
        """modify data duplicated list"""
        start_indices = self.get_indeices_of_regex(
            conf_list, pattern=r'\s{1,}data\s{1,}{')

        start_end_pairs = self.get_curly_brace_pair_indices(
            conf_list, start_indices)

        return self.replace_duplicate_key(
            conf_list,
            start_end_pairs,
            inside_pattern=r'data(\s{1,}{)',
            inside_replace_pattern='\\1',
            edge_start_pattern=r'(data)\s{1,}{',
            edge_start_replece_pattern='\\1: [',
            edge_end_pattern=r'(\s{1,})}',
            edge_end_replace_pattern='\\1]'
        )
