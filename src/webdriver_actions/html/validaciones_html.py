from selenium.webdriver.remote.webdriver import WebDriver
from src.models.result_step import ResultStep
from src.models.correo import Correo
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from random import randint
import selenium.common.exceptions as SelExcept
import time
import logging


class ValidacionesHTML:
    log = logging.getLogger(__name__)

    @staticmethod
    def verificar_elemento_encontrado_por_id(webdriver: WebDriver, id_elem_html: str):
        """
        verifica si se encontro el elemento deseado mediante el id
        retorna True si se encontro el elemento
        en caso contrario retorna False

        :param webdriver:
        :param id_elem_html:
        :return:
        """
        elemento_html = None

        try:
            elemento_html = webdriver.find_element_by_id(id_elem_html)
            ValidacionesHTML.log.info(
                'Se localiza el elemento con el id {} correctamente'.format(id_elem_html))
            return True
        except SelExcept.NoSuchElementException as e:
            ValidacionesHTML.log.error(
                'No se encontro el elemento con el id: {}'.format(id_elem_html))
            return False

    @staticmethod
    def verificar_elemento_encontrado_por_xpath(webdriver: WebDriver, xpath: str):
        """
        verifica si se encontro el elemento deseado mediante el xpath
        retorna True si se encontro el elemento
        en caso contrario retorna False

        :param webdriver:
        :param xpath:
        :return:
        """
        elemento_html = None

        try:
            elemento_html = webdriver.find_element_by_xpath(xpath)
            ValidacionesHTML.log.info(
                'Se localiza el elemento mediante el xpath {} correctamente'.format(xpath))
            return True
        except SelExcept.NoSuchElementException as e:
            ValidacionesHTML.log.error(
                'No se encontro el elemento mediante el xpath: {}'.format(xpath))
            return False

    @staticmethod
    def verificar_elemento_encontrado_por_clase_js(webdriver, clase: str):
        """
        :param webdriver:
        :param clase:
        :return:
        """
        elementos_html = []

        elementos_html = webdriver.execute_script(
            "return document.getElementsByClassName('{}');".format(clase))

        if elementos_html is not None and len(elementos_html) >= 1:
            ValidacionesHTML.log.info('Se encontraron elementos Html con la clase {}'.format(clase))
            return True
        else:
            ValidacionesHTML.log.info('No se encontraron elementos Html con la clase {}'.format(clase))
            return False

    @staticmethod
    def verificar_error_plataforma(driver: WebDriver):
        """
        verifica si en la plataforma existe algun error presente, las cuales se enlistan a continuacion y
        que se han descubierto hasta este momento:

        1) elemento title HTML con leyenda "Error"
        2) En el body de la plataforma se se presente la leyenda 'NegotiateSecurityContext failed with for host'

        :param driver:
        :return:
        """
        existe_error = False
        leyenda_title = driver.title
        mensaje_error_localizado = ''

        if leyenda_title is None:
            leyenda_title = ''

        if 'Error' in leyenda_title:
            existe_error = True

            if ValidacionesHTML.verificar_elemento_encontrado_por_id(driver, 'errMsg'):
                elemento_mensaje_error = driver.find_element_by_id('errMsg')
                mensaje_error_localizado = elemento_mensaje_error.get_attribute('innerHTML')
                existe_error = True

        elif ValidacionesHTML.verificar_elemento_encontrado_por_xpath(driver, '//body'):

            elemento_body = driver.find_element_by_xpath('//body')
            mensaje_error_localizado = elemento_body.get_attribute('innerHTML')

            if mensaje_error_localizado is None:
                mensaje_error_localizado = ''

            if 'NegotiateSecurityContext' in mensaje_error_localizado or \
                    'LogonDenied' in mensaje_error_localizado:
                existe_error = True

        if existe_error:
            ValidacionesHTML.log.error('Se localiza error dentro de la plataforma owa: '
                                       '{}'.format(mensaje_error_localizado))
            ValidacionesHTML.txt_mensaje_error_encontrado_owa = mensaje_error_localizado
            ValidacionesHTML.mensaje_error_encontrado_owa = existe_error
        else:
            ValidacionesHTML.log.info('No se localizo error alguno dentro de la plataforma owa')

        return existe_error

    @staticmethod
    def obtener_mensaje_error_plataforma(driver: WebDriver):

        existe_error = False
        leyenda_title = driver.title
        mensaje_error_localizado = ''

        if leyenda_title is None:
            leyenda_title = ''

        if 'Error' in leyenda_title:
            existe_error = True

            if ValidacionesHTML.verificar_elemento_encontrado_por_id(driver, 'errMsg'):
                elemento_mensaje_error = driver.find_element_by_id('errMsg')
                mensaje_error_localizado = elemento_mensaje_error.get_attribute('innerHTML')
                existe_error = True

        elif ValidacionesHTML.verificar_elemento_encontrado_por_xpath(driver, '//body'):

            elemento_body = driver.find_element_by_xpath('//body')
            mensaje_error_localizado = elemento_body.get_attribute('innerHTML')

            if mensaje_error_localizado is None:
                mensaje_error_localizado = ''

            if 'NegotiateSecurityContext' in mensaje_error_localizado or \
                    'LogonDenied' in mensaje_error_localizado:
                existe_error = True

        if existe_error:
            ValidacionesHTML.log.error('Se localiza error dentro de la plataforma owa: '
                                       '{}'.format(mensaje_error_localizado))
        else:
            ValidacionesHTML.log.info('No se localizo error alguno dentro de la plataforma owa')

        return mensaje_error_localizado


    # verifica que no aparezca el dialogo de interrupcion (dialogo informativo que en algunas ocasiones
    # aparece cuando se ingresa a una carpeta con correos nuevos)
    @staticmethod
    def verificar_dialogo_de_interrupcion(driver, result):
        if len(driver.find_elements_by_id('divPont')) > 0:
            ValidacionesHTML.log.info('Se ha encontrado un dialogo informativo, se procede a cerrarlo')

            try:
                time.sleep(4)
                boton_remover_dialogo = driver.find_element_by_id('imgX')
                boton_remover_dialogo.click()
            except SelExcept.ElementClickInterceptedException:
                ValidacionesHTML.log.error('Se encontro un dialogo informativo pero fue imposible cerrarlo. Se '\
                                           'intenta nuevamente el cierre del dialogo')
                ValidacionesHTML.verificar_dialogo_de_interrupcion(driver, result)


    @staticmethod
    def intento_ingreso_nuevamente_al_portal(result: ResultStep, correo: Correo, driver: WebDriver,
                                             numero_de_intentos_por_ingresar: int = 3, step_evaluacion: str = ''):

        ValidacionesHTML.log.info('Se presentan problemas para el paso {}. se realizaran {} intentos para ingresar '
            'nuevamente al portal Exchange OWA'.format(step_evaluacion, numero_de_intentos_por_ingresar))

        for intento in range(numero_de_intentos_por_ingresar):
            ValidacionesHTML.log.info('Se realizara el intento numero {} para ingresar al buzon de entrada de la cuenta'.
                                      format(intento+1))
            try:
                boton_inicio_sesion = None
                driver.delete_all_cookies()
                driver.refresh()

                driver.get(correo.url)

                WebDriverWait(driver, 18).until(EC.visibility_of_element_located((By.ID, 'username')))

                input_usuario = driver.find_element_by_id('username')
                input_password = driver.find_element_by_id('password')

                input_usuario.clear()
                input_password.clear()

                if ValidacionesHTML.verificar_elemento_encontrado_por_id(driver, 'chkBsc'):
                    check_casilla_owa_2010_version_ligera = driver.find_element_by_id('chkBsc')
                    check_casilla_owa_2010_version_ligera.click()

                if ValidacionesHTML.verificar_elemento_encontrado_por_xpath(driver, "//input[@type='submit'][@class='btn']"):
                    boton_inicio_sesion = driver.find_element_by_xpath("//input[@type='submit'][@class='btn']")

                elif ValidacionesHTML.verificar_elemento_encontrado_por_xpath(driver, "//div[@class='signinbutton']"):
                    boton_inicio_sesion = driver.find_element_by_xpath("//div[@class='signinbutton']")

                # num_random = randint(1,1000)
                # driver.save_screenshot('./Logs/{}_0.png'.format(num_random))
                time.sleep(3)
                input_usuario.send_keys(correo.correo)
                # driver.save_screenshot('./Logs/{}_1.png'.format(num_random))
                time.sleep(3)
                input_password.send_keys(correo.password)
                # driver.save_screenshot('./Logs/{}_2.png'.format(num_random))

                time.sleep(2)
                boton_inicio_sesion.click()
                # driver.save_screenshot('./Logs/{}_5.png'.format(num_random))

                time.sleep(30)
                # driver.save_screenshot('./Logs/{}_6.png'.format(num_random))

                # se verifica si encuentra al menos las carpetas en la bandeja
                if ValidacionesHTML.verificar_elemento_encontrado_por_clase_js(driver, "_n_C4") or \
                        ValidacionesHTML.verificar_elemento_encontrado_por_clase_js(driver, "_n_Z6") or \
                        ValidacionesHTML.verificar_elemento_encontrado_por_xpath(driver, "//a[@name='lnkFldr']"):

                    result.validacion_correcta = True
                    result.mensaje_error = 'Se ingresa nuevamente de manera correcta al buzon de entrada de la ' \
                                           'cuenta {}'.format(correo.correo)

                    ValidacionesHTML.log.info(result.mensaje_error)

                    break
                elif ValidacionesHTML.verificar_error_plataforma(driver):
                    msg_error = ValidacionesHTML.obtener_mensaje_error_plataforma(driver)
                    result.validacion_correcta = False
                    result.mensaje_error = 'Ingreso al buzon de entrada no exitosa, se presenta el siguiente error ' \
                        'dentro de la plataforma Exchange OWA: {}'.format(msg_error)

                    ValidacionesHTML.log.error(result.mensaje_error)
                else:
                    result.validacion_correcta = False
                    result.mensaje_error = 'Ingreso al buzon de entrada no exitosa. Se intento ingresar a la ' \
                        'bandeja de entrada de la plataforma Exchange OWA, se presenta problemas de carga de pagina'

                    ValidacionesHTML.log.error(result.mensaje_error)

            except SelExcept.NoSuchElementException as e:
                result.validacion_correcta = False
                result.mensaje_error = 'No fue posible ingresar nuevamente a la bandeja de entrada. No se ' \
                                       'localizaron correctamente los inputs para el ingreso de usuario y password'

                ValidacionesHTML.log.error(result.mensaje_error)
            except SelExcept.TimeoutException as e:
                result.validacion_correcta = False
                result.mensaje_error = 'No fue posible ingresar nuevamente a la bandeja de entrada. Se tiene un ' \
                                       'problema de tiempo de carga en la pagina'

                ValidacionesHTML.log.error(result.mensaje_error)


        return result



