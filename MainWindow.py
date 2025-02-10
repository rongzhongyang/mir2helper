import datetime
import MainWindowUI
from PyQt6 import QtWidgets
from PyQt6.QtGui import QIcon, QPixmap
import subprocess
import icon
from ctypes import *
import win32gui
import win32con
import win32api
import configparser
from MyThread import SubWorkerThread, CloneThread


class TBBUTTON(Structure):
    _pack_ = 1
    _fields_ = [
        ('iBitmap', c_int),
        ('idCommand', c_int),
        ('fsState', c_ubyte),
        ('fsStyle', c_ubyte),
        ('bReserved', c_ubyte * 2),
        ('dwData', c_ulong),
        ('iString', c_int),
    ]


class TEXT(Structure):
    _fields_ = [
        ('value', c_char * 128),
        ('raw', c_char * 128)
    ]


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


# set_icon()


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
        # 读配置文件
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.lineEdit_workDir.setText(config['conf']['工作目录'])
        self.lineEdit_workDir_2.setText(config['conf']['工作目录'])
        self.lineEdit_mainDir.setText(config['conf']['主区文件夹'])
        self.lineEdit_mainDir_2.setText(config['conf']['主区文件夹'])
        self.lineEdit_minDir.setText(config['conf']['小区文件夹'])
        self.lineEdit_maxDir.setText(config['conf']['大区文件夹'])
        self.lineEdit_thisDir.setText(config['conf']['合区文件夹'])
        self.lineEdit_workTime.setText(config['conf']['合区时间'])
        self.lineEdit_minPort.setText(config['conf']['最小端口'])
        self.lineEdit_maxPort.setText(config['conf']['最大端口'])
        self.label_6.setText(config['conf']['合区工具'])
        self.label_listfile.setText(config['conf']['列表文件'])
        # 禁用窗口最大化按钮
        self.setWindowTitle("航界软件 0.0.1")
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

    def enum_windows_find(self, hwnd, lparam):
        '''依据窗口标题 和窗口类名称 查询窗口'''
        windows_title = win32gui.GetWindowText(hwnd)
        windows_class = win32gui.GetClassName(hwnd)
        if lparam[0] in windows_title and lparam[1] in windows_class:
            lparam[2].append(hwnd)

    def enum_child_windows_find(self, hwnd, param):
        '''依据主窗口handle, 查询 标题为param[0]的子窗口 赋值到param[1]'''
        window_title = win32gui.GetWindowText(hwnd)
        print(f"子窗口句柄: {hwnd}, 标题: {window_title}")
        if param[0] in window_title:
            param[1] = hwnd

    def slot_btn1(self):
        # 'GameOfMir引擎控制台 [神龙冰雪 D:\\mir2\\Mirserver_神龙冰雪_7020\\]'
        引擎控制台列表 = []
        lparam = ['GameOfMir引擎控制台', 'TFrmMain', 引擎控制台列表]
        win32gui.EnumWindows(self.enum_windows_find, lparam)
        引擎控制台列表 = lparam[2]
        if self.引擎控制台状态:
            for index, 引擎控制台 in enumerate(引擎控制台列表):
                win32gui.ShowWindow(3280844, win32con.SW_HIDE)
                win32gui.ShowWindow(引擎控制台, win32con.SW_HIDE)
                print(win32gui.GetParent(引擎控制台))

            self.引擎控制台状态 = not self.引擎控制台状态
        else:
            行 = 0
            列 = 0
            for index, 引擎控制台 in enumerate(引擎控制台列表):
                win32gui.ShowWindow(引擎控制台, win32con.SW_NORMAL)
                win32gui.ShowWindow(3280844, win32con.SW_NORMAL)
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
                win32gui.ShowWindow(引擎控制台, win32con.SW_MINIMIZE)
            self.引擎控制台状态 = not self.引擎控制台状态
        else:
            for 引擎控制台 in M2引擎列表:
                win32gui.ShowWindow(引擎控制台, win32con.SW_NORMAL)
            self.引擎控制台状态 = not self.引擎控制台状态

    def slot_btn3(self):

        def enum_child_windows(hwnd, lparam):
            window_title = win32gui.GetWindowText(hwnd)
            if lparam in window_title:
                if self.其它窗口状态:
                    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                else:
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

        for 窗口title in ['数据库服务器', '帐号登录服务器', '引擎日志服务器', '游戏网关', '角色网关', '登录网关', '[商业版]']:
            lparam = 窗口title
            win32gui.EnumWindows(enum_child_windows, lparam)
        for 窗口title in ['Dbserver', 'Loginsrv', 'Logdataserver', 'Rungate', 'Selgate', 'Logingate', 'M2server']:
            lparam = 窗口title
            win32gui.EnumWindows(enum_child_windows, lparam)
        self.其它窗口状态 = not self.其它窗口状态

    def slot_start(self):
        if self.开合区状态:
            self.pushButton_start.setText('运行')
            self.pushButton_start.setDisabled(False)
            self.lineEdit_workDir.setDisabled(False)
            self.lineEdit_mainDir.setDisabled(False)
            self.lineEdit_minDir.setDisabled(False)
            self.lineEdit_maxDir.setDisabled(False)
            self.lineEdit_thisDir.setDisabled(False)
            self.lineEdit_workTime.setDisabled(False)
            self.pushButton_4.setDisabled(False)
            self.pushButton_select_listfile.setDisabled(False)
            self.开合区状态 = not self.开合区状态
            self.thread.exit()
        else:
            self.pushButton_start.setText('停止')
            # 写配置文件
            config = configparser.ConfigParser()
            config['conf'] = {
                '工作目录': self.lineEdit_workDir.text(),
                '主区文件夹': self.lineEdit_mainDir.text(),
                '小区文件夹': self.lineEdit_minDir.text(),
                '大区文件夹': self.lineEdit_maxDir.text(),
                '合区文件夹': self.lineEdit_thisDir.text(),
                '合区时间': self.lineEdit_workTime.text(),
                '列表文件': self.label_listfile.text(),
                '最小端口': self.lineEdit_minPort.text(),
                '最大端口': self.lineEdit_maxPort.text(),
                '合区工具': self.label_6.text()
            }
            with open('config.ini', 'w', encoding='gbk') as configfile:
                config.write(configfile)
            self.lineEdit_workDir.setDisabled(True)
            self.lineEdit_mainDir.setDisabled(True)
            self.lineEdit_minDir.setDisabled(True)
            self.lineEdit_maxDir.setDisabled(True)
            self.lineEdit_thisDir.setDisabled(True)
            self.lineEdit_workTime.setDisabled(True)
            self.pushButton_4.setDisabled(True)
            self.pushButton_select_listfile.setDisabled(True)
            self.开合区状态 = not self.开合区状态
            # 创建子线程和 Worker 对象
            self.thread = SubWorkerThread({
                '工作目录': self.lineEdit_workDir.text(),
                '主区文件夹': self.lineEdit_mainDir.text(),
                '小区文件夹': self.lineEdit_minDir.text(),
                '大区文件夹': self.lineEdit_maxDir.text(),
                '合区文件夹': self.lineEdit_thisDir.text(),
                '合区时间': self.lineEdit_workTime.text(),
                '列表文件': self.label_listfile.text(),
                '合区工具': self.label_6.text()
                                           })
            self.thread.msg.connect(self.updateMsg)
            self.thread.start()

    def updateMsg(self, msg):
        msg = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "->" + msg
        self.textBrowser_log.append(msg)

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
