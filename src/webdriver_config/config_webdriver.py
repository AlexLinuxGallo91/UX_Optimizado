from selenium import webdriver
from src.evaluacion_json import constantes_json
import src.webdriver_config.constantes_configuracion_web_driver as const
import logging
import warnings
import sys


class ConfiguracionWebDriver:

    def __init__(self, ruta_web_driver, driver_por_configurar):
        self.log = logging.getLogger(__name__)
        self.ruta_web_driver = ruta_web_driver
        self.driver_por_configurar = driver_por_configurar

    def inicializar_webdriver_phantom_js(self):

        webdriver_phantomjs = None

        # suprime el mensaje warning del uso de phantomjs ya que es una libreria obsoleta
        warnings.filterwarnings('ignore')

        try:
            webdriver_phantomjs = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'],
                                                      executable_path=self.ruta_web_driver,
                                                      service_log_path=constantes_json.DEV_NULL
                                                      )
            webdriver_phantomjs.set_window_size(1120, 550)
        except FileNotFoundError as e:
            self.log.error('Sucedio un error al intentar configurar el webdriver: {}'.format(e))
        except Exception as e:
            self.log.error('Sucedio una excepcion al intentar configurar el webdriver {}'.format(e))

        return webdriver_phantomjs

    # inicializa un nuevo driver (firefox) para la experiencia de usuario
    # con el uso del navefador Mozilla Firefox
    def inicializar_webdriver_firefox(self):
        # ruta para deshabilitar log inecesario del geckodriver
        webdriver_firefox = None
        opciones_firefox = webdriver.FirefoxOptions()
        perfil_firefox = webdriver.FirefoxProfile()

        firefox_capabilities = webdriver.DesiredCapabilities().FIREFOX.copy()
        firefox_capabilities.update(
            {'acceptInsecureCerts': True, 'acceptSslCerts': True})
        firefox_capabilities['acceptSslCerts'] = True

        # ignora las certificaciones de seguridad, esto solamente se realiza
        # para la experiencia de usuario
        opciones_firefox.add_argument('--ignore-certificate-errors')
        opciones_firefox.accept_insecure_certs = True
        perfil_firefox.accept_untrusted_certs = True
        perfil_firefox.assume_untrusted_cert_issuer = False

        opciones_firefox.headless = False
        try:
            webdriver_firefox = webdriver.Firefox(executable_path=self.ruta_web_driver,
                                                  firefox_options=opciones_firefox,
                                                  firefox_profile=perfil_firefox,
                                                  capabilities=firefox_capabilities,
                                                  #log_path=constantes_json.DEV_NULL
                                                  )
        except FileNotFoundError as e:
            self.log.error('Sucedio un error al intentar configurar el webdriver: {}'.format(e))
        except Exception as e:
            self.log.error('Sucedio una excepcion al intentar configurar el webdriver {}'.format(e))

        return webdriver_firefox

    # inicializa un nuevo driver (chrome driver) para la experiencia de usuario
    # con el uso del navefador google chrome
    def inicializar_webdriver_chrome(self):

        webdriver_chrome = None

        opciones_chrome = webdriver.ChromeOptions()

        # ignora las certificaciones de seguridad, esto solamente se realiza
        # para la experiencia de usuario
        opciones_chrome.add_argument('--ignore-certificate-errors')
        opciones_chrome.add_argument("--headless")
        opciones_chrome.add_argument('--allow-running-insecure-content')
        opciones_chrome.add_argument("--enable-javascript")
        opciones_chrome.add_argument('window-size=1920x1080')
        opciones_chrome.add_argument('--no-sandbox')
        opciones_chrome.add_experimental_option('excludeSwitches', ['enable-logging'])

        chrome_capabilities = webdriver.DesiredCapabilities().CHROME.copy()
        chrome_capabilities['acceptSslCerts'] = True
        chrome_capabilities['acceptInsecureCerts'] = True

        try:
            webdriver_chrome = webdriver.Chrome(self.ruta_web_driver,
                                                chrome_options=opciones_chrome,
                                                desired_capabilities=chrome_capabilities,
                                                service_log_path=constantes_json.DEV_NULL)
        except FileNotFoundError as e:
            self.log.error('Sucedio un error al intentar configurar el webdriver: {}'.format(e))
        except Exception as e:
            self.log.error('Sucedio una excepcion al intentar configurar el webdriver {}'.format(e))

        return webdriver_chrome

    def configurar_obtencion_web_driver(self):
        driver_configurado = None

        if len(self.ruta_web_driver.strip()) == 0:
            self.log.error(const.MSG_ERROR_PROP_INI_WEBDRIVER_SIN_CONFIGURAR)
            sys.exit()
        elif self.driver_por_configurar == const.CHROME:
            driver_configurado = self.inicializar_webdriver_chrome()
            self.log.info(const.MSG_INFO_INICIO_CONFIGURACION_DRIVER.format(const.CHROME))
        elif self.driver_por_configurar == const.FIREFOX:
            driver_configurado = self.inicializar_webdriver_firefox()
            self.log.info(const.MSG_INFO_INICIO_CONFIGURACION_DRIVER.format(const.FIREFOX))
        elif self.driver_por_configurar == const.PHANTOMJS:
            driver_configurado = self.inicializar_webdriver_phantom_js()
            self.log.info(const.MSG_INFO_INICIO_CONFIGURACION_DRIVER.format(const.PHANTOMJS))
        else:
            self.log.error(const.MSG_ERROR_CONFIGURACION_DRIVER)
            sys.exit()

        return driver_configurado

