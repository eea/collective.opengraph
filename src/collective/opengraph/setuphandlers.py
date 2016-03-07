import logging
from plone import api
import transaction
from zope import interface
from zope.component.interfaces import ComponentLookupError

from collective.opengraph.interfaces import IOpengraphable, IOpengraphMarker
from collective.opengraph.interfaces import IOpengraphMarkerUtility

log = logging.getLogger(__name__)


def uninstall(context):
    marker = 'collective.opengraph_uninstall.txt'
    if context.readDataFile(marker) is None:
        return

    query = {'object_provides':
             'collective.opengraph.interfaces.IOpengraphable'}
    catalog = api.portal.get_tool('portal_catalog')
    res = catalog(query)
    log.info("Removing interfaces from %s objects", len(res))
    for item in res:
        ob = item.getObject()
        interface.directlyProvides(
            ob,
            interface.directlyProvidedBy(ob)-IOpengraphable-IOpengraphMarker)
        ob.reindexObject(idxs=['object_provides'])
    log.info("Unregistering utility")
    portal = api.portal.get()
    sm = portal.getSiteManager()
    try:
        util = sm.getUtility(IOpengraphMarkerUtility)
        del util
    except ComponentLookupError:
        pass
    sm.unregisterUtility(provided=IOpengraphMarkerUtility)
    sm.utilities.unsubscribe((), IOpengraphMarkerUtility)
    try:
        del sm.utilities.__dict__['_provided'][IOpengraphMarkerUtility]
    except KeyError:
        # already removed
        pass

    log.info("Committing transaction...")
    transaction.commit()
    log.info("done.")
