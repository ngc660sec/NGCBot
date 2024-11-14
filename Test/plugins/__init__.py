from pluginbase import PluginBase

plugin_base = PluginBase(package='plugins')

# 定义插件的基类
class BasePlugin:
    def __init__(self, wcf_instance):
        self.wcf_instance = wcf_instance

    def run(self):
        raise NotImplementedError("Plugins must implement the run method.")
