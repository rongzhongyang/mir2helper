import datetime

from PyQt6.QtWidgets import QLineEdit

import MainWindowUI
from PyQt6 import QtWidgets
from PyQt6.QtGui import QIcon, QPixmap
import psutil, subprocess
import win32process
import icon
import win32gui
import win32con
import win32api
import configparser
from MyThread import SubWorkerThread, CloneThread, Updateipaddr, UpdateServer
from MyLogger import MyLogger


def set_icon():
    # 把icon.ico文件以bytes写入.py文件中的变量icon_bytes中
    try:
        with open('icon.ico', 'rb') as file_icon:
            icon_str = file_icon.read()
            icon_bytes = 'icon_bytes = ' + str(icon_str)
        with open('icon.py', 'w+') as icon_py:
            icon_py.write(icon_bytes)
    except:
        ...

def get_icon():
    # 从icon_bytes变量中提取bytes字符串，并转成QPixmap
    icon_img = icon.icon_bytes  # 解码
    icon_pixmap = QPixmap()  # 新建QPixmap对象
    icon_pixmap.loadFromData(icon_img)  # 往QPixmap中写入数据
    return icon_pixmap


class CMyMainWindow(QtWidgets.QMainWindow, MainWindowUI.Ui_MainWindow):
    def __init__(self):
        super(CMyMainWindow, self).__init__()
        self.setupUi(self)  # 设置 UI
        self.log = MyLogger(log_name='log')
        # 读配置文件
        config = configparser.ConfigParser()
        self.comboBox.addItems(['全部', '数据库服务器', '帐号登录服务器', '引擎日志服务器', '游戏网关', '角色网关', '登录网关', '[商业版]'])

        if config.read('config.ini') and 'conf' in config:
            self.lineEdit_db_version.setText(config['conf'].get('数据库版本') if config['conf'].get('数据库版本') else '')
            self.lineEdit_workDir.setText(config['conf'].get('工作目录') if config['conf'].get('工作目录') else '')
            self.lineEdit_workDir_2.setText(config['conf'].get('工作目录') if config['conf'].get('工作目录') else '')
            self.lineEdit_mainDir.setText(config['conf'].get('主区文件夹') if config['conf'].get('主区文件夹') else '')
            self.lineEdit_mainDir_2.setText(config['conf'].get('主区文件夹') if config['conf'].get('主区文件夹') else '')
            self.lineEdit_minDir.setText(config['conf'].get('小区文件夹_月') if config['conf'].get('小区文件夹_月') else '')
            self.lineEdit_maxDir.setText(config['conf'].get('大区文件夹_月') if config['conf'].get('大区文件夹_月') else '')
            self.lineEdit_workTime.setText(config['conf'].get('合区时间_月') if config['conf'].get('合区时间_月') else '')
            self.lineEdit_minDir_1.setText(config['conf'].get('小区文件夹_周') if config['conf'].get('小区文件夹_周') else '')
            self.lineEdit_maxDir_1.setText(config['conf'].get('大区文件夹_周') if config['conf'].get('大区文件夹_周') else '')
            self.lineEdit_workTime_1.setText(config['conf'].get('合区时间_周') if config['conf'].get('合区时间_周') else '')
            self.lineEdit_minDir_2.setText(config['conf'].get('小区文件夹_日') if config['conf'].get('小区文件夹_日') else '')
            self.lineEdit_maxDir_2.setText(config['conf'].get('大区文件夹_日') if config['conf'].get('大区文件夹_日') else '')
            self.lineEdit_workTime_2.setText(config['conf'].get('合区时间_日') if config['conf'].get('合区时间_日') else '')
            self.lineEdit_minPort.setText(config['conf'].get('最小端口') if config['conf'].get('最小端口') else '')
            self.lineEdit_maxPort.setText(config['conf'].get('最大端口') if config['conf'].get('最大端口') else '')
            self.label_6.setText(config['conf'].get('合区工具') if config['conf'].get('合区工具') else '')
            self.label_listfile.setText(config['conf'].get('列表文件') if config['conf'].get('列表文件') else '')
            self.lineEdit_server_addr.setText(config['conf'].get('服务器地址') if config['conf'].get('服务器地址') else '')

            self.label_dir_1.setText(config['conf'].get('清空文件夹一') if config['conf'].get('清空文件夹一') else '')
            self.label_dir_2.setText(config['conf'].get('清空文件夹二') if config['conf'].get('清空文件夹二') else '')
            self.label_file_1.setText(config['conf'].get('删除文件一') if config['conf'].get('删除文件一') else '')
            self.label_file_2.setText(config['conf'].get('删除文件二') if config['conf'].get('删除文件二') else '')
            self.label_file_3.setText(config['conf'].get('删除文件三') if config['conf'].get('删除文件三') else '')
            self.label_file_4.setText(config['conf'].get('删除文件四') if config['conf'].get('删除文件四') else '')

            self.getthisDir(合区类型='月')
            self.getthisDir(合区类型='周')
            self.getthisDir(合区类型='日')
        # 禁用窗口最大化按钮
        self.setWindowTitle(f"航界软件-传奇助手 1.0.0 【{self.lineEdit_mainDir.text().rsplit('_', 1)[0]}】")
        self.setWindowIcon(QIcon(get_icon()))
        self.setFixedSize(self.width(), self.height())  # 固定窗口小大
        self.开合区状态 = False
        self.引擎控制台状态 = False
        self.M2引擎状态 = False
        self.其它窗口状态 = False
        self.screen_width = win32api.GetSystemMetrics(0)  # 屏幕宽度
        self.screen_height = win32api.GetSystemMetrics(1)  # 屏幕高度
        # 设置样式表
        self.setStyleSheet("""
                        QMainWindow {
                            background-color: #f0f0f0;
                        }
                    """)
        self.taskHandle = 0
        # 监听控件失去焦点事件
        for widget in self.findChildren(QLineEdit):
            widget.focusOutEvent = self.on_focus_out
        #self.begin() # 禁用 ip 更新

    def begin(self):
        server_addr = self.lineEdit_server_addr.text()
        listFile = self.label_listfile.text()
        mainDir = self.lineEdit_workDir.text() + '\\' + self.lineEdit_mainDir.text()
        self.thread_up_ip_addr = Updateipaddr(listFile=listFile, serverAddr=server_addr, mainDir=mainDir)
        self.thread_up_ip_addr.msg.connect(self.updateMsg)
        self.thread_server = UpdateServer(listFile=listFile, serverAddr=server_addr, mainDir=mainDir)
        self.thread_server.msg.connect(self.updateMsg)
        if server_addr:
            self.thread_up_ip_addr.start()
        else:
            self.thread_server.start()

    def on_focus_out(self, event):
        # 写配置文件
        config = configparser.ConfigParser()
        config['conf'] = {
            '数据库版本': self.lineEdit_db_version.text(),
            '工作目录': self.lineEdit_workDir.text(),
            '主区文件夹': self.lineEdit_mainDir.text(),
            '小区文件夹_月': self.lineEdit_minDir.text(),
            '大区文件夹_月': self.lineEdit_maxDir.text(),
            '合区文件夹_月': self.lineEdit_thisDir.text(),
            '合区时间_月': self.lineEdit_workTime.text(),
            '小区文件夹_周': self.lineEdit_minDir_1.text(),
            '大区文件夹_周': self.lineEdit_maxDir_1.text(),
            '合区文件夹_周': self.lineEdit_thisDir_1.text(),
            '合区时间_周': self.lineEdit_workTime_1.text(),
            '小区文件夹_日': self.lineEdit_minDir_2.text(),
            '大区文件夹_日': self.lineEdit_maxDir_2.text(),
            '合区文件夹_日': self.lineEdit_thisDir_2.text(),
            '合区时间_日': self.lineEdit_workTime_2.text(),
            '列表文件': self.label_listfile.text(),
            '最小端口': self.lineEdit_minPort.text(),
            '最大端口': self.lineEdit_maxPort.text(),
            '合区工具': self.label_6.text(),
            '服务器地址': self.lineEdit_server_addr.text(),
            '清空文件夹一': self.label_dir_1.text(),
            '清空文件夹二': self.label_dir_2.text(),
            '删除文件一': self.label_file_1.text(),
            '删除文件二': self.label_file_2.text(),
            '删除文件三': self.label_file_3.text(),
            '删除文件四': self.label_file_4.text()
        }
        # if self.lineEdit_server_addr.text():
        #     self.thread_server.running = False
        #     self.thread_up_ip_addr.running = True
        #     self.thread_up_ip_addr.start()
        # else:
        #     self.thread_server.running = True
        #     self.thread_up_ip_addr.running = False
        #     self.thread_server.start()
        with open('config.ini', 'w', encoding='gbk') as configfile:
            config.write(configfile)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)  # 调用父类的 focusOutEvent

    def getthisDir(self, 合区类型: str):
        列表文件 = self.label_listfile.text()
        分区list = []
        if 列表文件:
            try:
                with open(列表文件, 'r', encoding='gbk') as fp:
                    strList = fp.readlines()
                    for temStr in strList:  # 获取周循环列表
                        if f'{合区类型}循环分区' in temStr:
                            分区list.append(temStr)
            except:
                try:
                    with open(列表文件, 'r', encoding='utf-8') as fp:
                        strList = fp.readlines()
                        for temStr in strList:  # 获取周循环列表
                            if f'{合区类型}循环分区' in temStr:
                                分区list.append(temStr)
                except:
                    ...
                return
            if len(分区list) < 1:
                return
            端口 = 7000 + int(分区list[-1].split('|70')[1][:2])
            合区目录 = self.lineEdit_mainDir.text().rsplit('_', 1)[0] + '_' + str(端口)
            if 合区类型 == '月':
                self.lineEdit_thisDir.setText(合区目录)
            if 合区类型 == '周':
                self.lineEdit_thisDir_1.setText(合区目录)
            if 合区类型 == '日':
                self.lineEdit_thisDir_2.setText(合区目录)
        else:
            self.lineEdit_thisDir.text('先设置列表文件')
            self.lineEdit_thisDir_2.text('先设置列表文件')

    def enum_windows_find(self, hwnd, lparam):
        '''依据窗口标题 和窗口类名称 查询窗口'''
        windows_title = win32gui.GetWindowText(hwnd)
        windows_class = win32gui.GetClassName(hwnd)
        if '*' in lparam[0]:
            titles = lparam[0].split('*')
            for title in titles:
                if title not in windows_title:
                    return
        else:
            if lparam[0] not in windows_title:
                return
        if lparam[1].upper() in windows_class.upper():
            lparam[2].append(hwnd)

    def enum_child_windows_find(self, hwnd, param):
        '''依据主窗口handle, 查询 标题为param[0]的子窗口 赋值到param[1]'''
        window_title = win32gui.GetWindowText(hwnd)
        windows_class = win32gui.GetClassName(hwnd)
        #print(f"子窗口句柄: {hwnd}, 标题: {window_title}, 类名：{windows_class}")
        if param[0] in window_title and param[1].upper() in windows_class.upper():
            param[2].append(hwnd)

    def slot_btn1(self):
        # 'GameOfMir引擎控制台 [神龙冰雪 D:\\mir2\\Mirserver_神龙冰雪_7020\\]'
        引擎控制台列表 = []
        lparam = [f'引擎控制台*{self.lineEdit_mainDir.text().rsplit("_", 1)[0]}', 'TFrmMain', 引擎控制台列表]
        win32gui.EnumWindows(self.enum_windows_find, lparam)
        引擎控制台列表 = lparam[2]
        if len(引擎控制台列表) < 1:
            try:
                subprocess.Popen(self.lineEdit_workDir.text() + '\\' + self.lineEdit_mainDir.text() +'\\GameOfMir引擎控制器.exe', creationflags=subprocess.DETACHED_PROCESS)
            except:
                subprocess.Popen(
                    self.lineEdit_workDir.text() + '\\' + self.lineEdit_mainDir.text() + '\\GameCenter.exe', creationflags=subprocess.DETACHED_PROCESS)
            最小端口_月 = int(self.lineEdit_minDir.text().rsplit('_', 1)[1]) if self.lineEdit_minDir.text() else None
            最大端口_月 = int(self.lineEdit_maxDir.text().rsplit('_', 1)[1]) if self.lineEdit_minDir.text() else None
            最小端口_周 = int(self.lineEdit_minDir_1.text().rsplit('_', 1)[1]) if self.lineEdit_minDir_1.text() else None
            最大端口_周 = int(self.lineEdit_maxDir_1.text().rsplit('_', 1)[1]) if self.lineEdit_minDir_1.text() else None
            最小端口_日 = int(self.lineEdit_minDir_2.text().rsplit('_', 1)[1]) if self.lineEdit_minDir_2.text() else None
            最大端口_日 = int(self.lineEdit_maxDir_2.text().rsplit('_', 1)[1]) if self.lineEdit_minDir_2.text() else None
            if 最小端口_月 and 最大端口_月:
                for i in range(最小端口_月, 最大端口_月 + 1):
                    try:
                        subprocess.Popen(self.lineEdit_workDir.text() + '\\' + self.lineEdit_minDir.text().replace(f'{最小端口_月}', str(i)) + '\\GameOfMir引擎控制器.exe', creationflags=subprocess.DETACHED_PROCESS)
                    except:
                        subprocess.Popen(
                            self.lineEdit_workDir.text() + '\\' + self.lineEdit_minDir.text().replace(f'{最小端口_月}',
                                                                                                  str(i)) + '\\GameCenter.exe', creationflags=subprocess.DETACHED_PROCESS)
            if 最小端口_周 and 最大端口_周:
                for i in range(最小端口_周, 最大端口_周 + 1):
                    try:
                        subprocess.Popen(self.lineEdit_workDir.text() + '\\' + self.lineEdit_minDir_1.text().replace(f'{最小端口_周}', str(i)) + '\\GameOfMir引擎控制器.exe', creationflags=subprocess.DETACHED_PROCESS)
                    except:
                        subprocess.Popen(
                            self.lineEdit_workDir.text() + '\\' + self.lineEdit_minDir_1.text().replace(f'{最小端口_周}',
                                                                                                  str(i)) + '\\GameCenter.exe', creationflags=subprocess.DETACHED_PROCESS)
            if 最小端口_日 and 最大端口_日:
                for i in range(最小端口_日, 最大端口_日 + 1):
                    try:
                        subprocess.Popen(self.lineEdit_workDir_2.text() + '\\' + self.lineEdit_minDir_2.text().replace(f'{最小端口_日}', str(i)) + '\\GameOfMir引擎控制器.exe', creationflags=subprocess.DETACHED_PROCESS)
                    except:
                        subprocess.Popen(
                            self.lineEdit_workDir_2.text() + '\\' + self.lineEdit_minDir_2.text().replace(f'{最小端口_日}',
                                                                                                      str(i)) + '\\GameCenter.exe', creationflags=subprocess.DETACHED_PROCESS)
            self.引擎控制台状态 = not self.引擎控制台状态
        if self.引擎控制台状态:
            for index, 引擎控制台 in enumerate(引擎控制台列表):
                win32gui.ShowWindow(引擎控制台, win32con.SW_HIDE)
            self.引擎控制台状态 = not self.引擎控制台状态
        else:
            行 = 0
            列 = 0
            for index, 引擎控制台 in enumerate(引擎控制台列表):
                win32gui.ShowWindow(引擎控制台, win32con.SW_NORMAL)
                left, top, right, bottom = win32gui.GetWindowRect(引擎控制台列表[0])
                x = (列 + index) * (right - left)
                y = 行 * (bottom - top)
                if x + (right - left) > self.screen_width:
                    行 += 1
                    列 -= (index + 1)
                win32gui.SetWindowPos(引擎控制台, win32con.HWND_TOP, x, y, right - left, bottom - top, win32con.SWP_NOZORDER)
            self.引擎控制台状态 = not self.引擎控制台状态

    def slot_btn2(self):
        M2引擎列表 = []
        lparam = ['[商业版]', 'TFrmMain', M2引擎列表]
        win32gui.EnumWindows(self.enum_windows_find, lparam)
        M2引擎列表 = lparam[2]
        if self.引擎控制台状态:
            for 引擎控制台 in M2引擎列表:
                win32gui.ShowWindow(引擎控制台, win32con.SW_HIDE)
            self.引擎控制台状态 = not self.引擎控制台状态
        else:
            行 = 0
            列 = 0
            for index, 引擎控制台 in enumerate(M2引擎列表):
                win32gui.ShowWindow(引擎控制台, win32con.SW_SHOW)
                left, top, right, bottom = win32gui.GetWindowRect(M2引擎列表[0])
                x = (列 + index) * (right - left)
                y = 行 * (bottom - top)
                if x + (right - left) > self.screen_width:
                    行 += 1
                    列 -= (index + 1)
                win32gui.SetWindowPos(引擎控制台, win32con.HWND_TOP, x, y, right - left, bottom - top, win32con.SWP_NOZORDER)
                子窗口列表 = []
                lparam = ['', 'TJvRichEdit', 子窗口列表]
                win32gui.EnumChildWindows(引擎控制台, self.enum_child_windows_find, lparam)
                if len(子窗口列表):
                    hwnd = 子窗口列表[0]  # 获取第一个子窗口句柄
                    # 要追加的文本
                    # 获取窗口的进程ID
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    # 使用 psutil 获取进程信息
                    process = psutil.Process(pid)
                    # 获取进程路径
                    process_path = process.exe()+'\r\n'  # 返回进程的可执行文件路径
                    # 将光标移动到文本末尾
                    win32gui.SendMessage(hwnd, win32con.EM_SETSEL, -1, -1)
                    # 追加文本（保留格式）
                    win32gui.SendMessage(hwnd, win32con.EM_REPLACESEL, True, process_path.encode('utf-16le'))
            self.引擎控制台状态 = not self.引擎控制台状态

    def slot_btn3(self):
        def enum_child_windows(hwnd, lparam):
            window_title = win32gui.GetWindowText(hwnd)
            if lparam in window_title:
                if self.其它窗口状态:
                    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                else:
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
        list_1 = ['数据库服务器', '帐号登录服务器', '引擎日志服务器', '游戏网关', '角色网关', '登录网关', '[商业版]']
        list_2 = ['Dbserver', 'Loginsrv', 'Logdataserver', 'Rungate', 'Selgate', 'Logingate', 'M2server']
        if self.comboBox.currentText() == '全部':
            窗口title_list = list_1
            窗口title_list_ = list_2
        else:
            server_dict = dict(zip(list_1, list_2))
            窗口title_list = [self.comboBox.currentText()]
            窗口title_list_ = [server_dict[self.comboBox.currentText()]]
        for 窗口title in 窗口title_list:
            lparam = 窗口title
            win32gui.EnumWindows(enum_child_windows, lparam)
        for 窗口title in 窗口title_list_:
            lparam = 窗口title
            win32gui.EnumWindows(enum_child_windows, lparam)
        self.其它窗口状态 = not self.其它窗口状态

    def slot_start(self):
        if self.开合区状态:
            self.pushButton_start.setText('运行')
            for w in self.findChildren(QLineEdit):
                w.setDisabled(False)
            self.pushButton_start.setDisabled(False)
            self.pushButton_4.setDisabled(False)
            self.pushButton_select_listfile.setDisabled(False)
            self.开合区状态 = not self.开合区状态
            self.thread.stop()
        else:
            self.pushButton_start.setText('停止')
            for w in self.findChildren(QLineEdit):
                w.setDisabled(True)
            self.pushButton_4.setDisabled(True)
            self.pushButton_select_listfile.setDisabled(True)
            self.开合区状态 = not self.开合区状态
            # 创建子线程和 Worker 对象
            self.thread = SubWorkerThread({
                '数据库版本': self.lineEdit_db_version.text(),
                '工作目录': self.lineEdit_workDir.text(),
                '主区文件夹_月': self.lineEdit_mainDir.text(),
                '小区文件夹_月': self.lineEdit_minDir.text(),
                '大区文件夹_月': self.lineEdit_maxDir.text(),
                '合区文件夹_月': self.lineEdit_thisDir.text(),
                '合区时间_月': self.lineEdit_workTime.text(),
                '小区文件夹_周': self.lineEdit_minDir_1.text(),
                '大区文件夹_周': self.lineEdit_maxDir_1.text(),
                '合区文件夹_周': self.lineEdit_thisDir_1.text(),
                '合区时间_周': self.lineEdit_workTime_1.text(),
                '小区文件夹_日': self.lineEdit_minDir_2.text(),
                '大区文件夹_日': self.lineEdit_maxDir_2.text(),
                '合区文件夹_日': self.lineEdit_thisDir_2.text(),
                '合区时间_日': self.lineEdit_workTime_2.text(),
                '列表文件': self.label_listfile.text(),
                '合区工具': self.label_6.text(),
                '清空文件夹一': self.label_dir_1.text(),
                '清空文件夹二': self.label_dir_2.text(),
                '删除文件一': self.label_file_1.text(),
                '删除文件二': self.label_file_2.text(),
                '删除文件三': self.label_file_3.text(),
                '删除文件四': self.label_file_4.text()
                                           })
            self.thread.msg.connect(self.updateMsg)
            self.thread.start()

    def updateMsg(self, msg):
        if msg:
            self.log.log(msg)
            thistime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            msg = f'<span style="color: green;">{thistime}：</span><span style="color: blue;">{msg}</span>'
            self.textBrowser_log.append(msg)
        else:
            self.getthisDir(合区类型='月')
            self.getthisDir(合区类型='周')
            self.getthisDir(合区类型='日')

    def slot_select_file(self):
        # 打开文件选择对话框
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', '', '所有文件 (*);;文本文件 (*.txt)')
        if file_name:
            self.label_6.setText(f'{file_name}')

    def slot_select_listfile(self):
        # 打开文件选择对话框
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', '', '所有文件 (*);;文本文件 (*.txt)')
        if file_name:
            self.label_listfile.setText(f'{file_name}')
            self.getthisDir(合区类型='周')
            self.getthisDir(合区类型='日')

    def toggle_ui(self, enabled):
        """ 启用/禁用 UI 控件 """
        self.pushButton_clone.setDisabled(not enabled)
        self.lineEdit_workDir_2.setDisabled(not enabled)
        self.lineEdit_mainDir_2.setDisabled(not enabled)
        self.lineEdit_minPort.setDisabled(not enabled)
        self.lineEdit_maxPort.setDisabled(not enabled)

    def slot_clone(self):
        """ 开始克隆 """
        self.pushButton_clone.setDisabled(True)
        self.statusbar.showMessage('开始克隆...')

        # 获取参数
        src = self.lineEdit_workDir_2.text() + '\\' + self.lineEdit_mainDir_2.text()
        dstPath = self.lineEdit_workDir_2.text() + '\\' + self.lineEdit_mainDir_2.text().rsplit('_', 1)[0] + '_'
        minPort = int(self.lineEdit_minPort.text())
        maxPort = int(self.lineEdit_maxPort.text())

        # 创建并启动线程
        self.clone_thread = CloneThread(src, dstPath, minPort, maxPort)
        self.clone_thread.update_status.connect(self.statusbar.showMessage)  # 更新状态栏
        self.clone_thread.update_ui.connect(self.toggle_ui)  # 启用/禁用 UI
        self.clone_thread.start()

    def closeEvent(self, event) -> None:
        try:
            self.hide()
        except:
            pass


    def slot_select_dir_1(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, '选择文件夹', '')
        if folder_path:
            if 'Mir200' in folder_path:
                folder_path = folder_path.split('Mir200')[1]
            self.label_dir_1.setText(f'{folder_path}')

    def slot_select_dir_2(self):
        ...

    def slot_select_file_1(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', '', '所有文件 (*);;文本文件 (*.txt)')
        if file_name:
            file_name = file_name.split('Mir200')[1]
            self.label_file_1.setText(f'{file_name}')

    def slot_select_file_2(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', '', '所有文件 (*);;文本文件 (*.txt)')
        if file_name:
            file_name = file_name.split('Mir200')[1]
            self.label_file_2.setText(f'{file_name}')

    def slot_select_file_3(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', '', '所有文件 (*);;文本文件 (*.txt)')
        if file_name:
            file_name = file_name.split('Mir200')[1]
            self.label_file_3.setText(f'{file_name}')

    def slot_select_file_4(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择文件', '', '所有文件 (*);;文本文件 (*.txt)')
        if file_name:
            file_name = file_name.split('Mir200')[1]
            self.label_file_4.setText(f'{file_name}')