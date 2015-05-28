import pyblish.api
import ftrack

@pyblish.api.log
class FtrackCreateVersion(pyblish.api.Conformer):
    """ Creates ftrack version for currently running publish.

        Arguments:
            ftrackData (dictionary): Necessary ftrack information gathered by select_ftrack
            ftrackComponent (string):  path that will be saved as a component
            createFtrackVersion (boolean): boolean variable set by validate_ftrack_version
    """

    order = pyblish.api.Conformer.order + 0.1
    families = ['*']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        if instance.has_data('ftrackComponent'):
            if instance.context.data('createFtrackVersion') and not instance.context.has_data('ftrackVersionID'):
                self.log.info('CREATING VERSION')
                versionNumber = instance.context.data('ftrackData')['version']['number']

                taskid = instance.context.data('ftrackData')['task']['id']

                asset = ftrack.Asset(id=instance.context.data('ftrackData')['asset']['id'])
                self.log.info('Using ftrack asset {}'.format(asset.getName()))

                version = asset.createVersion(comment='', taskid=taskid)

                if int(version.getVersion()) != int(versionNumber):
                    version.set('version', value=int(versionNumber))

                instance.context.set_data('ftrackVersionID', value=version.getId())
                version.publish()
        else:
            self.log.warning('Didn\'t create ftrack version because workfile wasn\'t published')
