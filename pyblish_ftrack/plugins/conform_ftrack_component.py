import pyblish.api
import os
import ftrack

@pyblish.api.log
class FtrackUploadComponent(pyblish.api.Conformer):
    """ Creates component within supplied version.

        Arguments:
            ftrackComponents (dict): keys are names of components
                path (string): path of component
                reviewable (bool, optional): uploads the component as review
            ftrackData (dictionary): Necessary ftrack information gathered by select_ftrack
    """

    order = pyblish.api.Conformer.order + 0.11
    families = ['*']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        # check for components exsitence
        if instance.has_data('ftrackComponents'):

            # check for AssetVersion existence
            ftrack_data = instance.context.data('ftrackData')
            if 'AssetVersion' in ftrack_data:
                version_id = ftrack_data['AssetVersion']['id']
                version = ftrack.AssetVersion(id=version_id)

                components = instance.data('ftrackComponents')
                for component_name in components:
                    # creating component
                    path = components[component_name]['path']

                    try:
                        version.createComponent(name=component_name, path=path)
                    except:
                        msg = 'No new component created.'
                        msg += ' Existing component matches'
                        self.log.debug(msg)
            else:
                self.log.warning('No AssetVersion id found in context')
        else:
            self.log.warning('No components found!')
