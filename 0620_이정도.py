#미니 포토샵 만들기
#이러한 소프트웨어를 '영상처리 프로그램' 이라고 한다.

from tkinter import*
from tkinter.filedialog import*
from tkinter.simpledialog import*
from wand.image import*
from tkinter.colorchooser import *
from PIL import *



#모든 함수들이 공통적으로 사용할 전역 변수 선언
window, canvas, paper = None, None, None
photo, photo2, photo3 = None, None, None  #photo는 처음 불러들인 원본 이미지, photo2는 처리 결과를 저장하는 변수, photo3는 undo를 위해 배열에 저장할 변수
oriX,oriY,newX,newY=0,0,0,0 #원본 이미지의 쪽과 높이를 저장하는 변수
photoHistory=[]
lastx, lasty = 0, 0
result="black"

#함수 선언

def displayImage(img, width, height):
    global window,canvas,paper,photo, photo2, oriX, oriY

    #window.geometry(str(width)+"x"+str(height)) #불러오는 이미지에 맞는 창 사이즈 조정
    
    if canvas != None : #캔버스가 파괴되지 않아서 새로 불러올때마다 계속 쌓임
        canvas.destroy()

    canvas = Canvas(Imageframe, width=width, height=height) # 새 캔버스
    paper=PhotoImage(width=width, height=height) # 새 이미지
    canvas.create_image( (width/2, height/2), image=paper, state="normal")
    '''
    blob = img.make_blob(format='RGB')
    for i in range(0, width) :
        for k in range(0, height) :
            r = blob[(i*3*width)+(k*3) + 0]
            g = blob[(i*3*width)+(k*3) + 1]
            b = blob[(i*3*width)+(k*3) + 2]
            paper.put("#%02x%02x%02x" % (r,g,b) , (k, i)) #이미지 1픽셀부터 한칸씩 대신 ===로딩 많이 느림===
    '''
    #기존 img.make_blob(format='RGB')는 픽셀을 하나하나 찍어서 표현하기 때문에 처리시간이 길다.
    #blob=img.make_blob(format='png') 방식으로 처리할 경우 
    blob=img.make_blob(format='png')
    paper.put(blob)
    #canvas.place(x=(689-width)/2, y=(548-height)/2+15)
    canvas.place(relx=0.5, rely=0.5, anchor="center") #이미지 중앙 고정
    canvas.bind("<Button-1>",xy)
    canvas.bind("<B1-Motion>",addLine)


    
def func_open():
    #pass #임시로 만들어놓았을때( 함수에 아무것도 없으면 실행자체가 안되기때문)
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY
    readFp = askopenfilename(parent=window, filetypes=(("모든 그림 파일", "*.jpg;*.jpeg;*.bmp;*.png;*.tif;*.gif"),  ("모든 파일", "*.*") ))
    
    #이미지는 gif, jpg, png를 불러와 모두 처리하기 위해 photoImage()가 아닌
    #Wand 라이브러리에서 제공하는 Image()를 사용
    photo = Image(filename=readFp)
    oriX = photo.width  # 원본 이미지의 가로 사이즈를 oriX에 저장
    oriY = photo.height # 원본 이미지의 세로 사이즈를 oriY에 저장

    #photo2는 처리 결과를 저장할 변수
    photo2 = photo.clone()#원본 이미지의 photo를 복사해서 photo2에 저장.
    newX = photo2.width
    newY = photo2.height
    photo3 = photo2.clone()  #undo를 위해 photo3변수에 저장후
    photoHistory.append(photo3) #photohistory 배열에  photo3 변수값 저장
    
    displayImage(photo, oriX, oriY)



def func_save():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY

    #photo2는 func_open()함수를 실행할때 생성됨
    #파일을 열지 않았다면 저장하기를 눌렀을 떄 함수를 빠져나감
    if photo2 == None:
        return


    #대화 상자로부터 넘겨받은 파일의 정보를 saveFp에 저장
    saveFp = asksaveasfile(parent=window, mode="w", defaultextension=".jpg", filetypes=(("JPG 파일", "*.JPG;*.JPEG"),("모든 파일", "*.*")))
    savePhoto = photo2.convert("jpg") #결과 이미지인 photo2를 jpg로 변환
    savePhoto.save(filename=saveFp.name) #파일 저장 대화창에서 입력받은 파일 이름으로 저장



def func_restore():
    global photo, photo2, newX, newY, oriX, oriY
    photo2 = photo.clone()
    newX = oriX
    newY = oriY

    displayImage(photo, oriX, oriY)

    

def func_exit():
    window.quit() #프로그램 종료
    window.destroy() #창 없애기



#wand라이브러리에서 제공하는 resize(가로,세로)함수를 사용
def func_zoomin():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3
    
    if photo2 == None:     #사진이 없을때도 실행되는것 방지하는 조건문
        return
    #print(photo2.width)
    scale = askinteger("확대배수", "확대할 배수를 입력하세요(2~4)", minvalue=2, maxvalue=4)
    #print(scale)
    photo2.resize(int(newX * scale),int(newY * scale))
    newX =photo2.width
    newY = photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    #처리된 이미지의 이미지, 가로, 세로 정보를 displayImage() 함수에 넘겨줌
    displayImage(photo2, newX, newY)
    


def func_zoomout():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3

    if photo2 == None:
        return
    
    scale = askinteger("축소배수", "축소할 배수를 입력하세요(2~4)", minvalue=2, maxvalue=4)
    photo2.resize(int(newX / scale), int(newY / scale))  #입력한 값만큼 나눠서 축소
    newX = photo2.width
    newY = photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    displayImage(photo2, newX, newY)



def func_mirror1():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3

    if photo2 == None:
        return
    
    photo2.flip() #상하 반전 메소드
    newX=photo2.width
    newY=photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    displayImage(photo2, newX, newY)



def func_mirror2():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3

    if photo2 == None:
        return
    
    photo2.flop() #좌우 반전 메소드
    newX=photo2.width
    newY=photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    displayImage(photo2, newX, newY)



def func_rotate():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3

    if photo2 == None:
        return
    
    kakudo=askinteger("회전", "회전할 각도를 입력하세요", minvalue=0, maxvalue=360)
    photo2.rotate(kakudo) #회전 메소드
    newX=photo2.width
    newY=photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    displayImage(photo2, newX, newY)


###modulate ( brightness, saturation, hue) 순으로 설정
def func_brightness():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3

    if photo2 == None:
        return
    
    value=askinteger("명도", "값을 입력하세요(0~200)", minvalue=0, maxvalue=200)
    photo2.modulate(value, 100, 100) #명도 변경 메소드
    newX =photo2.width
    newY = photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    displayImage(photo2, newX, newY)

    

def func_saturation():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3

    if photo2 == None:
        return
    
    value = askinteger("채도 ", "값을 입력하세요(0~200)", minvalue=0, maxvalue=200)
    photo2.modulate(100, value, 100) #채도 변경 메소드
    newX =photo2.width
    newY=photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    displayImage(photo2, newX, newY)



def func_hue():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3

    if photo2 == None:
        return
    
    value = askinteger("색상 ", "값을 입력하세요(0~200)", minvalue=0, maxvalue=200)
    photo2.modulate(100, 100, value) #색상 변경 메소드
    newX =photo2.width
    newY=photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    displayImage(photo2, newX, newY)



def func_blur():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3

    if photo2 == None:
        return
    
    photo2.blur(sigma = 4) #블러처리
    newX=photo2.width
    newY=photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    displayImage(photo2, newX, newY)



def func_bw():
    global window, canvas, paper, photo, photo2, oriX, oriY, newX, newY, photo3

    if photo2 == None:
        return
    
    photo2.type="grayscale" #흑백 전환
    #(bilevel, grayscale, grayscalealpha, palette, palettealpha, truecolor, truecoloralpha, colorseparation, colorseparationalpha.) 등 입력가능
    newX=photo2.width
    newY = photo2.height
    photo3 = photo2.clone()
    photoHistory.append(photo3)
    displayImage(photo2, newX, newY)


def func_undo():
    global photoHistory, photo2, newX, newY, oriX, oriY, photo3
    
    if len(photoHistory) == 1:
        messagebox.showwarning(title="warning", message="작업한 이미지가 없음")
    else:
        photoHistory.pop()
        photo2 = photoHistory[len(photoHistory) - 1].clone()
        newX = oriX
        newY = oriY
        displayImage(photo2, photo2.width, photo2.height)



#def func_draw():
    #global callback, xy, addLine
    #canvas.bind("<Button-1>",xy)
    #canvas.bind("<B1-Motion>",addLine)

def callback() : #rgb색상선택함수
    global result
    result = askcolor(title = "Color Chooser")
    result = result[1]

def xy(event) :
    global lastx, lasty
    lastx, lasty = event.x, event.y
    
def addLine(event) :
    global lastx, lasty
    canvas.create_line((lastx, lasty, event.x, event.y), fill=result)
    lastx, lasty = event.x, event.y


#메인코드
window = Tk()
window.geometry("1180x760")
window.title("미니 포토샵(VER .002)")
#window.columnconfigure(0, weight=1)
#window.rowconfigure(0, weight=1)



#프레임 생성
#버튼프레임
btnframe = Frame(window, relief="solid", bd=1)
btnframe.configure(width=50, height=800, bg='Gray')
btnframe.pack(side="left", fill="y")   #fill=y 해야 고정

#open image용 프레임
Imageframe = Frame(window, relief="sunken", bd=1, highlightthickness=2, highlightbackground="black")
Imageframe.configure(bg="gray44")
Imageframe.pack(expand=YES, fill="both")

#그림판 ui용 프레임
rightframe = Frame(window, relief="solid", bd=1)
Imageframe.configure(bg="gray44")
rightframe.pack(side='right', fill="y")

#버튼1
#btn=Button(window, text="Button", width=5, height=8, bg="gold", fg="blue")
#btn.pack()
Button(btnframe, text="Open", width=5, height=6, bg="gray", command=func_open).pack()
Button(btnframe, text="Save", width=5, height=6, bg="gray", command=func_save).pack()
Button(btnframe, text="Restore", width=5, height=6, bg="gray", command=func_restore).pack()
Button(btnframe, text="Undo", width=5, height=6, bg="gray", command=func_undo).pack()
#Button(btnframe, text="Painting", width=5, height=6, bg="gray", command=func_draw).pack()
Button(btnframe, text="Exit", width=5, height=6, bg="gray", command=func_exit).pack()

#그림판용  색상 버튼
Button(rightframe, text='Choose Color', fg="darkgreen", command=callback).pack()


#배경 이미지 출력
#canvas1 = Canvas(window, width=1000, height=1000)
#canvas1.pack()
#bg_photo = PhotoImage(file="bgimg1.png")
#canvas1.create_image(345,270,image=bg_photo)

#pLabel = Label(window, image=bg_photo)
#pLabel.place(x=0, y=0)  #원하는 좌표값 설정



#메뉴구현

#메뉴 자체 생성
mainMenu = Menu(window)
window.config(menu=mainMenu)

#상위 메뉴1 생성
fileMenu = Menu(mainMenu, tearoff=0, bg='Gray32', fg='white')
mainMenu.add_cascade(label="File", menu=fileMenu)
#하위 메뉴1 생성
fileMenu.add_command(label="Open", command=func_open)
fileMenu.add_command(label="Save", command=func_save)
fileMenu.add_command(label="Restore", command=func_restore)
fileMenu.add_separator() #구분선 삽입
fileMenu.add_command(label="Exit", command=func_exit)


#상위 메뉴2 생성
editMenu = Menu(mainMenu, tearoff=0, bg='Gray32', fg='white')
mainMenu.add_cascade(label="Edit", menu=editMenu)
#하위 메뉴2 생성
editMenu.add_command(label="Undo", command=func_undo)




#상위 메뉴3 생성
image1Menu = Menu(mainMenu, tearoff=0, bg='Gray32', fg='white')
mainMenu.add_cascade(label="Image1", menu=image1Menu)
#하위 메뉴3 생성
image1Menu.add_command(label="Zoom In",command=func_zoomin)
image1Menu.add_command(label="Zoom Out",command=func_zoomout)
image1Menu.add_separator()
image1Menu.add_command(label="Vertical",command=func_mirror1)
image1Menu.add_command(label="Horizontal",command=func_mirror2)
image1Menu.add_command(label="Rotate",command=func_rotate)



#상위 메뉴4 생성
image2Menu = Menu(mainMenu, tearoff=0, bg='Gray32', fg='white')
mainMenu.add_cascade(label="Image2", menu=image2Menu)
#하위 메뉴4 생성
image2Menu.add_command(label="Brightness",command=func_brightness)
image2Menu.add_command(label="Saturation",command=func_saturation)
image2Menu.add_command(label="Hue",command=func_hue)
image2Menu.add_separator()
image2Menu.add_command(label="Blur",command=func_blur)
image2Menu.add_command(label="Black&White",command=func_bw)



window.mainloop()
