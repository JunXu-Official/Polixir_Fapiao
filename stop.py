#encoding: gbk
import subprocess
import os
import time

# 仓库路径（本机路径）
# repo_path = r"D:\polixir\algorithm\Polixir_Fapiao"
# Python 服务启动脚本
service_script = "start.py"
env = "jsbsim"

current_pid = os.getpid()
# 使用 taskkill 过滤掉当前 PID
close_cmd = f'taskkill /f /im python.exe /fi "PID ne {current_pid}"'
sleep_seconds = 3
try:
    subprocess.run(close_cmd, shell=True, check=True)
    print("本机：其他 Python 进程已关闭")
except subprocess.CalledProcessError:
    print("本机：关闭进程失败或进程不存在")

work_dir = os.path.dirname(os.path.abspath(__file__))
subprocess.Popen(f'cmd /c start cmd /k "conda activate {env} && python {service_script}"', cwd=work_dir, shell=True)

