from flask import current_app, request, render_template, redirect, url_for, Blueprint
from datetime import datetime
from app.logger import log_err

blueprint = Blueprint(
    'home',
    __name__,
    url_prefix='/',
    static_folder="static",
    template_folder="templates")

################
# En la última línea de este archivo se definen las rutas de las causas
################

accepted_causas = {
    'genero': 'Género',
    'ambiente': 'Ambiente',
    'ciencia': 'Ciencia',
    'vivienda': 'Vivienda',
    'transparencia': 'Transparencia',
    'drogas': 'Drogas',
    'trabajo': 'Trabajo'
}


def get_menu_navs():
    navs = {'index': '', 'causas': '', 'agenda': '', 'contacto': ''}
    if request.endpoint:
        endpoint = request.endpoint.split('.')[1] if '.' in request.endpoint else request.endpoint
        if endpoint in accepted_causas.keys():
            navs['causas'] = 'active'
        elif endpoint in navs.keys():
            navs[endpoint] = 'active'
    return navs


def render_error(msg):
    return render_template(
        "error.html",
        navs=get_menu_navs(),
        msg=msg,
        url='/')


########################### ERRORES
@blueprint.app_errorhandler(500)
def server_error(e):
    log_err(current_app, 'Server error 500.', e, True)

    if not request.endpoint or request.endpoint == 'home.index':
        msg = "¡Ups! La página no está funcionando correctamente<br>"\
               "El equipo técnico ya está trabajando para arreglarla<br>"\
               "Por favor, vuelva más tarde"
    else:
        msg = "¡Ups! Ha surgido un error<br>"\
               "Por favor, regrese a la <a href='/'>página principal</a> y vuelva a internarlo"

    return render_error(msg)


@blueprint.app_errorhandler(404)
def not_found(e):
    msg = "No encontramos la página que está buscando<br>"\
          "Por favor, verifique que la dirección esté bien escrita o vuelva a la <a href='/'>página principal</a>"
    return render_error(msg)


@blueprint.before_request
def before_request():
    # si no está activo directus cancelamos la request, pero si es a un recurso estático la dejamos pasar
    if request.endpoint != 'home.index':
        if not current_app.config['_using_directus'] and 'static' not in request.endpoint and 'home.' in request.endpoint:
            log_err(current_app, 'Directus in error state.', None, True)

            msg = "La página se encuentra en mantenimiento<br>"\
                  "Por favor, vuelva más tarde"
            return render_error(msg)


@blueprint.after_request
def after_request(response):
    # para que el cliente pueda (solo) cargar las imágenes del dominio de directus
    if current_app.config['_using_directus']:
        response.headers['Access-Control-Allow-Origin'] = current_app.config['DIRECTUS_URL_EXTERNAL']
    return response


@blueprint.route("/", methods=['GET'])
def index():
    if current_app.config['_using_directus']:
        import app.directus as directus
        # dimgsnav = directus.dapi.get_imgs_pagina('Navegacion')
        # dimgsfooter = directus.dapi.get_imgs_pagina('Footer')
        dtextos = directus.dapi.get_textos_pagina('Home')
        dimgs = directus.dapi.get_imgs_pagina('Home')
        itemspropuestas = directus.dapi.get_items_propuestas()
        # itemsnovedades = directus.dapi.get_items_novedades('Home')
        itemsagenda = directus.dapi.get_items_agenda('Home')
        galeriahackaton = directus.dapi.get_items_hackaton()
    else:
        import app.content as content
        dtextos = content.textos_home()
        dimgs = {}
        itemspropuestas = content.items_propuestas()
        itemsagenda = {}
        galeriahackaton = content.items_hackaton()


    return render_template(
        'index.html',
        navs=get_menu_navs(),
        # dimgsnav=dimgsnav,
        # dimgsfooter=dimgsfooter,
        dtextos=dtextos,
        dimgs=dimgs,
        # itemsnovedades=itemsnovedades,
        itemsagenda=itemsagenda,
        itemspropuestas=itemspropuestas,
        galeriahackaton=galeriahackaton)


@blueprint.route("/contacto", methods=['GET'])
def contacto():
    import app.directus as directus
    # dimgsnav = directus.dapi.get_imgs_pagina('Navegacion')
    # dimgsfooter = directus.dapi.get_imgs_pagina('Footer')

    dtextos = directus.dapi.get_textos_pagina('Contacto')
    dimgs = directus.dapi.get_imgs_pagina('Contacto')

    return render_template(
        'contacto.html',
        navs=get_menu_navs(),
        # dimgsnav=dimgsnav,
        # dimgsfooter=dimgsfooter,
        dtextos=dtextos,
        dimgs=dimgs)


def _get_causa_from_endpoint():
    split = request.endpoint.split('.')
    if len(split) < 2:
        return None

    causa = request.endpoint.split('.')[1]
    # a algunos endpoints (como el de scrollys) le ponemos "_" en el nombre, después del nombre de la causa
    causa = causa.split('_')[0]
    if causa not in accepted_causas.keys():
        return None

    return causa


def causas_route():
    causa = _get_causa_from_endpoint()
    if causa is None:
        return redirect(url_for('home.index'))

    import app.directus as directus

    # dimgsnav = directus.dapi.get_imgs_pagina('Navegacion')
    # dimgsfooter = directus.dapi.get_imgs_pagina('Footer')

    dtextoscausas = directus.dapi.get_textos_pagina('Causas')
    dtextos = directus.dapi.get_textos_pagina(causa)
    dimgs = directus.dapi.get_imgs_pagina(causa)

    itemstemas = directus.dapi.get_items_tema(causa)
    itemsseguidores = directus.dapi.get_items_seguidor(causa)
    itemsnovedades = directus.dapi.get_items_novedades(causa)
    itemsagenda = directus.dapi.get_items_agenda(causa)

    variables = {
        'navs': get_menu_navs(),
        # 'dimgsnav': dimgsnav,
        # 'dimgsfooter': dimgsfooter,

        'dtextoscausas': dtextoscausas,
        'dtextos': dtextos,
        'dimgs': dimgs,

        'itemstemas': itemstemas,
        'itemsseguidores': itemsseguidores,
        'itemsnovedades': itemsnovedades,
        'itemsagenda': itemsagenda,

        'show_wiki_btn': True,
        'nombre_causa': accepted_causas[causa]}

    if causa == 'ciencia':
        variables['show_wiki_btn'] = False

    return render_template('causa.html', **variables)


def causas_scrolly_route():
    causa = _get_causa_from_endpoint()
    if causa is None:
        return redirect(url_for('home.index'))

    return 'Hola 123 ' + causa


@blueprint.route("/cuentas", methods=['GET'])
def cuentas():
    import app.directus as directus
    dimgsnav = directus.dapi.get_imgs_pagina('Navegacion')
    dimgsfooter = directus.dapi.get_imgs_pagina('Footer')

    dtextos = directus.dapi.get_textos_pagina('Cuentas')

    import app.datos as datos
    presu_heads = datos.get_rendered_headers()

    # if current_app._gsheetapi:
    if False:
        presu_data = datos.get_rows_from_gsheet(current_app._gsheetapi)
    else:
        # cols = datos.get_cols_from_csv(blueprint.static_folder + '/datos-presupuesto.csv')
        presu_data = datos.get_rows_from_csv(blueprint.static_folder + '/datos-presupuesto.csv')

    fechas_epoch = []
    fecha_i = presu_heads.index('fecha')
    for row in presu_data:
        try:
            date = datetime.strptime(row[fecha_i], '%d/%m/%Y')
            date = date.strftime('%s')
        except:
            date = ''
        fechas_epoch.append(date)

    presu_heads = [h.capitalize() for h in presu_heads]

    return render_template(
        'transparencia.html',
        navs=get_menu_navs(),
        dimgsnav=dimgsnav,
        dimgsfooter=dimgsfooter,
        dtextos=dtextos,
        presu_heads=presu_heads,
        presu_data=presu_data,
        fechas_epoch=fechas_epoch)


for causa in accepted_causas.keys():
    blueprint.add_url_rule(f'/{causa}', endpoint=causa, view_func=causas_route)
    blueprint.add_url_rule(f'/{causa}/scrolly', endpoint=f'{causa}_scrolly', view_func=causas_scrolly_route)
