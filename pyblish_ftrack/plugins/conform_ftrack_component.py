import pyblish.api
import os
import ftrack

@pyblish.api.log
class FtrackUploadComponent(pyblish.api.Conformer):
    """ Creates component within supplied version.

        Arguments:
            ftrackComponent (string): path that will be saved as a component
            ftrackComponentName (string): component name
            ftrackData (dictionary): Necessary ftrack information gathered by select_ftrack
            ftrackReviewable (string, optional): will make
    """

    order = pyblish.api.Conformer.order + 0.11
    families = ['*']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        if instance.has_data('ftrackComponent') and instance.has_data('ftrackComponentName'):
            sourcePath = os.path.normpath(instance.data('ftrackComponent'))

            ftrack_data = instance.context.data('ftrackData')

            if 'AssetVersion' in ftrack_data:
                version = ftrack.AssetVersion(id=ftrack_data['AssetVersion']['id'])
                componentName = instance.data('ftrackComponentName')

                createComponent = True
                for c in version.getComponents():
                    if c.getName() == componentName:
                        if c.getFile() == sourcePath:
                            createComponent = False

                if createComponent:
                    self.log.info('creating component {}'.format(componentName))
                    version.createComponent(name=componentName, path=sourcePath)
                else:
                    self.log.info('Component already exists.')

                # make reviewable
                if instance.has_data('ftrackReviewable'):
                    ftrack.Review.makeReviewable(version, sourcePath)
            else:
                self.log.info('No versionID found in context')

        else:
            self.log.warning('No published component found!')
