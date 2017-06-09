""" Evolve 11 profile
"""
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
from collective.opengraph.interfaces import IOpengraphSettings
from Products.CMFCore.utils import getToolByName


def evolve(context):
    """ Update the registry with the latest added fields """
    registry = queryUtility(IRegistry)
    registry.registerInterface(IOpengraphSettings)
    pactions = getToolByName(context, 'portal_actions')
    object_buttons = pactions.object_buttons
    if getattr(object_buttons, 'enable_opengraph'):
        object_buttons.enable_opengraph.available_expr = "python:not object." \
            "restrictedTraverse('@@opengraph_enabled')() and " \
            "not object.restrictedTraverse('@@opengraph_sitewide_enabled')()"
    if getattr(object_buttons, 'disable_opengraph'):
        object_buttons.disable_opengraph.available_expr = "python:object." \
        "restrictedTraverse('@@opengraph_enabled')() and " \
        "not object.restrictedTraverse('@@opengraph_enabled')()"
