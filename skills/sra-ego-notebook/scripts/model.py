#!/usr/bin/env python3
"""
搜索/列出 EGO 模型

用法:
    model.py [--name <name>] [--scope <1|2>] [--json]

示例:
    # 搜索模型（先个人再全部）
    model.py --name base_model

    # 列出个人所有模型
    model.py

    # 列出所有人的模型
    model.py --scope 1

    # JSON 格式输出
    model.py --name base_model --json
"""

import sys
import json
import argparse
import os
import re
import requests
from pathlib import Path


def load_env_from_shell():
    env_vars = {}
    for config_file in [Path.home() / '.zshrc', Path.home() / '.bashrc']:
        if not config_file.exists():
            continue
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    match = re.match(r'^\s*export\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line.strip())
                    if match:
                        var_name = match.group(1)
                        var_value = match.group(2).strip().strip('"').strip("'")
                        if (var_name.startswith('EGO_') or var_name == 'USER_ID_OPENAPI') and var_name not in os.environ:
                            env_vars[var_name] = var_value
        except:
            continue
    return env_vars


def get_api_config():
    shell_env = load_env_from_shell()
    base_url = os.getenv('EGO_API_URL') or shell_env.get('EGO_API_URL', 'https://ego-portal.mlp.live-test.shopee.io/api/ego/portal')
    token = os.getenv('USER_ID_OPENAPI') or shell_env.get('USER_ID_OPENAPI')
    if not token:
        raise ValueError("需要设置 USER_ID_OPENAPI 环境变量")
    return base_url, token


def api_request(method, endpoint, token, base_url, **kwargs):
    url = base_url.rstrip('/') + '/' + endpoint.lstrip('/')
    session = requests.Session()
    session.cookies.set('userID', token)
    session.headers.update({'Content-Type': 'application/json'})
    response = session.request(method=method, url=url, **kwargs)
    response.raise_for_status()
    result = response.json()
    if isinstance(result, dict) and 'code' in result:
        code = str(result['code'])
        if code.startswith('4') or code.startswith('5'):
            raise ValueError(f"API Error: {result.get('msg', 'Unknown error')}")
    return result


def main():
    parser = argparse.ArgumentParser(
        description='搜索/列出 EGO 模型',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--name', help='按模型名搜索（精确匹配）')
    parser.add_argument('--scope', type=int, help='范围: 1=所有人, 2=个人。不指定时按名搜索先 2 后 1')
    parser.add_argument('--page-size', type=int, default=50, help='每页数量 (默认 50)')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')

    args = parser.parse_args()

    try:
        base_url, token = get_api_config()

        params = {'current': 1, 'pageSize': args.page_size}
        if args.name:
            params['model_name'] = args.name

        scopes = [args.scope] if args.scope else ([2, 1] if args.name else [2])
        all_models = []

        for scope in scopes:
            params['scope'] = scope
            resp = api_request('GET', '/models', token, base_url, params=params)
            models = resp.get('data', {}).get('data', [])

            if args.name:
                models = [m for m in models if m.get('model_name') == args.name]

            if models:
                all_models = models
                break

        if args.json:
            print(json.dumps({'models': [
                {
                    'model_id': m.get('model_id'),
                    'model_name': m.get('model_name'),
                    'description': m.get('description', ''),
                }
                for m in all_models
            ]}, ensure_ascii=False, indent=2))
        else:
            if not all_models:
                if args.name:
                    print(f"❌ 未找到模型: {args.name}")
                else:
                    print("📭 没有找到模型")
                return 1

            print(f"\n📦 找到 {len(all_models)} 个模型:\n")
            for m in all_models:
                mid = m.get('model_id', '-')
                mname = m.get('model_name', '-')
                desc = m.get('description', '')
                desc_short = (desc[:40] + '...') if len(desc) > 40 else desc
                print(f"   model_id={mid:<8} {mname:<30} {desc_short}")

        return 0

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
