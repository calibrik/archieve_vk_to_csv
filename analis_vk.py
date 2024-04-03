from bs4 import BeautifulSoup
import pandas as pd
import os
import codecs
import pickle
import time

month = {"янв": "01", "фев": "02", "мар": "03", "апр": "04", "мая": "05", "июн": "06", "июл": "07", "авг": "08",
         "сен": "09", "окт": "10", "ноя": "11", "дек": "12"}


def name_id_setup(dirname):
    name_id = []
    flag = 0
    path = dirname + '/index-messages.html'
    with codecs.open(path, 'r', 'windows-1251') as f:
        text = f.read()
    soup = BeautifulSoup(text, 'html.parser')
    divs = soup.find_all('div', class_='message-peer--id')
    for i in divs:
        a = i.find('a')
        a = a['href'].split('/')
        a = int(a[0])
        if a >= 0:
            i = i.text[1:-1]
            i = i.replace('/', '')
            if flag != 0 and i == 'DELETED':
                i += str(flag)
                flag += 1
            elif i == 'DELETED':
                flag = 1
            name_id.append([i, a])
    return name_id


def get_mesg(id_mesg, dirname):
    dialog = {'Автор': [], 'Дата отправки': [], 'Сообщение': [], 'Вложение': []}
    namedir = dirname + '/' + id_mesg
    mesg = os.listdir(namedir)
    for j in mesg:
        path = namedir + '/' + j
        with codecs.open(path, 'r', 'windows-1251') as f:
            text = f.read()
        soup = BeautifulSoup(text, 'html.parser')
        divs = soup.find_all('div', class_='message')
        for div in divs:
            a = div.find('a', class_='attachment__link')
            div = div.text.split('\n')
            div.pop(0)
            if div[2] == '':
                div[2] = 'NaN'
            elif a != None:
                div[2] = a['href']
            author = div[0].split(',')
            date = author[1]
            date = date.split(' ')
            if len(date) < 6: continue
            date.pop(0)
            date.pop(3)
            date[1] = month[date[1]]
            if len(date[0]) == 1:
                date[0] = '0' + date[0]
            if len(date[3]) == 7:
                date[3] = '0' + date[3]
            date = date[2] + '-' + date[1] + '-' + date[0] + '-' + date[3]
            author = author[0]
            message = div[1]
            if message == '':
                message = 'NaN'
            involved = div[2]
            dialog['Автор'].append(author)
            dialog['Дата отправки'].append(date)
            dialog['Сообщение'].append(message)
            dialog['Вложение'].append(involved)
    return dialog


def combine(name_dialog, dialog, savename):
    table = pd.DataFrame(dialog)
    name = savename + name_dialog + '.csv'
    table = table.sort_values('Дата отправки')
    name = name.replace('|', '')
    name = name.replace('?', '')
    try:
        table.to_csv(name, index=False, encoding='utf-8')
    except Exception as exp:
        print('ОШИБКА ', exp, ' с диалогом ', name_dialog)


def save_obj(obj, name):
    with open(name, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name, 'rb') as f:
        return pickle.load(f)


def dump_all(name_id, savename, dirname):
    count = 0
    for i in name_id:
        i[0] = i[0].replace('|', '')
        i[0] = i[0].replace('?', '')
        logfile = logdir + '/' + i[0] + '.pkl'
        if os.path.exists(logfile):
            dialog = load_obj(logfile)
        else:
            dialog = get_mesg(str(i[1]), dirname)
            save_obj(dialog, logfile)
        combine(i[0], dialog, savename + '/')
        count += 1
        print('Обработан ', count, ' диалог')


if __name__ == '__main__':
    dirname = input('Введите папку с распакованным архивом: ')
    savename = 'dialogs_in_csv/' + dirname
    logdir = '.log/' + dirname
    dirname = dirname + '/messages'
    if os.path.exists(dirname):
        if os.path.exists('.log') == False:
            os.mkdir('.log')
        if os.path.exists(logdir) == False:
            os.mkdir(logdir)
        if os.path.exists(logdir + '/name_id.pkl') == False:
            name_id = name_id_setup(dirname)
            save_obj(name_id, logdir + '/name_id.pkl')
        else:
            name_id = load_obj(logdir + '/name_id.pkl')
        if os.path.exists('dialogs_in_csv') == False:
            os.mkdir('dialogs_in_csv')
        if os.path.exists(savename) == False:
            os.mkdir(savename)
        for i in range(len(name_id)):
            print(i, '.', name_id[i][0], sep='')
        type_input = input('Вы хотите выбирать диалог по имени или по номеру? (0/1):')
        while True:
            a = input('Введите номер диалога или имя, all, если хотите перевести в csv все диалоги, exit, чтобы выйти:')
            if a == 'exit':
                break
            elif a == 'all':
                t = time.time()
                dump_all(name_id, savename, dirname)
                print('Done')
                print('Затрачено времени: ', time.time() - t, 'c')
            else:
                t = time.time()
                if type_input == '0':
                    flag = 0
                    for i in name_id:
                        if i[0] == a:
                            flag = 1
                            logfile = logdir + '/' + i[0] + '.pkl'
                            if os.path.exists(logfile):
                                dialog = load_obj(logfile)
                            else:
                                dialog = get_mesg(str(i[1]), dirname)
                                save_obj(dialog, logfile)
                            combine(i[0], dialog, savename + '/')
                            print('Done')
                            break
                    if flag == 0:
                        print('Неверный ввод')
                    flag = 1
                else:
                    try:
                        logfile = logdir + '/' + name_id[int(a)][0] + '.pkl'
                    except Exception:
                        print('Неверный ввод')
                    else:
                        if os.path.exists(logfile):
                            dialog = load_obj(logfile)
                        else:
                            dialog = get_mesg(str(name_id[int(a)][1]), dirname)
                            save_obj(dialog, logfile)
                        combine(name_id[int(a)][0], dialog, savename + '/')
                        print('Done')

                print('Затрачено времени: ', time.time() - t, 'c')
    else:
        print('Неверная папка, в ней нет messages')
