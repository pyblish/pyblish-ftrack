import pyblish.api

import ftrack

@pyblish.api.log
class ValidateFtrackComponent(pyblish.api.Validator):
    """ Validates whether ftrack version with matching version number exists

        Arguments:
            ftrackComponents (dict): keys are names of components
                path (string): path of component
                reviewable (bool, optional): uploads the component as review
            ftrackData (dictionary): Necessary ftrack information gathered by select_ftrack
    """

    families = ['*']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        # skipping validation if the extension wants to create a new version
        if instance.context.data('createFtrackVersion'):
            msg = 'Skipping component validation,'
            msg += ' since createFtrackVersion is enabled.'
            self.log.debug(msg)
            return

        # checking for required items
        if instance.has_data('ftrackComponents') and \
        instance.context.has_data('ftrackData'):

           ftrack_data = instance.context.data('ftrackData')

           # raising error, as we are assuming the user wants to publish
           # to ftrack at this point
           msg = 'No version found for validating components'
           assert 'AssetVersion' in ftrack_data, msg

           version_id = ftrack_data['AssetVersion']['id']
           asset_version = ftrack.AssetVersion(id=version_id)
           online_components = asset_version.getComponents()
           local_components = instance.data('ftrackComponents')

           for local_c in local_components:
               local_component = local_components[local_c]
               for online_c in online_components:

                   # checking name matching
                   if local_c == online_c.getName():

                       # checking value matching
                       path = local_component['path']
                       if path != online_c.getFile():
                           msg = "Component exists, but values aren't the same:"
                           msg += "\n\nComponent: %s" % local_c
                           msg += "\n\nLocal value: %s" % path
                           msg += "\n\nOnline value: %s" % online_c.getFile()
                           raise ValueError(msg)
                       else:
                           self.log.debug('Component exists!')
        else:
            msg = 'No ftrackData or ftrackComponents present. '
            msg += 'Skipping this instance.'
            self.log.debug(msg)
