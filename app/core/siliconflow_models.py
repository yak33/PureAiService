# 硅基流动平台支持的模型列表
# 更多模型信息请访问: https://docs.siliconflow.cn/docs

SILICONFLOW_MODELS = {
    "glm": {
        "zai-org/GLM-4.5": {
            "name": "zai-org/GLM-4.5",
            "description": "智谱 AI 的对话模型",
            "max_tokens": 32768,
            "input_price": 0,
            "output_price": 0
        },
        "zai-org/GLM-4.5V": {
            "name": "zai-org/GLM-4.5V",
            "description": "智谱 AI 的视觉语言模型（VLM）",
            "max_tokens": 8192,
            "input_price": 0,
            "output_price": 0
        }
    },
    "kimi": {
        "moonshotai/Kimi-K2-Instruct-0905": {
            "name": "moonshotai/Kimi-K2-Instruct-0905",
            "description": "Moonshot AI 文本对话模型",
            "max_tokens": 32768,
            "input_price": 0,
            "output_price": 0
        }
    },
    "image_edit": {
        "Qwen/Qwen-Image-Edit-2509": {
            "name": "Qwen/Qwen-Image-Edit-2509",
            "description": "通义千问图片编辑模型，支持基于自然语言指令的图片编辑",
            "max_tokens": 2048,
            "input_price": 0,
            "output_price": 0
        }
    }
}

# 默认模型配置
DEFAULT_MODEL = "zai-org/GLM-4.5"

# 根据用途推荐的模型
RECOMMENDED_MODELS = {
    "chat": "zai-org/GLM-4.5",
    "vision": "zai-org/GLM-4.5V",
    "kimi": "moonshotai/Kimi-K2-Instruct-0905",
    "image_edit": "Qwen/Qwen-Image-Edit-2509"
}

def get_model_info(model_id: str):
    """获取模型信息"""
    for category in SILICONFLOW_MODELS.values():
        if model_id in category:
            return category[model_id]
    return None

def list_free_models():
    """列出所有免费模型"""
    free_models = []
    for category in SILICONFLOW_MODELS.values():
        for model_id, info in category.items():
            if info.get("input_price", 0) == 0 and info.get("output_price", 0) == 0:
                free_models.append({
                    "id": model_id,
                    "name": info["name"],
                    "description": info["description"]
                })
    return free_models