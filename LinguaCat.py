from random import choice, shuffle, random
from copy import deepcopy
import sys
from PyQt5.QtCore import Qt, QTimer, QThread
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLabel, QListView
from PyQt5.QtWidgets import QLineEdit, QMainWindow, QCheckBox, QPlainTextEdit
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QFormLayout, QListWidget, QListWidgetItem, QDialog
from PyQt5 import uic
from PyQt5.QtGui import QPalette, QImage, QBrush, QPixmap, QIcon
import sqlite3
import requests
import json
import time

alfabet_en = 'abcdefghijklmnopqrstuvwxyz1234567890'
alfabet_ru = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'
con = sqlite3.connect('dict.db')
cursor = con.cursor()


class LinguaCat(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/main.ui', self)
        self.setWindowIcon(QIcon('design/images/cat1.png'))
        self.setWindowTitle('LinguaCat')
        self.set_background()
        # self.translate_form()
        self.minigames_form()
        self.translate1.clicked.connect(self.translate_form)
        self.dict1.clicked.connect(self.dict_form)
        self.minigames1.clicked.connect(self.minigames_form)
        self.statistic1.clicked.connect(self.statistic_form)
        self.settings1.clicked.connect(self.settings_form)

    def set_background(self):
        '''Change background'''
        global cursor
        res = cursor.execute('''SELECT background FROM settings''').fetchone()[0]
        self.palette = QPalette()
        self.im = QImage(res)
        self.im = self.im.scaledToWidth(self.width())
        self.im = self.im.scaledToHeight(self.height())
        self.palette.setBrush(QPalette.Background, QBrush(self.im))
        self.setPalette(self.palette)

    def keyPressEvent(self, event):
        '''Hot keys'''
        if int(event.modifiers()) == Qt.CTRL:
            if event.key() == Qt.Key_Return:
                self.translate2()
            elif event.key() == Qt.Key_S:
                self.add_word()
        elif int(event.modifiers()) == (Qt.CTRL + Qt.ShiftModifier):
            if event.key() == Qt.Key_F:
                self.pasx()

    def add_word(self):
        '''Call function to add word'''
        try:
            self.newForm.add_word_to_dict()
        except BaseException:
            pass

    def translate2(self):
        '''Call translation function'''
        try:
            self.newForm.translate()
        except BaseException:
            pass

    def translate_form(self):
        '''Translation form'''
        self.translate1.setEnabled(False)
        self.dict1.setEnabled(True)
        self.minigames1.setEnabled(True)
        self.statistic1.setEnabled(True)
        self.settings1.setEnabled(True)
        self.scroll1.takeWidget()
        self.newForm = Translate()
        self.scroll1.setWidget(self.newForm)

    def dict_form(self):
        '''Dictionary form'''
        self.translate1.setEnabled(True)
        self.dict1.setEnabled(False)
        self.minigames1.setEnabled(True)
        self.statistic1.setEnabled(True)
        self.settings1.setEnabled(True)
        self.scroll1.takeWidget()
        self.newForm = Dictionary()
        self.scroll1.setWidget(self.newForm)

    def minigames_form(self):
        '''Form with minigames'''
        self.translate1.setEnabled(True)
        self.dict1.setEnabled(True)
        self.minigames1.setEnabled(False)
        self.statistic1.setEnabled(True)
        self.settings1.setEnabled(True)
        self.scroll1.takeWidget()
        self.newForm = Minigames(self)
        self.scroll1.setWidget(self.newForm)

    def statistic_form(self):
        '''Statistic form'''
        self.translate1.setEnabled(True)
        self.dict1.setEnabled(True)
        self.minigames1.setEnabled(True)
        self.statistic1.setEnabled(False)
        self.settings1.setEnabled(True)
        self.scroll1.takeWidget()
        self.newForm = Statistic()
        self.scroll1.setWidget(self.newForm)

    def settings_form(self):
        '''Settings form'''
        self.translate1.setEnabled(True)
        self.dict1.setEnabled(True)
        self.minigames1.setEnabled(True)
        self.statistic1.setEnabled(True)
        self.settings1.setEnabled(False)
        self.scroll1.takeWidget()
        self.newForm = Settings(self)
        self.scroll1.setWidget(self.newForm)

    def pasx(self):
        '''I know you like cats) meow <3'''
        self.palette = QPalette()
        self.im = QImage('design/images/cat.jpg')
        self.im = self.im.scaledToWidth(self.width())
        self.im = self.im.scaledToHeight(self.height())
        self.palette.setBrush(QPalette.Background, QBrush(self.im))
        self.setPalette(self.palette)

    def closeEvent(self, event):
        '''Ask do you want to close programm?'''
        q = Question('Вы действительно хотите выйти?')
        q.show()
        q.exec()
        if q.result():
            event.accept()
        else:
            event.ignore()


class Translate(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/translate_form.ui', self)
        # self.output.setReadOnly(True)
        self.input.setPlaceholderText('Введите текст')
        self.output.setPlaceholderText('Перевод')
        self.lang1 = 'ru'
        self.lang2 = 'en'
        self.lbl1.setAlignment(Qt.AlignCenter)
        self.lbl2.setAlignment(Qt.AlignCenter)
        self.lbl_usl.setText('<a href="http://translate.yandex.ru">Переведено сервисом «Яндекс.Переводчик»</a>')
        self.lbl_usl.setOpenExternalLinks(True)
        self.lbl_usl.setAlignment(Qt.AlignCenter)
        self.change1.clicked.connect(self.change_lang)
        # self.input.textChanged.connect(self.translate)
        self.translate1.clicked.connect(self.translate)
        self.add_to_dict.clicked.connect(self.add_word_to_dict)

    def change_lang(self):
        '''Button change language'''
        one = self.lbl1.text()
        two = self.lbl2.text()
        self.lbl1.setText(two)
        self.lbl2.setText(one)
        self.lang1, self.lang2 = self.lang2, self.lang1

    def translate(self):
        '''Translate function'''
        url = f'https://translate.yandex.net/api/v1.5/tr.json/translate'
        translate_params = {
            'key': 'trnsl.1.1.20191028T102129Z.9daef2eca8217847.138130454cbac21810b727472a4db0aeb40b9f7e',
            'text': self.input.toPlainText(),
            'lang': f'{self.lang1}-{self.lang2}'}
        try:
            response = requests.get(url, params=translate_params)
        except requests.ConnectionError:
            q = Error('Проблемы с доступом <br/> к интернету')
            q.show()
            q.exec()
            self.output.setPlainText('')
        if response.status_code == 200:
            data = response.json()['text'][0]
            self.output.setPlainText(data)
        else:
            self.output.setPlainText('')

    def add_word_to_dict(self):
        '''Button add word to your dictionary'''
        global cursor
        try:
            if self.input.toPlainText() == '' or self.output.toPlainText() == '':
                q = Error('Необходимо ввести слово')
                q.show()
                q.exec()
            elif len(self.input.toPlainText()) > 45 or len(self.output.toPlainText()) > 45:
                q = Error('Словарь не может содержать <br/> слово длиннее 45 символов')
                q.show()
                q.exec()
            else:
                if self.lbl1.text() == 'Русский':
                    word_ru = self.input.toPlainText()
                    word_en = self.output.toPlainText()
                else:
                    word_en = self.input.toPlainText()
                    word_ru = self.output.toPlainText()
                cursor.execute('''INSERT INTO Words(english, russian, training) VALUES (?, ?, ?)''',
                               (word_en, word_ru, 1))
                con.commit()
                q = Info('Слово успешно <br/> добавлено в словарь')
                q.show()
                q.exec()

        except ValueError:
            q = Error('Error')
            q.show()
            q.exec()


class Dictionary(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/dict_form.ui', self)
        # self.lw.setSelectionMode(2)
        self.add1.clicked.connect(self.add)
        self.update_dict()
        self.search1.setPlaceholderText('Найти')
        self.lw.itemSelectionChanged.connect(self.show_)
        self.lw.itemDoubleClicked.connect(self.edit1)
        self.sort1.currentIndexChanged.connect(self.update_dict)
        self.search1.textChanged.connect(self.update_dict)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.del1()

    def del1(self):
        '''Call function to delete word from dictionary'''
        if self.lw.currentItem() is not None:
            item = self.lw.currentItem()
            self.widget = self.lw.itemWidget(item)
            self.current = self.lw.row(item) - 1
            self.widget.del_word()

    def add(self):
        '''MAke dialog window to add word'''
        self.dial = DialogAdd(self, 'add')
        self.dial.show()

    def sort_words(self):
        '''Sort words in dictionary'''
        s = self.sort1.currentText()
        if s == 'По алфавиту':
            self.words.sort(key=lambda x: (str(x[1]), str(x[2])))
        elif s == 'По добавлению':
            self.words.sort(key=lambda x: -x[0])
        elif s == 'По количеству ошибок':
            self.words.sort(key=lambda x: -x[5])
        elif s == 'Тренировать':
            words1 = []
            for i in self.words:
                if i[3] == 1:
                    words1.append(i)
            self.words = deepcopy(words1)
        elif s == 'По количеству ошибок':
            pass

    def edit1(self):
        '''Call function to edit word in dictionary'''
        item = self.lw.currentItem()
        self.widget = self.lw.itemWidget(item)
        self.widget.edit()
        self.current = self.lw.row(item)

    def do1(self, word_ru, word_en, tren):
        '''Add word to database'''
        global cursor
        try:
            if word_ru[0].lower() in alfabet_en:
                word_ru, word_en = word_en, word_ru
            if tren.checkState() == Qt.Checked:
                a = 1
            else:
                a = 0
            cursor.execute('''INSERT INTO Words(english, russian, training) VALUES (?, ?, ?)''',
                           (word_en, word_ru, a))
            con.commit()
            print('accept')
        except BaseException:
            print('error')

    def update_dict(self):
        '''Update list widget with words from dict'''
        global cursor
        txt = self.search1.text()
        if txt != '':
            if txt[0].lower() in alfabet_en:
                self.words = cursor.execute('''SELECT * FROM Words WHERE english LIKE ?''', (txt + '%',)).fetchall()
            elif txt[0].lower() in alfabet_ru:
                self.words = cursor.execute('''SELECT * FROM Words WHERE russian LIKE ?''', (txt + '%',)).fetchall()
            self.lw.clear()
            if self.words != []:
                self.sort_words()
                for i in self.words:
                    item = QListWidgetItem(self.lw)
                    str1 = f'{str(i[1])}'
                    str2 = f'{str(i[2])}'
                    tr = i[3]
                    self.mw = WordsForm(self, str1, str2, tr)
                    self.lw.addItem(item)
                    self.lw.setItemWidget(item, self.mw)
                    item.setSizeHint(self.mw.size())
            else:
                self.lw.addItem('В словаре нет слов удовлетворяющих запросу')
        else:
            self.words = cursor.execute('''SELECT * FROM Words''').fetchall()
            self.sort_words()
            self.lw.clear()
            for i in self.words:
                item = QListWidgetItem(self.lw)
                str1 = f'{str(i[1])}'
                str2 = f'{str(i[2])}'
                tr = i[3]
                self.mw = WordsForm(self, str1, str2, tr)
                self.lw.addItem(item)
                self.lw.setItemWidget(item, self.mw)
                item.setSizeHint(self.mw.size())
        try:
            self.lw.setCurrentRow(self.current)
        except BaseException:
            pass

    def show_(self):
        '''Hide and show buttons in item of list widget'''
        try:
            self.widget.hide_btns()
        except BaseException:
            pass
        item = self.lw.currentItem()
        self.widget = self.lw.itemWidget(item)
        self.widget.show_btns()


class DialogAdd(QMainWindow):
    def __init__(self, dict, func, one='', two='', a=1):
        self.dict = dict
        super().__init__()
        uic.loadUi('design/dialog_add.ui', self)
        self.setFixedSize(348, 324)
        self.inp1.setPlaceholderText('Введите слово или фразу')
        self.inp2.setPlaceholderText('Введите перевод')
        self.tren.setChecked(True)
        self.tren.setTristate(False)
        self.func = func
        if func == 'add':
            self.setWindowTitle('Добавить')
            self.setWindowIcon(QIcon('design/images/add.png'))
            self.add2.clicked.connect(self.add)
        elif func == 'edit':
            self.setWindowTitle('Редактировать')
            self.setWindowIcon(QIcon('design/images/rewrite.png'))
            self.inp1.setText(one)
            self.inp2.setText(two)
            self.one = one
            self.two = two
            self.tr = a
            if a == 0:
                self.tren.setChecked(False)
            self.add2.clicked.connect(self.edit)
        self.cancel2.clicked.connect(self.cancel)

    def keyPressEvent(self, event):
        '''Hot keys'''
        try:
            if event.key() == Qt.Key_Return:
                if self.func == 'add':
                    self.add()
                elif self.func == 'edit':
                    self.edit()
        except BaseException:
            pass

    def add(self):
        '''Call function to add word to database'''
        global cursor
        if self.inp1.text() == '' or self.inp2.text() == '':
            q = Error('Необходимо ввести слово')
            q.show()
            q.exec()
        elif len(self.inp1.text()) > 45 or len(self.inp2.text()) > 45:
            q = Error('Словарь не может содержать слов <br/> длиннее 45 символов')
            q.show()
            q.exec()
        else:
            res = cursor.execute('''SELECT english, russian FROM Words''').fetchall()
            a = (self.inp1.text(), self.inp2.text())
            a1 = (self.inp2.text(), self.inp1.text())
            if a in res or a1 in res:
                q = Error('Словарь не может содержать <br/> одинаковых слов')
                q.show()
                q.exec()
            else:
                self.dict.do1(self.inp1.text(), self.inp2.text(), self.tren)
                self.dict.update_dict()
                self.close()

    def edit(self):
        '''Call function to edit word in database'''
        if self.inp1.text() == '' or self.inp2.text() == '':
            q = Error('Необходимо ввести слово')
            q.show()
            q.exec()
        elif len(self.inp1.text()) > 45 or len(self.inp2.text()) > 45:
            q = Error('Словарь не может содержать <br/> слово длиннее 45 символов')
            q.show()
            q.exec()
        else:
            self.dict.do2(self.one, self.two, self.inp1.text(), self.inp2.text(), self.tren)
            self.close()

    def cancel(self):
        '''Exit'''
        self.close()


class WordsForm(QWidget):
    def __init__(self, dict, engl, rus, tr):
        super().__init__()
        uic.loadUi('design/words_form.ui', self)
        self.dict = dict
        self.fl = True
        self.engl1.setText(engl)
        self.rus1.setText(rus)
        self.tr = tr
        self.hide_btns()
        self.del1.clicked.connect(self.del_word)
        self.edit1.clicked.connect(self.edit)

    def hide_btns(self):
        '''Hide buttons of item list widget'''
        self.tren1.hide()
        self.edit1.hide()
        self.del1.hide()

    def show_btns(self):
        '''Show buttons of item list widget'''
        if self.tr == 1:
            self.tren1.show()
        self.edit1.show()
        self.del1.show()

    def del_word(self):
        '''Delete word from database'''
        global cursor
        if self.dict.lw.currentItem() is not None and self.fl:
            self.fl = False
            q = Question('Вы действительно хотите удалить <br/> это слово из словаря?')
            q.show()
            q.exec()
            if q.result():
                word1 = self.engl1.text()
                word2 = self.rus1.text()
                cursor.execute('''DELETE FROM Words WHERE english = ? AND russian = ?''', (word1, word2))
                con.commit()
                self.fl = True
                self.dict.update_dict()
            else:
                self.fl = True

    def edit(self):
        '''Call function to edit word'''
        global cursor
        try:
            old_en = self.engl1.text()
            old_ru = self.rus1.text()
            tr = cursor.execute('''SELECT training FROM Words 
            WHERE english = ? AND russian = ?''', (old_en, old_ru)).fetchone()[0]
            self.dial = DialogAdd(self, 'edit', old_en, old_ru, tr)
            self.dial.show()
        except ValueError:
            print('error')

    def do2(self, old_en, old_ru, engl, rus, tren):
        '''Change database to edit word'''
        global cursor
        try:
            if tren.checkState() == Qt.Checked:
                a = 1
            else:
                a = 0
            cursor.execute(f'''UPDATE Words
                SET english = ?, russian = ?, training = ?
                WHERE english = ? AND russian = ?''', (engl, rus, a, old_en, old_ru))
            con.commit()
            print('accept')
            self.dict.update_dict()
        except ValueError:
            print('error')


class Question(QDialog):
    def __init__(self, text):
        super().__init__()
        uic.loadUi('design/message_box.ui', self)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setText(text)
        self.setWindowIcon(QIcon('design/images/ques1.png'))
        self.setWindowTitle('Внимание')
        self.yes1.setDefault(True)
        self.yes1.clicked.connect(self.yes)
        self.no1.clicked.connect(self.no)

    def yes(self):
        self.accept()

    def no(self):
        self.reject()


class Error(QDialog):
    def __init__(self, text):
        super().__init__()
        uic.loadUi('design/error_box.ui', self)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.setWindowIcon(QIcon('design/images/er1.png'))
        self.setWindowTitle('Ошибка')
        self.lbl.setText(text)
        self.yes1.clicked.connect(self.yes)

    def yes(self):
        self.accept()


class Info(QDialog):
    def __init__(self, text):
        super().__init__()
        uic.loadUi('design/info_box.ui', self)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.setWindowIcon(QIcon('design/images/inf1.png'))
        self.setWindowTitle('Информация')
        self.lbl.setText(text)
        self.yes1.clicked.connect(self.yes)

    def yes(self):
        self.accept()


class Minigames(QWidget):
    def __init__(self, main):
        super().__init__()
        uic.loadUi('design/minigames_form.ui', self)
        self.main = main
        self.trening1.clicked.connect(self.word_translate)
        self.trening2.clicked.connect(self.translate_word)
        self.trening4.clicked.connect(self.fifty_fifty)
        # self.fifty_fifty()

    def word_translate(self):
        res = cursor.execute('''SELECT english, russian FROM Words WHERE training = 1''').fetchall()
        if len(res) < 2:
            q = Error('Для игры необходимо более <br/> одного слова для тренировки')
            q.show()
            q.exec()
        else:
            self.main.scroll1.takeWidget()
            self.game = GameWordTranslate(self.main, 'en')
            self.main.scroll1.setWidget(self.game)

    def translate_word(self):
        res = cursor.execute('''SELECT english, russian FROM Words WHERE training = 1''').fetchall()
        if len(res) < 2:
            q = Error('Для игры необходимо более <br/> одного слова для тренировки')
            q.show()
            q.exec()
        else:
            self.main.scroll1.takeWidget()
            self.game = GameWordTranslate(self.main, 'ru')
            self.main.scroll1.setWidget(self.game)

    def fifty_fifty(self):
        res = cursor.execute('''SELECT english, russian FROM Words WHERE training = 1''').fetchall()
        if len(res) < 2:
            q = Error('Для игры необходимо более <br/> одного слова для тренировки')
            q.show()
            q.exec()
        else:
            self.main.scroll1.takeWidget()
            self.game = GameChoise(self.main)
            self.main.scroll1.setWidget(self.game)


class GameWordTranslate(QWidget):
    def __init__(self, main, lang):
        super().__init__()
        self.main = main
        uic.loadUi('design/game_word_translate.ui', self)
        self.count = 0
        self.dif = []
        self.answer = False
        self.true_w_count = 0
        self.btns = [self.w1, self.w2, self.w3, self.w4, self.w5]
        self.block1()
        self.make_sp(lang)
        self.game_main()
        self.back1.clicked.connect(self.back)
        self.ans1.clicked.connect(self.ans_next)
        self.w1.clicked.connect(self.check_truly)
        self.w2.clicked.connect(self.check_truly)
        self.w3.clicked.connect(self.check_truly)
        self.w4.clicked.connect(self.check_truly)
        self.w5.clicked.connect(self.check_truly)

    def block1(self):
        '''Block to change tab'''
        self.main.translate1.setEnabled(False)
        self.main.dict1.setEnabled(False)
        self.main.minigames1.setEnabled(False)
        self.main.statistic1.setEnabled(False)
        self.main.settings1.setEnabled(False)

    def keyPressEvent(self, event):
        '''Hot keys'''
        if event.key() == Qt.Key_Return:
            self.ans_next()
        elif event.key() == Qt.Key_Escape:
            self.back()

    def change_count(self):
        '''Update counts'''
        self.count = self.all - len(self.words_sp) - 1
        self.words1.setText(f'Слова: {self.count}/{self.all}')
        self.true_words1.setText(f'Правильных: {self.true_w_count}/{self.all}')

    def ans_next(self):
        '''Main button'''
        if self.ans1.text() == 'Не знаю':
            for i in self.btns:
                i.setEnabled(False)
                if i.text() == self.true_word:
                    i.setStyleSheet('background: #58BB55')
            self.add_error()
            self.ans1.setText('Далее')
        elif self.ans1.text() == 'Далее':
            self.ans1.setText('Не знаю')
            if self.words_sp != []:
                self.game_main()
            else:
                self.end_game()

    def game_main(self):
        '''Main game function'''
        self.cur_word = self.words_sp.pop(0)
        self.true_word = self.cur_word[1]
        self.need_word.setText(self.cur_word[0])
        self.make_btns_words()
        self.change_count()

    def make_btns_words(self):
        '''This function make 5 variants of answer'''
        for i in self.btns:
            i.setEnabled(True)
            i.setText('')
            i.setStyleSheet('background: white')
        self.dif = []
        self.dif.append(self.true_word)
        btn = choice(self.btns)
        btn.setText(self.true_word)
        for i in self.btns:
            if i.text() == '':
                word = choice(self.other_words)
                while word in self.dif:
                    word = choice(self.other_words)
                self.dif.append(word)
                i.setText(word)

    def check_truly(self):
        '''Chose answer and check its truly'''
        for i in self.btns:
            i.setEnabled(False)
        if self.sender().text() == self.true_word:
            self.sender().setStyleSheet('background: #58BB55')
            self.true_w_count += 1
            self.add_true()
        else:
            self.sender().setStyleSheet('background: #FC172E')
            self.add_error()
            for i in self.btns:
                if i.text() == self.true_word:
                    i.setStyleSheet('background: #58BB55')
        self.ans1.setText('Далее')

    def add_true(self):
        global cursor
        '''Add true writing to database'''
        cursor.execute('''UPDATE Words
        SET true = 1 + (SELECT true FROM Words 
        WHERE (english = ? AND russian = ?) OR (english = ? AND russian = ?))
        WHERE (english = ? AND russian = ?) OR (english = ? AND russian = ?)''',
                       (self.cur_word[0], self.cur_word[1], self.cur_word[1], self.cur_word[0],
                        self.cur_word[0], self.cur_word[1], self.cur_word[1],
                        self.cur_word[0]))  # not enogh information
        con.commit()

    def add_error(self):
        '''Add error writing to database'''
        cursor.execute('''UPDATE Words
                SET error = 1 + (SELECT error FROM Words 
                WHERE (english = ? AND russian = ?) OR (english = ? AND russian = ?))
                WHERE (english = ? AND russian = ?) OR (english = ? AND russian = ?)''',
                       (self.cur_word[0], self.cur_word[1], self.cur_word[1], self.cur_word[0],
                        self.cur_word[0], self.cur_word[1], self.cur_word[1],
                        self.cur_word[0]))
        con.commit()

    def make_sp(self, lang):
        global cursor
        '''Main function for translation game'''
        self.other_words = []
        if lang == 'en':
            res = cursor.execute('''SELECT english, russian FROM Words WHERE training = 1''').fetchall()
            all_w = cursor.execute('''SELECT russian FROM Words WHERE training = 1''').fetchall()
        elif lang == 'ru':
            res = cursor.execute('''SELECT russian, english FROM Words WHERE training = 1''').fetchall()
            all_w = cursor.execute('''SELECT english FROM Words WHERE training = 1''').fetchall()
        for i in all_w:
            self.other_words.append(str(i[0]))
        self.words_sp = []

        if len(res) < 10:
            shuffle(res)
            for i in res:
                self.words_sp.append((str(i[0]), str(i[1])))
        else:
            for i in range(10):
                a = choice(res)
                res.remove(a)
                self.words_sp.append((str(a[0]), str(a[1])))
        self.all = len(self.words_sp)
        if self.all < 5:
            for i in range(5 - self.all):
                a = self.btns.pop(-1)
                a.hide()

    def end_game(self):
        '''This function is the end of your way, the game is over, then only death'''
        self.main.translate1.setEnabled(True)
        self.main.dict1.setEnabled(True)
        self.main.minigames1.setEnabled(False)
        self.main.statistic1.setEnabled(True)
        self.main.settings1.setEnabled(True)
        self.main.scroll1.takeWidget()
        self.end = EndGame(self.main, self.true_w_count, self.all)
        self.main.scroll1.setWidget(self.end)

    def back(self):
        '''Exit from game'''
        q = Question('Вы действительно хотите <br/> завершить игру?')
        q.show()
        q.exec()
        if q.result():
            self.main.translate1.setEnabled(True)
            self.main.dict1.setEnabled(True)
            self.main.minigames1.setEnabled(False)
            self.main.statistic1.setEnabled(True)
            self.main.settings1.setEnabled(True)
            self.main.scroll1.takeWidget()
            self.game = Minigames(self.main)
            self.main.scroll1.setWidget(self.game)


class EndGame(QWidget):
    def __init__(self, main, true_ans, all):
        super().__init__()
        uic.loadUi('design/end_game_form.ui', self)
        self.main = main
        self.res = true_ans / all * 100
        self.results1.setText(f'Ваш результат: {round(self.res)}%')
        if 75 <= self.res <= 100:
            self.status1.setIcon(QIcon('design/images/cat_smile.png'))
        elif 50 <= self.res < 75:
            self.status1.setIcon(QIcon('design/images/pochti_good.png'))
        elif 25 <= self.res < 50:
            self.status1.setIcon(QIcon('design/images/cat_angry.png'))
        elif self.res < 25:
            self.status1.setIcon(QIcon('design/images/cat_v_shoke.png'))
        self.update_stat(true_ans, all - true_ans, all)
        self.stat1.clicked.connect(self.stat_form)
        self.back1.clicked.connect(self.back)
        self.sanovo1.clicked.connect(self.sanovo)

    def stat_form(self):
        self.main.scroll1.takeWidget()
        self.game = Statistic()
        self.main.scroll1.setWidget(self.game)

    def update_stat(self, tr, er, all):
        global cursor
        cursor.execute('''INSERT INTO Statistic(true_input, error_input, words_count) 
        VALUES(?, ?, ?)''', (tr, er, all))
        cursor.execute('''UPDATE settings
        SET played_games = (SELECT played_games FROM settings) + 1''')
        con.commit()

    def sanovo(self):
        self.main.scroll1.takeWidget()
        self.game = Minigames(self.main)
        self.main.scroll1.setWidget(self.game)

    def back(self):
        '''Exit from resalts form'''
        self.main.scroll1.takeWidget()
        self.game = Minigames(self.main)
        self.main.scroll1.setWidget(self.game)


class GameChoise(QWidget):
    def __init__(self, main):
        super().__init__()
        uic.loadUi('design/game_choice.ui', self)
        self.main = main
        self.t2 = QTimer()
        self.score = 0
        self.broke_chain()
        self.block1()
        self.begin_timer(3)
        self.generate()
        self.back1.clicked.connect(self.back)
        self.ans1.clicked.connect(self.check_truly)
        self.ans2.clicked.connect(self.check_truly)
        # self.start_game()
        # self.end_game()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.check_truly()
        elif event.key() == Qt.Key_Return:
            self.check_truly(True)

    def begin_timer(self, k):
        '''Start back countdown until the game. 3...2...1...0..GOOOO! '''
        self.t1 = QTimer()
        self.timer1.setText(str(k))
        self.t1.setSingleShot(True)
        self.t1.timeout.connect(lambda: self.updateTime(k - 1))
        self.t1.start(1000)

    def del_block(self):
        '''Make buttons clickable'''
        self.ans1.setEnabled(True)
        self.ans2.setEnabled(True)

    def updateTime(self, k):
        self.timer1.setText(str(k))
        if k > 0:
            self.begin_timer(k)
        else:
            self.del_block()
            self.setTimer()
            self.start_game()

    def setTimer(self):
        self.t2 = QTimer()
        self.timer1.setText(str(30))
        self.t2.setSingleShot(True)
        self.t2.start(30000)
        self.t2.timeout.connect(self.end_game)

    def broke_chain(self):
        self.one.hide()
        self.two.hide()
        self.three.hide()
        self.bonus = 20
        self.chain = 0

    def check_bonus(self):
        self.chain += 1
        if self.chain == 1:
            self.one.show()
            self.two.hide()
            self.three.hide()
        elif self.chain == 2:
            self.one.show()
            self.two.show()
            self.three.hide()
        elif self.chain == 3:
            self.one.show()
            self.two.show()
            self.three.show()
            self.chain = 0
            self.score += self.bonus
            self.bonus += 10

    def start_game(self):
        '''Main function'''
        self.word1, self.word2 = self.make_new_words()
        self.need_word.setText(self.word1)
        self.is_true.setText(self.word2)

    def check_truly(self, true=False):
        '''Check you answer and write verdict'''
        if self.sender().text() == 'Верно' or true:
            if (self.word1, self.word2) in self.words:
                self.verdict.setIcon(QIcon('design/images/true1.png'))
                self.score += 10
                self.score1.setText(str(self.score))
                self.check_bonus()
            else:
                self.verdict.setIcon(QIcon('design/images/wrong1.png'))
                self.broke_chain()
        else:
            if (self.word1, self.word2) not in self.words:
                self.verdict.setIcon(QIcon('design/images/true1.png'))
                self.score += 10
                self.score1.setText(str(self.score))
                self.check_bonus()
            else:
                self.verdict.setIcon(QIcon('design/images/wrong1.png'))
                self.broke_chain()
        self.start_game()

    def end_game(self):
        '''This function is the end of your way, the game is over, then only death'''
        self.main.translate1.setEnabled(True)
        self.main.dict1.setEnabled(True)
        self.main.minigames1.setEnabled(False)
        self.main.statistic1.setEnabled(True)
        self.main.settings1.setEnabled(True)
        self.main.scroll1.takeWidget()
        self.end = EndTimerGame(self.main, self.score)
        self.main.scroll1.setWidget(self.end)

    def make_new_words(self):
        '''Make new words'''
        r = random()
        if r > 0.6:
            word = choice(self.words)
            return word
        else:
            word1 = choice(self.words)[0]
            word2 = choice(self.words)[1]
            return (word1, word2)

    def generate(self):
        '''Generate list of words'''
        global cursor
        res = cursor.execute('''SELECT english, russian FROM Words WHERE training = 1''')
        self.words = []
        for i in res:
            self.words.append(i)

    def block1(self):
        '''Block to change tab'''
        self.ans1.setEnabled(False)
        self.ans2.setEnabled(False)
        self.main.translate1.setEnabled(False)
        self.main.dict1.setEnabled(False)
        self.main.minigames1.setEnabled(False)
        self.main.statistic1.setEnabled(False)
        self.main.settings1.setEnabled(False)

    def back(self):
        '''Exit from game'''
        q = Question('Вы действительно хотите <br/> завершить игру?')
        q.show()
        q.exec()
        if q.result():
            self.main.translate1.setEnabled(True)
            self.main.dict1.setEnabled(True)
            self.main.minigames1.setEnabled(False)
            self.main.statistic1.setEnabled(True)
            self.main.settings1.setEnabled(True)
            self.main.scroll1.takeWidget()
            self.game = Minigames(self.main)
            self.main.scroll1.setWidget(self.game)


class EndTimerGame(QWidget):
    def __init__(self, main, score):
        super().__init__()
        uic.loadUi('design/end_timer_game.ui', self)
        self.main = main
        self.results1.setText(f'Ваш набрали: {score} очков')
        rec = cursor.execute('''SELECT record FROM settings''').fetchone()[0]
        if score > rec:
            rec = score
            cursor.execute('''UPDATE settings
            SET record = ?''', (score,))
        self.record1.setText(f'Рекорд: {str(rec)} очков')
        self.back1.clicked.connect(self.back)
        self.sanovo1.clicked.connect(self.sanovo)

    def sanovo(self):
        self.main.scroll1.takeWidget()
        self.game = Minigames(self.main)
        self.main.scroll1.setWidget(self.game)

    def back(self):
        '''Exit from resalts form'''
        self.main.scroll1.takeWidget()
        self.game = Minigames(self.main)
        self.main.scroll1.setWidget(self.game)


class Statistic(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('design/statistic_form.ui', self)
        self.update_graph()
        self.update_counts()

    def update_counts(self):
        '''Update counts true inputs and games count'''
        global cursor
        tr = cursor.execute('''SELECT played_games FROM settings''').fetchone()[0]
        self.all1.setText(f'Всего сыграно: {str(tr)}')
        all = cursor.execute('''SELECT true_input, error_input FROM Statistic''').fetchall()
        s = 0
        for i in all:
            s += i[0]
        self.true1.setText(f'Правильных вводов: {str(s)}')
        s = 0
        for i in all:
            s += i[1]
        self.false1.setText(f'Ошибочных вводов: {str(s)}')

    def update_graph(self):
        '''Build graph'''
        try:
            res = cursor.execute('''SELECT true_input, words_count FROM Statistic''').fetchall()
            last = res[-1]
            self.graph1.clear()
            self.graph1.plot([i for i in range(last[1])],
                             [last[0] / last[1] for i in range(last[1])], pen='g')
            self.graph2.clear()
            self.graph2.plot([i for i in range(len(res))],
                             [res[i][0] / res[i][1] for i in range(len(res))], pen='r')
        except BaseException:
            pass


class Settings(QWidget):
    def __init__(self, main):
        super().__init__()
        uic.loadUi('design/settings_form.ui', self)
        self.main = main
        self.sp_bg = ['design/images/grad1.png', 'design/images/grad2.png', 'design/images/grad3.png',
                      'design/images/grad4.png', 'design/images/grad5.png', 'design/images/grad6.png']
        self.change_bg.clicked.connect(self.change_background)
        self.set_my_bg1.clicked.connect(self.set_my_bg)
        self.reset_stat.clicked.connect(self.res_stat)
        self.reset_all.clicked.connect(self.res_all)

    def change_background(self):
        global cursor
        '''Change background'''
        res = cursor.execute('''SELECT background FROM settings''').fetchone()[0]
        if res in self.sp_bg:
            a = self.sp_bg.index(res)
            if a == len(self.sp_bg) - 1:
                el = self.sp_bg[0]
            else:
                el = self.sp_bg[a + 1]
        else:
            el = self.sp_bg[0]
        cursor.execute('''UPDATE settings
        SET background = ?''', (el,))
        con.commit()
        self.main.set_background()

    def set_my_bg(self):
        try:
            self.fname = QFileDialog.getOpenFileName(self, 'Выбрать фон', '')[0]
            cursor.execute('''UPDATE settings
                    SET background = ?''', (self.fname,))
            con.commit()
            self.main.set_background()
        except ValueError:
            pass

    def res_all(self):
        '''Delete all that you love'''
        global cursor
        q = Question('Вы действительно хотите <br/> очистить все данные?')
        q.show()
        q.exec()
        if q.result():
            self.res_stat()
            cursor.execute('''DELETE FROM Words''')
            cursor.execute('''UPDATE settings
            SET background = ""''')
        self.change_background()

    def res_stat(self):
        '''Delete all statistic data'''
        global cursor
        q = Question('Вы действительно хотите <br/> очистить всю статистику?')
        q.show()
        q.exec()
        if q.result():
            cursor.execute('''DELETE FROM Statistic''')
            cursor.execute('''UPDATE Words
            SET true = 0, error = 0''')
            cursor.execute('''UPDATE settings
            SET played_games = 0, record = 0''')
            con.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    n = LinguaCat()
    n.show()
    sys.exit(app.exec_())
# 1061 811
