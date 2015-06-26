import os
import json
import base64
import sys
import ftrack
import pyblish_qml
import pyblish.api


@pyblish.api.log
class CollectFtrackData(pyblish.api.Selector):
    """Collects ftrack data from FTRACK_CONNECT_EVENT
        Arguments:
            version (int): version number of the publish
    """

    order = pyblish.api.Selector.order + 0.11
    hosts = ['*']
    version = (0, 1, 0)

    def process(self, context):

        decodedEventData = json.loads(
            base64.b64decode(
                os.environ.get('FTRACK_CONNECT_EVENT')
            )
        )

        taskid = decodedEventData.get('selection')[0]['entityId']
        ftrack_data = self.get_data(taskid)

        self.log.debug(str(ftrack_data))
        # Get ftrack Asset
        task = ftrack.Task(taskid)

        try:
            parent = ftrack.Shot(id=ftrack_data['Shot']['id'])
        except:
            parent = ftrack.Shot(id=ftrack_data['Asset_Build']['id'])

        asset_type = ftrack_data['Task']['code']

        if asset_type == 'light':
            asset_type = 'render'

        asset_name = ftrack_data['Task']['type']

        assets = task.getAssets(assetTypes=[asset_type])

        if assets:
            for a in assets:
                if a.getName() == asset_name:
                    self.log.info('Found existing asset with name\
                    {}'.format(a.getName()))
                    asset = a
                    break
                else:
                    self.log.info('Found existing asset with name\
                    {}'.format(a.getName()))
                    asset = a
        else:
            self.log.info('Creating new asset')
            asset = parent.createAsset(name=asset_name,
                                       assetType=asset_type,
                                       task=task)

        self.log.info('Using ftrack asset {}'.format(asset.getName()))

        ftrack_data['Asset'] = {'id': asset.getId(),
                                'name': asset.getName()
                                }

        # Get ftrack AssetVersion or set 'createFtrackVersion' argument
        if context.data('version'):
            version_number = int(context.data('version'))
            version = None

            for v in asset.getVersions():
                if int(v.getVersion()) == version_number:
                    version = v
                    ftrack_data['AssetVersion'] = {'id': version.getId(),
                                                   'number': version_number,
                                                   }
                    self.log.warning('This version already exists. Will\
                                     check for existence of  components')

            if not version:
                context.set_data('createFtrackVersion', value=True)
                self.log.debug('Setting createFtrackVersion arguments')
        else:
            context.set_data('createFtrackVersion', value=True)
            self.log.debug('Setting createFtrackVersion arguments')
            self.log.warning('Missing version number in context.')

        # set ftrack data
        context.set_data('ftrackData', value=ftrack_data)

        context.set_data("label", "The World")

        pyblish_qml.settings.WindowTitle = 'testin path/ shot/ task'

        self.log.info('Found ftrack data: \n\n%s' % ftrack_data)

    def get_data(self, taskid):

        task_codes = {
            'Animation': 'anim',
            'Layout': 'layout',
            'FX': 'fx',
            'Compositing': 'comp',
            'Motion Graphics': 'mograph',
            'Lighting': 'light',
            'Modelling': 'geo',
            'Rigging': 'rig',
            'Art': 'art',
        }

        try:
            task = ftrack.Task(id=taskid)
        except ValueError:
            task = None

        parents = task.getParents()
        project = ftrack.Project(task.get('showid'))
        taskType = task.getType().getName()
        entityType = task.getObjectType()

        ctx = {
            'Project': {
                    'name': project.get('fullname'),
                    'code': project.get('name'),
                    'id': task.get('showid'),
                    'root': project.getRoot(),
            },
            entityType: {
                    'type': taskType,
                    'name': task.getName(),
                    'id': task.getId(),
                    'code': task_codes.get(taskType, None)
            }
        }

        for parent in parents:
            tempdic = {}
            if parent.get('entityType') == 'task' and parent.getObjectType():
                objectType = parent.getObjectType()
                tempdic['name'] = parent.getName()
                tempdic['description'] = parent.getDescription()
                tempdic['id'] = parent.getId()
                if objectType == 'Asset Build':
                    tempdic['type'] = parent.getType().get('name')
                    objectType = objectType.replace(' ', '_')

                ctx[objectType] = tempdic

        return ctx
