from pyramid.renderers import render
from pyramid.threadlocal import get_current_request
from pyramid.i18n import TranslationStringFactory
from kotti.resources import get_root
from kotti.security import has_permission
from kotti.util import extract_from_settings
from kotti.views.slots import (
    RenderRightSlot,
    RenderLeftSlot,
    register,
)

from logging import getLogger
log = getLogger('kotti_navigation: ')

_ = TranslationStringFactory('kotti_navigation')

NAVIGATION_WIDGET_DEFAULTS = {
    'include_root': 'true',
    'open_all': 'false',
    }


def kotti_configure(settings):
    settings['pyramid.includes'] += ' kotti_navigation.include_navigation_widget'


def navigation_settings(name=''):
    prefix = 'kotti_navigation.navigation_widget.'
    if name:
        prefix += name + '.'  # pragma: no cover
    settings = NAVIGATION_WIDGET_DEFAULTS.copy()
    settings.update(extract_from_settings(prefix))
    return settings


def check_true(value):
    if value == u'true':
        return True
    return False


def get_children(context, request):
    childs = [child for child in context.values()
                  if child.in_navigation and
                  has_permission('view', child, request)]
    return childs


def open_tree(item, request):
    """ Check if the tree should be opened for the given item.
    """
    # if all_open is true this is always True
    if check_true(navigation_settings()['open_all']):
        return True

    context = request.context

    root = get_root()
    open_tree = False
    while 1:
        if item == context:
            open_tree = True
            break
        if root == context:
            break
        context = context.__parent__
    return open_tree


def nav_tree(context, request):
    return {'open_tree': open_tree,
            'children': get_children(context, request),
            }


def include_view(config, name=''):
    config.add_view(
        'kotti_navigation.nav_tree',
        name='nav-tree',
        permission='view',
        renderer='kotti_navigation:templates/nav_tree.pt',
        )
    config.add_static_view('static-kotti_navigation', 'kotti_navigation:static')


def render_navigation_widget(context, request, name=''):
    settings = navigation_settings()

    root = get_root()

    include_root = check_true(settings['include_root'])
    current_level = 2

    children = get_children(root, request)

    return render(
        'kotti_navigation:templates/navigation.pt',
        dict(root=root,
             children=children,
             include_root=include_root,
             current_level=current_level,
            ),
        request,
    )


def include_navigation_widget(config, where=RenderLeftSlot):  # pragma: no cover
    include_view(config)
    register(where, None, render_navigation_widget)


def include_navigation_widget_right(config):  # pragma: no cover
    include_navigation_widget(config, RenderRightSlot)
