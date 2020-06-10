from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.models.correo import Correo
from selenium.webdriver.remote.webdriver import WebDriver
from src.models.validaciones_list_json import ValidacionResultList
from src.models.result_step import ResultStep
from src.utils.temporizador import Temporizador
from src.utils.format_utils import FormatUtils
from src.webdriver_actions.html.validaciones_html import ValidacionesHTML
from src.evaluacion_json import constantes_json
from src.webdriver_actions import constantes_webdriver_actions
import selenium.common.exceptions as selExcep
import logging
import time


class AccionesHtml:
    # variable/bandera el cual indica que version del owa se esta analizando
    owa_descubierto = 0
    cuenta_sin_dominio = ''
    url_owa_exchange = ''
    log = logging.getLogger(__name__)

    # bandera para revisar si se encontro error en la plataforma
    mensaje_error_encontrado_owa = False
    txt_mensaje_error_encontrado_owa = ''

    @staticmethod
    def navegar_a_portal_principal_owa(driver: WebDriver, url: str, result_list: ValidacionResultList):
        resultado = ResultStep()
        resultado.tiempo_inicio_de_ejecucion = 0
        resultado.inicializar_tiempo_de_ejecucion()

        AccionesHtml.log.info(constantes_webdriver_actions.NAVEGAR_SITIO_MSG_INGRESO_SITIO.format(url))

        try:
            driver.set_page_load_timeout(100)
            driver.get(url)

            resultado.mensaje_error = constantes_webdriver_actions.NAVEGAR_SITIO_MSG_INGRESO_SITIO_CON_EXITO. \
                format(url)

            resultado.validacion_correcta = True
            AccionesHtml.log.info(resultado.mensaje_error)

        except selExcep.TimeoutException as e:

            resultado.mensaje_error = constantes_webdriver_actions.NAVEGAR_SITIO_MSG_TIMEOUT_EXCEP_MSG_ERROR. \
                format(url, FormatUtils.formatear_excepcion(e))

            resultado.validacion_correcta = False
            AccionesHtml.log.error(resultado.mensaje_error)

        except selExcep.WebDriverException as e:

            resultado.mensaje_error = constantes_webdriver_actions.NAVEGAR_SITIO_MSG_WEBDRIVER_EXCEP_MSG_ERROR. \
                format(FormatUtils.formatear_excepcion(e))

            resultado.validacion_correcta = False
            AccionesHtml.log.error(resultado.mensaje_error)

        resultado.finalizar_tiempo_de_ejecucion()
        resultado.establecer_tiempo_de_ejecucion()
        result_list.result_validacion_ingreso_url = resultado

        return result_list

    # Metodo el cual se encarga de establecer las credenciales en los inputs de la pagina principal del OWA
    @staticmethod
    def iniciar_sesion_en_owa(webdriver: WebDriver, correo: Correo, result_list: ValidacionResultList):

        AccionesHtml.cuenta_sin_dominio = FormatUtils.formatear_correo(correo.correo)
        AccionesHtml.url_owa_exchange = correo.url

        resultado = ResultStep()

        resultado.tiempo_inicio_de_ejecucion = Temporizador.obtener_tiempo_timer()
        resultado.datetime_inicial = Temporizador.obtener_fecha_tiempo_actual()

        try:
            time.sleep(3)
            input_usuario = webdriver.find_element_by_id(
                constantes_webdriver_actions.INICIAR_SESION_EN_OWA_ID_INPUT_USER)

            input_password = webdriver.find_element_by_id(
                constantes_webdriver_actions.INICIAR_SESION_EN_OWA_ID_INPUT_PASSWORD)

            boton_ingreso_correo = None

            if ValidacionesHTML.verificar_elemento_encontrado_por_id(
                    webdriver, constantes_webdriver_actions.
                            INICIAR_SESION_EN_OWA_ID_CHECKBOX_PORTAL_LIGHTWEIGHT_OWA_2010):

                check_casilla_owa_2010_version_ligera = webdriver.find_element_by_id(
                    constantes_webdriver_actions.INICIAR_SESION_EN_OWA_ID_CHECKBOX_PORTAL_LIGHTWEIGHT_OWA_2010)

                check_casilla_owa_2010_version_ligera.click()
                AccionesHtml.owa_descubierto = 2010

            if ValidacionesHTML.verificar_elemento_encontrado_por_xpath(
                    webdriver, constantes_webdriver_actions.INICIAR_SESION_EN_OWA_XPATH_BTN_OWA_2010):

                boton_ingreso_correo = webdriver.find_element_by_xpath(
                    constantes_webdriver_actions.INICIAR_SESION_EN_OWA_XPATH_BTN_OWA_2010)

                AccionesHtml.owa_descubierto = 2010

            elif ValidacionesHTML.verificar_elemento_encontrado_por_xpath(
                    webdriver, constantes_webdriver_actions.INICIAR_SESION_EN_OWA_XPATH_BTN_OWA_2013_2016):

                boton_ingreso_correo = webdriver.find_element_by_xpath(
                    constantes_webdriver_actions.INICIAR_SESION_EN_OWA_XPATH_BTN_OWA_2013_2016)

                AccionesHtml.owa_descubierto = 2016

            time.sleep(1)
            input_usuario.send_keys(correo.correo)

            time.sleep(1)
            input_password.send_keys(correo.password)

            time.sleep(1)
            boton_ingreso_correo.click()

            time.sleep(18)

            AccionesHtml.log.info(constantes_webdriver_actions.INICIAR_SESION_EN_OWA_MOSTRAR_TITLE_AND_URL.format(
                webdriver.title, webdriver.current_url))

        except selExcep.NoSuchElementException as e:

            resultado.mensaje_error = constantes_webdriver_actions.INICIAR_SESION_MSG_NOSUCHELEM_EXCEP_MSG_ERROR. \
                format(FormatUtils.formatear_excepcion(e))

            resultado.validacion_correcta = False
            AccionesHtml.log.error(resultado.mensaje_error)

        except selExcep.WebDriverException as e:

            resultado.mensaje_error = constantes_webdriver_actions.INICIAR_SESION_MSG_WEBDRIVER_EXCEP_MSG_ERROR. \
                format(FormatUtils.formatear_excepcion(e))

            resultado.validacion_correcta = False
            AccionesHtml.log.error(resultado.mensaje_error)

        if not resultado.validacion_correcta:
            try:

                if AccionesHtml.owa_descubierto == 2010:

                    mensaje_error_de_credenciales = webdriver.find_element_by_xpath(
                        constantes_webdriver_actions.INICIAR_SESION_EN_OWA_XPATH_ERROR_CREDENCIALES_OWA_2010)

                    texto_mensaje_error = mensaje_error_de_credenciales.get_attribute('innerHTML')
                    resultado.msg_error_de_credenciales = texto_mensaje_error

                    AccionesHtml.log.error(constantes_webdriver_actions.INICIAR_SESION_LOG_MSG_ERROR_CREDENCIALES_OWA.
                                           format(texto_mensaje_error))

                    resultado.mensaje_error = constantes_webdriver_actions. \
                        INICIAR_SESION_LOG_MSG_ERROR_CREDENCIALES_OWA.format(texto_mensaje_error)

                    resultado.validacion_correcta = False
                    resultado.error_inicio_de_sesion_credenciales_erroneas = True

                elif AccionesHtml.owa_descubierto == 2016 or AccionesHtml.owa_descubierto == 2013:

                    mensaje_error_de_credenciales = webdriver.execute_script(
                        constantes_webdriver_actions.INICIAR_SESION_JS_LOCATE_ID_MSG_ERROR_CREDENCIALES_OWA_2016_2013)

                    AccionesHtml.log.error(
                        constantes_webdriver_actions.INICIAR_SESION_LOG_MSG_ERROR_CREDENCIALES_OWA.format(
                            mensaje_error_de_credenciales))

                    resultado.mensaje_error = constantes_webdriver_actions. \
                        INICIAR_SESION_LOG_MSG_ERROR_CREDENCIALES_OWA.format(mensaje_error_de_credenciales)

                    resultado.msg_error_de_credenciales = mensaje_error_de_credenciales

                    resultado.validacion_correcta = False
                    resultado.error_inicio_de_sesion_credenciales_erroneas = True

            except selExcep.NoSuchElementException as e:
                resultado.mensaje_error = constantes_json.OUTPUT_EXITOSO_1_1
                resultado.validacion_correcta = True
                AccionesHtml.log.info(resultado.mensaje_error)
            except selExcep.InvalidSessionIdException as e:
                resultado.mensaje_error = constantes_webdriver_actions. \
                    INICIAR_SESION_CREDENCIALES_INVALIDSESION_ID_EXCEP_MSG_ERROR.format(e)

                resultado.validacion_correcta = False
                AccionesHtml.log.error(resultado.mensaje_error)
            except selExcep.JavascriptException as e:
                # Se ingresa correctamente, debido a que no se encontro el mensaje de error de credenciales incorrectas
                resultado.mensaje_error = constantes_json.OUTPUT_EXITOSO_1_1
                resultado.validacion_correcta = True
                AccionesHtml.log.info(resultado.mensaje_error)
            except selExcep.WebDriverException as e:
                # Se ingresa correctamente, debido a que no se encontro el mensaje de error de credenciales incorrectas
                resultado.mensaje_error = constantes_json.OUTPUT_EXITOSO_1_1
                resultado.validacion_correcta = True
                AccionesHtml.log.info(resultado.mensaje_error)

        # realiza la validacion de ingreso correcto de sesion se verifica que no haya algun error que se presente en la
        # plataforma en caso contrario se obtiene el mensaje del error y se establecer en el objeto resultado

        if ValidacionesHTML.verificar_error_plataforma(webdriver):
            msg_error = ValidacionesHTML.obtener_mensaje_error_plataforma(webdriver)
            resultado.mensaje_error = constantes_webdriver_actions.INICIAR_SESION_MSG_ERROR_EN_PLATAFORMA.\
                format(msg_error)

            resultado.validacion_correcta = False
            resultado.error_plataforma_inicio_de_sesion = True

        resultado.finalizar_tiempo_de_ejecucion()
        resultado.establecer_tiempo_de_ejecucion()
        result_list.result_validacion_acceso_portal_owa = resultado

        return result_list

    # cuando se ingresa correctamen al OWA, se localizan las listas de folders que contiene el usuario en sesion
    @staticmethod
    def obtener_carpetas_en_sesion(driver: WebDriver):

        lista_de_carpetas_localizadas = []
        lista_nombres_de_carpetas_formateadas = []
        tiempo_de_inicio = Temporizador.obtener_tiempo_timer()
        tiempo_de_finalizacion = 0
        se_encontraron_carpetas = False

        while tiempo_de_finalizacion < 60:
            time.sleep(10)

            if ValidacionesHTML.verificar_elemento_encontrado_por_clase_js(
                    driver, constantes_webdriver_actions.OBTENER_CARPETAS_EN_SESION_CSS_CARPETA_OWA_2016):
                AccionesHtml.owa_descubierto = 2016
                se_encontraron_carpetas = True
            elif ValidacionesHTML.verificar_elemento_encontrado_por_clase_js(
                    driver, constantes_webdriver_actions.OBTENER_CARPETAS_EN_SESION_CSS_CARPETA_OWA_2013):
                AccionesHtml.owa_descubierto = 2013
                se_encontraron_carpetas = True
            elif ValidacionesHTML.verificar_elemento_encontrado_por_xpath(
                    driver, constantes_webdriver_actions.OBTENER_CARPETAS_EN_SESION_XPATH_CARPETA_OWA_2010):
                AccionesHtml.owa_descubierto = 2010
                se_encontraron_carpetas = True

            tiempo_de_finalizacion = Temporizador.obtener_tiempo_timer() - tiempo_de_inicio

            if tiempo_de_finalizacion % 20 == 0:
                AccionesHtml.navegar_a_portal_principal_owa(AccionesHtml.url_owa_exchange)
                driver.refresh()

            if se_encontraron_carpetas:
                AccionesHtml.log.info(constantes_webdriver_actions.
                    OBTENER_CARPETAS_EN_SESION_LOG_INFO_LOCALIZACION_EXITOSA_CARPETAS.format(
                    FormatUtils.
                        truncar_float_cadena(tiempo_de_finalizacion)))
                break
            else:
                AccionesHtml.log.error(constantes_webdriver_actions.
                                       OBTENER_CARPETAS_EN_SESION_LOG_ERROR_LOCALIZACION_SIN_EXITO_CARPETAS)

                AccionesHtml.log.info(constantes_webdriver_actions.OBTENER_CARPETAS_EN_SESION_MOSTRAR_TITLE_AND_URL
                                      .format(driver.title, driver.current_url))

        if not se_encontraron_carpetas:

            tiempo_de_finalizacion = Temporizador.obtener_tiempo_timer() - tiempo_de_inicio

            AccionesHtml.log.error(constantes_webdriver_actions.
                OBTENER_CARPETAS_EN_SESION_LOG_ERROR_LOCALIZACION_SIN_EXITO_CARPETAS_EXCESO_TIEMPO.format(
                FormatUtils.truncar_float_cadena(tiempo_de_finalizacion)))

            AccionesHtml.log.info(constantes_webdriver_actions.OBTENER_CARPETAS_EN_SESION_MOSTRAR_TITLE_AND_URL
                                  .format(driver.title, driver.current_url))

        else:
            AccionesHtml.log.info(constantes_webdriver_actions.OBTENER_CARPETAS_EN_SESION_OWA_LOCALIZADO.format(
                AccionesHtml.owa_descubierto))

            time.sleep(4)

            if AccionesHtml.owa_descubierto == 2010:
                lista_de_carpetas_localizadas = driver.find_elements_by_xpath(
                    constantes_webdriver_actions.OBTENER_CARPETAS_EN_SESION_XPATH_CARPETA_OWA_2010)
            elif AccionesHtml.owa_descubierto == 2013:
                lista_de_carpetas_localizadas = driver.execute_script(constantes_webdriver_actions.
                                                                      OBTENER_CARPETAS_EN_SESION_JS_OBTENER_CARPETA_2013)
            elif AccionesHtml.owa_descubierto == 2016:
                lista_de_carpetas_localizadas = driver.execute_script(constantes_webdriver_actions.
                                                                      OBTENER_CARPETAS_EN_SESION_JS_OBTENER_CARPETA_2016)

        for carpeta in lista_de_carpetas_localizadas:

            if AccionesHtml.owa_descubierto == 2010:
                nombre_de_carpeta = carpeta.text
            else:
                nombre_de_carpeta = FormatUtils.remover_backspaces(carpeta.get_attribute('innerHTML'))

            AccionesHtml.log.info(constantes_webdriver_actions.OBTENER_CARPETAS_EN_SESION_OWA_CARPETA_OBTENIDA.
                                  format(nombre_de_carpeta))

            lista_nombres_de_carpetas_formateadas.append(nombre_de_carpeta)

        return lista_nombres_de_carpetas_formateadas

    # ejecuta la navegacion de cada una de las carpetas que tiene la sesion de correo electronico se establece como
    # parametro el numero de segundos en que se estara ejecutando la navegacion entre carpetas (lo estipulado son
    # 2 min -> 120 s)
    @staticmethod
    def navegacion_de_carpetas_por_segundos(correo: Correo, lista_carpetas: list, driver: WebDriver,
                                            result_list: ValidacionResultList, numero_de_segundos: int = 120):

        result_navegacion_carpetas = ResultStep()
        result_navegacion_carpetas.inicializar_tiempo_de_ejecucion()
        tiempo_por_verificar = numero_de_segundos + Temporizador.obtener_tiempo_timer()
        tiempo_de_inicio = Temporizador.obtener_tiempo_timer()
        segundos = 0

        # verifica si se tiene error de credenciales, por lo cual si se tiene este error, se establece el mensaje
        # de error y envia el result como finalizado, esto debido a que no se podra navegar entre carpetas por no
        # estar loggeado y sin tener acceso al buzon de la plataforma
        if result_list.result_validacion_acceso_portal_owa.error_inicio_de_sesion_credenciales_erroneas:
            result_navegacion_carpetas.finalizar_tiempo_de_ejecucion()
            result_navegacion_carpetas.establecer_tiempo_de_ejecucion()
            result_navegacion_carpetas.validacion_correcta = False

            result_navegacion_carpetas.mensaje_error = constantes_webdriver_actions.\
                NAVEGACION_CARPETAS_SEG_MSG_ERROR_CREDENCIALES_OWA.format(
                result_list.result_validacion_acceso_portal_owa.msg_error_de_credenciales)

            result_list.result_validacion_navegacion_carpetas = result_navegacion_carpetas

            AccionesHtml.log.error(constantes_webdriver_actions.NAVEGACION_CARPETAS_SEG_MSG_ERROR_CREDENCIALES_OWA.
                                   format(result_list.result_validacion_acceso_portal_owa.msg_error_de_credenciales))

            return result_list

        # verifica si hay error en plataforma, en caso de ser asi, intenta realizar n intentos para volver a loggearse
        # y verificar si ingreso correctamente al buzon de entrada para navegar entre las carpetas
        if ValidacionesHTML.verificar_error_plataforma(driver):
            result_navegacion_carpetas = ValidacionesHTML.intento_ingreso_nuevamente_al_portal(
                result_navegacion_carpetas, correo, driver, step_evaluacion='Navegacion carpetas y buzon de entrada')

        # verifica si aun se sigue mostrando el mensaje de error en la plataforma, en caso contrario la prueba falla
        # y notificaria al cliente de presentar un error de plataforma

        if ValidacionesHTML.verificar_error_plataforma(driver):

            result_navegacion_carpetas.finalizar_tiempo_de_ejecucion()
            result_navegacion_carpetas.establecer_tiempo_de_ejecucion()
            result_navegacion_carpetas.validacion_correcta = False
            msg_error = ValidacionesHTML.obtener_mensaje_error_plataforma(driver)
            result_navegacion_carpetas.mensaje_error = constantes_webdriver_actions. \
                NAVEGACION_CARPETAS_SEG_MSG_ERROR_PLATAFORMA_OWA.format(msg_error)

            result_list.result_validacion_navegacion_carpetas = result_navegacion_carpetas

            return result_list

        elif len(lista_carpetas) == 0:

            result_navegacion_carpetas.finalizar_tiempo_de_ejecucion()
            result_navegacion_carpetas.establecer_tiempo_de_ejecucion()
            result_navegacion_carpetas.validacion_correcta = False
            result_navegacion_carpetas.mensaje_error = constantes_webdriver_actions. \
                NAVEGACION_CARPETAS_SEG_LOG_ERROR_LISTA_CARPETAS_VACIA

            result_list.result_validacion_navegacion_carpetas = result_navegacion_carpetas

            AccionesHtml.log.error(constantes_webdriver_actions.NAVEGACION_CARPETAS_SEG_LOG_ERROR_LISTA_CARPETAS_VACIA)

            return result_list

        while Temporizador.obtener_tiempo_timer() <= tiempo_por_verificar:
            for carpeta in lista_carpetas:
                segundos = Temporizador.obtener_tiempo_timer() - tiempo_de_inicio

                if segundos > numero_de_segundos:
                    AccionesHtml.log.info(constantes_webdriver_actions.
                                          NAVEGACION_CARPETAS_SEG_LOG_INFO_NAVEGACION_CARPETAS_FINALIZADA)
                    break

                AccionesHtml.log.info(constantes_webdriver_actions.NAVEGACION_CARPETAS_SEG_LOG_INFO_INGRESO_CARPETA.
                                      format(carpeta))

                try:

                    if AccionesHtml.owa_descubierto == 2016:
                        elemento_html_carpeta = driver.execute_script(constantes_webdriver_actions.
                            NAVEGACION_CARPETAS_SEG_JS_LOCALIZAR_CARPETA_OWA_2016.format(
                            carpeta))

                        elemento_html_carpeta.click()
                        time.sleep(6)
                    elif AccionesHtml.owa_descubierto == 2010:
                        elemento_html_carpeta = driver.find_element_by_xpath(constantes_webdriver_actions.
                            NAVEGACION_CARPETAS_SEG_XPATH_CARPETA_OWA_2010.format(
                            carpeta))

                        time.sleep(3)
                        ValidacionesHTML.verificar_dialogo_de_interrupcion(driver, result_navegacion_carpetas)
                        time.sleep(3)
                        elemento_html_carpeta.click()
                    elif AccionesHtml.owa_descubierto == 2013:
                        elemento_html_carpeta = driver.execute_script(constantes_webdriver_actions.
                            NAVEGACION_CARPETAS_SEG_JS_LOCALIZAR_CARPETA_OWA_2013.format(
                            carpeta))

                        elemento_html_carpeta.click()
                        time.sleep(6)

                except selExcep.StaleElementReferenceException as e:

                    AccionesHtml.log.error(
                        constantes_webdriver_actions.NAVEGACION_CARPETAS_SEG_LOG_ERROR_STA_ELEM_REF_EXCEP
                            .format(FormatUtils.formatear_excepcion(e)))

                    driver.refresh()
                    time.sleep(3)
                except selExcep.ElementClickInterceptedException as e:

                    AccionesHtml.log.error(constantes_webdriver_actions.
                        NAVEGACION_CARPETAS_SEG_LOG_ERROR_ELEM_CLICK_INTERCEP_EXCEP.format(
                        FormatUtils.formatear_excepcion(e)))

                    driver.refresh()
                    time.sleep(3)
                except selExcep.NoSuchElementException as e:

                    AccionesHtml.log.error(
                        constantes_webdriver_actions.NAVEGACION_CARPETAS_SEG_LOG_ERROR_NO_SUCH_ELEM_EXCEP.format(
                            FormatUtils.formatear_excepcion(e)))

                    driver.refresh()
                    time.sleep(3)
                except selExcep.TimeoutException as e:

                    AccionesHtml.log.error(constantes_webdriver_actions.NAVEGACION_CARPETAS_SEG_LOG_ERROR_TIMEOUT_EXCEP.
                                           format(FormatUtils.formatear_excepcion(e)))

                    driver.refresh()
                    time.sleep(3)
                except selExcep.WebDriverException as e:

                    AccionesHtml.log.error(
                        constantes_webdriver_actions.NAVEGACION_CARPETAS_SEG_LOG_ERROR_WEBDRIVER_EXCEP.format(
                            FormatUtils.formatear_excepcion(e)))

                    time.sleep(3)

        result_navegacion_carpetas.finalizar_tiempo_de_ejecucion()
        result_navegacion_carpetas.establecer_tiempo_de_ejecucion()

        # verifica que no haya algun mensaje de error en la plataforma, en caso contrario se muestra el mensaje de
        # error que aparace en la plataforma dentro del result
        if ValidacionesHTML.verificar_error_plataforma(driver):
            msg_error = ValidacionesHTML.obtener_mensaje_error_plataforma(driver)
            result_navegacion_carpetas.validacion_correcta = False
            result_navegacion_carpetas.mensaje_error = constantes_webdriver_actions. \
                NAVEGACION_CARPETAS_SEG_MSG_ERROR_PLATAFORMA_OWA.format(msg_error)
        else:
            result_navegacion_carpetas.validacion_correcta = True
            result_navegacion_carpetas.mensaje_error = constantes_json.OUTPUT_EXITOSO_2_1

        result_list.result_validacion_navegacion_carpetas = result_navegacion_carpetas

        return result_list

    @staticmethod
    def cerrar_sesion(webdriver: WebDriver, result_list: ValidacionResultList, correo: Correo):

        timeout_cierre_sesion = 10
        resultado_cierre_sesion = ResultStep()
        resultado_cierre_sesion.inicializar_tiempo_de_ejecucion()
        cierre_sesion_exitosa = False

        # verifica si se tiene error de credenciales, por lo cual si se tiene este error, se establece el mensaje
        # de error y envia el result como finalizado, esto debido a que no puede localizar el boton de cierre de
        # sesion sin antes haberse loggeado dentro de la plataforma
        if result_list.result_validacion_acceso_portal_owa.error_inicio_de_sesion_credenciales_erroneas:
            resultado_cierre_sesion.finalizar_tiempo_de_ejecucion()
            resultado_cierre_sesion.establecer_tiempo_de_ejecucion()
            resultado_cierre_sesion.validacion_correcta = False

            resultado_cierre_sesion.mensaje_error = constantes_webdriver_actions.\
                CERRAR_SESION_MSG_ERROR_CREDENCIALES_OWA.format(result_list.result_validacion_acceso_portal_owa.
                                                                msg_error_de_credenciales)

            result_list.result_validacion_cierre_sesion = resultado_cierre_sesion

            AccionesHtml.log.error(constantes_webdriver_actions.CERRAR_SESION_MSG_ERROR_CREDENCIALES_OWA.format(
                result_list.result_validacion_acceso_portal_owa.msg_error_de_credenciales))

            return result_list

        # verifica si hay error en plataforma, en caso de ser asi, intenta realizar n intentos para volver a loggearse
        # y verificar si ingreso correctamente al buzon de entrada para navegar entre las carpetas
        if ValidacionesHTML.verificar_error_plataforma(webdriver):
            resultado_cierre_sesion = ValidacionesHTML.intento_ingreso_nuevamente_al_portal(
                resultado_cierre_sesion, correo, webdriver, step_evaluacion='cierre de sesion')

        try:
            webdriver.refresh()
            time.sleep(5)

            # verifica que no haya algun dialogo que impida el cierre de sesion
            ValidacionesHTML.verificar_dialogo_de_interrupcion(
                webdriver, resultado_cierre_sesion)

            # intenta salir de la sesion ejecutando un script js el cual simula un clic en el boton de cierre de sesion

            if AccionesHtml.owa_descubierto == 2010:
                time.sleep(4)
                elemento_html_btn_cerrar_sesion = webdriver.find_element_by_id(
                    constantes_webdriver_actions.CERRAR_SESION_CIERRE_SESION_ID_BTN_CIERRE_SESION_OWA_2010)
                time.sleep(4)
                elemento_html_btn_cerrar_sesion.click()
                time.sleep(4)
            elif AccionesHtml.owa_descubierto == 2016:
                time.sleep(4)

                boton_cierre_sesion_owa_2016 = webdriver.execute_script(
                    constantes_webdriver_actions.JS_LOCATE_DIV_CONTENT_BTN_CIERRE_SESION_OWA_2016)

                time.sleep(4)
                boton_cierre_sesion_owa_2016.click()
                time.sleep(8)

                boton_cierre_sesion_owa_2016 = webdriver.execute_script(
                    constantes_webdriver_actions.JS_LOCATE_BTN_CIERRE_SESION_OWA_2016)

                boton_cierre_sesion_owa_2016.click()

            elif AccionesHtml.owa_descubierto == 2013:

                boton_cierre_sesion_owa_2013 = webdriver.execute_script(
                    constantes_webdriver_actions.JS_LOCATE_DIV_CONTENT_BTN_CIERRE_SESION_OWA_2013)

                boton_cierre_sesion_owa_2013.click()
                time.sleep(8)

                boton_cierre_sesion_owa_2013 = webdriver.execute_script(
                    constantes_webdriver_actions.JS_LOCATE_BTN_CIERRE_SESION_OWA_2013_SPANISH)

                if boton_cierre_sesion_owa_2013 is None:
                    AccionesHtml.log.error(constantes_webdriver_actions.CERRAR_SESION_LOG_ERROR_BTN_CIERRE_SIGN_OUT)

                    boton_cierre_sesion_owa_2013 = webdriver.execute_script(
                        constantes_webdriver_actions.JS_LOCATE_BTN_CIERRE_SESION_OWA_2013_ENGLISH)

                boton_cierre_sesion_owa_2013.click()

            # obtiene la url actual como una cadena
            time.sleep(2)

            AccionesHtml.log.info(constantes_webdriver_actions.CERRAR_SESION_LOG_INFO_CIERRE_SESION_TITLE_URL
                                  .format(webdriver.title, webdriver.current_url))

            webdriver.refresh()

            time.sleep(2)

            # verifica que nos encontremos en la pagina de cierre de sesion del OWA verifica que el title de la pagina
            # contenfa Outlook
            condicion_contenido_en_title = EC.title_contains(constantes_webdriver_actions.
                                                             CERRAR_SESION_TITLE_CIERRE_SESION)

            WebDriverWait(webdriver, timeout_cierre_sesion).until(condicion_contenido_en_title)

            cierre_sesion_exitosa = True

        except selExcep.NoSuchElementException as e:

            AccionesHtml.log.error(constantes_webdriver_actions.CERRAR_SESION_LOG_ERROR_NO_SUCH_ELEM_EXCEP.format(
                FormatUtils.formatear_excepcion(e)))

            resultado_cierre_sesion.mensaje_error = constantes_webdriver_actions. \
                CERRAR_SESION_LOG_ERROR_NO_SUCH_ELEM_EXCEP.format(FormatUtils.formatear_excepcion(e))

            resultado_cierre_sesion.validacion_correcta = False

        except selExcep.ElementClickInterceptedException as e:

            AccionesHtml.log.error(constantes_webdriver_actions.CERRAR_SESION_LOG_ERROR_ELEM_INTERCEP_EXCEP.format(
                FormatUtils.formatear_excepcion(e)))

            webdriver.refresh()

            time.sleep(2)

            AccionesHtml.cerrar_sesion(webdriver, result_list, correo)

        except selExcep.TimeoutException as e:

            AccionesHtml.log.error(constantes_webdriver_actions.CERRAR_SESION_LOG_ERROR_TIMEOUT_EXCEP.format(
                FormatUtils.formatear_excepcion(e)))

            resultado_cierre_sesion.mensaje_error = constantes_webdriver_actions. \
                CERRAR_SESION_LOG_ERROR_TIMEOUT_EXCEP.format(FormatUtils.formatear_excepcion(e))

            resultado_cierre_sesion.validacion_correcta = False

        except selExcep.WebDriverException as e:

            AccionesHtml.log.error(constantes_webdriver_actions.CERRAR_SESION_LOG_ERROR_WEBDRIVER_EXCEP
                                   .format(FormatUtils.formatear_excepcion(e)))

            resultado_cierre_sesion.mensaje_error = constantes_webdriver_actions. \
                CERRAR_SESION_LOG_ERROR_WEBDRIVER_EXCEP.format(FormatUtils.formatear_excepcion(e))

            resultado_cierre_sesion.validacion_correcta = False

        except AttributeError:

            AccionesHtml.log.error(constantes_webdriver_actions.CERRAR_SESION_LOG_ERROR_ATRIBUTE_ERROR_EXCEP)
            resultado_cierre_sesion.mensaje_error = constantes_webdriver_actions. \
                CERRAR_SESION_LOG_ERROR_ATRIBUTE_ERROR_EXCEP
            resultado_cierre_sesion.validacion_correcta = False

        finally:

            # verifica que no haya algun mensaje de error en la plataforma, en caso contrario se muestra el mensaje de
            # error que aparace en la plataforma dentro del result
            if ValidacionesHTML.verificar_error_plataforma(webdriver):
                resultado_cierre_sesion.validacion_correcta = False
                msg_error = ValidacionesHTML.obtener_mensaje_error_plataforma(webdriver)

                resultado_cierre_sesion.mensaje_error = constantes_webdriver_actions.CERRAR_SESION_ERROR_PLATAFORMA. \
                    format(msg_error)

                cierre_sesion_exitosa = False

            AccionesHtml.log.info(constantes_webdriver_actions.CERRAR_SESION_LOG_INFO_CIERRE_WEB_DRIVER)

            webdriver.close()
            webdriver.quit()

        if cierre_sesion_exitosa:
            AccionesHtml.log.info(constantes_webdriver_actions.CERRAR_SESION_LOG_INFO_CIERRE_SESION_EXITOSA)
            resultado_cierre_sesion.mensaje_error = constantes_json.OUTPUT_EXITOSO_3_1
            resultado_cierre_sesion.validacion_correcta = True

        resultado_cierre_sesion.finalizar_tiempo_de_ejecucion()
        resultado_cierre_sesion.establecer_tiempo_de_ejecucion()
        result_list.result_validacion_cierre_sesion = resultado_cierre_sesion

        return result_list
