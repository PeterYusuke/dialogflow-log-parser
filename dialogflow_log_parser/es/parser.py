from pyhocon.config_tree import ConfigTree
from .logic import response_conf_logic, response_hocon_logic


class BaseLog():
    PATTERN_REMOVE = r''

    def __init__(self) -> None:
        pass

    @classmethod
    def remove_pattern(self, log_string: str) -> str:
        """remove unnecessary string"""
        import re
        return re.sub(self.PATTERN_REMOVE, '', log_string)

    @classmethod
    def get_config_list(
        self,
        log_string: str,
        split_string: str = '\n'
    ) -> list[str]:
        """split target string

        Args:
          log_string (str) : A target string to split
          split_string (str) : split string 
        """
        return log_string.split(split_string)


class ResponseLog(BaseLog):
    PATTERN_REMOVE = r'^Dialogflow\s{1}Response\s{1}:\s{1,}'

    def list_to_hocon(self, conf_list: list[str]) -> ConfigTree:
        """parse config list to hocon ConfigTree

        Args:
          conf_list (list[str]) : config string list
        """
        return response_conf_logic.list_to_hocon(conf_list)

    def hocon_to_dict(self, hocon: ConfigTree):
        return response_hocon_logic.hocon_to_dict(hocon)
