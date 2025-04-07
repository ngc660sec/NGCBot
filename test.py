import webview


def init_webview():
    """
    初始化 WebView 并加载解密相关 WASM 代码
    返回 webview 窗口实例和 JavaScript 执行接口
    """
    window = webview.create_window(
        title='WASM Decryptor',
        html='''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>WASM Decryptor</title>
            <script>
                // 配置 WASM 路径和内存大小
                window.VTS_WASM_URL = "https://aladin.wxqcloud.qq.com/aladin/ffmepeg/video-decode/1.2.50/wasm_video_decode.wasm";
                window.MAX_HEAP_SIZE = 33554432;

                // 全局解密器数组
                var decryptor_array;

                // Uint8Array 转 Base64
                function Uint8ArrayToBase64(bytes) {
                    let binary = '';
                    const len = bytes.byteLength;
                    for (let i = 0; i < len; i++) {
                        binary += String.fromCharCode(bytes[i]);
                    }
                    return window.btoa(binary);
                }

                // Base64 转 Uint8Array
                function base64ToUint8Array(base64) {
                    const binaryString = window.atob(base64);
                    const len = binaryString.length;
                    const bytes = new Uint8Array(len);
                    for (let i = 0; i < len; i++) {
                        bytes[i] = binaryString.charCodeAt(i);
                    }
                    return bytes;
                }

                // WASM 生成的 ISAAC 解密器
                function wasm_isaac_generate(t, e) {
                    decryptor_array = new Uint8Array(e);
                    var r = new Uint8Array(Module.HEAPU8.buffer, t, e);
                    decryptor_array.set(r.reverse());
                }

                // 获取解密器数组（Base64 编码）
                function get_decryptor_array(seed) {
                    let decryptor = new Module.WxIsaac64(seed);
                    decryptor.generate(131072);
                    return Uint8ArrayToBase64(decryptor_array);
                }
            </script>
            <!-- 加载 WASM 解密库 -->
            <script src="https://aladin.wxqcloud.qq.com/aladin/ffmepeg/video-decode/1.2.50/wasm_video_decode.js"></script>
        </head>
        <body>
            <!-- 空页面，所有操作通过 JavaScript 完成 -->
        </body>
        </html>
        ''',
        js_api=None,
        width=0,  # 最小化窗口
        height=0,
        resizable=False
    )

    # 启动 WebView（非阻塞模式）
    webview.start()
    return window


def get_decryptor(seed):
    """
    获取解密器数组
    :param seed: 解密种子
    :return: Base64 编码的解密器数组
    """
    window = init_webview()

    # 等待 WASM 加载完成（实际使用时需要更完善的等待机制）
    import time
    time.sleep(3)

    # 执行 JavaScript 获取解密器
    result = window.evaluate_js(f'get_decryptor_array({seed})')
    return result


if __name__ == '__main__':
    # 示例用法
    test_seed = 123456
    decryptor_data = get_decryptor(test_seed)
    print(f"获取到的解密器数据（Base64）:\n{decryptor_data}")