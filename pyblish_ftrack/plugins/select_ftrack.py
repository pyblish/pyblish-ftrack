import os
import json
import base64
import sys
import ftrack

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pyblish_ftrack_utils

import pyblish.api


@pyblish.api.log
class CollectFtrack(pyblish.api.Selector):
    """Collects ftrack data from FTRACK_CONNECT_EVENT"""

    order = pyblish.api.Selector.order + 0.1
    hosts = ['*']
    version = (0, 1, 0)

    def process_context(self, context):

        decodedEventData = json.loads(
            base64.b64decode(
                os.environ.get('FTRACK_CONNECT_EVENT')
            )
        )

        taskid = decodedEventData.get('selection')[0]['entityId']
        ftrackData = pyblish_ftrack_utils.getData(taskid)

        # Get ftrack Asset
        task = ftrack.Task(taskid)

        shot = ftrack.Shot(id=ftrackData['Shot']['id'])

        assetType = ftrackData['Task']['code']
        assetName = ftrackData['Task']['type']

        assets = task.getAssets(assetTypes=[assetType])

        if assets:
            for a in assets:
                if a.getName() == assetName:
                    self.log.info('Found existing asset with name {}'.format(a.getName()))
                    asset = a
                    break
                else:
                    self.log.info('Found existing asset with name {}'.format(a.getName()))
                    asset = a
        else:
            self.log.info('creating new asset')
            asset = shot.createAsset(name=assetName, assetType=assetType, task=task)

        self.log.info('Using ftrack asset {}'.format(asset.getName()))

        ftrackData['Asset'] = {'id': asset.getId(),
                               'name': asset.getName()
                               }
        # Get version number
        if context.has_data('version'):
            ftrackData['version'] = {'number': int(context.data('version'))}
        else:
            directory, filename = os.path.split(context.data('currentFile'))
            try:
                prefix, version = pyblish_ftrack_utils.version_get(filename, 'v')
                ftrackData['version'] = {'number': int(version)}
            except ValueError:
                self.log.warning('Cannot find version string in filename.')
                return None

        self.log.info('Publish Version: {}'.format(ftrackData['version']['number']))

        # set ftrack data
        context.set_data('ftrackData', value=ftrackData)

        self.log.info('Found ftrack data')