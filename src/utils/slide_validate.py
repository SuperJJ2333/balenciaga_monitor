import random


def slide_validate(page, url, ocr):
    """
    执行滑块验证
    :return:
    """
    page.listen.start('data:image/png')
    if page.latest_tab.url != url:
        page.get(url)
    else:
        page.refresh()
    target_img_bytes = ''
    background_img_bytes = ''
    # 滑块验证码
    for i in page.listen.steps(count=2):
        img_str = i.response.body

        if not target_img_bytes or len(img_str) < len(target_img_bytes):
            print("目标图片获取成功：", len(img_str))
            target_img_bytes = img_str

        if not background_img_bytes or len(img_str) > len(background_img_bytes):
            print("背景图片获取成功：", len(img_str))
            background_img_bytes = img_str

    res = ocr.slide_match(target_img_bytes, background_img_bytes, simple_target=True)

    print(f"识别到的滑动距离: {res['target'][0]}")

    slide_button = page.ele('x://*[@class="slider"]')

    # 使用简单直接的方式滑动到目标位置
    # 添加少量随机性使滑动更像人类操作
    target_distance = res['target'][0] * random.uniform(0.98, 1.02)

    # 方法1：使用链式API直接滑动（推荐）
    page.actions.hold(slide_button).right(target_distance).release()


if __name__ == '__main__':
    pass