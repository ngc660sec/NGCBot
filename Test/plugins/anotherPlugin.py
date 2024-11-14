class AnotherPlugin:
    def __init__(self, wcf_instance, msg):
        self.wcf_instance = wcf_instance
        self.msg = msg

    def run(self):
        print(f"anotherPlugin: {self.wcf_instance.returnWcf()} (this is another plugin)", self.msg)
