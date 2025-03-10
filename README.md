# 🌟 Alist Windows 服务安装工具

Alist Windows 服务安装工具是一个便捷的安装程序，帮助用户在Windows系统上快速安装和配置Alist服务。该工具支持将Alist注册为Windows服务，并提供了简单的卸载和管理方法。

## 📖 项目简介

Alist是一款强大的文件列表程序，支持多种存储服务和云盘，包括但不限于：
- 本地存储
- 阿里云盘
- OneDrive
- Google Drive
- 百度网盘
- 天翼云盘
- 夸克网盘
- S3兼容存储
- WebDAV
- FTP/SFTP

通过本安装工具，您可以在Windows系统上一键部署Alist，并将其设置为系统服务，实现开机自启动和后台运行，无需手动管理进程。

## 💻 系统要求

- Windows 7/8/10/11 或 Windows Server 2012/2016/2019/2022
- 管理员权限（安装服务必需）
- 至少100MB可用磁盘空间
- .NET Framework 4.5或更高版本（通常已预装在Windows系统中）
- 开放的5244端口（Alist默认Web端口）

## 🛠️ 安装步骤

1. **准备文件**：
   - 下载`alist_service_installer.exe`安装程序
   - 程序会自动包含`alist.exe`和`nssm.exe`，无需单独下载

2. **运行安装程序**：
   - 右键点击`alist_service_installer.exe`
   - 选择"以管理员身份运行"
   - 如果出现UAC提示，请点击"是"允许程序运行

3. **配置安装选项**：
   安装程序支持以下命令行参数：
   ```
   --install-dir "D:\MyAlist"    # 自定义安装目录
   --service-name "MyAlist"      # 自定义服务名称
   --port 5244                   # 设置Alist监听端口
   --force                       # 强制重新安装
   --no-shortcut                 # 不创建桌面快捷方式
   --no-path                     # 不添加到系统环境变量PATH
   --no-confirm                  # 跳过确认提示直接安装
   ```

   例如：`alist_service_installer.exe --install-dir "D:\MyAlist" --port 8080`

4. **确认安装**：
   - 程序会显示安装信息和警告
   - 输入"y"确认安装
   - 安装过程会自动执行，包括：
     * 释放文件到安装目录
     * 初始化Alist配置
     * 注册Windows服务
     * 添加环境变量
     * 创建桌面快捷方式

5. **完成安装**：
   - 安装完成后，程序会显示访问地址和管理员密码
   - 请保存好管理员密码，这是访问Alist管理界面的唯一凭证

## 🚀 使用说明

### 基本访问
- 安装完成后，打开浏览器访问 `http://localhost:5244` 即可使用Alist
- 首次访问管理界面的账号为 `admin`，密码为安装程序显示的随机密码

### 服务管理
- **启动服务**：`net start AlistService`
- **停止服务**：`net stop AlistService`
- **重启服务**：`net stop AlistService && net start AlistService`
- **查看服务状态**：`sc query AlistService`

### 命令行操作
Alist提供了丰富的命令行功能，常用命令如下：
- **查看管理员信息**：`alist admin info`
- **重置管理员密码**：`alist admin reset`
- **手动启动服务**：`alist server`
- **查看帮助**：`alist --help`
- **查看版本**：`alist version`
- **创建新用户**：`alist admin add [username] [password] [2fa]`

### 文件位置
- **可执行文件**：`C:\Program Files\Alist\alist.exe`
- **配置文件**：`C:\Program Files\Alist\data\config.json`
- **数据库文件**：`C:\Program Files\Alist\data\data.db`
- **日志文件**：`C:\Program Files\Alist\data\log\xxx.log`

## 🔄 更新Alist

要更新Alist到最新版本，您可以：

1. 下载最新版本的`alist.exe`
2. 停止Alist服务：`sc stop AlistService`
3. 替换安装目录中的`alist.exe`
4. 启动Alist服务：`sc start AlistService`


## 💻自行编译安装脚本

1. 下载最新版本的`alist.exe`
2. 添加到项目的根目录 
3. 自行使用“PyInstaller” 打包 `pyinstaller --onefile --add-data "alist.exe;." --add-data "nssm.exe;." --uac-admin --icon=alist_icon.ico --versi
on-file=version_info.txt alist_service_installer.py`


## 🗑️ 卸载指南

1. 以管理员身份打开命令提示符。
2. 输入命令：`sc stop AlistService`（停止服务）。
3. 输入命令：`sc delete AlistService`（删除服务）。
4. 删除安装目录：`rmdir /s /q "C:\Program Files\Alist"`。

## ❓ 常见问题

- **服务未启动**：请确保以管理员身份运行安装程序，并检查服务状态。
- **无法访问Web界面**：检查防火墙设置，确保端口5244未被阻止。

## 🤝 贡献指南

欢迎对本项目进行贡献！请通过GitHub提交Pull Request或Issue。

## 📬 联系信息

如有任何问题或建议，请联系开发者：WKEA 
