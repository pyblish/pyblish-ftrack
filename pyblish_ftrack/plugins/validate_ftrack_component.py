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
    name = "Validate Ftrack Components"

    def process(self, instance):

        # skipping validation if the extension wants to create a new version
        if instance.context.data('createFtrackVersion'):
            msg = 'Skipping component validation,'
            msg += ' since createFtrackVersion is enabled.'
            self.log.debug(msg)
            return

        # checking for required items
        if instance.has_data('ftrackComponents') and instance.context.has_data('ftrackData'):

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
                for online_c in online_components:
                    online_name = online_c.getName()
                    # checking name matching
                    if 'reviewable' in local_components[local_c]:
                        msg = 'Reviewable component already exists in the version. To replace it' \
                              ' delete it in the webUI first'
                        assert online_name not in ('ftrackreview-mp4', 'ftrackreview-webm'), msg
                    if local_c == online_name:
                        self.log.warning('{} component already exists! To replace it'
                                         ' delete it in the webUI first'.format(local_c))
        else:
            msg = 'No ftrackData or ftrackComponents present. '
            msg += 'Skipping this instance.'
            self.log.debug(msg)
