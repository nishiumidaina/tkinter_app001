import sqlite3
import tkinter
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import threading
import subprocess
import math
import shutil
import os
from decimal import Decimal
from turtle import clear

root = Tk()
root.title("混雑度可視化システム（試作品）")    
root.geometry("500x300+140+40")
b_count = 0 #2重クリック防止用

def register():
    #ライブカメラと記録間隔の登録
    global textbox_url
    textbox_url = str(txt1.get())
    print(textbox_url)

def counter():
    #DB接続
    dbname = "personcount.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = 1")
    # countテーブルの定義
    ddl = "CREATE TABLE IF NOT EXISTS count(count_id INTEGER PRIMARY KEY AUTOINCREMENT,count_data TNTEGER,count_record TEXT);"
    # SQLの発行
    c.execute(ddl)
    sql = "SELECT IFNULL(count_data, 'None'),MAX(count_record) FROM count"
    c.execute(sql)
    ave = c.fetchall()[0][0]
    if not ave == "None":
        count_ave = math.floor(Decimal(ave))
    else:
        count_ave = "None"
    label["text"] = count_ave
    conn.close()
    root.after(1000, counter) # 1秒毎にcounter()を実行

def start():
    global b_count
    thread = threading.Thread(target=count)
    b_count = b_count + 1
    thread.start()

def count():
    global flg, N, b_count
    if flg == False:
        N.terminate()
        flg = True
    else:#2重クリック防止用
        if b_count == 1:
            N = subprocess.Popen('python yolov5/detect2.py --source {0} --class 0 --nosave'.format(textbox_url))
        else:
            messagebox.showinfo("アラート", "処理中です。しばらくお待ちください。")
            print("処理中です。")

def stop():
    global flg, b_count
    flg = False
    b_count = 0
    count()
    #yolov5の動画出力をさせないための処理
    target_dir = "yolov5/runs/detect"
    shutil.rmtree(target_dir)
    os.mkdir(target_dir)

def clearDB():
    #テーブル内データのリセット
    dbname = "personcount.db"
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("PRAGMA foreign_keys = 1")
    # countテーブルの定義
    ddl = "CREATE TABLE IF NOT EXISTS count(count_id INTEGER PRIMARY KEY AUTOINCREMENT,count_data TNTEGER,count_record TEXT);"
    # SQLの発行
    c.execute(ddl)
    sql = "DROP TABLE count"
    c.execute(sql)
    ave2 = c.fetchall()
    print(ave2)
    conn.close()

def close():
    if b_count >= 1:
        messagebox.showinfo("アラート", "処理を停止させてください")
    else:
        root.destroy()

flg = True

#開始ボタン
btn1 = tk.Button(root, text="開始",command=start,width = 6)
btn1.grid(row=0,column=0)
btn1.place(x=370, y=120)
#停止ボタン
btn2 = tk.Button(root, text="停止",command=stop,width = 6)
btn2.grid(row=1,column=0)
btn2.place(x=427, y=120)
#DB削除ボタン
btn4 = tk.Button(root, text="DB削除",command=clearDB,width = 14)
btn4.grid(row=0,column=0)
btn4.place(x=370, y=80)
#URL登録フォーム
lbl = tkinter.Label(text="URL")
lbl.place(x=25, y=40)
txt1 = tkinter.Entry(width=35)
txt1.place(x=100, y=40)
#登録ボタン
btn3 = tk.Button(root, text="登録",command=register,width = 14)
btn3.grid(row=0,column=0)
btn3.place(x=370, y=40)
#1分毎の混雑度(人のカウント)
lbl2 = tkinter.Label(text="混雑度/60秒")
lbl2.place(x=25, y=80)
label = tk.Label(font=("Ubunt Mono", 20))
label.place(x=160,y=80)
counter() # 最初のcounter()を実行しリアルタイム処理を始める
root.protocol("WM_DELETE_WINDOW", close)
root.mainloop()
