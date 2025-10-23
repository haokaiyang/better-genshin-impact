#!/usr/bin/env python3
"""
从 genshin-data 仓库更新 TCG 角色卡牌数据
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def transform_skill(skill: Dict[str, Any]) -> Dict[str, Any]:
    """转换技能数据格式"""
    # 转换消耗点数
    cost = []
    for point in skill.get('points', []):
        if point:  # 跳过空值
            cost.append({
                'id': point['_id'],
                'nameEn': point['id'],
                'type': point['type'],
                'count': point['count']
            })

    return {
        'nameEn': skill['id'],
        'name': skill['name'],
        'skillTag': skill['skillTag'],
        'cost': cost
    }


def transform_character(data: Dict[str, Any]) -> Dict[str, Any]:
    """转换角色数据格式"""
    # 转换所有技能（包括被动技能）
    skills = [transform_skill(skill) for skill in data['skills']]

    return {
        'id': data['_id'],
        'nameEn': data['id'],
        'type': 'character',
        'name': data['name'],
        'hp': data['attributes']['hp'],
        'energy': data['attributes']['energy'],
        'element': data['attributes']['element'],
        'weapon': data['attributes']['weapon'],
        'skills': skills
    }


def process_genshin_data(input_dir: Path, output_file: Path) -> None:
    """
    处理 genshin-data 目录中的所有角色 JSON 文件

    Args:
        input_dir: genshin-data 的 tcg_characters 目录路径
        output_file: 输出的 JSON 文件路径
    """
    if not input_dir.exists():
        print(f"❌ 错误: 输入目录不存在: {input_dir}", file=sys.stderr)
        sys.exit(1)

    characters = []

    # 遍历所有 JSON 文件
    json_files = sorted(input_dir.glob('*.json'))

    if not json_files:
        print(f"❌ 错误: 在 {input_dir} 中没有找到 JSON 文件", file=sys.stderr)
        sys.exit(1)

    print(f"📁 找到 {len(json_files)} 个角色文件")

    for json_file in json_files:
        print(f"  处理: {json_file.name}")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                character = transform_character(data)
                characters.append(character)
        except Exception as e:
            print(f"⚠️  警告: 处理 {json_file.name} 时出错: {e}", file=sys.stderr)
            continue

    # 按 ID 排序
    characters.sort(key=lambda x: x['id'])

    # 输出 JSON 文件
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(characters, f, ensure_ascii=False, indent=4)

    print(f"✅ 成功生成 {len(characters)} 个角色数据")
    print(f"📄 输出文件: {output_file}")


def main():
    """主函数"""
    # 设置路径
    if len(sys.argv) > 1:
        input_dir = Path(sys.argv[1])
    else:
        # 默认路径（用于 GitHub Actions）
        input_dir = Path('genshin-data/src/data/chinese-simplified/tcg_characters')

    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        # 默认输出路径
        output_file = Path('BetterGenshinImpact/GameTask/AutoGeniusInvokation/Assets/tcg_character_card.json')

    print(f"🔄 开始处理 TCG 角色卡牌数据")
    print(f"📥 输入目录: {input_dir}")
    print(f"📤 输出文件: {output_file}")
    print()

    process_genshin_data(input_dir, output_file)


if __name__ == '__main__':
    main()
