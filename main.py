import sensor, image, time, lcd
from Maix import GPIO
from fpioa_manager import fm, board_info
import _thread
import math

def Pass():
    print('\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b')

def min(a, b):
    if(a>b):
        return a
    else:
        return b

def Cosplay_Handler(name):
    pass

def SuMiao(gray_img):
    #反色
    img_gray_1 = gray_img.negate()
    #高斯模糊
    img_gray_2 = img_gray_1.gaussian(5)
    #融合：颜色减淡
    #减淡公式：C =MIN( A +（A×B）/（255-B）,255)，其中C为混合结果，
             #A为去色后的像素点，B为高斯模糊后的像素
    img_ = img_gray_2.copy()
    for y in range(0,img_.height(),1):
        for x in range(0,img_.width(),1):
            A = img_gray_1.get_pixel(x,y)
            B = img_gray_2.get_pixel(x,y)
            img_.set_pixel(x,y,int(min(A+(A*B)/(256-B), 255)))
    return img_


def reminiscence(img):
    img_ = img.copy()
    for y in range(0,img_.height(),1):
        for x in range(0,img_.width(),1):
            (R,G,B) = img.get_pixel(x,y)
            newR = 0.393*R+0.769*G+0.189*B
            newG = 0.349*R+0.686*G+0.168*B
            newB = 0.272*R+0.534*G+0.131*B
            if(newB<0):
                newB = 0
            elif(newB>255):
                newB = 255
            else:
                newB = int(newB)
            if(newR<0):
                newR = 0
            elif(newR>255):
                newR = 255
            else:
                newR = int(newR)
            if(newG<0):
                newG = 0
            elif(newG>255):
                newG = 255
            else:
                newG = int(newG)
            img_.set_pixel(x,y,(newR,newG,newB))
    return img_


if __name__ == "__main__":
    lcd.init(freq=15000000)
    sensor.reset()						# Reset and initialize the sensor. It will
                                        # run automatically, call sensor.run(0) to stop
    sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
    sensor.set_framesize(sensor.QVGA)	# Set frame size to QVGA (320x240)
    sensor.set_hmirror(False)
    sensor.run(1)
    clock = time.clock()				# Create a clock object to track the FPS.

    #### 用于openmv的HaarCascade特征描述符
    face_haar = image.HaarCascade("frontalface")
    eye_haar = image.HaarCascade("eye")

    hat_img = image.Image("/sd/hat.jpg")
    img_gray = image.Image()

    '''
    对于简单的滤波而言，可以将两个sigma值设置成相同的值，如果值<10，
    则对滤波器影响很小，如果值>150则会对滤波器产生较大的影响，会使图片看起来像卡通。
    '''
    value1 = 1		#控制模糊程度
    value2 = 100	#控制美白程度
    value3 = 50		#控制美白程度

    # 识别贴图时的线程
    _thread.start_new_thread(Cosplay_Handler,('cosplay',))

    while(True):
        clock.tick()					# Update the FPS clock.
        img = sensor.snapshot()			# Take a picture and return the image.
        img.replace(img,hmirror=False,vflip=True)

        #### 人脸检测及贴图
        img_gray = img.to_grayscale(copy=True)
        face_area = img_gray.find_features(face_haar)
        if(face_area):
            for i in range(len(face_area)):
                face_img = img_gray.copy(face_area[i])
                #img.draw_rectangle(face_area[i])
                print("\r\nface = ",face_area[i],"\r\n")

                #### 进行磨皮美白--双边滤波+高斯滤波
                img_whitening = img.copy(face_area[i])
                img_whitening = img_whitening.bilateral(value1, color_sigma=value2, space_sigma=value3)
                img.draw_image(img_whitening, face_area[i][0], face_area[i][1]) #粘贴回去

                #### 进行简易贴图,正中脸贴图
                (x_,y_,w_,h_) = face_area[i]
                for i in range(x_+w_//2-25, x_+w_//2+25, 1):
                    for j in range(y_-25, y_+25, 1):
                        (R,G,B) = hat_img.get_pixel(i-x_-w_//2+25, j-y_+25)
                        if(R<20 and G<20 and B<20): # 黑色像素进行剔除，因为贴图图片中时黑色背景
                            pass
                        else:
                            img.set_pixel(i, j, (R,G,B))


        #### 风格转换 : 浮雕 & 素描 & 怀旧色 & 连环画 & 熔铸 & 冰冻
        #### References:https://blog.csdn.net/yangtrees/article/details/9116337
        #浮雕
        #img = img.morph(1, (2,0,0,0,0,0,0,0,-2))
        #素描
        #img = SuMiao(img_gray)
        #怀旧
        img = reminiscence(img)

        fps = clock.fps()
        img.draw_string(2,2, ("%2.1ffps" %(fps)), color=(255,0,0), scale=2)
        lcd.display(img)				# Display on LCD
