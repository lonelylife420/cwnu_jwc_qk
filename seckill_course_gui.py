from PySide2.QtWidgets import *
from PySide2.QtUiTools import *
from PySide2.QtCore import *
from PySide2.QtCore import QThread
import requests,json,os,time
requests.packages.urllib3.disable_warnings()  # 屏蔽ssl-warnings

class SecKillThread(QThread):
    global mainWindow
    result = Signal()
    def __init__(self):
        QThread.__init__(self)
 
    def run(self) -> None:
        while (mainWindow.isOK):
            if mainWindow.demo.Get_Surplus():
               if mainWindow.demo.Select_Lesson():
                    mainWindow.isOK = False
            mainWindow.ui.log_plain.ensureCursorVisible()
            time.sleep(float(mainWindow.ui.yc_time.toPlainText())/1000)

class MainWindow(QThread):
    def __init__(self):
        self.isOK = True
        qfile = QFile('./cwnu_gui.ui')
        qfile.open(QFile.ReadOnly)
        qfile.close()
        self.ui = QUiLoader().load(qfile)
        self.ui.initButton.clicked.connect(self.Init_config)
        
        

    def Init_config(self):
        cookie = self.Get_Cookie()
        self.demo = secKill(cookie)
        self.secKillThread = SecKillThread()
        self.ui.select_type.currentIndexChanged.connect(
            self.Set_SelectedLessonOption)
        self.ui.all_course.currentIndexChanged.connect(
            self.Set_SelectedLessonID)
        self.Set_SelectedLessonOption()
        self.ui.startButton.clicked.connect(self.Start)
        self.ui.stopButton.clicked.connect(self.Stop)
        
        

    def Get_Cookie(self):
        cookie = self.ui.cookie_plain.toPlainText()
        try:
            cookie.replace("Cookie:", "")
            if (cookie[0] == ' '):
                cookie.strip()
            new_cookie = {item.split('=')[0]: item.split(
                '=')[1] for item in cookie.split('; ')}
            self.Log_Print("读取cookie正常")
            return new_cookie
        except:
            self.Log_Print("cookie有误，请重新输入")

    def Log_Print(self, content):
        self.ui.log_plain.append(content)
        self.ui.log_plain.ensureCursorVisible()

    def Set_Combox_addItem(self, obj, content):
        obj.addItem(f'{content}')

    def Set_SelectedLessonOption(self):
        self.demo.SelectedLessonOption = int(self.ui.select_type.currentText().split(
            ':')[-1])
        self.demo.Get_ItemsList()

    def Set_SelectedLessonID(self):
        self.demo.lessonAssoc = int(self.ui.all_course.currentText().split(':')[-1])
        print(self.demo.lessonAssoc)

    def Start(self):
        self.isOK = True
        self.secKillThread.start()
    
    def Stop(self):
        self.isOK = False


class secKill():
    global mainWindow
    cookies = {}
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8',
        'Connection': 'keep-alive',
        'Origin': 'https://webvpn.cwnu.edu.cn:8106',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    studentId = 0
    SelectedLessonOption = 0
    PredictionId = ""
    lessonAssoc = 0
    lessonName = ""
    limitNum = {}

    def __init__(self, cookie) -> None:
        try:
            self.cookies = cookie
            self.Get_StudentId()
            self.Get_UserInfo()
            self.Get_LessonOptions()

        except Exception as e:
            print(f"[-]初始化失败：{e}")

    def Get_StudentId(self):
        response = requests.get('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/for-std/exam-arrange',
                                cookies=self.cookies, headers=self.headers, allow_redirects=False)
        if response.status_code == 302:
            result = response.headers['Location']
            self.studentId = int(result.split('/')[-1])
            if (self.studentId != 0 and self.studentId != "exam-arrange"):
                mainWindow.Log_Print(f"[+]获取StudentId成功:{self.studentId}")
            else:
                mainWindow.Log_Print(f"[-]获取StudentId失败")

    def Get_UserInfo(self):
        # 获取用户信息
        response = requests.get(
            'https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/student/home-page/students?vpn-12-o2-jwxt.cwnu.edu.cn', cookies=self.cookies, headers=self.headers)
        UserInfo = response.json()
        if response.status_code == 200:
            name = UserInfo['person']['name']
            code = UserInfo['cultivateTypeList'][0]['code']
            grade = UserInfo['cultivateTypeList'][0]['grade']
            department = UserInfo['cultivateTypeList'][0]['department']
            major = UserInfo['cultivateTypeList'][0]['major']
            adminClass = UserInfo['cultivateTypeList'][0]['adminClass']
            mainWindow.Log_Print("[+]获取用户信息成功")
            mainWindow.Log_Print(
                f"姓名：{name} 学号：{code} 学院：{department} 专业：{major} 班级：{adminClass}")

        else:
            mainWindow.Log_Print("[-]获取用户信息失败")

    def Get_LessonOptions(self):
        # 获取选课项目类型
        data = {
            'bizTypeId': '2',
            'studentId': f'{self.studentId}',
        }

        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/open-turns?vpn-12-o2-jwxt.cwnu.edu.cn',
                                 cookies=self.cookies, headers=self.headers, data=data)
        if response.status_code == 200:
            Options = (response.json())
            OptionsNum = len(Options)
            mainWindow.Log_Print(f"[+]获取到{OptionsNum}个选项")
            mainWindow.ui.select_type.clear()
            for index in range(OptionsNum):
                mainWindow.Set_Combox_addItem(
                    mainWindow.ui.select_type, f"[{index + 1}]{Options[index]['name']}| ID:{Options[index]['id']}")
        else:
            mainWindow.Log_Print("[-]获取选课项目失败")

    def Get_ItemsList(self):
        # 获取待选课程列表ID
        response = requests.get(
            f'https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/cache/course-select/version/{self.SelectedLessonOption}/version.json?vpn-12-o2-jwxt.cwnu.edu.cn&_=1694279005732', cookies=self.cookies, headers=self.headers, verify=False)
        if (response.status_code == 200):
            self.Get_SelectedLessons(response.json()['itemList'][0])
        else:
            mainWindow.Log_Print("[-]获取总选课表失败")

    def Get_SelectedLessons(self, ListId):
        # 获取待选课程列表
        response = requests.get(f'https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/cache/course-select/addable-lessons/{self.SelectedLessonOption}/{ListId}.json?vpn-12-o2-jwxt.cwnu.edu.cn',
                                cookies=self.cookies, headers=self.headers)
        if (response.status_code == 200):
            response.encoding = response.apparent_encoding
            Lessons = json.loads(response.json()['data'])
            LessonsNum = len(Lessons)
            mainWindow.Log_Print(f"[+]获取到{LessonsNum}个选项")
            mainWindow.ui.all_course.clear()
            for index in range(LessonsNum):
                LessonName = Lessons[index]['course']['nameZh']
                LessonId = Lessons[index]['id']
                self.limitNum[f'{LessonId}'] = Lessons[index]['limitCount']
                mainWindow.Set_Combox_addItem(
                    mainWindow.ui.all_course, f"[{index+1}]{LessonName}| ID:{LessonId}")
        else:
            mainWindow.Log_Print(f"[-]获取所有课程失败")

    def Get_AddPredicate(self):
        # 获取选课序列
        json_data = {
            'studentAssoc': self.studentId,
            'courseSelectTurnAssoc': self.SelectedLessonOption,
            'requestMiddleDtos': [
                {
                    'lessonAssoc': self.lessonAssoc,
                    'virtualCost': 0,
                    'scheduleGroupAssoc': None,
                },
            ],
            'coursePackAssoc': None,
        }
        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/add-predicate?vpn-12-o2-jwxt.cwnu.edu.cn',
                                 cookies=self.cookies, headers=self.headers, json=json_data)
        if response.status_code == 200:
            mainWindow.Log_Print("[+]获取选课序列成功")
            self.PredictionId = response.text
        else:
            mainWindow.Log_Print("[-]获取选课序列失败")

    def Get_PredicateResponse(self):
        # 获取序列响应
        data = {
            'studentId': f'{self.studentId}',
            'requestId': f'{self.PredictionId}',
        }
        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/predicate-response?vpn-12-o2-jwxt.cwnu.edu.cn',
                                 cookies=self.cookies, headers=self.headers, data=data)
        if response.status_code == 200:
            mainWindow.Log_Print("[+]获取选课序列结果成功")
            return response.json()['result'][f'{self.lessonAssoc}']

        else:
            mainWindow.Log_Print("[-]获取选课序列结果失败")
            return "error"

    def Get_AddDropResponse(self):
        data = {
            'studentId': f'{self.studentId}',
            'requestId': f'{self.PredictionId}',
        }

        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/add-drop-response?vpn-12-o2-jwxt.cwnu.edu.cn',
                                 cookies=self.cookies, headers=self.headers, data=data)
        if response.status_code == 200:
            mainWindow.Log_Print("[+]获取选课最终结果成功")
            result = response.json()
            if result['success'] == False:
                mainWindow.Log_Print(
                    f"[-]选课结果:{result['errorMessage']['textZh']}")
            else:
                mainWindow.Log_Print(f"[!]选课结果:选课成功，请前往[已选课程]确认.")
        else:
            mainWindow.Log_Print("[-]获取选课最终结果失败")

    def Get_AddRequest(self):
        # 获取选课序列
        json_data = {
            'studentAssoc': self.studentId,
            'courseSelectTurnAssoc': self.SelectedLessonOption,
            'requestMiddleDtos': [
                {
                    'lessonAssoc': self.lessonAssoc,
                    'virtualCost': 0,
                    'scheduleGroupAssoc': None,
                },
            ],
            'coursePackAssoc': None,
        }

        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/add-request?vpn-12-o2-jwxt.cwnu.edu.cn',
                                 cookies=self.cookies, headers=self.headers, json=json_data)
        if response.status_code == 200:
            mainWindow.Log_Print("[+]获取选课序列成功")
            self.PredictionId = response.text
        else:
            mainWindow.Log_Print("[-]获取选课序列失败")

    def Select_Lesson(self):
        self.Get_AddPredicate()
        result = self.Get_PredicateResponse()
        if result == None and result != "error":
            self.Get_AddRequest()
            self.Get_AddDropResponse()
            return True
        elif result == "error":
            mainWindow.Log_Print(f"[-]选课结果:请求出错")
        else:    
            mainWindow.Log_Print(f"[-]选课结果:{result['textZh']}")
        return False
    
    def Get_Surplus(self):
        # 查看已选课程剩余可选数
        data = {
            'lessonIds[]': [
                f'{self.lessonAssoc}',
            ],
        }

        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/std-count?vpn-12-o2-jwxt.cwnu.edu.cn',
                                 cookies=self.cookies, headers=self.headers, data=data)
        selectedNum = int(response.json()[f'{self.lessonAssoc}'].split('-')[0])
        mainWindow.Log_Print(f"[+]剩余可选人数:{self.limitNum[f'{self.lessonAssoc}'] - selectedNum}")
        if self.limitNum[f'{self.lessonAssoc}'] - selectedNum > 0:
            return True
        else:
            return False

if __name__ == "__main__":
    app = QApplication([])
    mainWindow = MainWindow()
    mainWindow.ui.show()
    app.exec_()
    os.system("pause")