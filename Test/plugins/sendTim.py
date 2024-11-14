class SendTim:
    def __init__(self, wcf_instance, msg):
        self.wcf_instance = wcf_instance
        self.msg = msg

    def run(self):
        print(f"sendTim plugin: {self.wcf_instance.returnWcf()}", self.msg)
