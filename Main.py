import sys
import sqlite3
from random import sample, randint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QAction
from PyQt5.QtWidgets import QWidget, QRadioButton, QLabel, QMessageBox
from Quiz_ui import Ui_MainWindow
from MainMenu_ui import Ui_MainMenu

SCREEN_SIZE = [800, 600]
IMAGES = 'images/'


class QuMainMenu(Ui_MainMenu, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.setGeometry(400, 200, *SCREEN_SIZE)

        self.pushButton_start.clicked.connect(self.start)

    def start(self):
        self.quiz = Quiz()
        self.quiz.show()
        self.close()


class Quiz(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.setGeometry(400, 200, *SCREEN_SIZE)

        self.con = sqlite3.connect("questions.db")
        self.cur = self.con.cursor()

        self.tasks_n = self.cur.execute("""SELECT seq FROM sqlite_sequence
        WHERE name = 'tasks'""").fetchall()[0][0]
        self.var_n = self.cur.execute("""SELECT seq FROM sqlite_sequence
        WHERE name = 'vars'""").fetchall()[0][0]


        self.restart()
        self.pushButton_next.clicked.connect(self.next_q)

    def __del__(self):
        self.con.close()

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

    def restart(self):
        self.seq = sample(range(1, self.tasks_n + 1), self.tasks_n)
        print(self.seq)
        self.i = 0
        self.answer = None
        self.q_num = 0
        self.next_q()
        self.score = 0

    def set_image(self, im_name):
        self.pixmap = QPixmap(IMAGES + im_name)
        self.label_image.setPixmap(self.pixmap)
        

    def show_result(self):
        self.show_res_widget = ShowResult(self.score, self.q_num)
        self.show_res_widget.show()

    def end(self):
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
                break
            
        if self.i < self.tasks_n:
            print('ok next')
            print('i =', self.i)
        else:
            if self.end():
                return None
            self.seq = sample(range(1, self.tasks_n + 1), self.tasks_n)
            self.i = 0
            print(self.seq)

        im_name, true_id = self.cur.execute(f"""SELECT image, "true" FROM tasks
        WHERE id = {self.seq[self.i]}""").fetchall()[0]
        print(im_name)
        self.set_image(im_name)

        false_vars = self.gen_false_vars(true_id)
        print(false_vars)
        true_var = self.cur.execute(f"""SELECT var FROM vars
        WHERE id = {true_id}""").fetchall()[0][0]

        self.answer = randint(1, 4)
        print(self.answer)

        for i in range(1, 5):
            if i != self.answer:
                print(false_vars)
                j = false_vars.pop()[0]
                self.ans_button(i).setText(j)
            else:
                print(i)
                self.ans_button(i).setText(true_var)

        self.i += 1
        self.q_num += 1


class ShowResult(QWidget):
    def __init__(self, *res):
        super().__init__()
        self.initUi(res)

    def initUi(self, res):
        self.setGeometry(500, 300, 200, 200)

        self.label = QLabel(self)
        self.label.setText("Поздраляем!\n Ваш результат " +
                           "{} из {}.".format(*res))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    quiz_app = QuMainMenu()
    quiz_app.show()
    sys.exit(app.exec())
