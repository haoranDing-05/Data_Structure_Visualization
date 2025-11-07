import requests
import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QTextEdit, QLabel, QFrame, QApplication)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPixmap, QMouseEvent
import threading


class QianWenAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def get_response(self, prompt, model="qwen-max", temperature=0.7):
        """
        调用通义千问API获取响应
        :param prompt: 提示词
        :param model: qwen-max
        :param temperature: 0.7
        :return: 模型返回的文本
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "temperature": temperature,
                "top_p": 0.9,
                "max_tokens": 1024
            }
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(data)
            )

            response_data = response.json()

            # 添加调试信息
            print("API响应状态码:", response.status_code)
            print("完整API响应:", json.dumps(response_data, indent=2, ensure_ascii=False))

            if response.status_code == 200:
                # 尝试不同的响应格式解析
                if "output" in response_data and "text" in response_data["output"]:
                    # 格式1: 直接包含text字段
                    return response_data["output"]["text"]
                elif "output" in response_data and "choices" in response_data["output"]:
                    # 格式2: 包含choices列表
                    choices = response_data["output"]["choices"]
                    if len(choices) > 0:
                        choice = choices[0]
                        if "message" in choice and "content" in choice["message"]:
                            return choice["message"]["content"]
                        elif "text" in choice:
                            return choice["text"]
                elif "output" in response_data:
                    # 格式3: 其他output格式
                    output = response_data["output"]
                    if isinstance(output, str):
                        return output
                    elif isinstance(output, dict):
                        # 尝试获取可能的文本字段
                        for key in ["text", "content", "result", "message"]:
                            if key in output:
                                return output[key]

                return f"API返回格式异常，无法解析响应: {response_data}"
            else:
                error_msg = response_data.get("message", "未知错误")
                return f"API调用失败: {error_msg} (状态码: {response.status_code})"

        except Exception as e:
            return f"请求发生错误: {str(e)}"


class AIAssistantThread(QThread):
    """AI助手线程"""
    response_received = pyqtSignal(str)

    def __init__(self, api, prompt):
        super().__init__()
        self.api = api
        self.prompt = prompt

    def run(self):
        try:
            response = self.api.get_response(self.prompt)
            self.response_received.emit(response)
        except Exception as e:
            self.response_received.emit(f"处理请求时出错: {str(e)}")





