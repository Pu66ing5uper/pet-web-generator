# pet-web-generator
An AI-powered interactive pet memorial site

# 宠物纪念网站生成器

## 项目目标
通过AI（Coze）自动生成个性化的虚拟宠物互动纪念页。

## 团队分工
- **薛涵汶（Coze专家）**：负责工作流开发，输出包含视频链接和互动指令的JSON。
- **秦皙霖（前端工程师）**：负责开发交互网页，接入JSON数据，实现动画状态机。
- **徐子安（自动化部署）**：负责将A生成的素材自动部署到云端，并更新数据接口。

## 核心数据接口规范（A同学必须遵循）
A同学Coze工作流的最终输出必须为如下格式的JSON：
```json
{
  "petName": "宠物名字",
  "idleAnimation": "待机动画的URL",
  "interactions": [
    {
      "action": "摸头",
      "animation": "反馈动画的URL",
      "triggerButtonText": "摸摸头"
    }
  ]
}
