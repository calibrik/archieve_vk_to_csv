import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import shutil
import codecs
import pickle
import time






def dialog_setup(dirname,*debug):
    dialog_combo=[]
    dialoges=os.listdir(dirname)
    dialoges.remove('index-messages.html')
    for i in range(len(dialoges)):
        dialoges[i]=int(dialoges[i])
    dialoges.sort()
    count=1
    for i in dialoges:
        if i>=0:
            dialog={'Автор':[],'Дата отправки':[],'Сообщение':[],'Вложение':[]}
            i=str(i)
            namedir=dirname+'/'+i
            mesg=os.listdir(namedir)
            for j in mesg:
                path=namedir+'/'+j
                with codecs.open(path,'r','windows-1251') as f:
                    text=f.read()
                soup=BeautifulSoup(text,'html.parser')
                divs=soup.find_all('div',class_='message')
                for div in divs:
                    a=div.find('a',class_='attachment__link')
                    div=div.text.split('\n')
                    div.pop(0)
                    if div[2]=='':
                        div[2]='NaN'
                    elif a!=None:
                        div[2]=a['href']
                    author=div[0].split(',')
                    date=author[1]
                    date=date.split(' ')
                    date.pop(0)
                    if len(date)>3:
                        date.pop(3)
                        if date[1]=='янв':
                            date[1]='01'
                        elif date[1]=='фев':
                            date[1]='02'
                        elif date[1]=='мар':
                            date[1]='03'
                        elif date[1]=='апр':
                            date[1]='04'
                        elif date[1]=='мая':
                            date[1]='05'
                        elif date[1]=='июн':
                            date[1]='06'
                        elif date[1]=='июл':
                            date[1]='07'
                        elif date[1]=='авг':
                            date[1]='08'
                        elif date[1]=='сен':
                            date[1]='09'
                        elif date[1]=='окт':
                            date[1]='10'
                        elif date[1]=='ноя':
                            date[1]='11'
                        elif date[1]=='дек':
                            date[1]='12'
                        if len(date[0])==1:
                            date[0]='0'+date[0]
                        if len(date[3])==7:
                            date[3]='0'+date[3]
                        date=date[2]+'-'+date[1]+'-'+date[0]+'-'+date[3]
                    else:
                        date=dialog['Дата отправки'][-1]
                    author=author[0]
                    message=div[1]
                    if message=='':
                        message='NaN'
                    involved=div[2]
                    dialog['Автор'].append(author)
                    dialog['Дата отправки'].append(date)
                    dialog['Сообщение'].append(message)
                    dialog['Вложение'].append(involved)
            dialog_combo.append(dialog)
            print('Обработан ',count,' диалог')
            count+=1
    return dialog_combo

                



def name_setup(dirname):
    name_dialog=[]
    path=dirname+'/index-messages.html'
    with codecs.open(path,'r','windows-1251') as f:
        text=f.read()
    soup=BeautifulSoup(text,'html.parser')
    divs=soup.find_all('div',class_='message-peer--id')
    for i in divs:
        a=i.find('a')
        a=a['href'].split('/')
        a=int(a[0])
        if a>=0:
            i=i.text[1:-1]
            i=i.replace('/','')
            name_dialog.append(i)
    return name_dialog

def combine(name_dialog,dialog_combo,savename):
    table=pd.DataFrame(dialog_combo)
    name=savename+name_dialog+'.csv'
    table=table.sort_values('Дата отправки')
    name=name.replace('|','')
    name=name.replace('?','')
    try:
        table.to_csv(name,index=False,encoding='utf-8')
    except Exception as exp:
        print('ОШИБКА ',exp,' с диалогом ',name_dialog) 

def save_obj(obj, name ):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name, 'rb') as f:
        return pickle.load(f)

def dump_all(name_dialog,dialog_combo,savename):
    for i in range(len(name_dialog)):
        combine(name_dialog[i],dialog_combo[i],savename+'/')

   
if __name__=='__main__':
    dirname=input('Введите папку с распакованным архивом: ')
    t=time.time()
    logdir='.log/'+dirname
    savename='dialogs_in_csv/'+dirname
    dirname=dirname+'/messages'
    if os.path.exists(dirname):
        if os.path.exists('.log')==False:
            os.mkdir('.log')
        if os.path.exists(logdir)==False:
            os.mkdir(logdir)
            print("Создаем файлы подгрузки")
            name_dialog=name_setup(dirname)
            dialogs=dialog_setup(dirname)
            save_obj(name_dialog,logdir+'/name_dialog.pkl')
            save_obj(dialogs,logdir+'/dialogs.pkl')
        else:
            print("Подгружаем данные")
            name_dialog=load_obj(logdir+'/name_dialog.pkl')
            dialogs=load_obj(logdir+'/dialogs.pkl')
        if os.path.exists('dialogs_in_csv')==False:
            os.mkdir('dialogs_in_csv')
        if os.path.exists(savename)==True:
            shutil.rmtree(savename)
        os.mkdir(savename)
        print('Затрачено времени: ',time.time()-t,'c')
        while True:
            a=input('Введите имя диалога (кроме групп), 1, если хотите перевести в csv все диалоги, 0, чтобы выйти:')
            if a=='0':
                break
            elif a=='1':
                dump_all(name_dialog,dialogs,savename)
                print('Done')
            else:
                try:
                    combine(name_dialog[name_dialog.index(a)],dialogs[name_dialog.index(a)],savename+'/')
                except ValueError:
                    print('Такого диалога нет')
                else:
                    print('Done')
    else:
        print('Неверная папка, в ней нет messages')
