import requests,json,re,os
import time
requests.packages.urllib3.disable_warnings() #屏蔽ssl-warnings

class secKill():
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

    def __init__(self,cookie) -> None:
        try:
            self.cookies = cookie
            self.Get_StudentId()
            self.Get_UserInfo()
            self.Get_LessonOptions()
            self.Get_ItemsList()
        except Exception as e:
            print(f"[-]初始化失败：{e}")
    
    def Get_StudentId(self):
        response = requests.get('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/for-std/course-select/single-student/turns', cookies=self.cookies, headers=self.headers)
        result = re.search('studentId:(.*?),',response.text)
        
        self.studentId  = int(result.group()[11:-1])

    def Get_UserInfo(self):
        #获取用户信息
        response = requests.get('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/student/home-page/students?vpn-12-o2-jwxt.cwnu.edu.cn', cookies=self.cookies, headers=self.headers)
        UserInfo = response.json()
        if response.status_code == 200:
            name = UserInfo['person']['name']
            code = UserInfo['cultivateTypeList'][0]['code']
            grade = UserInfo['cultivateTypeList'][0]['grade']
            department = UserInfo['cultivateTypeList'][0]['department']
            major = UserInfo['cultivateTypeList'][0]['major']
            adminClass = UserInfo['cultivateTypeList'][0]['adminClass']
            print("[+]获取用户信息成功")
            print(f"姓名：{name}\t学号：{code}\t学院：{department}\t专业：{major}\t班级：{adminClass}")
            
        else:
            print("[-]获取用户信息失败")

    def Get_LessonOptions(self):
        #获取选课项目类型
        data = {
            'bizTypeId': '2',
            'studentId': f'{self.studentId}',
        }

        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/open-turns?vpn-12-o2-jwxt.cwnu.edu.cn',
                                 cookies=self.cookies, headers=self.headers, data=data)
        if response.status_code == 200:
            Options = (response.json())
            OptionsNum = len(Options)
            print(f"[+]获取到以下{OptionsNum}个选项")
            for index in range(OptionsNum):
                print(f"[{index + 1}]{Options[index]['name']}| ID:{Options[index]['id']}")

            #选择选课项目类型
            selected = input('请输入选课类型序号:')
            while(not selected.isdigit):
                selected = input('输入有误,请输入选课类型序号:')
            self.SelectedLessonOption = Options[int(selected) - 1]['id']

        else:
            print("[-]获取选课项目失败")
    
    def Get_ItemsList(self):
        #获取待选课程列表ID
        response = requests.get(f'https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/cache/course-select/version/{self.SelectedLessonOption}/version.json?vpn-12-o2-jwxt.cwnu.edu.cn&_=1694279005732', cookies=self.cookies, headers=self.headers, verify=False)
        if(response.status_code==200):
            self.Get_SelectedLessons(response.json()['itemList'][0])       
        else:
            print("[-]获取总选课表失败")

    def Get_SelectedLessons(self,ListId):
        #获取待选课程列表
        response = requests.get(f'https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/cache/course-select/addable-lessons/{self.SelectedLessonOption}/{ListId}.json?vpn-12-o2-jwxt.cwnu.edu.cn',
                                 cookies=self.cookies, headers=self.headers)
        if(response.status_code == 200):
            response.encoding = response.apparent_encoding
            Lessons = json.loads(response.json()['data'])
            LessonsNum = len(Lessons)
            print(f"[+]获取到以下{LessonsNum}个选项")
            for i in range(LessonsNum):
                LessonName = Lessons[i]['course']['nameZh']
                LessonId = Lessons[i]['id']
                self.limitNum[f'{LessonId}'] = Lessons[i]['limitCount']
                print(f"[{i + 1}]{LessonName}| ID:{LessonId}")

            #选择课程
            selected = input('请输入课程序号:')
            while(not selected.isdigit):
                selected = input('输入有误,请输入课程序号:')
            self.lessonAssoc = Lessons[int(selected) - 1]['id']
        else:
            print(f"[-]获取所有课程失败")

    def Get_AddPredicate(self):
        #获取选课序列
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

        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/add-predicate?vpn-12-o2-jwxt.cwnu.edu.cn', cookies=self.cookies, headers=self.headers, json=json_data)
        if response.status_code == 200:
            print("[+]获取选课序列成功")
            self.PredictionId = response.text
        else:
            print("[-]获取选课序列失败")    
            print(response.text)
                
    def Get_PredicateResponse(self):
        #获取序列响应
        data = {
            'studentId': f'{self.studentId}',
            'requestId': f'{self.PredictionId}',
        }
        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/predicate-response?vpn-12-o2-jwxt.cwnu.edu.cn', cookies=self.cookies, headers=self.headers, data=data)
        if response.status_code == 200:
            print("[+]获取选课序列结果成功")
            return response.json()['result'][f'{self.lessonAssoc}']

        else:
            print("[-]获取选课序列结果失败")
    
    def Get_AddDropResponse(self):
        data = {
            'studentId': f'{self.studentId}',
            'requestId': f'{self.PredictionId}',
        }

        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/add-drop-response?vpn-12-o2-jwxt.cwnu.edu.cn', cookies=self.cookies, headers=self.headers, data=data)
        if response.status_code == 200:
            print("[+]获取选课最终结果成功")
            result = response.json()
            if result['success'] == False:
                print(f"[-]选课结果:{result['errorMessage']['textZh']}")
            else:
                print(f"[!]选课结果:选课成功，请前往[已选课程]确认.")
        else:
            print("[-]获取选课最终结果失败")

    def Get_AddRequest(self):
        #获取选课序列
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

        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/add-request?vpn-12-o2-jwxt.cwnu.edu.cn', cookies=self.cookies, headers=self.headers, json=json_data)
        if response.status_code == 200:
            print("[+]获取选课序列成功")
            self.PredictionId = response.text
        else:
            print("[-]获取选课序列失败")    
            print(response.text)

    def Select_Lesson(self):
        self.Get_AddPredicate()
        result = self.Get_PredicateResponse()
        if result == None:
            self.Get_AddRequest()
            
            self.Get_AddDropResponse()
        else:
            print(f"[-]选课结果:{result['textZh']}")

    def Get_Surplus(self):
        #查看已选课程剩余可选数
        data = {
            'lessonIds[]': [
                f'{self.lessonAssoc}',
            ],
        }

        response = requests.post('https://webvpn.cwnu.edu.cn:8106/https/77726476706e69737468656265737421fae0598869337f5e6b468ca88d1b203b/student/ws/for-std/course-select/std-count?vpn-12-o2-jwxt.cwnu.edu.cn', cookies=self.cookies, headers=self.headers, data=data)
        selectedNum = int(response.json()[f'{self.lessonAssoc}'].split('-')[0])
        print(f"[+]剩余可选人数:{self.limitNum[f'{self.lessonAssoc}'] - selectedNum}")
        if self.limitNum[f'{self.lessonAssoc}'] - selectedNum > 0:
            return True
        else:
            return False

def PrintTitle():
    code = '''
     _____                    
    / ____|                   
    | |  __      ___ __  _   _ 
    | |  \ \ /\ / / '_ \| | | |  By:Gs
    | |___\ V  V /| | | | |_| | 
     \_____\_/\_/ |_| |_|\__,_|  注：仅供学习交流参考，请勿用于非法途径.
                                
    使用方法：填入cookie，选择需要监控的课程即可，请选择自己账号能选的课程，否则会异常。
    '''

    print(code)

def cookie_to_dic(cookie):
    cookie.replace("Cookie:", "")
    if (cookie[0] == ' '):
        cookie.strip()
    return {item.split('=')[0]: item.split('=')[1] for item in cookie.split('; ')}

if __name__ == "__main__": 
    PrintTitle()
    cookie = input("请输入cookie:")
    cookie = cookie_to_dic(cookie)
    try:
        demo = secKill(cookie)
        #初始化并配置完成调用Select_Lesson方法确定选课
        print("配置完成，开始监控：")
        flushTime = input("请输入监控间隔(单位：ms  1s = 1000ms):")
        while(not flushTime.isdigit()):
            flushTime = input("输入有误，请重新输入:")
        while(True):
            if demo.Get_Surplus():
                demo.Select_Lesson()
                break
            time.sleep(float(flushTime)/1000)
        print("[+]捡漏成功，已自动停止.")    
    
    except Exception as error:
        print("捕获到异常：",error)
    os.system("pause")
