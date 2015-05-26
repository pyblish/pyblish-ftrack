import pyblish.api

import ftrack

@pyblish.api.log
class ConformFtrackCreateVersion(pyblish.api.Conformer):
    """Creates ftrack version for currently running publish.

    Expected data members:
    'ftrackData' - Necessary frack information gathered by select_ftrack
    'publishedFile' - path that will be saved as a component
    'createFtrackVersion' - boolean variable set by validate_ftrack_version
    'version' - version of publish
    """

    order = pyblish.api.Conformer.order + 0.1
    families = ['workFile']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        if instance.has_data('publishedFile'):
            if instance.context.data('createFtrackVersion'):
                self.log.info('CREATING VERSION')
                versionNumber = instance.context.data('version')

                taskid = instance.context.data('ftrackData')['task']['id']
                task = ftrack.Task(taskid)

                shot = ftrack.Shot(id=instance.context.data('ftrackData')['shot']['id'])

                assetType = instance.context.data('ftrackData')['task']['code']
                assetName = instance.context.data('ftrackData')['task']['type']

                asset = shot.createAsset(name=assetName, assetType=assetType, task=task)

                self.log.info('Using ftrack asset {}'.format(assetName))

                taskid = instance.context.data('ftrackData')['task']['id']
                task = ftrack.Task(taskid)
                shot = ftrack.Shot(id=instance.context.data('ftrackData')['shot']['id'])
                assetType = instance.context.data('ftrackData')['task']['code']
                assetName = instance.context.data('ftrackData')['task']['type']
                asset = shot.createAsset(name=assetName, assetType=assetType, task=task)


                version = asset.createVersion(comment='', taskid=taskid)
                if int(version.getVersion()) != int(versionNumber):
                    version.set('version', value=int(versionNumber))
                instance.context.set_data('createFtrackVersion', value=True)

                instance.context.set_data('ftrackVersionID', value=version.getId())
                print 'version: ' + str(version)
                version.publish()

        else:
            self.log.warning('Didn\'t create ftrack version because workfile wasn\'t published')
