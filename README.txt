# CSU_yuketang_automator
基于selenium实现的中南大学雨课堂刷课脚本

本项目通过 Selenium 模拟浏览器行为，实现对雨课堂课程内容的自动化操作。

当前支持功能：

- 自动登录（通过注入 Cookie）
- 自动选择课程
- 自动完成文档阅读
- 自动静音播放视频
- 自动完成讨论发言
- 自动跳转至下一个未完成任务

## 🛠 技术栈

- Python
- Selenium 4
- ChromeDriver
- XPath 定位
- 显式等待（WebDriverWait）

## 🚀 安装方式

### 1. 克隆项目
git clone https://github.com/sakuraChiku/CSU_yuketang_automator.git

### 2. 安装依赖
pip install selenium

### 3. 下载 ChromeDriver
确保 ChromeDriver 版本与本地 Chrome 版本相近。

## ▶ 使用方式

1. 打开浏览器的调试台
2. 在“应用”选项卡的Cookies选项中获取雨课堂的 csrftoken 与 sessionid
3. 在 yuketang.py 中填入：

csftoken = 'your_token'
sessionid = 'your_sessionid'

4. 运行：

python yuketang.py

## 🧠 核心逻辑说明

### 课程初始化

在课程列表中刷新以获得最新课程状态
抓取第一个未完成状态的子课程并点击进入

### 文档阅读

文档任务打开即视为完成，因此不等待“已读”状态，而是：

- 等待页面加载
- 延时 1 秒
- 关闭窗口

### 视频播放

直接操作 HTML5 video 标签：

xt-playbutton
xt-volumebutton

绕过 UI 控件，保证稳定性。

同时每隔五秒获取一次播放进度：

在xt-time标签下分别获取当前播放时长与视频总时长，并转换为秒数

当进度为100%时自动退出并进行下一个任务

### 讨论发言

通过 ActionChains 模拟输入并提交某个固定评论（可在make_a_comment方法中修改变量text_content）。

## 📂 项目结构

yuketang_for_csu.py       # 主程序
README.md         # 项目说明

## ⚠ 已知问题

- 打开页面瞬间可能会被重定向至中南大学雨课堂主页，导致获取课程列表失败。此时重启程序即可。
- 不支持自动答题功能

## ⚖ 免责声明

本项目仅用于学习 Selenium 自动化技术。
请勿将本项目用于违反学校或平台规则的行为。
作者不承担任何后果。
