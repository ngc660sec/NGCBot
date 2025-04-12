from WebServer.webRoute import webRoute
import Config.ConfigServer as Cs
from OutPut.outPut import op
import logging
import uvicorn


class CancelFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return not ("Invalid HTTP request received" in msg or "CancelledError" in msg)


class WebServer:
    def __init__(self, wcf, httpHost, httpPort):
        """
        HTTP接口服务
        :param wcf:
        :param httpHost:
        :param httpPort:
        """
        global uvicorn_server
        self.wcf = wcf
        webServerConfig = Cs.returnConfigData().get('WebServerConfig')
        self.httpHost = httpHost
        if not httpPort:
            httpPort = 0
        self.httpPort = int(httpPort)
        self.cbApi = webServerConfig.get('cbApi')
        self.http = webRoute(wcf=self.wcf, title='NGCBot API接口',
                             description='https://github.com/ngc660sec/NGCBot', docs_url="/docs", redoc_url=None,
                             version="2.3")
        self.server = None

    def run(self, ):
        if not self.httpHost and not self.httpPort:
            return
        try:
            # 修改：设置更全面的日志过滤
            logger_names = ("uvicorn.error", "uvicorn.access", "uvicorn")
            for name in logger_names:
                logger = logging.getLogger(name)
                logger.addFilter(CancelFilter())
                logger.propagate = False
            # 修改：配置更严格的日志级别
            config = uvicorn.Config(
                app=self.http,
                host=self.httpHost,
                port=self.httpPort,
                lifespan="on",
                log_level="warning"
            )
            op(f'[+]: API文档地址: http://{self.httpHost.replace("0.0.0.0", "127.0.0.1")}:{self.httpPort}/docs')
            self.server = uvicorn.Server(config)
            self.server.install_signal_handlers = False
            self.server.run()
        except Exception as e:
            pass

    def stopWebServer(self, ):
        """
        停止WebServer服务
        :return:
        """
        if self.server:
            self.server.should_exit = True
            self.server.force_exit = True
