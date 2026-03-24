#!/usr/bin/env python3
"""
搜索/列出 EGO 模型版本

用法:
    version.py --model-id <id> [--name <version_name>] [--json]
    version.py --model-name <name> [--name <version_name>] [--json]

示例:
    # 列出模型下所有版本
    version.py --model-id 763

    # 通过模型名列出版本
    version.py --model-name base_model

    # 搜索特定版本
    version.py --model-id 763 --name test_version

    # 通过模型名+版本名查找（最常用）
    version.py --model-name base_model --name test_version

    # JSON 格式输出
    version.py --model-name base_model --json
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


def resolve_model_name(model_name, token, base_url):
    for scope in [2, 1]:
        resp = api_request('GET', '/models', token, base_url, params={
            'model_name': model_name,
            'scope': scope,
            'current': 1,
            'pageSize': 50,
        })
        for m in resp.get('data', {}).get('data', []):
            if m.get('model_name') == model_name:
                return m.get('model_id'), m.get('model_name')
    return None, None


def main():
    parser = argparse.ArgumentParser(
        description='搜索/列出 EGO 模型版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--model-id', type=int, help='模型 ID')
    group.add_argument('--model-name', help='模型名称（自动解析为 model_id）')

    parser.add_argument('--name', help='按版本名搜索（精确匹配）')
    parser.add_argument('--page-size', type=int, default=100, help='每页数量 (默认 100)')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')

    args = parser.parse_args()

    try:
        base_url, token = get_api_config()

        model_id = args.model_id
        model_name = args.model_name

        if model_name and not model_id:
            model_id, resolved_name = resolve_model_name(model_name, token, base_url)
            if not model_id:
                print(f"❌ 未找到模型: {model_name}", file=sys.stderr)
                return 1
            if not args.json:
                print(f"📦 模型: {model_name} (model_id={model_id})")

        resp = api_request('GET', f'/model/{model_id}/versions', token, base_url, params={
            'current': 1,
            'pageSize': args.page_size,
        })
        versions = resp.get('data', {}).get('data', [])

        if args.name:
            versions = [v for v in versions if v.get('version_name') == args.name]

        if args.json:
            result = {'model_id': model_id}
            if model_name:
                result['model_name'] = model_name
            if args.name and versions:
                v = versions[0]
                result['version_id'] = v.get('version_id')
                result['version_name'] = v.get('version_name')
            else:
                result['versions'] = [
                    {'version_id': v.get('version_id'), 'version_name': v.get('version_name')}
                    for v in versions
                ]
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if not versions:
                if args.name:
                    print(f"❌ 未找到版本: {args.name}")
                    all_versions = api_request('GET', f'/model/{model_id}/versions', token, base_url, params={
                        'current': 1, 'pageSize': args.page_size,
                    }).get('data', {}).get('data', [])
                    if all_versions:
                        print(f"\n可用版本:")
                        for v in all_versions:
                            print(f"   - {v.get('version_name')} (version_id={v.get('version_id')})")
                else:
                    print(f"📭 模型 (model_id={model_id}) 下没有版本")
                return 1

            if args.name:
                v = versions[0]
                print(f"\n✅ 解析结果:")
                print(f"   model_id     = {model_id}")
                print(f"   version_id   = {v.get('version_id')}")
                print(f"   version_name = {v.get('version_name')}")
            else:
                print(f"\n📋 共 {len(versions)} 个版本:\n")
                for i, v in enumerate(versions, 1):
                    vid = v.get('version_id', '-')
                    vname = v.get('version_name', '-')
                    print(f"   {i:3d}. {vname:<30} (version_id={vid})")

        return 0

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
