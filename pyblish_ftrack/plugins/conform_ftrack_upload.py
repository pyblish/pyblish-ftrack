import pyblish.api
import os

import ftrack

@pyblish.api.log
class ConformFtrackUpload(pyblish.api.Conformer):
    """Creates scene component with in supplied version"""

    order = pyblish.api.Conformer.order + 0.11
    families = ['workFile']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        if instance.has_data('publishedFile'):
            sourcePath = os.path.normpath(instance.data('publishedFile'))

            if instance.context.has_data('ftrackVersionID'):
                version = ftrack.AssetVersion(id=instance.context.data('ftrackVersionID'))

                componentName = 'scene'

                try:
                    component = version.getComponent(name=componentName)
                    component.delete()
                    self.log.info('Replacing component with name "%s"' % componentName)
                except:
                    self.log.info('Creating component with name "%s"' % componentName)

                version.createComponent(name=componentName, path=sourcePath)
                self.log.info('Component {} created'.format(componentName))
            else:
                self.log.info('No versionID found in context')
                # instance.context.set_data('ftrackVersionID', value=version.getId())
        else:
            self.log.warning('Didn\'t create ftrack version because workfile wasn\'t published')
