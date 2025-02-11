from PyQt6 import QtCore
import time
import win32gui
import win32con
import win32api
import subprocess
import configparser


class SubWorkerThread(QtCore.QThread):

    msg = QtCore.pyqtSignal(str)

    def __init__(self, data: dict):
        super(SubWorkerThread, self).__init__()
        self.data = data
        self.running = True

    def 鼠标点击(self, hwnd, x=0, y=0):
        rect = win32gui.GetWindowRect(hwnd)
        if x == 0:
            x = (rect[0] + rect[2]) // 2  # 窗口中心点的 x 坐标
        if y == 0:
            y = (rect[1] + rect[3]) // 2  # 窗口中心点的 y 坐标
        point = win32api.MAKELONG(x - rect[0], y - rect[1])
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

    def 点击提示信息(self):
        确认信息 = []
        while not len(确认信息):
            lparam = [f'提示信息', '#32770', 确认信息]
            win32gui.EnumWindows(self.enum_windows_find, lparam)
            确认信息 = lparam[2]
            if len(确认信息):
                win32gui.PostMessage(确认信息[0], win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(确认信息[0], win32con.WM_KEYUP, win32con.VK_RETURN, 0)

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
        # 'GameOfMir引擎控制台 [神龙冰雪 D:\\mir2\\Mirserver_神龙冰雪_7020\\]'
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
        if 开始清理按键句柄:
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

    def 合区任务(self, 主区目录, 合区目录):
        # 修改合区工具配置
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
        with open(filepath + '\\RunGate\\RunGate.ini', 'r+', encoding='gbk') as configfile:
            filestr = configfile.read()  # 读取原始内容
            filestr = filestr.replace(self.src, filepath)  # 进行替换
            filestr = filestr.replace(str(src_port + 200), str(dis_port + 200))  # 进行替换
            filestr = filestr.replace(str(src_port - 2000), str(dis_port - 2000))  # 进行替换
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
            subprocess.run(["xcopy", self.src, dst, "/E", "/I"], shell=True)
            self.修改配置(dst, port - self.src_port)

        self.update_status.emit('克隆完成')
        self.update_ui.emit(True)  # 启用 UI