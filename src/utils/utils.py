import toml


def load_toml(filename, logging):
    """
    从toml文件中加载配置
    :param logging:
    :param filename: toml文件路径
    :return: 配置字典
    """
    try:
        # 尝试直接加载文件
        return toml.load(filename)
    except FileNotFoundError as e:
        logger = logging
        logger.error(f"找不到配置文件: {filename}")
        
        # 尝试从当前执行目录加载
        import os
        import sys
        
        # 获取可能的路径
        possible_paths = [
            # 当前目录
            os.path.join(os.getcwd(), os.path.basename(filename)),
            # 脚本所在目录
            os.path.join(os.path.dirname(sys.argv[0]), os.path.basename(filename)),
            # 打包后可能的位置
            os.path.join(os.path.dirname(sys.executable), os.path.basename(filename)),
            # 项目根目录
            os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', os.path.basename(filename)))
        ]
        
        # 尝试每个可能的路径
        for path in possible_paths:
            logger.info(f"尝试加载配置文件: {path}")
            if os.path.exists(path):
                logger.info(f"找到配置文件: {path}")
                return toml.load(path)
        
        # 如果是password.toml，提供默认配置防止崩溃
        if os.path.basename(filename) == 'password.toml':
            logger.warning("未找到password.toml，使用默认配置")
            return {
                "user1": {
                    "username": "",
                    "password": ""
                },
                "page_port": {
                    "service1": "127.0.0.1:9222"
                },
                "search_limit": {
                    "export_limit": 50
                }
            }
        
        # 其他文件则抛出异常
        raise FileNotFoundError(f"无法找到配置文件: {filename}，尝试的路径: {possible_paths}")
