import os
import json
import time
import asyncio

from playwright.async_api import async_playwright


SCREENSHOT_INDEX = 1
SCREENSHOT_FOLDER_ALL = "./screenshot/all"
SCREENSHOT_FOLDER_RESULT = "./screenshot/result"
SCREENSHOT_ALL = False
SCREENSHOT_RESULT = True


async def screenshot(page, name, folder, screenshot_flag):
    if not SCREENSHOT_ALL and not SCREENSHOT_RESULT:
        return
    if not (SCREENSHOT_ALL or (SCREENSHOT_RESULT and screenshot_flag)):
        return
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        await page.screenshot(path=os.path.join(folder, f"{name}{SCREENSHOT_INDEX}.png"))
    except Exception as e:
        print(e)


async def get_login_cookie(account, password, cookie_file):
    """获取qq邮箱登录cookie"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge")  # 启动Chromium浏览器
        content = await browser.new_context()  # 创建一个新的浏览器上下文
        page = await content.new_page()  # 打开一个新的页面，默认属于浏览器上下文
        await page.goto("https://mail.qq.com/")  # 打开QQ邮箱网站
        await page.get_by_text("QQ登录").click()  # 点击登录按钮
        frame_locator = page.frame_locator("//div[@class='QQMailSdkTool_login_loginBox_qq']/iframe").frame_locator("iframe")
        await frame_locator.get_by_role('link', name="密码登录").click()  # 点击密码登录按钮
        await frame_locator.locator('//*[@id="u"]').fill(account)  # 输入账号
        await frame_locator.locator('//*[@id="p"]').fill(password)  # 输入密码
        await frame_locator.locator('//*[@id="login_button"]').click()  # 点击登录按钮
        time.sleep(5)
        await page.wait_for_load_state('load')
        await content.storage_state(path=cookie_file)  # 保存登录状态
        print(f"qq邮箱登陆成功，登录cookie保存成功!")
        await content.close()
        await browser.close()


def check_cookie(cookie_file):
    """检查cookie是否有效"""
    if not os.path.exists(cookie_file):
        print("cookie文件不存在")
        return False
    with open(cookie_file, 'r') as f:
        json_data = json.load(f)
        json_value_list = list(json_data.values())
        for item in json_value_list:
            if len(item) == 0:
                print("获取cookie失败")
                return False
    return True


async def open_qq_email(browser, cookie_file):
    """打开qq邮箱"""
    content = await browser.new_context(storage_state=cookie_file)  # 创建一个新的浏览器上下文
    page = await content.new_page()  # 打开一个新的页面，默认属于浏览器上下文
    await page.goto("https://mail.qq.com/")  # 打开QQ邮箱网站
    time.sleep(5)
    await page.wait_for_load_state('load')
    await screenshot(page, "qq_email", SCREENSHOT_FOLDER_ALL, SCREENSHOT_ALL)
    return page


async def open_receive_email(page):
    """打开收件箱"""
    await page.get_by_role("link", name="收件箱").click()
    time.sleep(5)
    await screenshot(page, "receive_email", SCREENSHOT_FOLDER_ALL, SCREENSHOT_ALL)
    return page


async def delete_email(page):
    """删除邮件"""
    await page.locator("iframe[name=\"mainFrame\"]").content_frame.get_by_role("checkbox", name="选中/取消选中").check()
    await page.locator("iframe[name=\"mainFrame\"]").content_frame.get_by_role("link", name="删除").first.click()
    time.sleep(5)
    await page.wait_for_load_state('load')
    await screenshot(page, "receive_email_after_delete", SCREENSHOT_FOLDER_ALL, SCREENSHOT_ALL)
    await screenshot(page, "receive_email_after_delete", SCREENSHOT_FOLDER_RESULT, SCREENSHOT_RESULT)


async def quit_browser(browser):
    """关闭浏览器"""
    await browser.close()


async def main(account, password, cookie_file):
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge")  # 启动Chromium浏览器
        try:
            if not check_cookie(cookie_file):
                await get_login_cookie(account, password, cookie_file)
            page = await open_qq_email(browser, cookie_file)
            await open_receive_email(page)
            await delete_email(page)

        except Exception as e:
            os.remove(cookie_file)
            print(e)

        finally:
            await quit_browser(browser)


if __name__ == '__main__':
    for i in range(60):  # 循环删除次数
        account = ""  # 请填写qq邮箱账号
        password = ""  # 请填写qq邮箱密码
        asyncio.run(main(account, password, "cookie.json"))
        print(f"删除邮件第{i}页")
        time.sleep(10)
