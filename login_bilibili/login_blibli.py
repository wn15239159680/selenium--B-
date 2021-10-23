from selenium.webdriver import Chrome #导入Chrome驱动
from selenium.webdriver import ActionChains
import time
import random
import base64
from PIL import Image
import io
import numpy as  np

#模拟人滑动滑块
def getTracks(distance, delay=2):
    """
        distance: 需要移动的总距离
        delay: 产生多次移动的序列
    """
    tracks = [] #每次移动的距离 列表
    offset = 0 #已经移动的距离
    for i in np.arange(0.1, delay, 0.1):
        #每次移动的距离
        delta_dis = round((1 - pow(2, -10 * i / delay)) * distance) - offset
        #需要移动的小段距离放入列表
        tracks.append(delta_dis)
        #已经移动的距离
        offset += delta_dis

    #最后一个小段距离累加上剩余的距离
    tracks[-1] += (distance - offset)
    return tracks

browser = Chrome()

browser.get("https://passport.bilibili.com/login")
browser.maximize_window()

#give time to browser to load page
time.sleep(random.uniform(1,3))

#no iframe here,so no need to switch_to
browser.find_element_by_xpath('//*[@id="login-username"]').send_keys("bili_10579848274")

time.sleep(random.uniform(1,2))

browser.find_element_by_xpath('//*[@id="login-passwd"]').send_keys("laufing123")

time.sleep(random.uniform(0,1))

#click to login
browser.find_element_by_xpath('//*[@id="geetest-wrap"]/div/div[5]/a[1]').click()
time.sleep(random.uniform(2,5))

#背景图形
#将画布中的图形，转为base64编码的数据链
#data:image/png;base64,abcxxxxx
image_ori_data_url = browser.execute_script('return document.getElementsByClassName("geetest_canvas_fullbg")[0].toDataURL("image/png");')

#获取base64数据链
image_ori_data_url = image_ori_data_url.split(',')[1]
#解码数据链，得到16进制的字节串
image_ori_bytes = base64.b64decode(image_ori_data_url)
#字节转为图片对象
image_ori_obj = Image.open(io.BytesIO(image_ori_bytes))
# image_ori_obj.show()

#滑块缺口图形
image_gap_data_url = browser.execute_script('return document.getElementsByClassName("geetest_canvas_bg")[0].toDataURL("image/png");')
image_gap_data_url = image_gap_data_url.split(',')[1]
image_gap_bytes = base64.b64decode(image_gap_data_url)
image_gap_obj = Image.open(io.BytesIO(image_gap_bytes))

# image_gap_obj.show()


#比较两张图的像素矩阵，获取缺口位置
gap_pos = []
for i in range(image_ori_obj.size[0]): #size->width,height
  if gap_pos:
    break
  for j in range(image_ori_obj.size[1]):
    pixel_ori = image_ori_obj.getpixel((i, j)) #每个像素有RGB三个通道的值
    pixel_gap = image_gap_obj.getpixel((i, j))

    #逐个通道进行比较
    if abs(pixel_ori[0] - pixel_gap[0]) > 10 and abs(pixel_ori[1] - pixel_gap[1]) > 10 and abs(pixel_ori[2] - pixel_gap[2]) > 10:
      gap_pos = [i, j]
      break

#获得了缺口坐标后，只需要控制滑块移动到缺口位置
# slider = driver_wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div[6]/div/div[1]/div[2]/div[2]')))
#slide to validate, geetest div
# find slider button 
slider_button = browser.find_element_by_xpath('/html/body/div[2]/div[2]/div[6]/div/div[1]/div[2]/div[2]')
#click and hold
action_chains = ActionChains(browser)
action_chains.click_and_hold(slider_button).perform() #一个对象hold住

#先移动一大段距离，剩下的慢慢来模拟人
ActionChains(browser).move_by_offset(xoffset=gap_pos[0]*0.8,yoffset=0).perform()
#产生多个移动的距离小段
tracks = getTracks(gap_pos[0] * 0.13)
for delta_dis in tracks:
  ActionChains(browser).move_by_offset(xoffset=delta_dis, yoffset=0).perform()

#释放鼠标左键
# ActionChains(browser).pause(0.5).release().perform()
action_chains.pause(0.5).release().perform()

time.sleep(100000)
browser.close()

