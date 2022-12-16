from . import parser

def response_to_dict(log_string: str) -> dict:
    """レスポンスファイルをJSON形式に変換する。

    Args:
      target_text: パースする文字列

    Returns:
      dict: A parsed response dictionary

    """
    log_parser = parser.ResponseLog()
    response_string = log_parser.remove_pattern(log_string)
    conf_list = log_parser.get_config_list(response_string)
    hocon = log_parser.list_to_hocon(conf_list)
    response = log_parser.hocon_to_dict(hocon)
    return response
