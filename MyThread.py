from PyQt6 import QtCore
import time,os, asyncio, re, requests
import win32gui
import win32con
import win32api
import subprocess
import configparser
import win32process
import psutil  # 用于获取进程信息
from aiohttp import web



class SubWorkerThread(QtCore.QThread):

    msg = QtCore.pyqtSignal(str)

    def __init__(self, data: dict):
        super(SubWorkerThread, self).__init__()
        self.data = data
        self.running = True

    def 鼠标点击(self, hwnd, x=0, y=0):
        rect = win32gui.GetWindowRect(hwnd)
        if x == 0 or y == 0:
            x = (rect[0] + rect[2]) // 2  # 窗口中心点的 x 坐标
            y = (rect[1] + rect[3]) // 2  # 窗口中心点的 y 坐标
            point = win32api.MAKELONG(x - rect[0], y - rect[1])
        else:
            point = win32api.MAKELONG(x, y)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)

    def enum_windows_find(self, hwnd, lparam):
        '''依据窗口标题 和窗口类名称 查询窗口'''
        windows_title = win32gui.GetWindowText(hwnd)
        windows_class = win32gui.GetClassName(hwnd)
        if lparam[0] in windows_title and lparam[1].upper() in windows_class.upper():
            lparam[2].append(hwnd)

    def enum_child_windows_find(self, hwnd, param):
        '''依据主窗口handle, 查询 标题为param[0]的子窗口 赋值到param[1]'''
        window_title = win32gui.GetWindowText(hwnd)
        window_classname = win32gui.GetClassName(hwnd)
        #print(f"子窗口句柄: {hwnd}, 标题: {window_title}, 类名：{window_classname}")
        if param[0] in window_title:
            #print(f"子窗口句柄: {hwnd}, 标题: {window_title}, 类名：{window_classname}")
            param[2].append(hwnd)

    def 点击确认信息(self):
        确认信息 = []
        while not len(确认信息):
            lparam = [f'确认信息', '#32770', 确认信息]
            win32gui.EnumWindows(self.enum_windows_find, lparam)
            确认信息 = lparam[2]
            if len(确认信息):
                win32gui.PostMessage(确认信息[0], win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(确认信息[0], win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            time.sleep(0.5)

    def 点击提示信息(self):
        确认信息 = []
        # GOM 和领风在这里不同 GOM 清理数据 是'提示信息' 翎风是 '完成'
        while not len(确认信息):
            lparam_gom = [f'提示信息', '#32770', 确认信息]
            win32gui.EnumWindows(self.enum_windows_find, lparam_gom)
            确认信息_gom = lparam_gom[2]
            lparam_lf = [f'完成', '#32770', 确认信息]
            win32gui.EnumWindows(self.enum_windows_find, lparam_lf)
            确认信息_lf = lparam_lf[2]
            if len(确认信息_gom):
                确认信息 = 确认信息_gom
            if len(确认信息_lf):
                确认信息 = 确认信息_lf
            if len(确认信息):
                win32gui.PostMessage(确认信息[0], win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(确认信息[0], win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            time.sleep(0.5)

    def 点击数据合并完成(self):
        数据合并完成 = []
        lparam = [f'数据合并完成', '#32770', 数据合并完成]
        win32gui.EnumWindows(self.enum_windows_find, lparam)
        数据合并完成 = lparam[2]
        if len(数据合并完成):
            win32gui.PostMessage(数据合并完成[0], win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
            win32gui.PostMessage(数据合并完成[0], win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            return True
        return False

    def 获取引擎控制台窗口句柄(self, 文件夹名):
        引擎控制台列表 = []
        lparam = [f'{文件夹名}\\]', 'TfrmMain', 引擎控制台列表]
        win32gui.EnumWindows(self.enum_windows_find, lparam)
        引擎控制台列表 = lparam[2]
        return 引擎控制台列表[0]

    def 查找子窗口句柄(self, hwnd, 标题):
        子窗口列表 = []
        lparam = [标题, 'TButton', 子窗口列表]
        win32gui.EnumChildWindows(hwnd, self.enum_child_windows_find, lparam)
        if len(子窗口列表):
            return 子窗口列表[0]

    def 停止服务器(self, 文件夹名):
        引擎控制台窗口句柄 = self.获取引擎控制台窗口句柄(文件夹名)
        停止服务器按键句柄 = self.查找子窗口句柄(引擎控制台窗口句柄, '停止游戏服务器(&T)')
        if 停止服务器按键句柄:
            self.鼠标点击(停止服务器按键句柄)
            self.点击确认信息()
        self.msg.emit(f'{文件夹名} 停止中...')
        while not self.查找子窗口句柄(引擎控制台窗口句柄, '启动游戏服务器(&S)'):
            time.sleep(0.5)
        self.msg.emit(f'{文件夹名} 停止完成')

    def 启动服务器(self, 文件夹名):
        引擎控制台窗口句柄 = self.获取引擎控制台窗口句柄(文件夹名)
        启动服务器按键句柄 = self.查找子窗口句柄(引擎控制台窗口句柄, '启动游戏服务器(&S)')
        if 启动服务器按键句柄:
            self.鼠标点击(启动服务器按键句柄)
            self.点击确认信息()
        self.msg.emit(f'{文件夹名} 启动中...')

    def 清理数据(self, 文件夹名):
        引擎控制台窗口句柄 = self.获取引擎控制台窗口句柄(文件夹名)
        开始清理按键句柄 = self.查找子窗口句柄(引擎控制台窗口句柄, '开始清理')
        while not 开始清理按键句柄:
            h_TPageControl = win32gui.FindWindowEx(引擎控制台窗口句柄, 0, "TPageControl", None)
            self.鼠标点击(h_TPageControl, x=374, y=10) # 数据清理
            self.msg.emit(f'{文件夹名} 获取【开始清理】按键为None')
            time.sleep(0.5)
            self.鼠标点击(h_TPageControl, x=42, y=10) # 服务器控制
            开始清理按键句柄 = self.查找子窗口句柄(引擎控制台窗口句柄, '开始清理')
        self.鼠标点击(开始清理按键句柄)
        self.点击确认信息()
        self.点击提示信息()
        self.msg.emit(f'{文件夹名} 数据清理完成')

    def 更新列表(self):
        filePath = self.data['列表文件']
        writeStrList = []
        with open(filePath, 'r') as f_open:
            strList = f_open.readlines()
            day = time.strftime('%m{}%d{}', time.localtime()).format('月', '日')
            moth = time.strftime('%m{}', time.localtime()).format('月')
            week = time.strftime('%W{}', time.localtime()).format('周')
            循环列表 = []
            for temStr in strList:  # 获取周循环列表
                if '循环分区' in temStr:
                    循环列表.append(temStr)
            循环列表 = 循环列表[-1:] + 循环列表[:-1]  # 周列表循环
            新列表 = []
            循环列表[0] = 循环列表[0][0:循环列表[0].find('【') + 1] + day + 循环列表[0][循环列表[0].find('】'):]
            循环列表[0] = 循环列表[0].replace('】', '】刚开一秒')  # 添加新区刚开一秒标签
            循环列表[1] = 循环列表[1].replace('】刚开一秒', '】')  # 去除昨天刚开一秒标签
            i = 0
            for temStr in strList:
                if '分区' in temStr:
                    新列表.append(循环列表[i])
                    i = i + 1
                else:
                    新列表.append(temStr)
        writeStrList = 新列表
        with open(filePath, 'w') as f_open:  # 写入列表文
            for temStr in writeStrList:
                f_open.write(temStr)
        self.msg.emit('')
        self.msg.emit(f'{filePath} 列表文件更新成功')

    def 备份数据(self, 主区目录, 合区目录):
        bak = self.data['工作目录'] + '\\bak\\' +time.strftime('%Y{}%m{}%d{}%H{}%M{}', time.localtime()).format('年', '月', '日', '时', '分')
        主备 = self.data['工作目录'] + f'\\{主区目录}\\'
        合备 = self.data['工作目录'] + f'\\{合区目录}\\'
        try:
            subprocess.run(["xcopy", f'{主备}LoginSrv\\IDDB', f'{bak}\\{主区目录}\\LoginSrv\\IDDB', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{合备}LoginSrv\\IDDB', f'{bak}\\{合区目录}\\LoginSrv\\IDDB', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{主备}DBServer\\FDB', f'{bak}\\{主区目录}\\DBServer\\FDB', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{合备}DBServer\\FDB', f'{bak}\\{合区目录}\\DBServer\\FDB', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{主备}Mir200\\M2Data', f'{bak}\\{主区目录}\\Mir200\\M2Data', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{合备}Mir200\\M2Data', f'{bak}\\{合区目录}\\Mir200\\M2Data', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{主备}Mir200\\GuildBase', f'{bak}\\{主区目录}\\Mir200\\GuildBase', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{合备}Mir200\\GuildBase', f'{bak}\\{合区目录}\\Mir200\\GuildBase', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{主备}Mir200\\Envir\\MasterNo', f'{bak}\\{主区目录}\\Mir200\\Envir\\MasterNo', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{合备}Mir200\\Envir\\MasterNo', f'{bak}\\{合区目录}\\Mir200\\Envir\\MasterNo', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{主备}Mir200\\Envir\\Nations', f'{bak}\\{主区目录}\\Mir200\\Envir\\Nations', "/E", "/I", "/Y"])
            subprocess.run(["xcopy", f'{合备}Mir200\\Envir\\Nations', f'{bak}\\{合区目录}\\Mir200\\Envir\\Nations', "/E", "/I", "/Y"])
            self.msg.emit(f'备份数据成功')
        except:
            self.msg.emit(f'备份数据失败')


    def 合区任务(self, 主区目录, 合区目录):
        # 修改合区工具配置 GOM
        路径 = self.data['合区工具']
        配置文件路径 = 路径.rsplit('/', 1)[0] + '/Config.ini'
        config = configparser.ConfigParser()
        config['Setup'] = {
            'SavePath': self.data['工作目录'] + '\\data',
            'SortItemMakeIndex': 1,
            'Replace': 1,
            'Backup': 1,
            'CleanData': 0,
            'MinDay': 90,
            'MinLevel': 10
        }
        config['Master'] = {
            'MirServer': self.data['工作目录'] + '\\' + 主区目录,
            'ID': self.data['工作目录'] + '\\' + 主区目录 + '\\LoginSrv\\IDDB\\ID.DB',
            'Hum': self.data['工作目录'] + '\\' + 主区目录 + '\\DBServer\\FDB\\Hum.DB',
            'Mir': self.data['工作目录'] + '\\' + 主区目录 + '\\DBServer\\FDB\\Mir.DB',
            'HeroMir': self.data['工作目录'] + '\\' + 主区目录 + '\\DBServer\\FDB\\HeroMir.DB',
            'Guild': self.data['工作目录'] + '\\' + 主区目录 + '\\Mir200\\GuildBase\\',
            'Shop': self.data['工作目录'] + '\\' + 主区目录 + '\\Mir200\\Envir\\UserData\\Shop.dat',
            'ShopItem': self.data['工作目录'] + '\\' + 主区目录 + '\\Mir200\Envir\\UserData\\ShopItem.dat',
            '!Setup': self.data['工作目录'] + '\\' + 主区目录 + '\\Mir200\\!Setup.txt',
        }
        config['Slave'] = {
            'MirServer': self.data['工作目录'] + '\\' + 合区目录,
            'ID': self.data['工作目录'] + '\\' + 合区目录 + '\\LoginSrv\\IDDB\\ID.DB',
            'Hum': self.data['工作目录'] + '\\' + 合区目录 + '\\DBServer\\FDB\\Hum.DB',
            'Mir': self.data['工作目录'] + '\\' + 合区目录 + '\\DBServer\\FDB\\Mir.DB',
            'HeroMir': self.data['工作目录'] + '\\' + 合区目录 + '\\DBServer\\FDB\\HeroMir.DB',
            'Guild': self.data['工作目录'] + '\\' + 合区目录 + '\\Mir200\\GuildBase\\',
            'Shop': self.data['工作目录'] + '\\' + 合区目录 + '\\Mir200\\Envir\\UserData\\Shop.dat',
            'ShopItem': self.data['工作目录'] + '\\' + 合区目录 + '\\Mir200\Envir\\UserData\\ShopItem.dat',
            '!Setup': self.data['工作目录'] + '\\' + 合区目录 + '\\Mir200\\!Setup.txt'
        }
        with open(配置文件路径, 'w', encoding='gbk') as configfile:
            config.write(configfile)

        # 修改合区工具配置 翎风
        路径 = self.data['合区工具']
        配置文件路径 = 路径.rsplit('/', 1)[0] + '/config.txt'
        config = configparser.ConfigParser()
        config['Setup'] = {
            'SavePath': self.data['工作目录'] + '\\data'
        }
        config['Master'] = {
            'MirServer': self.data['工作目录'] + '\\' + 主区目录,
            'ApexID': self.data['工作目录'] + '\\' + 主区目录 + '\\LoginSrv\\IDDB\\ApexID.DB',
            'ApexMir': self.data['工作目录'] + '\\' + 主区目录 + '\\DBServer\\FDB\\\ApexMir.DB',
            'ApexM2Data': self.data['工作目录'] + '\\' + 主区目录 + '\\Mir200\\M2Data\\ApexM2Data.DB',
            'Guild': self.data['工作目录'] + '\\' + 主区目录 + '\\Mir200\\GuildBase\\',
            'MasterNo': self.data['工作目录'] + '\\' + 主区目录 + '\\Mir200\\Envir\\MasterNo\\',
            'Nations': self.data['工作目录'] + '\\' + 主区目录 + '\\Mir200\Envir\\Nations\\',
            '!Setup': self.data['工作目录'] + '\\' + 主区目录 + '\\Mir200\\!Setup.txt',
            'SqliteDBFile': self.data['工作目录'] + '\\' + 主区目录 + '\\Mud2\\DB\\ApexM2.DB',
            'DataSaveDBType': '0',
            'DataSaveDBServer': '',
            'DataSaveDBPort': '1',
            'DataSaveDBUser': '',
            'DataSaveDBPassword': '',
            'DataSaveDataBase': '',
        }
        config['Clear'] = {
            'HumanDayAndLevel': '0',
            'HumanDay': '90',
            'HumanLevel': '100',
            'ChrDelete': '0',
            'AccountNoChr': '1',
            'AccountDisable': '1',
            'HumanDisband': '1',
            'CopyItem': '1',
            'InvalidGuild': '1',
            'NoMasterGuild': '0',
            'ShopSelledItem': '1',
            'GuildHumanCount': '0',
            'GuildHumanCountValue': '1',
        }
        config['Slave'] = {
            'Count': '1'
        }
        config['Slave1'] = {
            'ServerDir': self.data['工作目录'] + '\\' + 合区目录,
            'DBType': '0',
            'AccountDB': self.data['工作目录'] + '\\' + 合区目录 + '\\LoginSrv\\IDDB\\ApexID.DB',
            'RoleDataDB': self.data['工作目录'] + '\\' + 合区目录 + '\\DBServer\\FDB\\ApexMir.DB',
            'M2DataDB': self.data['工作目录'] + '\\' + 合区目录 + '\\Mir200\\M2Data\\ApexM2Data.DB',
            'DBServer': '',
            'DBPort': '1',
            'DBUser': '',
            'DBPassword': '',
            'DBName': '',
            'GuildDir': self.data['工作目录'] + '\\' + 合区目录 + '\\Mir200\\GuildBase\\',
            'MasterNoDir': self.data['工作目录'] + '\\' + 合区目录 + '\\Mir200\\Envir\\MasterNo\\',
            'NationsDir': self.data['工作目录'] + '\\' + 合区目录 + '\\Mir200\Envir\\Nations\\',
            'SetupText': self.data['工作目录'] + '\\' + 合区目录 + '\\Mir200\\!Setup.txt',
            'ApexM2DB': self.data['工作目录'] + '\\' + 合区目录 + '\\Mud2\\DB\\ApexM2.DB',
        }
        with open(配置文件路径, 'w', encoding='gbk') as configfile:
            config.write(configfile)
        subprocess.Popen(路径)
        合区工具 = []
        while not len(合区工具):
            lparam = [f'合区工具', 'TFrmMain', 合区工具]
            win32gui.EnumWindows(self.enum_windows_find, lparam)
            合区工具 = lparam[2]
            time.sleep(0.5)
        子窗口列表 = []
        while not len(子窗口列表):
            lparam = ['开始合并', 'TButton', 子窗口列表]
            win32gui.EnumChildWindows(合区工具[0], self.enum_child_windows_find, lparam)
            if len(子窗口列表):
                self.鼠标点击(子窗口列表[0])
            time.sleep(0.5)
        while True:
            if self.点击数据合并完成():
                # 使用 xcopy 复制文件夹（/E 复制所有子目录，/I 目标是文件夹，/Y 覆盖）
                subprocess.run(["xcopy", self.data['工作目录']+ '\\data', self.data['工作目录']+ '\\' + 主区目录, "/E", "/I", "/Y"])
                self.备份数据(主区目录, 合区目录)
            time.sleep(0.5)
            style = win32gui.GetWindowLong(子窗口列表[0], win32con.GWL_STYLE)
            if bool(style & win32con.WS_DISABLED):
                time.sleep(0.5)
            else:
                win32gui.PostMessage(合区工具[0], win32con.WM_CLOSE, 0, 0)
                break

        self.msg.emit(f'{合区目录} 合并到 {主区目录} 完成')

    def 获取合区目录(self):
        列表文件 = self.data['列表文件']
        分区list = []
        if 列表文件:
            with open(列表文件, 'r') as fp:
                strList = fp.readlines()
                for temStr in strList:  # 获取周循环列表
                    if '循环分区' in temStr:
                        分区list.append(temStr)
            if not len(分区list):
                self.msg.emit(f'【循环分区】标签是否存完成？')
                return False
            端口 = 7000 + int(分区list[-1].split('|70')[1][:2])
            合区目录 = self.data['主区文件夹'].rsplit('_', 1)[0] + '_' + str(端口)
        return 合区目录

    def 开始合区(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        主区目录 = config['conf']['主区文件夹']
        合区目录 = self.获取合区目录()
        if 合区目录 == config['conf']['大区文件夹']:  # 如果碰到最大区名，开始循环
            下次合区目录 = config['conf']['大区文件夹']
        else:
            目录信息列表 = 合区目录.split('_')
            下次合区目录 = 目录信息列表[0] + "_" + 目录信息列表[1] + "_" + str(int(目录信息列表[2]) + 1)
        config.set("conf", "合区文件夹", 下次合区目录)
        with open('config.ini', 'w', encoding='gbk') as configfile:
            config.write(configfile)
        self.停止服务器(主区目录)
        self.停止服务器(合区目录)
        self.合区任务(主区目录, 合区目录)
        self.清理数据(合区目录)
        self.启动服务器(主区目录)
        self.启动服务器(合区目录)
        self.更新列表()

    def run(self):
        self.msg.emit('开合区任务线程启动...')
        while self.running:
            现在时间 = time.strftime("%H:%M:%S", time.localtime())
            现在日期 = time.strftime('%d{}', time.localtime()).format('日')
            现在星期 = time.strftime("%w{}", time.localtime()).format('周')
            if self.data['合区时间'] in 现在星期+现在时间:
                self.msg.emit('开始运行合区任务')
                self.开始合区()
                time.sleep(1)
            time.sleep(0.5)
        self.msg.emit('开合区任务线程结')

    def stop(self):
        """ 停止线程 """
        self.running = False  # 修改标志位，让线程退出


class CloneThread(QtCore.QThread):
    """ 线程类，执行文件夹克隆 """
    update_status = QtCore.pyqtSignal(str)  # 用于更新状态栏
    update_ui = QtCore.pyqtSignal(bool)  # 用于启用/禁用 UI 控件

    def __init__(self, src, dstPath, minPort, maxPort):
        super().__init__()
        self.src = src
        self.dstPath = dstPath
        self.minPort = minPort
        self.maxPort = maxPort
        self.src_port = int(src.rsplit('_', 1)[1])

    def 修改配置(self, filepath, 端口差值):
        path, port = self.src.rsplit('_', 1)
        src_port = int(port)
        dis_port = int(port) + 端口差值
        # 修改配置文件
        with open(filepath + '\\Config.ini', 'r+', encoding='gbk') as configfile:
            filestr = configfile.read()  # 读取原始内容
            filestr = filestr.replace(self.src, filepath)  # 进行替换
            filestr = filestr.replace('DBPort1=' + str(src_port + 20201), 'DBPort1=' + str(dis_port + 20201))  # LFM2
            filestr = filestr.replace('GatePort=' + str(src_port), 'GatePort=' + str(dis_port))  # 进行替换
            filestr = filestr.replace('GatePort=' + str(src_port + 100), 'GatePort=' + str(dis_port + 100))  # 进行替换
            filestr = filestr.replace('GatePort1=' + str(src_port + 200), 'GatePort1=' + str(dis_port + 200))  # 进行替换
            filestr = filestr.replace('Port=' + str(src_port + 3000), 'Port=' + str(dis_port + 3000))  # 进行替换
            filestr = filestr.replace('ServerPort=' + str(src_port - 1000), 'ServerPort=' + str(dis_port - 1000))  # 进行替换
            filestr = filestr.replace('ServerPort=' + str(src_port - 1400), 'ServerPort=' + str(dis_port - 1400))  # 进行替换
            filestr = filestr.replace('GatePort=' + str(src_port - 1500), 'GatePort=' + str(dis_port - 1500))  # 进行替换
            filestr = filestr.replace('GatePort=' + str(src_port - 1900), 'GatePort=' + str(dis_port - 1900))  # 进行替换
            filestr = filestr.replace('GatePort=' + str(src_port - 2000), 'GatePort=' + str(dis_port - 2000))  # 进行替换
            filestr = filestr.replace('MsgSrvPort=' + str(src_port - 2100), 'MsgSrvPort=' + str(dis_port - 2100))  # 进行替换
            configfile.seek(0)  # 移动到文件开头
            configfile.write(filestr)  # 写入修改后的内容
            configfile.truncate()  # 截断多余内容，防止残留旧数据
        with open(filepath + '\\DBServer\\dbsrc.ini', 'r+', encoding='gbk') as configfile:
            filestr = configfile.read()  # 读取原始内容
            filestr = filestr.replace(self.src, filepath)  # 进行替换
            filestr = filestr.replace(str(src_port - 1000), str(dis_port - 1000))  # 进行替换
            filestr = filestr.replace(str(src_port - 1900), str(dis_port - 1900))  # 进行替换
            filestr = filestr.replace(str(src_port - 1400), str(dis_port - 1400))  # 进行替换
            configfile.seek(0)  # 移动到文件开头
            configfile.write(filestr)  # 写入修改后的内容
            configfile.truncate()  # 截断多余内容，防止残留旧数据
        with open(filepath + '\\DBServer\\!serverinfo.txt', 'r+', encoding='gbk') as configfile:
            filestr = configfile.read()  # 读取原始内容
            filestr = filestr.replace(str(src_port + 200), str(dis_port + 200))  # 进行替换
            configfile.seek(0)  # 移动到文件开头
            configfile.write(filestr)  # 写入修改后的内容
            configfile.truncate()  # 截断多余内容，防止残留旧数据
        with open(filepath + '\\LoginSrv\\Logsrv.ini', 'r+', encoding='gbk') as configfile:
            filestr = configfile.read()  # 读取原始内容
            filestr = filestr.replace(self.src, filepath)  # 进行替换
            filestr = filestr.replace(str(src_port - 1500), str(dis_port - 1500))  # 进行替换
            filestr = filestr.replace(str(src_port - 1400), str(dis_port - 1400))  # 进行替换
            configfile.seek(0)  # 移动到文件开头
            configfile.write(filestr)  # 写入修改后的内容
            configfile.truncate()  # 截断多余内容，防止残留旧数据
        with open(filepath + '\\LoginSrv\\!addrtable.txt', 'r+', encoding='gbk') as configfile:
            filestr = configfile.read()  # 读取原始内容
            filestr = filestr.replace(self.src, filepath)  # 进行替换
            filestr = filestr.replace(str(src_port + 100), str(dis_port + 100))  # 进行替换
            configfile.seek(0)  # 移动到文件开头
            configfile.write(filestr)  # 写入修改后的内容
            configfile.truncate()  # 截断多余内容，防止残留旧数据
        with open(filepath + '\\LogServer\\LogData.ini', 'r+', encoding='gbk') as configfile:
            filestr = configfile.read()  # 读取原始内容
            filestr = filestr.replace(self.src, filepath)  # 进行替换
            filestr = filestr.replace(str(src_port + 3000), str(dis_port + 3000))  # 进行替换
            configfile.seek(0)  # 移动到文件开头
            configfile.write(filestr)  # 写入修改后的内容
            configfile.truncate()  # 截断多余内容，防止残留旧数据
        with open(filepath + '\\Mir200\\!Setup.txt', 'r+', encoding='gbk') as configfile:
            filestr = configfile.read()  # 读取原始内容
            filestr = filestr.replace(self.src, filepath)  # 进行替换
            filestr = filestr.replace('GatePort=' + str(src_port - 2000), 'GatePort=' + str(dis_port - 2000))  # 进行替换
            filestr = filestr.replace('DBPort=' + str(src_port - 1000), 'DBPort=' + str(dis_port - 1000))  # 进行替换
            filestr = filestr.replace('IDSPort=' + str(src_port - 1400), 'IDSPort=' + str(dis_port - 1400))  # 进行替换
            filestr = filestr.replace('MsgSrvPort=' + str(src_port - 2100), 'MsgSrvPort=' + str(dis_port - 2100))  # 进行替换
            filestr = filestr.replace('LogServerPort=' + str(src_port + 3000), 'LogServerPort=' + str(dis_port + 3000))  # 进行替换
            configfile.seek(0)  # 移动到文件开头
            configfile.write(filestr)  # 写入修改后的内容
            configfile.truncate()  # 截断多余内容，防止残留旧数据
        try:
            with open(filepath + '\\RunGate\\RunGate.ini', 'r+', encoding='gbk') as configfile:
                filestr = configfile.read()  # 读取原始内容
                filestr = filestr.replace(self.src, filepath)  # 进行替换
                filestr = filestr.replace(str(src_port + 200), str(dis_port + 200))  # 进行替换
                filestr = filestr.replace(str(src_port - 2000), str(dis_port - 2000))  # 进行替换
                configfile.seek(0)  # 移动到文件开头
                configfile.write(filestr)  # 写入修改后的内容
                configfile.truncate()  # 截断多余内容，防止残留旧数据
        except:
            # 更新LFM2
            with open(filepath + '\\RunGate\\Config.ini', 'r+', encoding='gbk') as configfile:
                filestr = configfile.read()  # 读取原始内容
                filestr = filestr.replace(self.src, filepath)  # 进行替换
                filestr = filestr.replace(str(src_port + 200), str(dis_port + 200))  # 进行替换
                filestr = filestr.replace(str(src_port - 2000), str(dis_port - 2000))  # 进行替换
                filestr = filestr.replace('DBPort=' + str(src_port + 20201), 'DBPort=' + str(dis_port + 20201))  # 进行替换
                configfile.seek(0)  # 移动到文件开头
                configfile.write(filestr)  # 写入修改后的内容
                configfile.truncate()  # 截断多余内容，防止残留旧数据
            with open(filepath + '\\DBServer\\!GateList.ini', 'r+', encoding='gbk') as configfile:
                filestr = configfile.read()  # 读取原始内容
                filestr = filestr.replace(str(src_port + 20201), str(dis_port + 20201))  # 进行替换
                configfile.seek(0)  # 移动到文件开头
                configfile.write(filestr)  # 写入修改后的内容
                configfile.truncate()  # 截断多余内容，防止残留旧数据
            with open(filepath + '\\LoginGate\\Config.ini', 'r+', encoding='gbk') as configfile:
                filestr = configfile.read()  # 读取原始内容
                filestr = filestr.replace(str(src_port), str(dis_port))  # 进行替换
                filestr = filestr.replace(str(src_port - 1500), str(dis_port - 1500))  # 进行替换
                configfile.seek(0)  # 移动到文件开头
                configfile.write(filestr)  # 写入修改后的内容
                configfile.truncate()  # 截断多余内容，防止残留旧数据
        with open(filepath + '\\SelGate\\Config.ini', 'r+', encoding='gbk') as configfile:
            filestr = configfile.read()  # 读取原始内容
            filestr = filestr.replace(self.src, filepath)  # 进行替换
            filestr = filestr.replace(str(src_port + 100), str(dis_port + 100))  # 进行替换
            filestr = filestr.replace(str(src_port - 1900), str(dis_port - 1900))  # 进行替换
            configfile.seek(0)  # 移动到文件开头
            configfile.write(filestr)  # 写入修改后的内容
            configfile.truncate()  # 截断多余内容，防止残留旧数据
        #

    def run(self):
        """ 执行克隆任务 """
        self.update_ui.emit(False)  # 禁用 UI

        for port in range(self.minPort, self.maxPort + 1):
            dst = self.dstPath + str(port)
            self.update_status.emit(f'克隆 {dst} ...')
            # 使用 xcopy 复制文件夹（/E 复制所有子目录，/I 目标是文件夹，/Y 覆盖）
            subprocess.run(["xcopy", self.src, dst, "/E", "/I", "/Y"])
            self.修改配置(dst, port - self.src_port)

        self.update_status.emit('克隆完成')
        self.update_ui.emit(True)  # 启用 UI


class Updateipaddr(QtCore.QThread):
    msg = QtCore.pyqtSignal(str)
    def __init__(self, listFile: str, serverAddr: str, mainDir: str, running: bool = True):
        super().__init__()
        self.running = running
        self.listFile = listFile
        self.serverAddr = serverAddr
        self.mainDir = mainDir

    def enum_windows_find(self, hwnd, lparam):
        '''依据窗口标题 和窗口类名称 查询窗口'''
        windows_title = win32gui.GetWindowText(hwnd)
        windows_class = win32gui.GetClassName(hwnd)
        if lparam[0] in windows_title and lparam[1].upper() in windows_class.upper():
            lparam[2].append(hwnd)

    def restartGate(self, ip: str, last_ip: str):
        gatePath = self.mainDir + '\\微端\\微端网关\\'
        configFile = gatePath + '!serverinfo.txt'
        gateFile = gatePath + 'MirUpdateGate.exe'
        if ip and last_ip:
            with open(configFile, 'r+') as fp:
                fileStr = fp.read()
                fileStr = fileStr.replace(last_ip, ip)
                fp.seek(0)  # 移动到文件开头
                fp.write(fileStr)  # 写入修改后的内容
                fp.truncate()  # 截断多余内容，防止残留旧数据
            self.msg.emit(f'{configFile}:{last_ip} 更换 {ip}')
        # 重启微端网关
        微端网关句柄列表 = []
        lparam = ['翎风微端网关 1.0.0 Build 20221201', "TFrmMain", 微端网关句柄列表]
        win32gui.EnumWindows(self.enum_windows_find, lparam)
        微端网关句柄列表 = lparam[2]
        文件列表 = []
        for item in 微端网关句柄列表:
            _, pid = win32process.GetWindowThreadProcessId(item)
            process = psutil.Process(pid)
            文件列表.append(process.exe())
            if process.exe() in gateFile:
                process.terminate()
                process.wait(timeout=3)
                self.msg.emit(f'结束进程:{gateFile}')
                try:
                    subprocess.Popen(gateFile, cwd=gatePath)
                    self.msg.emit(f'启动成功:{gateFile}')
                except:
                    self.msg.emit(f'启动失败:{gateFile}')
        if gateFile not in 文件列表:
            try:
                subprocess.Popen(gateFile, cwd=gatePath)
                self.msg.emit(f'启动成功:{gateFile}')
            except:
                self.msg.emit(f'启动失败:{gateFile}')


    def get_public_ip(self):
        response = requests.get('http://txt.go.sohu.com/ip/soip').text
        # 使用正则表达式提取IP地址
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        match = re.search(ip_pattern, response)
        if match:
            ip_address = match.group(0)
            if ip_address != '192.168.50.1':
                return ip_address
        return None

    def worker(self):
        try:
            ip = self.get_public_ip()
        except:
            ip =''
            self.msg.emit('get_public_ip获取ip失败')
        with open(self.listFile, 'r') as fp:
            lines = fp.readlines()
            for line in lines:
                if "固定主区" in line:
                    lastip = line.split('|')[3]
        if ip and ip != lastip:
            requests.get(f'http://{self.serverAddr}:30088/updateipaddr/{ip}')
            with open(self.listFile, 'r+') as fp:
                fileStr = fp.read()
                fileStr = fileStr.replace(lastip, ip)
                fp.seek(0)  # 移动到文件开头
                fp.write(fileStr)  # 写入修改后的内容
                fp.truncate()  # 截断多余内容，防止残留旧数据
            self.msg.emit(f'{self.listFile} {lastip} 更换 {ip}')
            self.restartGate(ip=ip, last_ip=lastip)  # 重启网关

    def run(self):
        self.msg.emit(f"ip监控线程启动成功，当前ip: {self.get_public_ip()}")
        self.restartGate(ip='', last_ip='')  # 重启网关
        while self.running:
            time.sleep(10)
            try:
                self.worker()
            except:
                ...
        self.msg.emit("ip监控线程结束")

    def stop(self):
        """ 停止线程 """
        self.running = False  # 修改标志位，让线程退出


class UpdateServer(QtCore.QThread):
    msg = QtCore.pyqtSignal(str)

    def __init__(self, listFile: str, serverAddr: str, mainDir: str, running: bool = True):
        super().__init__()
        self.running = running
        self.listFile = listFile
        self.serverAddr = serverAddr
        self.mainDir = mainDir

    def enum_windows_find(self, hwnd, lparam):
        '''依据窗口标题 和窗口类名称 查询窗口'''
        windows_title = win32gui.GetWindowText(hwnd)
        windows_class = win32gui.GetClassName(hwnd)
        if lparam[0] in windows_title and lparam[1].upper() in windows_class.upper():
            lparam[2].append(hwnd)
    def get_nginx_pids(self):
        # 使用 tasklist 获取所有进程
        tasklist_output = subprocess.check_output("tasklist", encoding="gbk")
        # 找到所有包含 'nginx.exe' 的行并提取 PID
        pids = []
        for line in tasklist_output.splitlines():
            if "nginx.exe" in line.lower():
                parts = line.split()
                pid = int(parts[1])  # 第二个字段是 PID
                pids.append(pid)
        return pids

    def kill_nginx_processes(self):
        pids = self.get_nginx_pids()
        for pid in pids:
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
                win32api.TerminateProcess(handle, 0)
                win32api.CloseHandle(handle)
                self.msg.emit(f"已结束 nginx 进程 (PID: {pid})")
            except Exception as e:
                self.msg.emit(f"无法结束 nginx 进程 (PID: {pid}): {e}")

    def enum_child_windows_find(self, hwnd, param):
        '''依据主窗口handle, 查询 标题为param[0]的子窗口 赋值到param[1]'''
        window_title = win32gui.GetWindowText(hwnd)
        window_classname = win32gui.GetClassName(hwnd)
        # print(f"子窗口句柄: {hwnd}, 标题: {window_title}, 类名：{window_classname}")
        if param[0] in window_title:
            # print(f"子窗口句柄: {hwnd}, 标题: {window_title}, 类名：{window_classname}")
            param[2].append(hwnd)

    def ip检查(self, ip):
        self.msg.emit(f'接收到ip更新通知 {ip}')
        小皮目录 = f'D:\\phpstudy_pro'
        目录 = f'{小皮目录}\\Extensions\\Nginx1.15.11\\conf\\vhosts\\'
        fileList = os.listdir(目录)
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        for filename in fileList:
            fileStr = ''
            原ip = ''
            if '.conf' in filename:
                with open(f'{目录}{filename}', 'r') as fp:
                    lines = fp.readlines()
                    fileStr = ''.join(lines)
                    for line in lines:
                        if 'proxy_pass' in line:
                            match = re.search(ip_pattern, line)
                            原ip = match.group(0)
            if 原ip and (ip not in 原ip):
                with open(f'{目录}{filename}', 'w') as fp:
                    fileStr = fileStr.replace(原ip, ip)
                    fp.write(fileStr)
                self.msg.emit(f"更新{filename}原ip {原ip}为{ip}")
        self.kill_nginx_processes()

    async def handle(self, request):
        try:
            ip = request.match_info.get('ip', "None")
            if ip != "None":
                text = "反向代理当前ip:" + self.ip检查(ip)
            else:
                text = "内部错误"
            return web.Response(text=text)
        except:
            return web.Response(text="内部错误")

    async def worker(self):
        port = 30088
        app = web.Application()
        app.add_routes([web.get('/', self.handle),
                        web.get('/updateipaddr/{ip}', self.handle)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        self.msg.emit(f"反代ip更新线程：http://0.0.0.0:{port}")
        # 保持主函数持续运行
        while self.running:
            await asyncio.sleep(1)  # 每小时执行一次异步操作，防止事件循环退出
        self.msg.emit("反代ip更新线程结束")

    def run(self):
        self.ip检查('')
        try:
            asyncio.run(self.worker())
        except KeyboardInterrupt:
            print("Server stopped manually")

    def stop(self):
        """ 停止线程 """
        self.running = False  # 修改标志位，让线程退出
