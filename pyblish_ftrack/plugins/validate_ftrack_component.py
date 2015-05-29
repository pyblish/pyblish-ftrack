import pyblish.api

import ftrack

@pyblish.api.log
class ValidateFtrackComponent(pyblish.api.Validator):
    """ Validates whether ftrack version with matching version number exists

        Arguments:
            ftrackComponentName (string): name of currently processed component
            ftrackData (dictionary): Necessary ftrack information gathered by select_ftrack
    """
    families = ['*']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        if instance.context.has_data('ftrackData'):
            ftrack_data = instance.context.data('ftrackData')

            if instance.has_data('ftrackComponentName'):
                if 'AssetVersion' in ftrack_data:
                    asset_version = ftrack.AssetVersion(id=ftrack_data['AssetVersion']['id'])
                    components = asset_version.getComponents()
                    component_name = instance.has_data('ftrackComponentName')

                    for c in components:
                        if component_name == c.getName():
                            raise pyblish.api.ValidationError('Component {} already exists in this ftrack version.'.format(component_name))

                else:
                    self.log.warning('No version found for validating components')
            else:
                self.log.warning('Missing ftrackComponentName')
        else:
            self.log.warning('No ftrackData present. Skipping this instance')