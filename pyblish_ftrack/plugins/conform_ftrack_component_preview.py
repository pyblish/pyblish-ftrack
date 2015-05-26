import pyblish.api
import os

import ftrack


@pyblish.api.log
class FtrackUploadPreview(pyblish.api.Conformer):
    """Creates Preview component within supplied version, also makes this preview reviewable.

    Expected data members:
    'publishedFile' - path that will be saved as a component
    'ftrackVersionID' - ID of a version where component should be created
    """

    order = pyblish.api.Conformer.order + 0.11
    families = ['preview']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        if instance.has_data('publishedFile'):
            sourcePath = os.path.normpath(instance.data('publishedFile'))
            version = None

            if instance.context.has_data('ftrackVersionID'):
                version = ftrack.AssetVersion(id=instance.context.data('ftrackVersionID'))
                componentName = 'preview'
                try:
                    component = version.getComponent(name=componentName)
                    component.delete()
                    self.log.info('Replacing component with name "%s"' % componentName)
                except:
                    self.log.info('Creating component with name "%s"' % componentName)

                version.createComponent(name='preview', path=sourcePath)
                # make reviewable
                ftrack.Review.makeReviewable(version, sourcePath)
            else:
                self.log.info('No versionID found in context')

        else:
            self.log.warning('No published flipbook found!')
