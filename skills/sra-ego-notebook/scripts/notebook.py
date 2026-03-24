#!/usr/bin/env python3
"""
EGO Notebook 管理工具

用法:
    notebook.py start <version_id> [--wait] [--expiration-time SECONDS]
    notebook.py stop <version_id> [--force]
    notebook.py list [--status STATUS] [--version-id ID]
    notebook.py extend <version_id> --extend-time SECONDS
    notebook.py configure <model_id> <version_id> [--interactive]

示例:
    # 启动 notebook 并等待
    notebook.py start 3904 --wait

    # 停止 notebook
    notebook.py stop 3904 --force

    # 列出运行中的 notebooks
    notebook.py list --status running

    # 延长 2 小时
    notebook.py extend 3904 --extend-time 7200

    # 交互式配置
    notebook.py configure 763 3904 --interactive
"""

import sys
import time
import json
import argparse
import os
import re
import requests
from pathlib import Path
from datetime import datetime


# ── API helpers ──────────────────────────────────────────────────────

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


def generate_ego_portal_url(base_url, model_name, model_id, version_name, version_id):
    portal_base = base_url.split('/api/')[0] if '/api/' in base_url else base_url.rstrip('/')
    return f"{portal_base}/jupyter/{model_name}:{model_id}/{version_name}:{version_id}"


def format_time(timestamp_ms):
    if not timestamp_ms or timestamp_ms == 0:
        return '-'
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_duration(seconds):
    if not seconds or seconds <= 0:
        return '-'
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


# ── subcommand: start ────────────────────────────────────────────────

def cmd_start(args):
    base_url, token = get_api_config()

    print(f"🚀 启动 Notebook (version_id={args.version_id})...")
    result = api_request(
        'POST', '/notebook/start', token, base_url,
        json={'version_id': args.version_id, 'expiration_time': args.expiration_time}
    )
    job_id = result.get('data')
    print(f"✅ 启动成功! Job ID: {job_id}")

    if args.wait:
        print(f"\n⏳ 等待 Notebook 启动...")
        start_time = time.time()

        while time.time() - start_time < args.timeout:
            time.sleep(2)
            resp = api_request(
                'GET', '/notebooks', token, base_url,
                params={
                    'version_id': args.version_id,
                    'pageSize': 1,
                    'orderBy': 'id',
                    'order': 'descend',
                    'scope': 2,
                    'current': 1,
                }
            )
            notebooks = resp.get('data', {}).get('data', [])
            if not notebooks:
                continue

            status = notebooks[0].get('notebook_status', '')
            print(f"   状态: {status}")

            if status == 'running':
                print(f"✅ Notebook 已启动!")
                nb = notebooks[0]
                model_name = nb.get('model_name', '')
                model_id = nb.get('model_id', '')
                version_name = nb.get('version_name', '')
                version_id = nb.get('version_id', '')

                if model_name and version_name:
                    ego_url = generate_ego_portal_url(base_url, model_name, model_id, version_name, version_id)
                    print(f"🔗 EGO Portal: {ego_url}")

                notebook_link = nb.get('notebook_link', '')
                if notebook_link:
                    print(f"🔗 直接访问: {notebook_link}")
                break
            elif status in ['failed', 'closed']:
                print(f"❌ 启动失败: {status}")
                return 1
        else:
            print(f"⏱️  等待超时，请在 EGO Portal 查看状态")

    print(f"\n✅ 完成!")
    return 0


# ── subcommand: stop ─────────────────────────────────────────────────

def cmd_stop(args):
    base_url, token = get_api_config()

    print(f"🔍 检查 Notebook 状态 (version_id={args.version_id})...")
    resp = api_request(
        'GET', '/notebooks', token, base_url,
        params={
            'version_id': args.version_id,
            'pageSize': 1,
            'orderBy': 'id',
            'order': 'descend',
            'scope': 2,
            'current': 1,
        }
    )

    notebooks = resp.get('data', {}).get('data', [])
    if not notebooks:
        print(f"❌ 没有找到 notebook 记录")
        return 1

    notebook = notebooks[0]
    status = notebook.get('notebook_status', '')
    print(f"   当前状态: {status}")

    if status not in ['created', 'pending', 'running']:
        print(f"⚠️  Notebook 状态为 {status}，无需停止")
        return 0

    if not args.force:
        notebook_id = notebook.get('notebook_id')
        print(f"\n⚠️  确认停止以下 Notebook?")
        print(f"   - Notebook ID: {notebook_id}")
        print(f"   - Version ID: {args.version_id}")
        print(f"   - Status: {status}")
        confirm = input("\n输入 'yes' 确认停止: ")
        if confirm.lower() != 'yes':
            print("已取消")
            return 0

    print(f"\n🛑 停止 Notebook...")
    api_request('POST', '/notebook/stop', token, base_url, json={'version_id': args.version_id})
    print(f"✅ Notebook 停止成功!")

    print(f"\n✅ 完成!")
    return 0


# ── subcommand: list ─────────────────────────────────────────────────

def cmd_list(args):
    base_url, token = get_api_config()

    params = {
        'scope': args.scope,
        'current': 1,
        'pageSize': args.page_size,
        'orderBy': 'id',
        'order': 'descend',
    }
    if args.status:
        params['notebook_status'] = args.status
    if args.version_id:
        params['version_id'] = args.version_id
    if args.model_id:
        params['model_id'] = args.model_id

    resp = api_request('GET', '/notebooks', token, base_url, params=params)
    notebooks = resp.get('data', {}).get('data', [])
    total = resp.get('data', {}).get('info', {}).get('total', 0)

    if args.json:
        output = {
            'success': True,
            'total': total,
            'count': len(notebooks),
            'notebooks': notebooks,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if not notebooks:
            print("📭 没有找到 notebook")
            return 0

        print(f"\n📊 找到 {len(notebooks)} 个 Notebook:\n")
        print(f"{'ID':<8} {'Model':<20} {'Version':<20} {'Status':<10} {'Creator':<20} {'Created':<20} {'Expiration':<12}")
        print("-" * 130)

        for nb in notebooks:
            notebook_id = nb.get('notebook_id', '-')
            model_name = nb.get('model_name', '-')[:19]
            version_name = nb.get('version_name', '-')[:19]
            status = nb.get('notebook_status', '-')
            creator = nb.get('creator', '-').split('@')[0][:19]
            created = format_time(nb.get('create_time', 0))
            expiration = '-'
            if status == 'running' and nb.get('expiration_time', 0) > 0:
                expiration = format_duration(nb['expiration_time'])
            print(f"{notebook_id:<8} {model_name:<20} {version_name:<20} {status:<10} {creator:<20} {created:<20} {expiration:<12}")

        print()
        running_notebooks = [nb for nb in notebooks if nb.get('notebook_status') == 'running']
        if running_notebooks:
            print("🔗 访问链接:")
            for nb in running_notebooks:
                mn = nb.get('model_name', '')
                mid = nb.get('model_id', '')
                vn = nb.get('version_name', '')
                vid = nb.get('version_id', '')
                if mn and vn:
                    ego_url = generate_ego_portal_url(base_url, mn, mid, vn, vid)
                    print(f"   [{mn}:{vn}] {ego_url}")
                else:
                    notebook_link = nb.get('notebook_link', '')
                    if notebook_link:
                        print(f"   [{mn}:{vn}] {notebook_link}")

        if len(notebooks) < total:
            print(f"\n📄 显示 {len(notebooks)}/{total} 个结果")
            print(f"   使用 --page-size 参数查看更多")

    return 0


# ── subcommand: extend ───────────────────────────────────────────────

def cmd_extend(args):
    if args.extend_time <= 0:
        print(f"❌ 延长时间必须大于 0", file=sys.stderr)
        return 1

    base_url, token = get_api_config()

    print(f"🔍 检查 Notebook 状态 (version_id={args.version_id})...")
    resp = api_request(
        'GET', '/notebooks', token, base_url,
        params={
            'version_id': args.version_id,
            'pageSize': 1,
            'orderBy': 'id',
            'order': 'descend',
            'scope': 2,
            'current': 1,
        }
    )

    notebooks = resp.get('data', {}).get('data', [])
    if not notebooks:
        print(f"❌ 没有找到 notebook 记录")
        return 1

    notebook = notebooks[0]
    status = notebook.get('notebook_status', '')
    print(f"   当前状态: {status}")

    if status != 'running':
        print(f"❌ Notebook 状态为 {status}，只能延长 running 状态的 notebook")
        return 1

    expiration_time = notebook.get('expiration_time', 0)
    if expiration_time > 0:
        hours = expiration_time // 3600
        minutes = (expiration_time % 3600) // 60
        print(f"   剩余时间: {hours}h {minutes}m")

    hours = args.extend_time // 3600
    minutes = (args.extend_time % 3600) // 60
    print(f"\n⏰ 延长运行时间: {hours}h {minutes}m ({args.extend_time} 秒)")

    extend_time_minutes = args.extend_time // 60
    api_request(
        'POST', '/notebook/extend_time', token, base_url,
        json={'version_id': args.version_id, 'extend_time': extend_time_minutes}
    )
    print(f"✅ 延长成功!")

    print(f"\n✅ 完成!")
    return 0


# ── subcommand: configure ────────────────────────────────────────────

def list_available_images(token, base_url):
    try:
        resp = api_request('GET', '/notebook/get_image', token, base_url)
        images = resp.get('data', [])
        if images:
            return images
        resp = api_request('GET', '/framework_versions', token, base_url)
        versions = resp.get('data', {}).get('framework_versions', [])
        return [v.get('image', '') for v in versions if v.get('image')]
    except Exception as e:
        print(f"⚠️  获取镜像列表失败: {e}")
        return []


def interactive_configure(model_id, version_id, token, base_url):
    print(f"🔧 配置 Notebook (model_id={model_id}, version_id={version_id})")
    print()

    try:
        version = api_request('GET', f'/model/{model_id}/version/{version_id}', token, base_url).get('data', {})
        current_image = version.get('notebook_image', '')
        current_resource = version.get('notebook_resource', {})
        print(f"📋 当前配置:")
        print(f"   Image: {current_image if current_image else '未配置'}")
        if current_resource:
            print(f"   CPU: {current_resource.get('cpu', 0)} cores")
            print(f"   Memory: {current_resource.get('memory', 0)} GiB")
        else:
            print(f"   Resource: 未配置")
        print()
    except Exception as e:
        print(f"⚠️  无法获取当前配置: {e}")
        print()

    print("1️⃣ 配置 Notebook Image")
    images = list_available_images(token, base_url)

    notebook_image = None
    if images:
        print(f"\n可用镜像 (共 {len(images)} 个):")
        for i, img in enumerate(images, 1):
            if 'tf2' in img.lower() or 'tensorflow-2' in img.lower():
                tag = "🔥 TF2"
            elif 'tf1' in img.lower() or 'tensorflow-1' in img.lower():
                tag = "TF1"
            else:
                tag = ""
            parts = img.split(':')
            if len(parts) >= 2:
                name = parts[-1].split('-')[0]
                print(f"   {i:2d}. {name:15s} {tag}")
            else:
                print(f"   {i:2d}. {img}")

        print()
        choice = input("选择镜像序号 (回车跳过): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(images):
            notebook_image = images[int(choice) - 1]
            print(f"✅ 已选择: {notebook_image}")
        else:
            print("⏭️  跳过镜像配置")
    else:
        print("❌ 无法获取镜像列表")

    print()
    print("2️⃣ 配置 Notebook Resource")
    print()

    cpu_input = input("CPU (cores, 默认 10): ").strip()
    cpu = int(cpu_input) if cpu_input.isdigit() else 10

    memory_input = input("Memory (GiB, 默认 40): ").strip()
    memory = int(memory_input) if memory_input.isdigit() else 40

    gpu_input = input("GPU (MIG GPU, 默认无): ").strip()
    mig_gpu = gpu_input if gpu_input else ""

    print()
    print(f"✅ 资源配置: CPU={cpu} cores, Memory={memory} GiB, GPU={mig_gpu if mig_gpu else 'None'}")
    print()

    print("📝 配置摘要:")
    if notebook_image:
        print(f"   Image: {notebook_image}")
    print(f"   Resource: CPU={cpu}, Memory={memory}, GPU={mig_gpu if mig_gpu else 'None'}")
    print()

    confirm = input("确认保存配置? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ 已取消")
        return False

    try:
        updates = {
            "notebook_resource": {
                "cpu": cpu, "memory": memory, "gpu": 0,
                "mig_gpu": mig_gpu, "gpuType": "", "replicas": 0,
            },
            "ps_resource": {
                "cpu": 0, "memory": 0, "gpu": 0,
                "mig_gpu": "", "gpuType": "", "replicas": 0,
            },
        }
        if notebook_image:
            updates["notebook_image"] = notebook_image
        api_request('PUT', f'/model/{model_id}/version/{version_id}', token, base_url, json=updates)
        print()
        print("✅ 配置保存成功!")
        return True
    except Exception as e:
        print()
        print(f"❌ 保存失败: {e}")
        return False


def direct_configure(model_id, version_id, token, base_url, image=None, cpu=10, memory=40, mig_gpu=""):
    print(f"🔧 配置 Notebook (model_id={model_id}, version_id={version_id})")
    updates = {
        "notebook_resource": {
            "cpu": cpu, "memory": memory, "gpu": 0,
            "mig_gpu": mig_gpu, "gpuType": "", "replicas": 0,
        },
        "ps_resource": {
            "cpu": 0, "memory": 0, "gpu": 0,
            "mig_gpu": "", "gpuType": "", "replicas": 0,
        },
    }
    if image:
        updates["notebook_image"] = image
    try:
        api_request('PUT', f'/model/{model_id}/version/{version_id}', token, base_url, json=updates)
        print("✅ 配置保存成功!")
        if image:
            print(f"   Image: {image}")
        print(f"   Resource: CPU={cpu}, Memory={memory}, GPU={mig_gpu if mig_gpu else 'None'}")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False


def cmd_configure(args):
    base_url, token = get_api_config()
    if args.interactive:
        success = interactive_configure(args.model_id, args.version_id, token, base_url)
    else:
        success = direct_configure(
            args.model_id, args.version_id, token, base_url,
            args.image, args.cpu, args.memory, args.mig_gpu
        )
    return 0 if success else 1


# ── CLI entry point ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='EGO Notebook 管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest='command', help='操作命令')
    subparsers.required = True

    # start
    p_start = subparsers.add_parser('start', help='启动 Notebook')
    p_start.add_argument('version_id', type=int, help='模型版本 ID')
    p_start.add_argument('--expiration-time', type=int, default=10800, help='过期时间（秒），默认 10800 (3小时)')
    p_start.add_argument('--wait', action='store_true', help='等待 notebook 启动完成')
    p_start.add_argument('--timeout', type=int, default=300, help='等待超时时间（秒），默认 300')
    p_start.set_defaults(func=cmd_start)

    # stop
    p_stop = subparsers.add_parser('stop', help='停止 Notebook')
    p_stop.add_argument('version_id', type=int, help='模型版本 ID')
    p_stop.add_argument('--force', action='store_true', help='跳过确认，直接停止')
    p_stop.set_defaults(func=cmd_stop)

    # list
    p_list = subparsers.add_parser('list', help='列出 Notebooks')
    p_list.add_argument('--status', help='按状态过滤 (running, closed, failed, etc.)')
    p_list.add_argument('--version-id', type=int, help='按版本 ID 过滤')
    p_list.add_argument('--model-id', type=int, help='按模型 ID 过滤')
    p_list.add_argument('--scope', type=int, default=2, help='范围: 1=所有人, 2=个人 (默认 2)')
    p_list.add_argument('--page-size', type=int, default=20, help='每页数量 (默认 20)')
    p_list.add_argument('--json', action='store_true', help='JSON 格式输出')
    p_list.set_defaults(func=cmd_list)

    # extend
    p_extend = subparsers.add_parser('extend', help='延长运行时间')
    p_extend.add_argument('version_id', type=int, help='模型版本 ID')
    p_extend.add_argument('--extend-time', type=int, required=True, help='延长时间（秒）')
    p_extend.set_defaults(func=cmd_extend)

    # configure
    p_conf = subparsers.add_parser('configure', help='配置镜像和资源')
    p_conf.add_argument('model_id', type=int, help='模型 ID')
    p_conf.add_argument('version_id', type=int, help='版本 ID')
    p_conf.add_argument('--interactive', '-i', action='store_true', help='交互式配置')
    p_conf.add_argument('--image', help='Notebook 镜像')
    p_conf.add_argument('--cpu', type=int, default=10, help='CPU cores (默认 10)')
    p_conf.add_argument('--memory', type=int, default=40, help='Memory GiB (默认 40)')
    p_conf.add_argument('--mig-gpu', default='', help='MIG GPU')
    p_conf.set_defaults(func=cmd_configure)

    args = parser.parse_args()

    try:
        return args.func(args)
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ 错误: {error_msg}", file=sys.stderr)

        if 'set notebook image' in error_msg or 'set notebook resource' in error_msg:
            print(f"\n💡 提示: 版本未配置 Notebook Image 或 Resource", file=sys.stderr)
            print(f"   python3 notebook.py configure <model_id> <version_id> --interactive", file=sys.stderr)
        elif 'notebook running' in error_msg:
            print(f"\n💡 提示: 已有运行中的 notebook，请先停止", file=sys.stderr)
            print(f"   python3 notebook.py stop <version_id> --force", file=sys.stderr)

        return 1


if __name__ == '__main__':
    sys.exit(main())
