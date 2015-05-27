import pyblish.api

import ftrack

@pyblish.api.log
class ValidateFtrackVersion(pyblish.api.Validator):
    """Validates whether ftrack version with matching version number exists

    expected data members:
    'ftrackData' - Necessary ftrack information gathered by select_ftrack
    'version' - version of publish
    """

    families = ['workFile']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        # TODO: potentially include version checking in here so we don't rely on it being passed from collector

        if instance.context.has_data('version'):

            versionNumber = instance.context.data('version')

            taskid = instance.context.data('ftrackData')['task']['id']
            task = ftrack.Task(taskid)

            shot = ftrack.Shot(id=instance.context.data('ftrackData')['shot']['id'])

            assetType = instance.context.data('ftrackData')['task']['code']
            assetName = instance.context.data('ftrackData')['task']['type']

            asset = shot.createAsset(name=assetName, assetType=assetType, task=task)

            self.log.info('Using ftrack asset {}'.format(assetName))

            version = None
            for v in asset.getVersions():
                if int(v.getVersion()) == int(versionNumber):
                    if not v.get('ispublished'):
                        version = v
                        instance.context.set_data('ftrackVersionID', value=version.getId())
                        raise pyblish.api.ValidationError('This version already exists, but is not visible in ftrack UI.'
                                                    'Repair to delete it. {}'.format(str(version)))
                    else:
                        version = v
                        instance.context.set_data('ftrackVersionID', value=version.getId())
                        raise pyblish.api.ValidationError('This version already exists Repair to delete it. '
                                                          '{}'.format(str(version)))

            if not version:
                instance.context.set_data('createFtrackVersion', value=True)

        else:
            self.log.warning('Can\'t determine file version')

    def repair_instance(self, instance):
        """Removes existing version
        """
        version = ftrack.AssetVersion(id=instance.context.data('ftrackVersionID'))
        version.delete()