import requests
import json


class QianWenAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    # 修改qianwen_api.py中的get_response方法
    def get_response(self, prompt, model="qwen3-max", temperature=0.7):
        """
        调用通义千问API获取响应
        :param prompt: 提示词
        :param model: qwen3-max
        :param temperature: 0.5
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

            if response.status_code == 200 and "output" in response_data:
                # 适配新的响应格式：从choices列表中获取message内容
                if "choices" in response_data["output"] and len(response_data["output"]["choices"]) > 0:
                    choice = response_data["output"]["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
                    else:
                        return f"API返回格式异常: 未找到message.content字段，响应数据: {str(response_data)}"
                else:
                    return f"API返回格式异常: 未找到有效的choices字段，响应数据: {str(response_data)}"
            else:
                error_msg = response_data.get("message", "未知错误")
                return f"API调用失败: {error_msg}"

        except Exception as e:
            return f"请求发生错误: {str(e)}"


