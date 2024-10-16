import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from requests_toolbelt import MultipartEncoder
import time

# Здесь собраны переменные, необходимо указать в них email`ы и номер телефона, к которым есть доступ,
# так как нужно будет вводить коды, приходящие на эти почты и телефон.
valid_login_email = 'email1'
valid_login_email1 = 'email2'
valid_login_phone = 'phone'
# Перечислены валидные пароли, их можно заменить (на валидные).
valid_password1 = 'Qfvjeori2wi5r'
valid_password2 = 'Xgkdpemt3ier4'
valid_password3 = 'L1jrog40itrio'
valid_password4 = 'J34;pdrgkoeie'
# Имена и фамилии нужны для регистрации пользователей, их также можно менять (на валидные).
name1 = 'Вася'
surname1 = 'Петров'
name2 = 'Петр'
surname2 = 'Васильев'
name3= 'Николай'
surname3 = 'Иванов'

# В фикстуре прописано явное ожидание, оно нужно, чтобы тесты начинались только после того,
# как сайт прогрузится.
@pytest.fixture(autouse=True)
def driver():
    driver = webdriver.Chrome()
    # В браузере открывается страница авторизации Ростелеком
    driver.get('https://b2c.passport.rt.ru/')
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "kc-register")))

    yield driver

    driver.quit()

# TC-1
# Позитивный тест, проверяет работу кнопки "Зарегистрироваться":
# нажатие на нее осуществляет переход на страницу регистрации.
def test_btn_login_on_auth_page(driver):
    driver.find_element(By.ID, 'kc-register').click()
    assert driver.find_element(By.ID, 'card-title')

# TC-2
# Позитивный тест, осуществляет регистрацию пользователя с валидными данными и использованием почты.
def test_login_with_valid_email_valid_password(driver):
    # Переход на страницу регистрации
    driver.find_element(By.ID, 'kc-register').click()
    # Последовательный ввод: имя, фамилия, валидный email и валидный пароль
    driver.find_element(By.NAME, 'firstName').send_keys(name1)
    driver.find_element(By.NAME, 'lastName').send_keys(surname1)
    driver.find_element(By.ID, 'address').send_keys(valid_login_email)
    driver.find_element(By.ID, 'password').send_keys(valid_password1)
    # Повторный ввод пароля
    driver.find_element(By.ID, 'password-confirm').send_keys(valid_password1)
    # Нажатие кнопки "Зарегистрироваться"
    driver.find_element(By.NAME, 'register').click()
    # Здесь заложена пауза 60с: необходимо успеть ввести шестизначный код самостоятельно из входящего письма
    time.sleep(60)
    # Данный ID находится в личном кабинете зарегистрированного пользователя
    assert driver.find_element(By.ID, 'login_input')

# TC-3
# Позитивный тест, осуществляет регистрацию пользователя с валидными данными и использованием номера телефона.
def test_login_with_valid_phone_valid_password(driver):
    # Переход на страницу регистрации
    driver.find_element(By.ID, 'kc-register').click()
    # Последовательный ввод: имя, фамилия, валидный номер телефона и валидный пароль
    driver.find_element(By.NAME, 'firstName').send_keys(name2)
    driver.find_element(By.NAME, 'lastName').send_keys(surname2)
    driver.find_element(By.ID, 'address').send_keys(valid_login_phone)
    driver.find_element(By.ID, 'password').send_keys(valid_password2)
    # Повторный ввод пароля
    driver.find_element(By.ID, 'password-confirm').send_keys(valid_password2)
    # Нажатие кнопки "Зарегистрироваться"
    driver.find_element(By.NAME, 'register').click()
    # Здесь заложена пауза 60с: необходимо успеть ввести шестизначный код из входящего СМС
    time.sleep(60)
    # Данный ID находится в личном кабинете зарегистрированного пользователя
    assert driver.find_element(By.ID, 'login_input')

# TC-4
# Негативный тест, осуществляет регистрацию пользователя с валидными данными и использованием почты,
# но использует неверный шестизначный код.
def test_login_with_valid_email_valid_password_invalid_key(driver):
    # Переход на страницу регистрации
    driver.find_element(By.ID, 'kc-register').click()
    # Последовательный ввод: имя, фамилия, валидный номер телефона и валидный пароль дважды
    driver.find_element(By.NAME, 'firstName').send_keys(name3)
    driver.find_element(By.NAME, 'lastName').send_keys(surname3)
    driver.find_element(By.ID, 'address').send_keys(valid_login_email1)
    driver.find_element(By.ID, 'password').send_keys(valid_password1)
    driver.find_element(By.ID, 'password-confirm').send_keys(valid_password1)
    # Нажатие кнопки "Зарегистрироваться"
    driver.find_element(By.NAME, 'register').click()
    # Ввод неверного шестизначного кода (можно подставить свой в ''). В этом случае переход ни на какую страницу не осуществляется,
    # тест падает.
    driver.find_element(By.ID, 'rt-code-input').send_keys('111111')
    assert Exception('NoSuchElementException')

# TC-5
# Негативный тест, осуществляет регистрацию пользователя с валидными данными и использованием почты,
# но использует шестизначный код с истекшим сроком действия (120с).
def test_login_with_valid_email_valid_password_expired_key(driver):
    # Переход на страницу регистрации
    driver.find_element(By.ID, 'kc-register').click()
    # Последовательный ввод: имя, фамилия, валидный номер телефона и валидный пароль дважды
    driver.find_element(By.NAME, 'firstName').send_keys(name3)
    driver.find_element(By.NAME, 'lastName').send_keys(surname3)
    driver.find_element(By.ID, 'address').send_keys(valid_login_email1)
    driver.find_element(By.ID, 'password').send_keys(valid_password1)
    driver.find_element(By.ID, 'password-confirm').send_keys(valid_password1)
    # Нажатие кнопки "Зарегистрироваться"
    driver.find_element(By.NAME, 'register').click()
    # Здесь заложена пауза 150с, код необходимо ввести вручную через 120с.
    # В этом случае переход ни на какую страницу не осуществляется, тест падает.
    time.sleep(150)
    assert Exception('NoSuchElementException')

# TC-6
# Очень большой негативный тест, проверяет невозможность регистрации с невалидными данными.
# Использована множественная параметризация, а именно: заложены 4 параметра - имя, фамилия, логин и пароль
# со следующим количеством проверяемых вариантов, соответственно: 5, 5, 8, 6. Это дает около 1200 сочетаний.
# Все эти тесты выполняются в автоматическом режиме, но на driver есть явное ожидание до 10с.
# При подборе вариантов использованы граничные значения, классы эквивалентности, учтены все ограничения из брифа,
# а также ограничения, выясненные в ходе тестирования.
@pytest.mark.parametrize('name'
   , ['', 'П', '-', 'ann', '123']
   , ids=['empty', '1 symbol', 'dash', 'latin', 'digit'])
@pytest.mark.parametrize('surname'
   , ['', 'П', '-', 'ann', '123']
   , ids=['empty', '1 symbol', 'dash', 'latin', 'digit'])
@pytest.mark.parametrize('email_phone'
   , ['', 'natalya.nesynova@gmail.com', 'natalya.nesynovagmail.com', 'natalya.nesynova@gmail', '11111111111', '1111111111111', 'wwwwwwwwwwww', '+79969314282']
   , ids=['empty', 'existing email', 'without @', 'without .com', '11 digit', '13 digit', '12 str', 'existing phone'])
@pytest.mark.parametrize('password'
   , ['', 'qW2edfr', 'qwscnkogjklde1we', 'Фыц3ува4ке5нпр', 'QgsdgtWfghbkmj', '123ABCD']
   , ids=['empty', '7 symbols', 'without upper', 'russian', 'no digit', 'insecure'])
def test_negative_login(driver, name, surname, email_phone, password):
    driver.find_element(By.ID, 'kc-register').click()
    driver.find_element(By.NAME, 'firstName').send_keys(name)
    driver.find_element(By.NAME, 'lastName').send_keys(surname)
    driver.find_element(By.ID, 'address').send_keys(email_phone)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.ID, 'password-confirm').send_keys(password)
    driver.find_element(By.NAME, 'register').click()
    # Тест падает, невалидные данные не принимаются
    assert Exception('NoSuchElementException')

# TC-7
# Позитивный тест, проверяет работу кнопки "Помощь" на странице регистрации:
# она открывает окно с популярными вопросами поверх страницы.
def test_btn_help_on_login_page(driver):
    # Переход на страницу регистрации
    driver.find_element(By.ID, 'kc-register').click()
    # Нажатие кнопки "Помощь"
    driver.find_element(By.LINK_TEXT, 'Помощь').click()
    # Проверка по "крестику" на открывшемся окне помощи
    assert driver.find_element(By.ID, 'faq-close')

# TC-8
# Позитивный тест, проверяет работу кнопки "Забыл пароль" на странице авторизации.
def test_btn_forget_password_on_login_page(driver):
    # Нажатие кнопки "Забыл пароль"
    driver.find_element(By.ID, 'forgot_password').click()
    # Проверка по ID капчи на странице восстановления пароля
    assert driver.find_element(By.ID, 'captcha_id')

# TC-9
# Позитивный тест, проверяет работу 4 кнопок в верхнем меню страницы восстановления пароля.
def test_4btns_password_recovery_on_recovery_page(driver):
    # Переход на страницу восстановления пароля
    driver.find_element(By.ID, 'forgot_password').click()
    # Клик по кнопке "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Проверка смены полупрозрачного текста в поле ввода
    assert driver.find_element(By.XPATH, '//span[text() = "Мобильный телефон"]')
    # Клик по кнопке "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Проверка смены полупрозрачного текста в поле ввода
    assert driver.find_element(By.XPATH, '//span[text() = "Электронная почта"]')
    # Клик по кнопке "Логин"
    driver.find_element(By.ID, 't-btn-tab-login').click()
    # Проверка смены полупрозрачного текста в поле ввода
    assert driver.find_element(By.XPATH, '//span[text() = "Логин"]')
    # Клик по кнопке "Лицевой счет"
    driver.find_element(By.ID, 't-btn-tab-ls').click()
    # Проверка смены полупрозрачного текста в поле ввода
    assert driver.find_element(By.XPATH, '//span[text() = "Лицевой счёт"]')

# TC-10
# Позитивный тест, проверяет работу кнопки "Помощь" на странице восстановления пароля:
# она открывает окно с популярными вопросами поверх страницы.
def test_btn_help_on_recovery_page(driver):
    # Нажатие кнопки "Забыл пароль" и переход на соответствующую страницу
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Помощь"
    driver.find_element(By.LINK_TEXT, 'Помощь').click()
    # Проверка по "крестику" на открывшемся окне
    assert driver.find_element(By.ID, 'faq-close')

# TC-11
# Позитивный тест, проверяет работу кнопки "Вернуться назад" на странице восстановления пароля.
def test_btn_reset_back_on_recovery_page(driver):
    # Переход на страницу восстановления пароля
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Вернуться назад"
    driver.find_element(By.ID, 'reset-back').click()
    # Проверка по ID элемента на странице авторизации
    assert driver.find_element(By.ID, "kc-login")

# TC-12
# Позитивный тест, проверяет возможность восстановления пароля с использованием валидных данных (email).
def test_recovery_with_valid_email_on_recovery_page(driver):
    # Нажатие кнопки "Забыл пароль"
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Пауза 30с для самостоятельного ввода символов с капчи в соответствующее поле
    time.sleep(30)
    # Ввод валидного email
    driver.find_element(By.ID, 'username').send_keys(valid_login_email)
    # Нажатие кнопки "Продолжить"
    driver.find_element(By.ID, 'reset').click()
    # Пауза 60с для самостоятельного ввода шестизначного кода из входящего письма
    time.sleep(60)
    # Ввод валидного пароля последовательно в два необходимых поля
    driver.find_element(By.ID, 'password-new').send_keys(valid_password2)
    driver.find_element(By.ID, 'password-confirm').send_keys(valid_password2)
    driver.find_element(By.ID, 't-btn-reset-pass').click()
    # Проверка по ID кнопки на странице авторизации,
    # куда система автоматически направляет после восстановления пароля.
    assert driver.find_element(By.ID, 't-btn-tab-mail')

# TC-13
# Позитивный тест, проверяет возможность восстановления пароля с использованием валидных данных (номер телефона).
def test_recovery_with_valid_phone_on_recovery_page(driver):
    # Нажатие кнопки "Забыл пароль"
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Пауза 30с для самостоятельного ввода символов с капчи в соответствующее поле
    time.sleep(30)
    # Ввод валидного номера телефона
    driver.find_element(By.ID, 'username').send_keys(valid_login_phone)
    # Нажатие кнопки "Продолжить"
    driver.find_element(By.ID, 'reset').click()
    # Пауза 45с для самостоятельного ввода шестизначного кода из входящего СМС
    time.sleep(45)
    # Ввод валидного пароля последовательно в два необходимых поля
    driver.find_element(By.ID, 'password-new').send_keys(valid_password3)
    driver.find_element(By.ID, 'password-confirm').send_keys(valid_password3)
    driver.find_element(By.ID, 't-btn-reset-pass').click()
    # Проверка по ID кнопки на странице авторизации,
    # куда система автоматически направляет после восстановления пароля.
    assert driver.find_element(By.ID, 't-btn-tab-mail')

# TC-14
# Негативный тест, проверяет возможность восстановления пароля с email и невалидным паролем.
def test_recovery_with_valid_email_invalid_password_on_recovery_page(driver):
    # Нажатие кнопки "Забыл пароль"
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Ввод валидного email
    driver.find_element(By.ID, 'username').send_keys(valid_login_email)
    # Пауза 30с для самостоятельного ввода символов с капчи в соответствующее поле
    time.sleep(30)
    # Нажатие кнопки "Продолжить"
    driver.find_element(By.ID, 'reset').click()
    # Пауза 60с для самостоятельного ввода шестизначного кода из входящего письма
    time.sleep(60)
    # Последовательный ввод невалидного пароля дважды (можно подставить свой в '')
    driver.find_element(By.ID, 'password-new').send_keys('edfr43')
    driver.find_element(By.ID, 'password-confirm').send_keys('edfr43')
    driver.find_element(By.ID, 't-btn-reset-pass').click()
    # Тест падает, невалидный пароль не принимается
    assert Exception('NoSuchElementException')

# TC-15
# Негативный тест, проверяет возможность восстановления пароля с номером телефона и невалидным паролем.
def test_recovery_with_valid_phone_invalid_password_on_recovery_page(driver):
    # Нажатие кнопки "Забыл пароль"
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Ввод валидного номера телефона
    driver.find_element(By.ID, 'username').send_keys(valid_login_phone)
    # Пауза 30с для самостоятельного ввода символов с капчи в соответствующее поле
    time.sleep(30)
    # Нажатие кнопки "Продолжить"
    driver.find_element(By.ID, 'reset').click()
    # Пауза 45с для самостоятельного ввода шестизначного кода из входящего СМС
    time.sleep(45)
    # Последовательный ввод невалидного пароля дважды (можно подставить свой в '')
    driver.find_element(By.ID, 'password-new').send_keys('edfr43')
    driver.find_element(By.ID, 'password-confirm').send_keys('edfr43')
    driver.find_element(By.ID, 't-btn-reset-pass').click()
    # Тест падает, невалидный пароль не принимается
    assert Exception('NoSuchElementException')

# TC-16
# Негативный тест, проверяет возможность восстановления пароля с валидным email и неверной капчей.
def test_recovery_with_valid_email_invalid_capcha_on_recovery_page(driver):
    # Нажатие кнопки "Забыл пароль"
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Ввод валидного email
    driver.find_element(By.ID, 'username').send_keys(valid_login_email)
    # Ввод неверной капчи (можно подставить свою в '')
    driver.find_element(By.ID,'captcha').send_keys('efuy239')
    driver.find_element(By.ID, 'reset').click()
    # Тест падает, неверная капча не принимается
    assert Exception('NoSuchElementException')


# TC-17
# Негативный тест, проверяет возможность восстановления пароля с валидным номером телефона и неверной капчей.
def test_recovery_with_valid_phone_invalid_capcha_on_recovery_page(driver):
    # Нажатие кнопки "Забыл пароль"
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Ввод валидного номера телефона
    driver.find_element(By.ID, 'username').send_keys(valid_login_phone)
    # Ввод неверной капчи (можно подставить свою в '')
    driver.find_element(By.ID,'captcha').send_keys('efuy239')
    driver.find_element(By.ID, 'reset').click()
    # Тест падает, неверная капча не принимается
    assert Exception('NoSuchElementException')

# TC-18
# Негативный тест, проверяет возможность восстановления пароля с валидным номером телефона и просроченным кодом.
def test_recovery_with_valid_phone_expired_key_on_recovery_page(driver):
    # Нажатие кнопки "Забыл пароль"
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Ввод валидного номера телефона
    driver.find_element(By.ID, 'username').send_keys(valid_login_phone)
    # Пауза 30с для введения капчи
    time.sleep(30)
    driver.find_element(By.ID, 'reset').click()
    # Пауза 150с, шестизначный код из входящего письма нужно ввести не ранее, чем через 120с
    time.sleep(150)
    # Тест падает, просроченный код не принимается
    assert Exception('NoSuchElementException')

# TC-19
# Негативный тест, проверяет возможность восстановления пароля с валидным email и неверным кодом.
def test_recovery_with_valid_email_invalid_key_on_recovery_page(driver):
    # Нажатие кнопки "Забыл пароль"
    driver.find_element(By.ID, 'forgot_password').click()
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Ввод валидного email
    driver.find_element(By.ID, 'username').send_keys(valid_login_email)
    # Пауза 30с для введения капчи
    driver.implicitly_wait(30)
    # Нажатие кнопки "Продолжить"
    driver.find_element(By.ID, 'reset').click()
    # Пауза 45с для введения неверного шестизначного кода
    driver.implicitly_wait(45)
    # Тест падает, неверный код не принимается
    assert Exception('NoSuchElementException')

# TC-20
# Позитивный тест, проверяет работу 4 кнопок в верхнем меню страницы авторизации.
def test_4btns_on_auth_page(driver):
    # Клик по кнопке "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Проверка смены полупрозрачного текста в поле ввода
    assert driver.find_element(By.XPATH, '//span[text() = "Мобильный телефон"]')
    # Клик по кнопке "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Проверка смены полупрозрачного текста в поле ввода
    assert driver.find_element(By.XPATH, '//span[text() = "Электронная почта"]')
    # Клик по кнопке "Логин"
    driver.find_element(By.ID, 't-btn-tab-login').click()
    # Проверка смены полупрозрачного текста в поле ввода
    assert driver.find_element(By.XPATH, '//span[text() = "Логин"]')
    # Клик по кнопке "Лицевой счет"
    driver.find_element(By.ID, 't-btn-tab-ls').click()
    # Проверка смены полупрозрачного текста в поле ввода
    assert driver.find_element(By.XPATH, '//span[text() = "Лицевой счёт"]')

# TC-21
# Позитивный тест, проверяет работу кнопки "Помощь" на странице авторизации:
# она открывает окно с популярными вопросами поверх страницы.
def test_btn_help_on_auth_page(driver):
    # Нажатие кнопки "Помощь"
    driver.find_element(By.LINK_TEXT, 'Помощь').click()
    # Проверка по "крестику" на открывшемся окне помощи
    assert driver.find_element(By.ID, 'faq-close')

# TC-22
# Позитивный тест, проверяет возможность авторизации с валидным номером телефона и валидным паролем.
def test_auth_with_valid_phone_valid_password(driver):
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Ввод валидных телефона и пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys(valid_login_phone)
    driver.find_element(By.ID, 'password').send_keys(valid_password2)
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Пауза 10с на прогрузку страницы
    time.sleep(10)
    # Проверка по ID элемента в личном кабинете
    assert driver.find_element(By.ID, 'login_input')

# TC-23
# Негативный тест, проверяет возможность авторизации с невалидным номером телефона и невалидным паролем.
def test_auth_with_invalid_phone_invalid_password(driver):
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Ввод невалидных телефона и пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys('88888888888')
    driver.find_element(By.ID, 'password').send_keys('Qqqqqqqq')
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')

# TC-24
# Негативный тест, проверяет возможность авторизации с валидным номером телефона и невалидным паролем.
def test_auth_with_valid_phone_invalid_password(driver):
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Ввод валидного номера телефона и невалидного пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys(valid_login_phone)
    driver.find_element(By.ID, 'password').send_keys('Qqqqqqqq')
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')

# TC-25
# Негативный тест, проверяет возможность авторизации с невалидным номером телефона и валидным паролем.
def test_auth_with_invalid_phone_valid_password(driver):
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Ввод невалидного номера телефона и валидного пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys('88888888888')
    driver.find_element(By.ID, 'password').send_keys(valid_password2)
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')

# TC-26
# Негативный тест, проверяет возможность авторизации с валидным номером телефона и пустым паролем.
def test_auth_with_valid_phone_empty_password(driver):
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Ввод валидного номера телефона и пустого пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys(valid_login_phone)
    driver.find_element(By.ID, 'password').send_keys('')
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')

# TC-27
# Негативный тест, проверяет возможность авторизации с пустым номером телефона и валидным паролем.
def test_auth_with_empty_phone_valid_password(driver):
    # Нажатие кнопки "Телефон"
    driver.find_element(By.ID, 't-btn-tab-phone').click()
    # Ввод пустого номера телефона и валидного пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys('')
    driver.find_element(By.ID, 'password').send_keys(valid_password2)
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')

# TC-28
# Позитивный тест, проверяет возможность авторизации с валидным email и валидным паролем.
def test_auth_with_valid_email_valid_password(driver):
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Ввод валидных email и пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys(valid_login_email)
    driver.find_element(By.ID, 'password').send_keys(valid_password1)
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Пауза 10с на прогрузку страницы
    time.sleep(10)
    # Проверка по ID элемента в личном кабинете
    assert driver.find_element(By.ID, 'login_input')

# TC-29
# Негативный тест, проверяет возможность авторизации с невалидным email и невалидным паролем.
def test_auth_with_invalid_email_invalid_password(driver):
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Ввод невалидных email и пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys('sergguko@mail.ru')
    driver.find_element(By.ID, 'password').send_keys('Qasdewrfg')
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')

# TC-30
# Негативный тест, проверяет возможность авторизации с валидным email и невалидным паролем.
def test_auth_with_valid_email_invalid_password(driver):
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Ввод валидного email и невалидного пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys(valid_login_email)
    driver.find_element(By.ID, 'password').send_keys('Qasdewrfg')
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')

# TC-31
# Негативный тест, проверяет возможность авторизации с невалидным email и валидным паролем.
def test_auth_with_invalid_email_valid_password(driver):
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Ввод невалидного email и валидного пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys('sergguko@mail.ru')
    driver.find_element(By.ID, 'password').send_keys(valid_password1)
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')

# TC-32
# Негативный тест, проверяет возможность авторизации с валидным email и пустым паролем.
def test_auth_with_valid_email_empty_password(driver):
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Ввод валидного email и пустого пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys(valid_login_email)
    driver.find_element(By.ID, 'password').send_keys('')
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')

# TC-33
# Негативный тест, проверяет возможность авторизации с пустым email и валидным паролем.
def test_auth_with_empty_email_valid_password(driver):
    # Нажатие кнопки "Почта"
    driver.find_element(By.ID, 't-btn-tab-mail').click()
    # Ввод пустого email и валидного пароля в соответствующие поля
    driver.find_element(By.ID, 'username').send_keys('')
    driver.find_element(By.ID, 'password').send_keys(valid_password1)
    # Нажатие кнопки "Войти"
    driver.find_element(By.ID, 'kc-login').click()
    # Тест падает, авторизация не происходит
    assert Exception('NoSuchElementException')