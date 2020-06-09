from src.models.correo import Correo
from src.utils.format_utils import FormatUtils
from src.evaluacion_json.generador_json_log_base import GeneradorJsonBaseEvaluacion
from src.evaluacion_json.llenado_log_json import EvaluacionStepsJson
from src.models.validaciones_list_json import ValidacionResultList
from src.webdriver_config.config_webdriver import ConfiguracionWebDriver
from src.webdriver_actions.acciones_html import AccionesHtml
from src.evaluacion_json import constantes_json
import configparser
import sys
import logging
import json
import os

correos_obtenidos = []


def generar_test_json(driver, url_a_navegar, correo):
    # objeto con lista de objetos result el cual verificara cada una de las validaciones para cada uno de los steps y
    # el cual nos permitira adjuntar el resultado en el JSON
    lista_validaciones = ValidacionResultList()

    # genera la estructura del archivo JSON (resultado/salida)
    objeto_json = GeneradorJsonBaseEvaluacion.generar_nuevo_template_json()

    # establece el datetime de inicio dentro del json
    objeto_json = EvaluacionStepsJson.establecer_fecha_tiempo_de_inicio(objeto_json)

    # empieza la primera validacion de ingresar a la url del portal
    lista_validaciones = AccionesHtml.navegar_a_portal_principal_owa(driver, url_a_navegar, lista_validaciones)

    # intenta ingresar las credenciales de la cuenta dentro del portal, verificando el acceso del correo desde el portal
    lista_validaciones = AccionesHtml.iniciar_sesion_en_owa(driver, correo, lista_validaciones)

    # se obtiene la lista de carpetas que contiene el correo electronico
    lista_carpetas_por_navegar = AccionesHtml.obtener_carpetas_en_sesion(driver)

    # empieza la validacion de la navegacion en cada una de las carpetas que se obtuvieron en la linea anterior
    lista_validaciones = AccionesHtml.navegacion_de_carpetas_por_segundos(lista_carpetas_por_navegar, driver,
                                                                          lista_validaciones)
    # se valida el cierre de sesion desde el OWA
    lista_validaciones = AccionesHtml.cerrar_sesion(driver, lista_validaciones)

    # establece los datos en el json con los resultados de cada una de las validaciones
    objeto_json = EvaluacionStepsJson.formar_cuerpo_json(lista_validaciones, objeto_json, correo)

    # establecen el json generado dentro de otra structura JSON con el correo como nodo
    objeto_json = GeneradorJsonBaseEvaluacion.establecer_estructura_principal_json(correo.correo, objeto_json)

    return objeto_json


def iniciar_prueba(correo, url_exchange):
    # obtiene los datos del archivo de configuracion
    config_web_driver = None
    archivo_configuracion_ini = FormatUtils.lector_archivo_ini()
    driver_por_usar = FormatUtils.CADENA_VACIA
    ruta_driver_navegador = FormatUtils.CADENA_VACIA
    driver = None
    objeto_json = None

    try:
        # url_exchange = archivo_configuracion_ini.get('UrlPorProbar','urlPortalExchange')
        driver_por_usar = archivo_configuracion_ini.get('Driver', 'driverPorUtilizar')
        ruta_driver_navegador = archivo_configuracion_ini.get('Driver', 'ruta')
    except configparser.Error as e:
        logging.error('Sucedio un error al momento de leer el archivo de configuracion')
        logging.error('{}'.format(e))
        sys.exit()

    # lista de carpetas por navegar (estos los obtenemos por medio del webdriver)
    carpetas_formateadas = []

    # obtiene los datos necesarios desde el archivo de configuracion

    # establece el driver por utilizar (chrome o firefox)
    config_web_driver = ConfiguracionWebDriver(ruta_driver_navegador, driver_por_usar)
    driver = config_web_driver.configurar_obtencion_web_driver()

    # se generan las validaciones y el resultado por medio de un objeto JSON
    objeto_json = generar_test_json(driver, url_exchange, correo)

    # se retorna el objeto json como cadena
    return json.dumps(objeto_json)


def configuracion_log(correo_por_probar):
    # verifica si el folder del log existe
    if not os.path.isdir(constantes_json.DIR_BASE_LOG):
        try:
            os.mkdir(constantes_json.DIR_BASE_LOG)
        except OSError as e:
            print('sucedio un error al crear el directorio del log {} : {}'
                  .format(constantes_json.DIR_BASE_LOG, e))
            print('Favor de establecer la carpeta Logs dentro del proyecto con los permisos necesarios, se procede a '
                  'terminar el script')
            sys.exit()

    # se verifica si el nombre del archivo existe, en caso contrario
    # crea el nuevo archivo log y sale del ciclo
    while True:

        # verifica que el archivo del log exista en caso contrario lo crea
        FormatUtils.generar_nombre_log(correo_por_probar)

        if not os.path.exists(constantes_json.PATH_ABSOLUTO_LOG):
            try:
                log = open(constantes_json.PATH_ABSOLUTO_LOG, 'x')
                log.close()
                break
            except OSError as e:
                print(
                    'Se tiene acceso denegado para escribir el archivo {}, favor de establecer los permisos necesarios'
                    ' en el directorio Logs'.format(e))
                print('Favor de establecer los permisos necesarios para escribir ficheros dentro del directorio Logs. '
                      'Se procede a finalizar el script')
                sys.exit()
        else:
            print('El log {}, ya existe, se procede a generar un nuevo log'.format(constantes_json.PATH_ABSOLUTO_LOG))
            continue

    logging.basicConfig(level=logging.INFO,
                        filename=constantes_json.PATH_ABSOLUTO_LOG,
                        filemode='w+',
                        format='%(asctime)s %(lineno)d %(name)s  %(levelname)s: %(message)s',
                        datefmt='%d-%m-%YT%H:%M:%S')

    logging.info('Inicializando log: {}'.format(constantes_json.PATH_ABSOLUTO_LOG))

    # verifica si es necesario la depuracion del directorio en donde residen los logs
    FormatUtils.verificacion_depuracion_de_logs(constantes_json.DIR_BASE_LOG)


# Punto de partida/ejecucion principal del script
def main():
    args = sys.argv[1:]
    cadena_json = args[0]
    response = FormatUtils.CADENA_VACIA
    correo_a_probar = None

    constantes_json.configurar_paths_constantes(__file__)

    # verifica que la cadena sea un json valido en caso contrario 
    # se omite la experiencia de usuario
    cadena_json = cadena_json.strip()

    if FormatUtils.cadena_a_json_valido(cadena_json):
        objeto_json = json.loads(cadena_json)

        url_exchange = objeto_json['url']
        usuario = objeto_json['user']
        password = objeto_json['password']

        configuracion_log(usuario)

        correo_a_probar = Correo(usuario, password, url_exchange)
        logging.info('"{}" - JSON valido'.format(cadena_json))
        response = iniciar_prueba(correo_a_probar, correo_a_probar.url)

    else:
        configuracion_log(constantes_json.JSON_INVALIDO)
        logging.error('"{}" - JSON invalido, se omite exp. de usuario'.format(cadena_json))
        print('"{}" - JSON invalido, se omite exp. de usuario'.format(cadena_json))
        response = '"{}" - JSON invalido, se omite exp. de usuario'.format(cadena_json)

    logging.info('Response generado: {}'.format(response))

    print(response)


main()
