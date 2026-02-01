#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宠物纪念站自动化部署脚本 (C同学)
功能：1. 上传视频到云存储 2. 更新JSON中的链接 3. 输出最终数据
注意：请先设置环境变量 COS_SECRET_ID 和 COS_SECRET_KEY
"""

import json
import os
import sys
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError

# ==================== 配置区域 ====================
# 从环境变量读取敏感信息，避免硬编码在代码中！
COS_SECRET_ID = os.environ.get('COS_SECRET_ID')
COS_SECRET_KEY = os.environ.get('COS_SECRET_KEY')

# 请检查环境变量是否已设置
if not COS_SECRET_ID or not COS_SECRET_KEY:
    print("错误：未检测到 COS_SECRET_ID 或 COS_SECRET_KEY 环境变量。")
    print("请在终端执行：")
    print("    export COS_SECRET_ID='你的SecretId'")
    print("    export COS_SECRET_KEY='你的SecretKey'")
    sys.exit(1)

# 存储桶的公共信息（可保留在代码中）
COS_REGION = 'ap-beijing'  # 请确保与你的存储桶地域一致
COS_BUCKET = 'qingzhouyiguowanchong-1401241131'
# ==================================================

def upload_to_cos(local_file_path, cos_object_name):
    """
    将本地文件上传到腾讯云COS，并返回文件的公开访问URL。
    """
    if not os.path.exists(local_file_path):
        print(f"[错误] 本地文件不存在: {local_file_path}")
        return None

    # 初始化配置和客户端
    config = CosConfig(Region=COS_REGION, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY)
    client = CosS3Client(config)

    try:
        print(f"[上传] {os.path.basename(local_file_path)} -> cos:{COS_BUCKET}/{cos_object_name}")
        # 执行上传
        response = client.upload_file(
            Bucket=COS_BUCKET,
            LocalFilePath=local_file_path,
            Key=cos_object_name,  # 文件在COS中的路径
            EnableMD5=False
        )
        # 构建公开访问URL（存储桶需为“公有读”权限）
        public_url = f"https://{COS_BUCKET}.cos.{COS_REGION}.myqcloud.com/{cos_object_name}"
        print(f"[成功] 链接: {public_url}")
        return public_url

    except (CosClientError, CosServiceError) as e:
        print(f"[错误] 腾讯云COS服务异常: {e}")
        return None
    except Exception as e:
        print(f"[错误] 上传过程发生未知异常: {e}")
        return None

def update_json_data(raw_json_path, new_animation_urls):
    """
    读取A同学生成的原始JSON，用新的永久链接替换其中的动画URL。
    """
    if not os.path.exists(raw_json_path):
        print(f"[错误] JSON文件不存在: {raw_json_path}")
        return None

    try:
        with open(raw_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[读取] 成功加载JSON，宠物名称: {data.get('petName', '未知')}")

        # 替换动画链接
        if new_animation_urls.get('idle'):
            data['idleAnimation'] = new_animation_urls['idle']
        if new_animation_urls.get('feedback') and data.get('interactions'):
            # 默认更新第一个交互动作的动画链接
            data['interactions'][0]['animation'] = new_animation_urls['feedback']

        print("[更新] 已替换视频链接为永久URL")
        return data

    except json.JSONDecodeError as e:
        print(f"[错误] JSON文件格式不正确: {e}")
        return None
    except Exception as e:
        print(f"[错误] 处理JSON文件时发生异常: {e}")
        return None

def main():
    """主函数，串联整个自动化流程"""
    print("=" * 40)
    print("开始自动化部署流程")
    print("=" * 40)

    # 定义原始素材路径（相对于脚本所在目录）
    raw_materials_dir = "./raw_materials"
    raw_idle_video = os.path.join(raw_materials_dir, "idle.mp4")
    raw_feedback_video = os.path.join(raw_materials_dir, "feedback.mp4")
    raw_json = os.path.join(raw_materials_dir, "pet_data.json")

    # 第一步：上传视频，获取永久链接
    print("\n[阶段1] 上传视频素材至云端...")
    idle_url = upload_to_cos(raw_idle_video, "pets/idle.mp4")
    feedback_url = upload_to_cos(raw_feedback_video, "pets/feedback.mp4")

    if not idle_url or not feedback_url:
        print("[中断] 视频上传失败，流程终止。请检查错误信息。")
        sys.exit(1)

    # 第二步：更新JSON数据
    print("\n[阶段2] 更新JSON数据中的链接...")
    new_urls = {'idle': idle_url, 'feedback': feedback_url}
    final_data = update_json_data(raw_json, new_urls)

    if not final_data:
        print("[中断] JSON数据更新失败，流程终止。")
        sys.exit(1)

    # 第三步：保存最终给B同学的JSON
    print("\n[阶段3] 保存最终配置文件...")
    output_dir = "./deploy_output"
    output_path = os.path.join(output_dir, "final_pet_data.json")
    os.makedirs(output_dir, exist_ok=True)  # 如果输出目录不存在则创建

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print(f"[成功] 最终配置文件已保存至: {os.path.abspath(output_path)}")
        print("\n" + "=" * 40)
        print("流程完成！请将以下文件交给B同学：")
        print(f"  1. JSON文件: {output_path}")
        print(f"  2. 待机动画URL: {idle_url}")
        print(f"  3. 互动动画URL: {feedback_url}")
        print("=" * 40)
    except Exception as e:
        print(f"[错误] 写入最终文件失败: {e}")

if __name__ == '__main__':
    main()
