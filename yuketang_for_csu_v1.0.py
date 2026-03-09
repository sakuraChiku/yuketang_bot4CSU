from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

def get_info() -> tuple[int, str, str]:
    """
    Return required infomation
    
    Returns:
        num (int): the number of the course
        csftoken (str): csftoken for cookie
        sessionid (str): sessionid for cookie
    """
    num = input('刷第几个课？(-1表示全刷): ')
    csftoken = 'your_token'
    sessionid = 'your_sessionid'
    return num, csftoken, sessionid

def mainpage_initialization(driver: webdriver.Chrome, csftoken: str, sessionid: str) -> None:
    """
    Open the browser
    Inject the cookies
    Refresh to enable the cookies

    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): the driver
        csftoken (str): csftoken for cookie
        sessionid (str): sessionid for cookie
    """
    # load the main page
    driver.get('https://bksycsu.yuketang.cn/pro/courselist')

    # insert cookies 这部分代码需要根据设备、平台不同，按需修改
    driver.add_cookie({'name': 'csrftoken', 'value': csftoken})
    driver.add_cookie({'name': 'platform_id', 'value': '3'})
    driver.add_cookie({'name': 'platform_type', 'value': '1'})
    driver.add_cookie({'name': 'sessionid', 'value': sessionid})
    driver.add_cookie({'name': 'university_id', 'value': '2952'})
    driver.add_cookie({'name': 'xtbz', 'value': 'cloud'})
    print(f"{time.asctime(time.localtime())} 已注入cookies, 刷新中……")
    time.sleep(2)
    driver.refresh()

def select_course(driver: webdriver.Chrome, num: int) -> None:
    """
    Select a course based on the number given
    
    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): the driver
        num (int): the number of the course
    """
    try:
        WebDriverWait(driver, 7).until(EC.presence_of_element_located(
            (By.XPATH, f'//*[@id="pane-student"]/div[2]/div/div[{num}]')
        ))
        course_name = driver.find_element(By.XPATH, f'//*[@id="pane-student"]/div[2]/div/div[{num}]//div[@class="top"]/h1').text
        course_host = driver.find_element(By.XPATH, f'//*[@id="pane-student"]/div[2]/div/div[{num}]//span[@class="className"]').text
        print(f"{time.asctime(time.localtime())} 已选择：{course_name} {course_host}")
        driver.find_element(By.XPATH, f'//*[@id="pane-student"]/div[2]/div/div[{num}]').click()

    except:
        driver.quit()
        print(f"{time.asctime(time.localtime())} 超时! 未找到相应课程")
    
def course_initialization(driver: webdriver.Chrome) -> None:
    """
    Check the latest incompleted task
    Get the basic infomation of the task
    Judge the type of the task
    Choose the method accordingly
    
    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): the driver
    """
    try:
        # check the first task marked as not completed, get the course type
        time.sleep(2)
        print(f"{time.asctime(time.localtime())} 刷新任务状态")
        driver.refresh()
        WebDriverWait(driver, 120).until(EC.presence_of_element_located(
            (By.XPATH, '//div[@class="progress-wrap fr"]/div[text()="未读" or text()="未开始" or text()="未发言"]')
        ))
        course_status = driver.find_element(By.XPATH, '//div[@class="progress-wrap fr"]/div[text()="未读" or text()="未开始" or text()="未发言"]')
        course_container = course_status.find_element(By.XPATH, 'ancestor::div[contains(@class, "el-tooltip leaf-detail")]')
        course_type = course_container.find_element(By.XPATH, './/i').get_attribute('class')

        # switch focus to the task page
        old_handles = driver.window_handles
        course_status.click()
        WebDriverWait(driver, 5).until(
            EC.number_of_windows_to_be(len(old_handles)+1)
        )
        new_handle = list(set(driver.window_handles)-set(old_handles))[0]
        driver.switch_to.window(new_handle)

        # wait for the title element
        WebDriverWait(driver, 120).until(EC.visibility_of_element_located(
            (By.XPATH, '//section[@class="title"]/div[1]')
        ))
        course_name = driver.find_element(By.XPATH, '//section[@class="title"]/div[1]').text

        # choose diffrent methods to deal with the task based on its type
        if course_type == 'iconfont icon--tuwen':
            print(f"{time.asctime(time.localtime())} 即将阅读文本《{course_name}》")
            read_document(driver)
        elif course_type == 'iconfont icon--taolun1':
            print(f"{time.asctime(time.localtime())} 即将在《{course_name}》中发言")
            make_a_comment(driver)
        elif course_type == 'iconfont icon--shipin':
            print(f"{time.asctime(time.localtime())} 即将播放《{course_name}》")
            play_video(driver)
        elif course_type == 'iconfont icon--zuoye':
            print(f"{time.asctime(time.localtime())} 即将运行《{course_name}》")
            answer_questions(driver)
        else:
            print('无法识别课程类型, 将进行下一个任务……')
            old_handles = driver.window_handles
            driver.close()
            WebDriverWait(driver, 5).until(
                EC.number_of_windows_to_be(len(old_handles)-1)
            )
            driver.switch_to.window(driver.window_handles[0])# switch focus to the video page
            course_initialization(driver)
        
    except:
        print("该课程已经全部刷完！")
        driver.back()
        time.sleep(3)

def play_video(driver: webdriver.Chrome) -> None:
    """
    Play the video
    change the speed
    print out video name
    print out the progress every 5 second
    check if the task is completed
    go to the next content
    
    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): the driver
    """
    # play and mute this video
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '//xt-speedvalue[@class="xt_video_player_common_value"]')
        )
    )
    title = driver.find_element(By.XPATH, '//div[@class="title-fl"]/span[1]').text
    print(f"{time.asctime(time.localtime())} 即将播放：《{title}》")
    time.sleep(1)
    play_button = driver.find_element(By.XPATH, '//xt-playbutton[contains(@class, "xt_video_player_play_btn")]')
    mute_button = driver.find_element(By.XPATH, '//xt-volumebutton[contains(@class, "xt_video_player_volume")]')
    ActionChains(driver)\
        .click(mute_button)\
        .click(play_button)\
        .perform()
    
    # monitor the progress every 10 seconds
    while True:
        current_time = driver.find_element(By.XPATH, '//xt-time[contains(@class, "xt_video_player_current_time_display")]/span[1]').text
        total_time = driver.find_element(By.XPATH, '//xt-time[contains(@class, "xt_video_player_current_time_display")]/span[2]').text
        seconds = 3600*int(current_time[0:2]) + 60*int(current_time[3:5]) + int(current_time[6:])
        total_seconds = 3600*int(total_time[0:2]) + 60*int(total_time[3:5]) + int(total_time[6:])
        progress = round(100 * seconds/total_seconds, 2)
        print(f"{time.asctime(time.localtime())} 播放进度：{progress}%")
        time.sleep(5)
        if progress == 100:
            print(f"{time.asctime(time.localtime())} 《{title}》已经播放完成")
            break
    
    time.sleep(2)

    # carry on the next task
    old_handles = driver.window_handles
    driver.close()
    WebDriverWait(driver, 5).until(
        EC.number_of_windows_to_be(len(old_handles)-1)
    )
    driver.switch_to.window(driver.window_handles[0])# switch focus to the video page
    time.sleep(1)
    course_initialization(driver)
    
def read_document(driver: webdriver.Chrome) -> None:
    """
    Read the document
    check if the task is completed
    go to the next content

    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): the driver
    """
    # aquire the title of the document
    time.sleep(1)
    course_name = driver.find_element(By.XPATH, '//section[@class="title"]/div[1]')
    course_name = course_name.text

    # carry on to the next task
    print(f"{time.asctime(time.localtime())} 已完成文档《{course_name}》的阅读，即将进行下一个任务……")
    time.sleep(1)
    old_handles = driver.window_handles
    driver.close()
    WebDriverWait(driver, 5).until(
        EC.number_of_windows_to_be(len(old_handles)-1)
    )
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    course_initialization(driver)

def answer_questions(driver: webdriver.Chrome) -> None:
    """
    due to the lack of a question bank, the questions has to be skipped

    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): the driver
    """
    time.sleep(3)
    # carry on to the next task
    print(f"{time.asctime(time.localtime())} 抱歉喵, 答题功能暂未开通喵QAQ")
    old_handles = driver.window_handles
    driver.close()
    WebDriverWait(driver, 5).until(
        EC.number_of_windows_to_be(len(old_handles)-1)
    )
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    course_initialization(driver)
    
def make_a_comment(driver: webdriver.Chrome) -> None:
    """
    Deliver a comment to the question
    
    Args:
        driver (selenium.webdriver.chrome.webdriver.WebDriver): the driver"""
    text_content = """CN No.1
    ⣿⣿⣿⣿⣿⠟⠋⠄⠄⠄⠄⠄⠄⠄⢁⠈⢻⢿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⠃⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⠈⡀⠭⢿⣿⣿⣿⣿
    ⣿⣿⣿⣿⡟⠄⢀⣾⣿⣿⣿⣷⣶⣿⣷⣶⣶⡆⠄⠄⠄⣿⣿⣿⣿
    ⣿⣿⣿⣿⡇⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠄⠄⢸⣿⣿⣿⣿
    ⣿⣿⣿⣿⣇⣼⣿⣿⠿⠶⠙⣿⡟⠡⣴⣿⣽⣿⣧⠄⢸⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣾⣿⣿⣟⣭⣾⣿⣷⣶⣶⣴⣶⣿⣿⢄⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣿⡟⣩⣿⣿⣿⡏⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣹⡋⠘⠷⣦⣀⣠⡶⠁⠈⠁⠄⣿⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣍⠃⣴⣶⡔⠒⠄⣠⢀⠄⠄⠄⡨⣿⣿⣿⣿⣿⣿
    ⣿⣿⣿⣿⣿⣿⣿⣦⡘⠿⣷⣿⠿⠟⠃⠄⠄⣠⡇⠈⠻⣿⣿⣿⣿
    ⣿⣿⣿⣿⡿⠟⠋⢁⣷⣠⠄⠄⠄⠄⣀⣠⣾⡟⠄⠄⠄⠄⠉⠙⠻
    ⡿⠟⠋⠁⠄⠄⠄⢸⣿⣿⡯⢓⣴⣾⣿⣿⡟⠄⠄⠄⠄⠄⠄⠄⠄
    ⠄⠄⠄⠄⠄⠄⠄⣿⡟⣷⠄⠹⣿⣿⣿⡿⠁⠄⠄⠄⠄⠄⠄⠄⠄"""
    # check if the textbar exists
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'el-textarea__inner')
    ))

    # make a comment
    text_bar = driver.find_element(By.CLASS_NAME, 'el-textarea__inner')
    ActionChains(driver)\
        .scroll_to_element(text_bar)\
        .click(text_bar)\
        .pause(1)\
        .send_keys(text_content)\
        .perform()
    send = driver.find_element(By.CLASS_NAME, 'postRight')
    send.click()
    time.sleep(1)

    # check if the task if completed
    WebDriverWait(driver, 7).until(EC.presence_of_element_located((
        By.XPATH,
        '//div[contains(@class,"progress-wrap")]//div[contains(text(),"已发言")]'
    ))
    )
    print(f"{time.asctime(time.localtime())} 已完成《讨论题》")

    # carry on to the next task
    old_handles = driver.window_handles
    driver.close()
    WebDriverWait(driver, 5).until(
        EC.number_of_windows_to_be(len(old_handles)-1)
    )
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    course_initialization(driver)
    
def main():
    num, csftoken, sessionid = get_info()
    if num and csftoken and sessionid:
        opt = Options()
        opt.add_argument('--disable-blink-features=AutomationControlled')
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_experimental_option("detach", True)
        opt.page_load_strategy = 'eager'
        service = Service('/Users/sakurachick/Programme/chromedriver-mac-arm64/chromedriver')
        browser = webdriver.Chrome(service=service, options=opt)
        browser.set_window_size(1200, 500)
        browser.set_window_position(0, 0)
        if num == -1:
            mainpage_initialization(browser, csftoken, sessionid)
            time.sleep(2)
            class_list = browser.find_elements(By.XPATH, '//div[contains(@class, "studentCol")]')
            class_num = len(class_list)
            for num in range(1, class_num+1):
                select_course(browser, num)
                course_initialization(browser)
        else:
            mainpage_initialization(browser, csftoken, sessionid)
            time.sleep(2)
            select_course(browser, num)
            course_initialization(browser)
            

if __name__ == '__main__':
    main()