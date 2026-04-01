import subprocess
import os
import sys

# ── 从环境变量读取配置 ──────────────────────────────────────────────
WORKER_DOMAIN = os.environ.get("WORKER_DOMAIN")
UPLOAD_TOKEN  = os.environ.get("UPLOAD_TOKEN")

if not WORKER_DOMAIN or not UPLOAD_TOKEN:
    print("❌ 错误：某个环境变量没有设置。")
    sys.exit(1)

# ── 仓库根目录（脚本所在目录的上级，即仓库根） ──────────────────────
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 待上传的规则文件列表 ────────────────────────────────────────────
RULES = [
    os.path.join(REPO_ROOT, "Rules", "Android",   "Android_DNS_Rules.txt"),
    os.path.join(REPO_ROOT, "Rules", "iOS",        "iOS_DNS_Rules.txt"),
    os.path.join(REPO_ROOT, "Rules", "Universal",  "Universal_DNS_Rules.txt"),
]

# ── 上传函数 ────────────────────────────────────────────────────────
def upload_file(file_path: str) -> bool:
    file_name = os.path.basename(file_path)

    if not os.path.isfile(file_path):
        print(f"⚠️  跳过（文件不存在）：{file_path}")
        return False

    url = (
        f"https://{WORKER_DOMAIN}/config/upload_config"
        f"/adguardhome_customized_rules/{file_name}"
        f"?token={UPLOAD_TOKEN}"
    )

    cmd = [
        "curl",
        "--silent",        # 不显示进度条
        "--show-error",    # 但仍显示错误信息
        "--fail",          # HTTP 错误时返回非零退出码
        "-X", "POST",
        "--data-binary", f"@{file_path}",
        url,
    ]

    print(f"🚀 正在上传：{file_name}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ 上传成功：{file_name}")
        if result.stdout.strip():
            print(f"   对端响应：{result.stdout.strip()}")
        return True
    else:
        print(f"❌ 上传失败：{file_name}")
        print(f"   错误信息：{result.stderr.strip()}")
        return False


# ── 主流程 ──────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  AdGuardHome DNS 规则同步脚本")
    print("=" * 50)

    success_count = 0
    fail_count    = 0

    for rule_file in RULES:
        if upload_file(rule_file):
            success_count += 1
        else:
            fail_count += 1

    print("-" * 50)
    print(f"📊 完成：成功 {success_count} 个 / 失败 {fail_count} 个")

    if fail_count > 0:
        sys.exit(1)  # 有失败时返回非零，让 Actions 标记为失败


if __name__ == "__main__":
    main()
