import pyblish.api

import ftrack

@pyblish.api.log
class ValidateFtrackComponent(pyblish.api.Validator):
    """ Validates whether ftrack version with matching version number exists

        Arguments:
            ftrackComponentName (string): name of currently processed component
            ftrackVersionID (string): ftrack version ID
    """
    families = ['*']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        if instance.has_data('ftrackComponentName'):
            if instance.context.data('ftrackVersionID'):
                version = ftrack.AssetVersion(id=instance.context.data('ftrackVersionID'))
                components = version.getComponents()
                for c in components:
                    if instance.data('ftrackComponentName') == c.getName():
                        raise pyblish.api.ValidationError('Component {} already exists in this ftrack version.'.format(instance.data('ftrackComponentName')))
            else:
                self.log.info('No components to validate againsts')
        else:
            self.log.warning('Missing ftrackComponentName')