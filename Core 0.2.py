import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import json
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)


        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.add_new_tab(QUrl("http://google.com"), "Главная")

        self.setWindowTitle('Core V0.2')

        navtb = QToolBar()
        self.addToolBar(navtb)

        home_btn = QAction("Домой", self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        back_btn = QAction("Назад", self)
        back_btn.triggered.connect(self.current_browser.back)
        navtb.addAction(back_btn)

        next_btn = QAction("Вперед", self)
        next_btn.triggered.connect(self.current_browser.forward)
        navtb.addAction(next_btn)

        reload_btn = QAction("Перезагрузить", self)
        reload_btn.triggered.connect(self.current_browser.reload)
        navtb.addAction(reload_btn)

        new_tab_btn = QAction("Новая вкладка", self)
        new_tab_btn.triggered.connect(self.add_new_tab_from_button)
        navtb.addAction(new_tab_btn)

        close_tab_btn = QAction("Закрыть вкладку", self)
        close_tab_btn.triggered.connect(self.close_current_tab)
        navtb.addAction(close_tab_btn)

        toggle_dark_btn = QAction("Сменить тему", self)
        toggle_dark_btn.triggered.connect(self.toggle_dark_theme)
        navtb.addAction(toggle_dark_btn)  # Добавляем кнопку в QToolBar
        self.load_state()  # Загрузка состояния вкладок


        self.show()

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        self.progress = QProgressBar()
        navtb.addWidget(self.progress)

        self.show()

    def toggle_dark_theme(self):
        # Логика смены темы
        if self.styleSheet() == "":
            self.setStyleSheet("background-color: #333; color: #fff;")
        else:
            self.setStyleSheet("")
        self.save_state()

    def closeEvent(self, event):
        self.save_state()  # Сохранение состояния вкладок при закрытии приложения
        event.accept()

    def save_state(self):
        state = {
            "current_tab_index": self.tabs.currentIndex(),
            "tab_urls": [self.tabs.widget(i).url().toString() for i in range(self.tabs.count())],
            "theme": self.styleSheet()
        }
        with open('browser_state.json', 'w') as f:
            json.dump(state, f)

    def load_state(self):
        try:
            with open('browser_state.json', 'r') as f:
                state = json.load(f)
                current_tab_index = state.get("current_tab_index", 0)
                tab_urls = state.get("tab_urls", [])
                theme = state.get("theme", "")

                if tab_urls:
                    for url in tab_urls:
                        self.add_new_tab(QUrl(url))
                    self.tabs.setCurrentIndex(current_tab_index)

                if theme:
                    self.setStyleSheet(theme)

        except FileNotFoundError:
            pass  # Игнорировать если файл состояния не найден


    def add_new_tab(self, qurl=None, label="Пустая страница"):
        if qurl is None:
            qurl = QUrl('http://google.com')

        browser = QWebEngineView()
        browser.setUrl(qurl)

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))
        browser.loadProgress.connect(self.update_progress)  # Связываем обновление прогресса загрузки с функцией

    def add_new_tab_from_button(self):
        self.add_new_tab()

    def close_current_tab(self):
        if self.tabs.count() < 2:
            return
        index = self.tabs.currentIndex()
        widget = self.tabs.widget(index)
        widget.deleteLater()

    def navigate_home(self):
        self.current_browser.setUrl(QUrl("http://google.com"))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("https")
        self.current_browser.setUrl(q)


    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def update_progress(self, progress):
        self.progress.setValue(progress)  # Обновляем значение прогресса загрузки

    @property
    def current_browser(self):
        return self.tabs.currentWidget()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
