"""
API密钥检查工具
"""

import os


def check_api_keys():
    """检查API密钥配置状态。

    规则：
    - 必需：至少配置一个LLM API Key（DeepSeek / DashScope / OpenAI / Anthropic / Google / Qianfan）
    - 可选：FINNHUB_API_KEY（美股/港股实时增强数据）
    - A股场景可直接使用 AkShare 免费数据源，无需 FINNHUB_API_KEY
    """

    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    qianfan_key = os.getenv("QIANFAN_API_KEY")

    details = {
        "DEEPSEEK_API_KEY": {
            "configured": bool(deepseek_key),
            "display": f"{deepseek_key[:12]}..." if deepseek_key else "未配置",
            "required": False,
            "description": "DeepSeek API密钥（推荐）"
        },
        "DASHSCOPE_API_KEY": {
            "configured": bool(dashscope_key),
            "display": f"{dashscope_key[:12]}..." if dashscope_key else "未配置",
            "required": False,
            "description": "阿里百炼API密钥"
        },
        "OPENAI_API_KEY": {
            "configured": bool(openai_key),
            "display": f"{openai_key[:12]}..." if openai_key else "未配置",
            "required": False,
            "description": "OpenAI API密钥"
        },
        "ANTHROPIC_API_KEY": {
            "configured": bool(anthropic_key),
            "display": f"{anthropic_key[:12]}..." if anthropic_key else "未配置",
            "required": False,
            "description": "Anthropic API密钥"
        },
        "GOOGLE_API_KEY": {
            "configured": bool(google_key),
            "display": f"{google_key[:12]}..." if google_key else "未配置",
            "required": False,
            "description": "Google AI API密钥"
        },
        "QIANFAN_API_KEY": {
            "configured": bool(qianfan_key),
            "display": f"{qianfan_key[:16]}..." if qianfan_key else "未配置",
            "required": False,
            "description": "文心一言（千帆）API Key（OpenAI兼容），一般以 bce-v3/ 开头"
        },
        "FINNHUB_API_KEY": {
            "configured": bool(finnhub_key),
            "display": f"{finnhub_key[:12]}..." if finnhub_key else "未配置",
            "required": False,
            "description": "金融数据API密钥（可选，增强美股/港股数据）"
        },
    }

    llm_provider_keys = [
        "DEEPSEEK_API_KEY",
        "DASHSCOPE_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "QIANFAN_API_KEY",
    ]
    llm_configured = any(details[key]["configured"] for key in llm_provider_keys)

    missing_required = []
    if not llm_configured:
        missing_required.append("ANY_LLM_API_KEY")

    return {
        "all_configured": len(missing_required) == 0,
        "required_configured": len(missing_required) == 0,
        "missing_required": missing_required,
        "llm_configured": llm_configured,
        "details": details,
        "summary": {
            "total": len(details),
            "configured": sum(1 for info in details.values() if info["configured"]),
            "required": 1,
            "required_configured": 1 - len(missing_required)
        }
    }


def get_api_key_status_message():
    """获取API密钥状态消息"""

    status = check_api_keys()

    if status["all_configured"]:
        return "✅ 已配置至少一个LLM API密钥，可开始分析（A股可直接用AkShare）"

    return "❌ 缺少必需配置: 至少一个LLM API Key（推荐 DEEPSEEK_API_KEY）"


def validate_api_key_format(key_type, api_key):
    """验证API密钥格式"""

    if not api_key:
        return False, "API密钥不能为空"

    # 基本长度检查
    if len(api_key) < 10:
        return False, "API密钥长度过短"

    # 特定格式检查
    if key_type == "DASHSCOPE_API_KEY":
        if not api_key.startswith("sk-"):
            return False, "阿里百炼API密钥应以'sk-'开头"
    elif key_type == "DEEPSEEK_API_KEY":
        if not api_key.startswith("sk-"):
            return False, "DeepSeek API密钥应以'sk-'开头"
    elif key_type == "OPENAI_API_KEY":
        if not api_key.startswith("sk-"):
            return False, "OpenAI API密钥应以'sk-'开头"
    elif key_type == "QIANFAN_API_KEY":
        if not api_key.startswith("bce-v3/"):
            return False, "千帆 API Key（OpenAI兼容）应以 'bce-v3/' 开头"

    return True, "API密钥格式正确"


def test_api_connection(key_type, api_key):
    """测试API连接（简单验证）"""

    is_valid, message = validate_api_key_format(key_type, api_key)

    if not is_valid:
        return False, message

    return True, "API密钥验证通过"
