import subprocess
import sys

# 远程 Windows 内网 IP 列表
remote_ips = []
try:
    with open("ip_list_win_all.txt", "r") as f:
        for line in f:
            ip = line.strip()
            if ip:
                remote_ips.append(ip)
except FileNotFoundError:
    print("Error: ip_list_win_all.txt not found.")
    sys.exit(1)
except Exception as e:
    print(f"Error reading ip_list_win_all.txt: {e}")
    sys.exit(1)

print("待同步的远程 IP:", remote_ips)
# PsExec 路径
psexec_path = r"D:\tools\PsExec.exe"
# 目标机器的用户名和密码
username = "polixir"
password = "polixir"
# 目标机器的待同步代码位置
repo_path = r"D:\train"
# python环境激活
env_name = "py38"
# python 服务启动训练脚本
service_script = "control_server.py"
work_dir = os.path.dirname(os.path.abspath(__file__))

# 循环每台远程机器
for ip in remote_ips:
    print(f"\n处理 {ip} ...")
    # 关闭进行和同步代码，执行2次，确保同步完毕！
    for _ in range(2):
        # 1、关闭 Python 和仿真进程
        close_cmd = f'{psexec_path} \\\\{ip} -u {username} -p {password} cmd /c "taskkill /f /im python.exe&& taskkill /f /im sim.exe"'
        try:
            subprocess.run(close_cmd, shell=True, check=True)
            print(f"{ip}：Python 和仿真进程已关闭")
        except subprocess.CalledProcessError:
            print(f"{ip}：关闭进程失败或进程不存在")
    for _ in range(2):
        # 2、同步代码
        git_cmd = f'{psexec_path} \\\\{ip} -u {username} -p {password} cmd /c "cd {repo_path} && git pull https://github.com/your_username/your_repository.git master"'  # 你的git仓库的URL地址
        try:
            subprocess.run(git_cmd, shell=True, check=True)
            print(f"{ip}：代码同步完成")
        except subprocess.CalledProcessError:
            print(f"{ip}：代码同步失败")

    # 启动 Python 服务
    subprocess.Popen(f'cmd /c start cmd /k "conda activate {env} && python {service_script}"', cwd=work_dir, shell=True)
