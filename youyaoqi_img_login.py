import PIL.Image as image
import requests
import PIL.ImageChops as imagechops
import time, re, io, random, requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
def get_merge_image(filename, location_list):
    '''
    根据位置对图片进行合并还原
    :filename:图片
    :location_list:图片位置
    '''
    pass

    im = image.open(filename)

    new_im = image.new('RGB', (260, 116))

    im_list_upper = []
    im_list_down = []

    for location in location_list:

        if location['y'] == -58:
            pass
            im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
        if location['y'] == 0:
            pass

            im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

    new_im = image.new('RGB', (260, 116))

    x_offset = 0
    for im in im_list_upper:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    x_offset = 0
    for im in im_list_down:
        new_im.paste(im, (x_offset, 58))
        x_offset += im.size[0]

    return new_im


def get_image(driver, div):
    '''
    下载并还原图片
    :driver:webdriver
    :div:图片的div
    '''
    pass

    # 找到图片所在的div
    background_images = driver.find_elements_by_css_selector(div)
    location_list = []
    print(len(background_images))
    imageurl = ''

    for background_image in background_images:
        location = {}

        # 在html里面解析出小图片的url地址，还有长高的数值

        location['x'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                       background_image.get_attribute('style'))[0][1])
        print(location['x'])
        location['y'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                       background_image.get_attribute('style'))[0][2])
        imageurl = re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                              background_image.get_attribute('style'))[0][0]
        location_list.append(location)
        imageurl = imageurl.replace("webp", "jpg")

    jpgfile = io.BytesIO(requests.get(imageurl).content)

    # 重新合并图片
    image = get_merge_image(jpgfile, location_list)
    image.show()
    return image

    #
    # print(get_image(driver,'#gc-box > div > div.gt_widget.gt_clean.gt_hide > div.gt_box_holder > div.gt_box > a.gt_bg.gt_show > div.gt_cut_bg.gt_show>div'))
    # print(get_image(driver,'#gc-box > div > div.gt_widget.gt_clean.gt_hide > div.gt_box_holder > div.gt_box > a.gt_fullbg.gt_show > div.gt_cut_fullbg.gt_show>div'))


def is_similar(image1, image2, x, y):
    '''
    对比RGB值
    '''
    pass

    pixel1 = image1.getpixel((x, y))
    pixel2 = image2.getpixel((x, y))

    for i in range(0, 3):
        if abs(pixel1[i] - pixel2[i]) >= 50:
            return False

    return True


def get_diff_location(image1, image2):
    '''
    计算缺口的位置
    '''

    i = 0

    for i in range(0, 260):
        for j in range(0, 116):
            if is_similar(image1, image2, int(i), int(j)) == False:
                return i


def get_track(length):
    '''
    根据缺口的位置模拟x轴移动的轨迹
    '''
    pass

    list = []

    #     间隔通过随机范围函数来获得
    x = random.randint(1, 3)

    while length - x >= 5:
        list.append(x)

        length = length - x
        x = random.randint(1, 3)

    for i in range(length):
        list.append(1)

    return list
def main():

    driver=webdriver.Firefox(executable_path='/usr/bin/geckodriver')

    driver.get('http://passport.u17.com/member_v2/login.php?url=http://www.u17.com/')
    USER_NAME = '1042521247@qq.com'
    PASSWORD = 'qingdian17'
    driver.find_element_by_id('login_username').clear()
    driver.find_element_by_id('login_username').send_keys(USER_NAME)
    # driver.find_element_by_id('login_pwd').clear()
    # driver.find_element_by_id('login_pwd').send_keys(PASSWORD)
    time.sleep(10)
    driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[1]/form/div[2]/div[3]/div/div[2]/div[1]/div[3]/span[1]').click()
    time.sleep(2)
    a = driver.find_element_by_xpath('/html/body/div[7]/div[2]/div[1]/div/div[1]/div[1]/div/a/div[1]/canvas')
    a.screenshot('a.jpg')

    driver.find_element_by_xpath('/html/body/div[7]/div[2]/div[1]/div/div[1]/div[2]/div[2]').click()
    time.sleep(3)

    js="$('.geetest_canvas_slice').css('position' ,'static')"
    driver.execute_script(js)
    time.sleep(3)

    b = driver.find_element_by_xpath('/html/body/div[7]/div[2]/div[1]/div/div[1]/div[1]/div/a/div[1]/div/canvas[1]')
    b.screenshot('b.jpg')
    loc = get_diff_location(image.open('a.jpg'),image.open('b.jpg'))
    track_list = get_track(loc)
    time.sleep(2)
    element = driver.find_element_by_xpath("/html/body/div[7]/div[2]/div[1]/div/div[1]/div[2]/div[2]")
    location = element.location
    y = location['y']
    ActionChains(driver).click_and_hold(element).perform()
    track_string = ""
    time.sleep(2)
    js="$('.geetest_canvas_slice').css('position' ,'absolute')"
    driver.execute_script(js)
    print(y)
    print(track_list)
    for track in track_list:

        track_string = track_string + "{%d,%d}," % (track, y - 445)
        #         xoffset=track+22:这里的移动位置的值是相对于滑动圆球左上角的相对值，而轨迹变量里的是圆球的中心点，所以要加上圆球长度的一半。
        #         yoffset=y-445:这里也是一样的。不过要注意的是不同的浏览器渲染出来的结果是不一样的，要保证最终的计算后的值是22，也就是圆球高度的一半
        ActionChains(driver).move_by_offset(xoffset= 30+track,yoffset=y-431).perform()
        #         间隔时间也通过随机函数来获得
        time.sleep(random.randint(5, 50) / random.randint(50, 100))
    ActionChains(driver).move_by_offset( xoffset=27+track, yoffset=y - 431).perform()
    time.sleep(0.2)
    ActionChains(driver).move_by_offset( xoffset=27+track, yoffset=y - 431).perform()
    time.sleep(0.15)
    ActionChains(driver).move_by_offset( xoffset=27+track, yoffset=y - 431).perform()
    time.sleep(0.05)
    ActionChains(driver).move_by_offset( xoffset=27+track, yoffset=y - 431).perform()
    time.sleep(0.2)
    ActionChains(driver).move_by_offset( xoffset=27+track, yoffset=y - 431).perform()
    ActionChains(driver).release(on_element=element).perform()

    time.sleep(5)
    print(driver.current_url)
    cookie=driver.get_cookie('SESSDATA')
    driver.quit()
    time.sleep(500)

    return cookie


if __name__ == '__main__':
    # cookie=""
    # while not cookie:
    #     cookie=main()
    main()
    loc = get_diff_location(image.open('a.jpg'), image.open('b.jpg'))
    print(loc)
