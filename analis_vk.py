import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import codecs
import pickle
import time





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

def get_id(dirname):
    id_mesg=os.listdir(dirname)
    id_mesg.remove('index-messages.html')
    i=0
    while i<len(id_mesg):
        id_mesg[i]=int(id_mesg[i])
        if id_mesg[i]<0:
            id_mesg.pop(i)
        else:
            i+=1
    id_mesg.sort()
    return id_mesg


def nameid_combine(dirname):
    id_mesg=get_id(dirname)
    name=name_setup(dirname)
    name_id=[]
    for i in range(len(id_mesg)):
        name_id.append([name[i],id_mesg[i]])
    return name_id



def get_mesg(id_mesg,dirname):
    dialog={'Автор':[],'Дата отправки':[],'Сообщение':[],'Вложение':[]}
    namedir=dirname+'/'+id_mesg
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
    return dialog

def combine(name_dialog,dialog,savename):
    table=pd.DataFrame(dialog)
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

def dump_all(name_id,savename,dirname):
    count=0
    for i in name_id:
        logfile=logdir+'/'+i[0]+'.pkl'
        if os.path.exists(logfile):
            dialog=load_obj(logfile)
        else:
            dialog=get_mesg(str(i[1]),dirname)
            save_obj(dialog,logfile)
        combine(i[0],dialog,savename+'/')
        count+=1
        print('Обработан ',count,' диалог')  
if __name__=='__main__':
    dirname=input('Введите папку с распакованным архивом: ')
    savename='dialogs_in_csv/'+dirname
    logdir='.log/'+dirname
    dirname=dirname+'/messages'
    if os.path.exists(dirname):
        if os.path.exists('.log')==False:
            os.mkdir('.log')
        if os.path.exists(logdir)==False:
            os.mkdir(logdir)
            name_id=nameid_combine(dirname)
            save_obj(name_id,logdir+'/name_id.pkl')
        else:
            name_id=load_obj(logdir+'/name_id.pkl')
        if os.path.exists('dialogs_in_csv')==False:
            os.mkdir('dialogs_in_csv')
        if os.path.exists(savename)==False:
            os.mkdir(savename)
        while True:
            a=input('Введите имя диалога (кроме пабликов), 1, если хотите перевести в csv все диалоги, 0, чтобы выйти:')
            if a=='0':
                break
            elif a=='1':
                t=time.time()
                dump_all(name_id,savename,dirname)
                print('Done')
                print('Затрачено времени: ',time.time()-t,'c')
            else:
                t=time.time()
                flag=0
                for i in name_id:
                    if i[0]==a:
                        flag=1
                        logfile=logdir+'/'+i[0]+'.pkl'
                        if os.path.exists(logfile):
                            dialog=load_obj(logfile)
                        else:
                            dialog=get_mesg(str(i[1]),dirname)
                            save_obj(dialog,logfile)
                        combine(i[0],dialog,savename+'/')  
                        print('Done')
                        break;
                if flag==0:
                    print('Такого диалога нет')
                flag=1
                print('Затрачено времени: ',time.time()-t,'c')
    else:
        print('Неверная папка, в ней нет messages')
