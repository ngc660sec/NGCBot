import importlib
import pkgutil
from wcf import WCF
from inflection import camelize

class Main:
    def __init__(self):
        wcfOd = 'test'
        wcf_instance = WCF(wcfOd)  # 创建 WCF 实例
        self.load_plugins(wcf_instance, 'msg')  # 加载插件

    def load_plugins(self, wcf_instance, msg):
        # 遍历插件目录并加载插件
        package_name = 'plugins'
        package = importlib.import_module(package_name)

        for _, plugin_name, _ in pkgutil.iter_modules(package.__path__):
            # 动态导入插件
            module = importlib.import_module(f"{package_name}.{plugin_name}")
            # 获取插件类
            plugin_cls = getattr(module, camelize(plugin_name))

            # 实例化插件类
            plugin_instance = plugin_cls(wcf_instance, msg)
            plugin_instance.run()  # 运行插件



if __name__ == '__main__':
    main = Main()  # 创建 Main 实例
