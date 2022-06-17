import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import codecs
import vk



def dialog_setup(dirname):
    dialog_combo=[]
    dialoges=os.listdir(dirname)
    count=1
    dialoges.remove('index-messages.html')
    for i in dialoges:
        i=int(i)
        dialog={'Автор':[],'Дата отправки':[],'Сообщение':[],'Вложение':[]}
        if i>=0:
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
                    div=div.text.split('\n')
                    div.pop(0)
                    if div[2]=='':
                        div[2]='NaN'
                    author=div[0].split(',')
                    date=author[1]
                    author=author[0]
                    message=div[1]
                    involved=div[2]
                    dialog['Автор'].append(author)
                    dialog['Дата отправки'].append(date)
                    dialog['Сообщение'].append(message)
                    dialog['Вложение'].append(involved)
        dialog['Автор']=dialog['Автор'][::-1]
        dialog['Дата отправки']=dialog['Дата отправки'][::-1]
        dialog['Сообщение']=dialog['Сообщение'][::-1]
        dialog['Вложение']=dialog['Вложение'][::-1]
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
            name_dialog.append(i)
    return name_dialog

def combine(name_dialog,dialog_combo):
    for i in range(len(dialog_combo)):
        table=pd.DataFrame(dialog_combo[i])
        name='dialogs_in_csv/'+name_dialog[i]+'.csv'
        table.to_csv(name)

        
        

              
os.mkdir('dialogs_in_csv')
dirname=input('Введите папку с распакованным архивом: ')
dirname=dirname+'/messages'
dialogs=dialog_setup(dirname)
name_dialog=name_setup(dirname)
combine(name_dialog,dialogs)
