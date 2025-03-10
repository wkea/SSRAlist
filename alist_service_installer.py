import os
import sys
import shutil
import subprocess
import argparse
import ctypes
import tempfile
import traceback
import time
import socket
import winreg
from colorama import init, Fore, Style

# 初始化colorama以支持彩色输出
init()

def print_banner():
    """打印程序字符画横幅"""
    banner = f"""
{Fore.CYAN}  ____  ____   ____      _     _      ___  ____  _____ 
 / ___|/ ___| |  _ \\    / \\   | |    |_ _|/ ___||_   _|
 \\___ \\\\___ \\ | |_) |  / _ \\  | |     | | \\___ \\  | |  
  ___) |___) ||  _ <  / ___ \\ | |___  | |  ___) | | |  
 |____/|____/ |_| \\_\\/_/   \\_\\|_____||___||____/  |_|  
                                                       
                                                       {Fore.YELLOW}---[ALIST安装器]ByWKEA{Style.RESET_ALL}
"""
    print(banner)
    print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}欢迎使用 Alist Windows 服务安装工具{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
    print()

def print_warning():
    """打印警告信息"""
    print(f"\n{Fore.YELLOW}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.RED}【警告】Alist将被注册为Windows系统服务，并设置为开机自启动。{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}如需卸载，请按以下步骤操作：{Style.RESET_ALL}")
    print(f"1. 以管理员身份打开命令提示符")
    print(f"2. 输入命令: {Fore.GREEN}sc stop AlistService{Style.RESET_ALL} (停止服务)")
    print(f"3. 输入命令: {Fore.GREEN}sc delete AlistService{Style.RESET_ALL} (删除服务)")
    print(f"4. 删除安装目录: {Fore.GREEN}rmdir /s /q \"C:\\Program Files\\Alist\"{Style.RESET_ALL}")
    print(f"\n或者使用本工具的{Fore.GREEN}--force{Style.RESET_ALL}参数重新安装来覆盖现有安装")
    print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
    
    confirm = input(f"{Fore.YELLOW}确认继续安装? (y/n): {Style.RESET_ALL}")
    if confirm.lower() != 'y':
        print(f"{Fore.RED}安装已取消{Style.RESET_ALL}")
        sys.exit(0)
    print()

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def resource_path(relative_path):
    """获取资源的绝对路径，适用于PyInstaller打包后的情况"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 创建一个临时socket连接以获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        # 如果失败，尝试其他方法
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except:
            return "localhost"

def create_desktop_shortcut(url, shortcut_name="Alist文件列表"):
    """在桌面创建URL快捷方式"""
    try:
        # 获取桌面路径
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        desktop_path = winreg.QueryValueEx(key, "Desktop")[0]
        winreg.CloseKey(key)
        
        # 创建.url文件
        shortcut_path = os.path.join(desktop_path, f"{shortcut_name}.url")
        
        with open(shortcut_path, "w") as f:
            f.write("[InternetShortcut]\n")
            f.write(f"URL={url}\n")
            f.write("IconIndex=0\n")
            # 可以添加图标
            # f.write(f"IconFile=C:\\Path\\To\\Icon.ico\n")
        
        print(f"{Fore.GREEN}已在桌面创建快捷方式: {shortcut_path}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}创建桌面快捷方式时出错: {str(e)}{Style.RESET_ALL}")
        return False

def add_to_path(directory):
    """将目录添加到系统环境变量PATH中"""
    try:
        print(f"正在将 {directory} 添加到系统环境变量...")
        
        # 打开系统环境变量注册表键
        env_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Environment", 
                               0, 
                               winreg.KEY_READ | winreg.KEY_WRITE)
        
        # 获取当前PATH值
        try:
            path_value, _ = winreg.QueryValueEx(env_key, "PATH")
        except:
            path_value = ""
        
        # 检查目录是否已在PATH中
        path_dirs = [dir.lower() for dir in path_value.split(';') if dir]
        if directory.lower() not in path_dirs:
            # 添加目录到PATH
            new_path = f"{path_value};{directory}" if path_value else directory
            winreg.SetValueEx(env_key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(env_key)
            
            # 广播环境变量更改消息
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x001A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 
                SMTO_ABORTIFHUNG, 5000, ctypes.byref(ctypes.c_ulong()))
            
            if result == 0:
                print(f"{Fore.YELLOW}环境变量已更新，但可能需要重启命令提示符或计算机才能生效{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}环境变量已成功更新{Style.RESET_ALL}")
            
            return True
        else:
            winreg.CloseKey(env_key)
            print(f"{Fore.YELLOW}目录 {directory} 已经在PATH环境变量中{Style.RESET_ALL}")
            return True
    except Exception as e:
        print(f"{Fore.RED}添加到环境变量时出错: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()
        return False

def check_existing_installation(install_dir, service_name, nssm_path=None):
    """检查是否已存在安装及服务"""
    alist_exists = os.path.exists(os.path.join(install_dir, "alist.exe"))
    
    # 检查服务是否存在
    service_exists = False
    try:
        result = subprocess.run(["sc", "query", service_name], 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        service_exists = result.returncode == 0
    except:
        # 如果sc命令失败，尝试使用nssm检查
        if nssm_path and os.path.exists(nssm_path):
            try:
                result = subprocess.run([nssm_path, "status", service_name], 
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                service_exists = "SERVICE_" in result.stdout.decode('gbk', errors='ignore')
            except:
                pass
    
    return alist_exists, service_exists

def remove_existing_installation(install_dir, service_name, nssm_path=None):
    """移除已存在的安装及服务"""
    success = True
    
    # 尝试使用系统SC命令停止并删除服务
    try:
        print(f"{Fore.YELLOW}尝试使用SC命令停止并删除服务 '{service_name}'...{Style.RESET_ALL}")
        subprocess.run(["sc", "stop", service_name], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)
        subprocess.run(["sc", "delete", service_name], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
    except Exception as e:
        print(f"{Fore.RED}使用SC命令移除服务时出错: {str(e)}{Style.RESET_ALL}")
    
    # 如果服务存在且有nssm路径，再尝试使用nssm停止并移除服务
    if nssm_path and os.path.exists(nssm_path):
        try:
            print(f"{Fore.YELLOW}尝试使用NSSM停止并移除现有服务 '{service_name}'...{Style.RESET_ALL}")
            # 停止服务
            subprocess.run([nssm_path, "stop", service_name], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)
            # 移除服务
            subprocess.run([nssm_path, "remove", service_name, "confirm"], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # 等待一会儿确保服务已移除
            time.sleep(2)
        except Exception as e:
            print(f"{Fore.RED}使用NSSM移除服务时出错: {str(e)}{Style.RESET_ALL}")
            success = False
    
    # 确认服务是否已删除
    try:
        check_result = subprocess.run(["sc", "query", service_name], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check_result.returncode == 0:
            print(f"{Fore.RED}警告: 服务 '{service_name}' 可能未完全删除{Style.RESET_ALL}")
    except:
        pass
    
    # 移除文件
    try:
        if os.path.exists(os.path.join(install_dir, "alist.exe")):
            print(f"{Fore.YELLOW}正在删除现有的 alist.exe...{Style.RESET_ALL}")
            os.remove(os.path.join(install_dir, "alist.exe"))
        
        if os.path.exists(os.path.join(install_dir, "nssm.exe")):
            print(f"{Fore.YELLOW}正在删除现有的 nssm.exe...{Style.RESET_ALL}")
            os.remove(os.path.join(install_dir, "nssm.exe"))
    except Exception as e:
        print(f"{Fore.RED}删除文件时出错: {str(e)}{Style.RESET_ALL}")
        success = False
    
    return success

def extract_files(install_dir):
    """提取alist.exe和nssm.exe到安装目录"""
    try:
        # 创建安装目录（如果不存在）
        os.makedirs(install_dir, exist_ok=True)
        
        # 复制alist.exe到安装目录
        alist_src = resource_path("alist.exe")
        alist_dst = os.path.join(install_dir, "alist.exe")
        shutil.copy2(alist_src, alist_dst)
        print(f"{Fore.GREEN}已复制 alist.exe 到 {alist_dst}{Style.RESET_ALL}")
        
        # 复制nssm.exe到安装目录
        nssm_src = resource_path("nssm.exe")
        nssm_dst = os.path.join(install_dir, "nssm.exe")
        shutil.copy2(nssm_src, nssm_dst)
        print(f"{Fore.GREEN}已复制 nssm.exe 到 {nssm_dst}{Style.RESET_ALL}")
        
        return alist_dst, nssm_dst
    except Exception as e:
        print(f"{Fore.RED}提取文件时出错: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()
        return None, None

def initialize_alist(alist_path, install_dir):
    """初始化Alist（生成配置文件）"""
    try:
        print(f"{Fore.YELLOW}正在初始化Alist...{Style.RESET_ALL}")
        # 切换到安装目录
        os.chdir(install_dir)
        
        # 运行alist命令以初始化
        init_process = subprocess.Popen([alist_path, "admin", "random"], 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 捕获输出以获取密码
        password = None
        try:
            for line in init_process.stdout:
                line_str = line.decode('utf-8', errors='ignore')
                if "password" in line_str.lower():
                    password = line_str.strip()
                    print(f"{Fore.GREEN}{line_str.strip()}{Style.RESET_ALL}")
                else:
                    print(line_str.strip())
        except:
            pass
        
        # 等待一段时间让配置文件生成
        time.sleep(3)
        init_process.terminate()  # 终止进程
        
        print(f"{Fore.GREEN}Alist初始化完成{Style.RESET_ALL}")
        return True, password
    except Exception as e:
        print(f"{Fore.RED}初始化Alist时出错: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()
        return False, None

def install_service(alist_path, nssm_path, install_dir, service_name="AlistService"):
    """使用nssm安装alist作为系统服务"""
    try:
        # 确保服务不存在
        try:
            subprocess.run(["sc", "stop", service_name], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["sc", "delete", service_name], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            pass
        
        # 再次使用nssm确保服务不存在
        subprocess.run([nssm_path, "stop", service_name], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run([nssm_path, "remove", service_name, "confirm"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(1)
        
        # 安装新服务
        print(f"{Fore.YELLOW}正在安装服务 '{service_name}'...{Style.RESET_ALL}")
        cmd_install = [nssm_path, "install", service_name, alist_path, "server"]
        result = subprocess.run(cmd_install, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            error_msg = result.stderr.decode('gbk', errors='ignore')
            print(f"{Fore.RED}安装服务失败: {error_msg}{Style.RESET_ALL}")
            return False
        
        # 设置服务描述
        subprocess.run([nssm_path, "set", service_name, "Description", "Alist文件列表服务"])
        
        # 设置服务工作目录
        subprocess.run([nssm_path, "set", service_name, "AppDirectory", install_dir])
        
        # 设置服务失败后自动重启
        subprocess.run([nssm_path, "set", service_name, "AppExit", "Default", "Restart"])
        
        # 设置服务启动参数
        subprocess.run([nssm_path, "set", service_name, "AppParameters", "server"])
        
        # 设置超时时间
        subprocess.run([nssm_path, "set", service_name, "AppStopMethodConsole", "1800000"])
        
        # 明确设置服务以LocalSystem账户运行（具有最高权限）
        print(f"{Fore.YELLOW}正在设置服务权限为系统账户...{Style.RESET_ALL}")
        subprocess.run([nssm_path, "set", service_name, "ObjectName", "LocalSystem"])
        
        # 设置服务的启动类型为自动
        subprocess.run([nssm_path, "set", service_name, "Start", "SERVICE_AUTO_START"])
        
        # 给予服务显示桌面交互的权限
        subprocess.run([nssm_path, "set", service_name, "Type", "SERVICE_INTERACTIVE_PROCESS"])
        
        print(f"{Fore.YELLOW}服务'{service_name}'安装成功，正在启动...{Style.RESET_ALL}")
        
        # 赋予安装目录完全权限
        try:
            print(f"{Fore.YELLOW}正在设置目录权限...{Style.RESET_ALL}")
            subprocess.run(["icacls", install_dir, "/grant", "Administrators:(OI)(CI)F", "/T"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["icacls", install_dir, "/grant", "SYSTEM:(OI)(CI)F", "/T"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"{Fore.YELLOW}设置目录权限时出错: {str(e)}{Style.RESET_ALL}")
        
        # 启动服务
        start_result = subprocess.run([nssm_path, "start", service_name], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务启动
        for i in range(5):
            print(f"{Fore.YELLOW}等待服务启动中... ({i+1}/5){Style.RESET_ALL}")
            time.sleep(1)
        
        # 使用SC命令检查服务状态
        service_running = False
        try:
            sc_result = subprocess.run(["sc", "query", service_name], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sc_output = sc_result.stdout.decode('gbk', errors='ignore')
            service_running = "RUNNING" in sc_output
            if service_running:
                print(f"{Fore.GREEN}服务状态检查: 运行中{Style.RESET_ALL}")
        except:
            pass
        
        # 使用NSSM检查服务状态(备用方法)
        if not service_running:
            try:
                status_result = subprocess.run([nssm_path, "status", service_name],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                status_output = status_result.stdout.decode('gbk', errors='ignore')
                # 移除所有空格后检查
                clean_output = status_output.replace(" ", "")
                service_running = "SERVICE_RUNNING" in clean_output or "RUNNING" in clean_output
                if service_running:
                    print(f"{Fore.GREEN}服务状态检查(NSSM): 运行中{Style.RESET_ALL}")
            except:
                pass
        
        if service_running:
            print(f"{Fore.GREEN}Alist服务 '{service_name}' 已成功运行{Style.RESET_ALL}")
            return True
        else:
            if start_result.returncode != 0:
                error_msg = start_result.stderr.decode('gbk', errors='ignore')
                print(f"{Fore.RED}启动服务失败: {error_msg}{Style.RESET_ALL}")
            else:
                # 尝试用不同的命令再次启动服务
                try:
                    print(f"{Fore.YELLOW}尝试使用NET START命令启动服务...{Style.RESET_ALL}")
                    subprocess.run(["net", "start", service_name],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    time.sleep(2)
                    # 再次检查状态
                    sc_result = subprocess.run(["sc", "query", service_name], 
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    sc_output = sc_result.stdout.decode('gbk', errors='ignore')
                    if "RUNNING" in sc_output:
                        print(f"{Fore.GREEN}使用net start成功启动Alist服务{Style.RESET_ALL}")
                        return True
                except:
                    pass
                
            print(f"{Fore.YELLOW}服务安装成功但状态检查失败，可能仍在启动中{Style.RESET_ALL}")
            
            # 即使状态检查失败，但如果服务已安装，也认为基本成功
            return True
    except Exception as e:
        print(f"{Fore.RED}安装服务时出错: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()
        return False

def get_admin_password(install_dir, init_password=None):
    """尝试从data/config.json获取管理员密码"""
    if init_password:
        return init_password
    
    try:
        import json
        config_path = os.path.join(install_dir, "data", "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if "password" in config:
                return config.get("password")
    except Exception as e:
        print(f"{Fore.RED}读取配置文件时出错: {str(e)}{Style.RESET_ALL}")
    
    # 尝试从运行alist admin info命令获取
    try:
        alist_path = os.path.join(install_dir, "alist.exe")
        if os.path.exists(alist_path):
            print(f"{Fore.YELLOW}尝试从命令行获取管理员密码...{Style.RESET_ALL}")
            info_process = subprocess.Popen([alist_path, "admin", "info"], 
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         cwd=install_dir)
            for line in info_process.stdout:
                line_str = line.decode('utf-8', errors='ignore')
                if "password" in line_str.lower():
                    info_process.terminate()
                    return line_str.strip()
            info_process.terminate()
    except:
        pass
    
    return f"{Fore.YELLOW}未能获取，请查看安装目录下的data/config.json文件或运行'alist.exe admin info'命令获取{Style.RESET_ALL}"

def main():
    parser = argparse.ArgumentParser(description="Alist Windows服务安装工具")
    parser.add_argument("--install-dir", type=str, default="C:\\Program Files\\Alist",
                       help="Alist安装目录（默认: C:\\Program Files\\Alist）")
    parser.add_argument("--service-name", type=str, default="AlistService",
                       help="Windows服务名称（默认: AlistService）")
    parser.add_argument("--force", action="store_true",
                       help="强制重新安装，即使已存在")
    parser.add_argument("--no-shortcut", action="store_true",
                       help="不创建桌面快捷方式")
    parser.add_argument("--no-path", action="store_true",
                       help="不添加到系统环境变量PATH")
    parser.add_argument("--port", type=int, default=5244,
                       help="Alist服务端口（默认: 5244）")
    parser.add_argument("--no-confirm", action="store_true",
                       help="跳过确认提示直接安装")
    
    args = parser.parse_args()
    
    # 打印横幅
    print_banner()
    
    # 检查管理员权限
    if not is_admin():
        print(f"{Fore.RED}需要管理员权限来安装系统服务。请以管理员身份运行此程序。{Style.RESET_ALL}")
        input("按任意键退出...")
        sys.exit(1)
    
    # 显示警告，除非使用了--no-confirm参数
    if not args.no_confirm:
        print_warning()
    
    # 检查是否已安装
    print(f"{Fore.CYAN}检查现有安装...{Style.RESET_ALL}")
    alist_exists, service_exists = check_existing_installation(args.install_dir, args.service_name)
    
    # 如果已存在或强制重新安装
    if alist_exists or service_exists or args.force:
        if args.force:
            print(f"{Fore.YELLOW}已指定强制重新安装，正在清理现有安装...{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}发现现有安装，正在清理...{Style.RESET_ALL}")
        
        # 临时提取nssm.exe用于服务清理
        temp_dir = tempfile.mkdtemp()
        nssm_src = resource_path("nssm.exe")
        temp_nssm = os.path.join(temp_dir, "nssm.exe")
        shutil.copy2(nssm_src, temp_nssm)
        
        remove_existing_installation(args.install_dir, args.service_name, temp_nssm)
        
        # 清理临时文件
        try:
            os.remove(temp_nssm)
            os.rmdir(temp_dir)
        except:
            pass
    
    print(f"{Fore.CYAN}开始安装Alist到 {args.install_dir}...{Style.RESET_ALL}")
    
    # 提取文件
    alist_path, nssm_path = extract_files(args.install_dir)
    if not alist_path or not nssm_path:
        print(f"{Fore.RED}提取文件失败，安装终止。{Style.RESET_ALL}")
        input("按任意键退出...")
        sys.exit(1)
    
    # 初始化Alist
    init_success, init_password = initialize_alist(alist_path, args.install_dir)
    
    # 安装服务
    success = install_service(alist_path, nssm_path, args.install_dir, args.service_name)
    
    # 添加到环境变量PATH
    path_added = False
    if not args.no_path:
        path_added = add_to_path(args.install_dir)
    
    admin_password = get_admin_password(args.install_dir, init_password)
    
    # 获取IP地址
    local_ip = get_local_ip()
    alist_url = f"http://{local_ip}:{args.port}"
    localhost_url = f"http://localhost:{args.port}"
    
    if success:
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Alist已成功安装为Windows服务!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"- 安装目录: {Fore.YELLOW}{args.install_dir}{Style.RESET_ALL}")
        print(f"- 服务名称: {Fore.YELLOW}{args.service_name}{Style.RESET_ALL}")
        print(f"- 本机访问地址: {Fore.GREEN}{localhost_url}{Style.RESET_ALL}")
        print(f"- 局域网访问地址: {Fore.GREEN}{alist_url}{Style.RESET_ALL}")
        print(f"- 默认管理员账号: {Fore.YELLOW}admin{Style.RESET_ALL}")
        print(f"- 默认管理员密码: {Fore.GREEN}{admin_password}{Style.RESET_ALL}")
        
        if path_added:
            print(f"- {Fore.CYAN}Alist已添加到系统环境变量，您可以在命令行中直接使用alist命令{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}注意：可能需要重新打开命令提示符才能生效{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        
        # 创建桌面快捷方式
        if not args.no_shortcut:
            create_desktop_shortcut(localhost_url, "Alist文件列表")
        
        print(f"\n{Fore.YELLOW}提示: 如果服务未自动启动，您可以在命令提示符中运行以下命令手动启动:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}net start {args.service_name}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}卸载指南:{Style.RESET_ALL}")
        print(f"1. 以管理员身份打开命令提示符")
        print(f"2. 输入命令: {Fore.GREEN}sc stop {args.service_name}{Style.RESET_ALL}")
        print(f"3. 输入命令: {Fore.GREEN}sc delete {args.service_name}{Style.RESET_ALL}")
        print(f"4. 删除安装目录: {Fore.GREEN}rmdir /s /q \"{args.install_dir}\"{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Alist常用命令:{Style.RESET_ALL}")
        print(f"- 查看管理员信息: {Fore.GREEN}alist admin info{Style.RESET_ALL}")
        print(f"- 重置管理员密码: {Fore.GREEN}alist admin random --data \"C:\Program Files\Alist\data\"{Style.RESET_ALL}")
        print(f"- 手动启动服务: {Fore.GREEN}alist server{Style.RESET_ALL}")
        print(f"- 手动修改密码: {Fore.GREEN}alist admin set YOUR_NEW_PASSWORD --data \"C:\Program Files\Alist\data\"{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}如果遇到:“token is invalidated”相关错误，请尝试在 后面添加参数 【--data \"C:\Program Files\Alist\data\"】{Style.RESET_ALL}")
        print(f"- 查看帮助: {Fore.GREEN}alist --help{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Alist服务安装过程中遇到问题，但文件已经复制到安装目录。{Style.RESET_ALL}")
        print(f"您可以尝试手动运行以下命令启动服务:")
        print(f"{Fore.GREEN}cd /d {args.install_dir}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{os.path.join(args.install_dir, 'alist.exe')} server{Style.RESET_ALL}")
    
    input(f"\n{Fore.YELLOW}按任意键退出...{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 
