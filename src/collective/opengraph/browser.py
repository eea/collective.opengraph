from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.event import notify
from zope.annotation import IAnnotations

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from z3c.form import field, form, button
from plone.z3cform.fieldsets import extensible
from plone.z3cform.layout import wrap_form
from plone.registry.interfaces import IRegistry

from interfaces import IOpengraphable
from interfaces import IOpengraphSettings
from events import OpengraphSettingsEvent

from collective.opengraph import OpengraphMessageFactory as _


class EnableOpengraph(BrowserView):

    def __call__(self):
        alsoProvides(self.context, IOpengraphable)
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.addPortalMessage(_(u"The opengraph tags has been enabled"))
        self.request.response.redirect(self.context.absolute_url())


class DisableOpengraph(BrowserView):

    def __call__(self):
        noLongerProvides(self.context, IOpengraphable)
        plone_utils = getToolByName(self.context, 'plone_utils')
        message = _(u"The opengraph tags has been disabled")
        plone_utils.addPortalMessage(message)
        self.request.response.redirect(self.context.absolute_url())


class OpengraphEnabled(BrowserView):
    """ Check if opengraph enabled
    """

    def __call__(self):
        return IOpengraphable.providedBy(self.context)


class OpengraphSitewideEnabled(BrowserView):
    """ Check if opengraph enabled sitewide
    """
    def __call__(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IOpengraphSettings, check=False)
        enabled_sitewide = settings.enabled_sitewide or False
        return enabled_sitewide


def back_to_controlpanel(self):
    root = getSite()
    return dict(url=root.absolute_url() + '/plone_control_panel')


class OpengraphControlpanelForm(extensible.ExtensibleForm, form.EditForm):
    successMessage = _(u'Data successfully updated.')
    noChangesMessage = _(u'No changes were applied.')
    formErrorsMessage = _(u"There were some errors.")

    form.extends(form.EditForm, ignoreButtons=True)
    fields = field.Fields(IOpengraphSettings)
    label = _(u'Configure Collective Opengraph')

    def __init__(self, context, request):
        super(OpengraphControlpanelForm, self).__init__(context, request)
        self.ptool = getToolByName(self.context, 'plone_utils')

    @button.buttonAndHandler(_(u'Apply'), name='apply')
    def handle_apply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IOpengraphSettings, check=False)
        IAnnotations(self.context)['old_content_types'] = settings.content_types

        changes = self.applyChanges(data)
        if changes:
            self.status = self.successMessage
            if not self.context.restrictedTraverse(
                    '@@opengraph_sitewide_enabled')():
                notify(OpengraphSettingsEvent(self.context, data))
        else:
            self.status = self.noChangesMessage

        self.ptool.addPortalMessage(self.status, 'info')
        self.request.response.redirect(self.back_link)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handle_cancel(self, action):
        self.ptool.addPortalMessage(self.noChangesMessage, 'info')
        self.request.response.redirect(self.back_link)

    @property
    def back_link(self):
        return back_to_controlpanel(self)['url']


OpengraphControlpanel = wrap_form(OpengraphControlpanelForm)
