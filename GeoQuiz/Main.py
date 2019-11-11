import sys
import sqlite3
from random import sample, randint
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QAction
from PyQt5.QtWidgets import QWidget, QRadioButton, QLabel, QMessageBox
from PyQt5.QtWidgets import QPushButton
from Quiz_ui import Ui_MainWindow, Ui_MainMenu, Ui_InfWindow

INIT_POS = [400, 200]
SCREEN_SIZE = [800, 600]
IMAGES = 'images/'
STATS = '.statistics'


def get_stats():
    with open(STATS) as stat_f:
        stat_data = stat_f.read().splitlines()
    return stat_data


def set_stats(stat_data=None):
    if stat_data is None:
        stat_data = ['0', '0']
    else:
        stat_data = [str(i) for i in stat_data]
    with open(STATS, 'w') as stat_f:
        stat_f.write('\n'.join(stat_data))


class QuMainMenu(Ui_MainMenu, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.setGeometry(*INIT_POS, *SCREEN_SIZE)

        self.check_stats()

        self.pushButton_start.clicked.connect(self.start)
        self.pushButton_stats.clicked.connect(self.stats)
        self.pushButton_exit.clicked.connect(self.exit_ask)

    def check_stats(self):
        try:
            get_stats()[1]
        except FileNotFoundError:
            set_stats()
        except IndexError:
            set_stats()

    def exit_ask(self):
        reply = QMessageBox.question(self, '',
                            "Вы уверены?",
                            QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

    def start(self):
        self.quiz = Quiz(self.show)
        self.quiz.show()
        self.hide()

    def stats(self):
        self.stat_window = Stats()
        self.stat_window.show()
            

class Stats(Ui_InfWindow, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.setGeometry(INIT_POS[0] + 50, INIT_POS[1] + 50, *SCREEN_SIZE)

        self.pushButton_back = QPushButton('<--Назад', self)
        self.pushButton_back.resize(self.pushButton_back.sizeHint())
        self.pushButton_back.move(40, 30)
        self.pushButton_back.clicked.connect(self.close)
        self.pushButton_back.setFont(QFont('Arial', 20))

        self.pushButton_reset  = QPushButton('Сбросить статистику', self)
        self.pushButton_reset.resize(self.pushButton_reset.sizeHint())
        self.pushButton_reset.move(90, 200)
        self.pushButton_reset.clicked.connect(self.reset_stats)
        self.pushButton_reset.setFont(QFont('Arial', 20))
        
        self.label_st = QLabel(self)
        self.label_st.move(50, 100)
        self.show_stats()
        self.label_st.resize(self.label_st.sizeHint())

    def show_stats(self):
        stat_data = get_stats()
        self.label_st.setText(f"Общее число тестов: {stat_data[0]}\nCредний "
                              f"процент выполнения:"
                              f"{stat_data[1]}%")

    def reset_stats(self):
        reset_sure = QMessageBox.question(self, '',
                                         "Вы точно хотите сбросить статистику "
                                         "без возможности восстановления?",
                                         QMessageBox.Yes | QMessageBox.No)
        if reset_sure == QMessageBox.Yes:
            set_stats()
        self.show_stats()

class Quiz(Ui_MainWindow, QMainWindow):
    def __init__(self, main_menu_show):
        super().__init__()
        self.setupUi(self)
        self.initUi()
        self.main_menu_show = main_menu_show

    def initUi(self):
        self.setGeometry(400, 200, *SCREEN_SIZE)

        self.safe_exit = True

        self.con = sqlite3.connect("questions.db")
        self.cur = self.con.cursor()

        self.tasks_n = self.cur.execute("""SELECT seq FROM sqlite_sequence
        WHERE name = 'tasks'""").fetchall()[0][0]
        self.var_n = self.cur.execute("""SELECT seq FROM sqlite_sequence
        WHERE name = 'vars'""").fetchall()[0][0]

        self.menu_options = self.menubar.addMenu("Опции")
        finish = QAction("Завершить", self)
        finish.setShortcut("Esc")
        finish.triggered.connect(self.close)
        main_menu = QAction("Главное Меню", self)
        main_menu.triggered.connect(self.open_main_menu)
        self.menu_options.addActions((main_menu, finish))

        self.restart()
        self.pushButton_next.clicked.connect(self.next_q)

    def __del__(self):
        self.con.close()

    def open_main_menu(self):
        exit_sure = self.finish()
        if exit_sure:
            self.main_menu_show()
            self.safe_exit = False
            self.close()

    def finish(self):
        finish_sure = QMessageBox.question(self, '',
                                         "Хотите узнать и сохранить результат "
                                         "перед выходом?",
                                         QMessageBox.Yes | QMessageBox.No |
                                         QMessageBox.Cancel)
        if finish_sure == QMessageBox.Yes:
            self.show_result()
            self.save_stats()
            return True
        elif finish_sure == QMessageBox.No:
            return True
        else:
            return False

    def closeEvent(self, event):
        if not self.safe_exit:
            super(Quiz, self).closeEvent(event)
        else:
            finish_sure = self.finish()
            if finish_sure:
                super(Quiz, self).closeEvent(event)
            else:
                event.ignore()

    def ans_button(self, i):
        if i > 2:
            if i > 3:
                return self.radioButton_4
            else:
                return self.radioButton_3
        elif i > 1:
            return self.radioButton_2
        else:
            return self.radioButton_1

    def correct_rate(self):
        return round(self.score / (self.q_num - 1) * 100, 2)

    def save_stats(self):
        stat_data = [int(i) for i in get_stats()]
        if self.q_num <= 1:
            stat_data[0] += 1
        else:
            stat_data[1] = stat_data[1] * stat_data[0] + self.correct_rate() /\
                           (stat_data[0] + 1)
            stat_data[0] += 1
        set_stats(stat_data)

    def restart(self):
        self.seq = sample(range(1, self.tasks_n + 1), self.tasks_n)
        self.i = 0
        self.answer = None
        self.q_num = 0
        self.next_q()
        self.score = 0

    def set_image(self, im_name):
        self.pixmap = QPixmap(IMAGES + im_name)
        self.label_image.setPixmap(self.pixmap)
        

    def show_result(self):
        self.show_res_widget = ShowResult(self.score, self.q_num - 1)
        self.show_res_widget.show()
        self.save_stats()

    def finish_all(self):
        retry = QMessageBox.question(self, '',
                            "Все задания теста пройдены.\n" +
                            "Хотите узнать результат и начать заново?",
                            QMessageBox.Yes, QMessageBox.No)
        if retry == QMessageBox.Yes:
            self.show_result()
            self.restart()
            return True
        else:
            return False

    def gen_false_vars(self, true_id):
        potential_var_ids = [i for i in range(1, self.var_n + 1)]
        potential_var_ids.remove(true_id)
        false_var_ids = tuple(sample(potential_var_ids, 3))
        return self.cur.execute(f"""SELECT var FROM vars
                        WHERE id IN {false_var_ids}""").fetchall()

    def next_q(self):
        for i in range(1, 5):
            if self.ans_button(i).isChecked():
                if self.answer == i:
                    self.score += 1
                checked_button = self.ans_button(i)
                checked_button.setAutoExclusive(False)
                checked_button.setChecked(False)
                checked_button.setAutoExclusive(True)
                break
            
        if self.i >= self.tasks_n:
            if self.finish_all():
                return None
            self.seq = sample(range(1, self.tasks_n + 1), self.tasks_n)
            self.i = 0

        im_name, true_id = self.cur.execute(f"""SELECT image, "true" FROM tasks
        WHERE id = {self.seq[self.i]}""").fetchall()[0]
        self.set_image(im_name)

        false_vars = self.gen_false_vars(true_id)
        true_var = self.cur.execute(f"""SELECT var FROM vars
        WHERE id = {true_id}""").fetchall()[0][0]

        self.answer = randint(1, 4)
        print(self.answer)

        for i in range(1, 5):
            if i != self.answer:
                j = false_vars.pop()[0]
                self.ans_button(i).setText(j)
            else:
                self.ans_button(i).setText(true_var)

        self.i += 1
        self.q_num += 1


class ShowResult(Ui_InfWindow, QWidget):
    def __init__(self, *res):
        super().__init__()
        self.setupUi(self)
        self.initUi(res)

    def initUi(self, res):
        self.setGeometry(500, 300, *SCREEN_SIZE)

        self.label = QLabel(self)
        self.label.setText("Поздраляем!\nВаш результат " +
                           "{} из {}.".format(*res))
        self.label.move(150, 150)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    quiz_app = QuMainMenu()
    quiz_app.show()
    sys.exit(app.exec())
