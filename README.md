## DeleteQQEmail脚本
### 简介
使用playwright自动化删除QQ邮箱收件箱中邮件

### 安装环境
#### 安装playwright
```
pip install playwright==1.48.0
```
#### 安装浏览器驱动
```
playwright install
```
### 运行脚本
#### 1.需要的数据
```
QQ邮箱账号
QQ邮箱密码
```
#### 2.运行脚本
```
python DeleteQQEmail.py
```

### 使用技巧
1.playwright支持录制脚本，可以录制脚本，然后修改脚本
```
playwright codegen -o script.py -b chromium
```
