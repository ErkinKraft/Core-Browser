import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.add_new_tab(QUrl("http://google.com"), "Главная")

        self.setWindowTitle('Core V0.3')

        navtb = self.addToolBar('Button')
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

        browser_menu = QMenu()
        for browser in ["Chrome", "Safari", "Yandex", "Yahoo", "FireFox"]:
            action = QAction(browser, self)
            action.triggered.connect(lambda checked, browser=browser: self.changeUserAgent(browser))
            browser_menu.addAction(action)

        select_browser_btn = QAction('Эмитация браузера', self)
        select_browser_btn.setMenu(browser_menu)
        navtb.addAction(select_browser_btn)

        navtb.addAction(toggle_dark_btn)  # Добавляем кнопку в QToolBar

        about_us_btn = QAction("О нас", self)  # Создаем кнопку "О нас"
        about_us_btn.triggered.connect(self.show_about_us_dialog)  # Подключаем обработчик события
        navtb.addAction(about_us_btn)  # Добавляем кнопку в QToolBar




        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        self.progress = QProgressBar()
        navtb.addWidget(self.progress)

        self.show()

    def show_about_us_dialog(self):
        self.current_browser.setUrl(QUrl("https://github.com/ErkinKraft"))
        msg = QMessageBox()
        msg.setWindowTitle("О нас")
        msg.setText("\n"
                    "Core 0.3\n"
                    "EK SoftWare \n")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()


    def changeUserAgent(self, browser):
        user_agents = {
            "Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Safari": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
            "Yandex": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 YaBrowser/21.6.1 Yowser/2.5 Safari/537.36",
            "Yahoo": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 YaBrowser/21.6.1 Yowser/2.5 Safari/537.36",
            "FireFox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"

        }

        user_agent = user_agents.get(browser, "")

        if user_agent:
            profile = QWebEngineProfile.defaultProfile()
            profile.setHttpUserAgent(user_agent)

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
        self.browser.setUrl(QUrl("https://www.example.com"))


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
