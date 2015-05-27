import pyblish.api
import os
import ftrack

@pyblish.api.log
class FtrackUploadComponent(pyblish.api.Conformer):
    """Creates component within supplied version.

    Expected data members:
    'ftrackComponent' - path that will be saved as a component
    'ftrackComponentName' - component name
    'ftrackVersionID' - ID of a version where component should be created
    Optional:
    'ftrackReviewable' - will make current instance reviewable
    """

    order = pyblish.api.Conformer.order + 0.11
    families = ['*']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        if instance.has_data('ftrackComponent') and instance.has_data('ftrackComponentName'):

            sourcePath = os.path.normpath(instance.data('ftrackComponent'))

            if instance.context.has_data('ftrackVersionID'):
                version = ftrack.AssetVersion(id=instance.context.data('ftrackVersionID'))

                componentName = instance.data('ftrackComponentName')

                try:
                    component = version.getComponent(name=componentName)
                    component.delete()
                    self.log.info('Replacing component with name "%s"' % componentName)
                except:
                    self.log.info('Creating component with name "%s"' % componentName)

                version.createComponent(name=componentName, path=sourcePath)
                # make reviewable
                if instance.has_data('ftrackReviewable'):
                    ftrack.Review.makeReviewable(version, sourcePath)
            else:
                self.log.info('No versionID found in context')

        else:
            self.log.warning('No published flipbook found!')
