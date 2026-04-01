import subprocess
import os
import sys

# ── 从环境变量读取配置 ──────────────────────────────────────────────
_HOST  = os.environ.get("SYNC_HOST")
_TOKEN = os.environ.get("SYNC_TOKEN")

if not _HOST or not _TOKEN:
    print("❌ 错误：必要的环境变量未设置，请检查配置。")
    sys.exit(1)

# ── 仓库根目录（脚本位于 Scripts/，上一级即为仓库根） ───────────────
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 待同步的规则文件列表 ────────────────────────────────────────────
RULES = [
    os.path.join(REPO_ROOT, "Rules", "Android",   "Android_DNS_Rules.txt"),
    os.path.join(REPO_ROOT, "Rules", "iOS",        "iOS_DNS_Rules.txt"),
    os.path.join(REPO_ROOT, "Rules", "Universal",  "Universal_DNS_Rules.txt"),
]

# ── 同步函数 ────────────────────────────────────────────────────────
def sync_file(file_path: str) -> bool:
    file_name = os.path.basename(file_path)

    if not os.path.isfile(file_path):
        print(f"⚠️  跳过（文件不存在）：{file_path}")
        return False

    endpoint = (
        f"https://{_HOST}/config/upload_config"
        f"/adguardhome_customized_rules/{file_name}"
        f"?token={_TOKEN}"
    )

    cmd = [
        "curl",
        "--silent",
        "--show-error",
        "--fail",
        "-X", "POST",
        "--data-binary", f"@{file_path}",
        endpoint,
    ]

    print(f"🔄 正在同步：{file_name}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ 同步成功：{file_name}")
        if result.stdout.strip():
            print(f"   响应：{result.stdout.strip()}")
        return True
    else:
        print(f"❌ 同步失败：{file_name}")
        print(f"   错误：{result.stderr.strip()}")
        return False


# ── 主流程 ──────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  DNS Rules Sync")
    print("=" * 50)

    success_count = 0
    fail_count    = 0

    for rule_file in RULES:
        if sync_file(rule_file):
            success_count += 1
        else:
            fail_count += 1

    print("-" * 50)
    print(f"📊 完成：成功 {success_count} 个 / 失败 {fail_count} 个")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
