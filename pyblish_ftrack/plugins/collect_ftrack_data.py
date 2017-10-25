import os
import json
import base64
import ftrack
import pyblish.api


@pyblish.api.log
class CollectFtrackData(pyblish.api.Selector):

    """Collects ftrack data from FTRACK_CONNECT_EVENT
        Arguments:
            version (int): version number of the publish
    """

    order = pyblish.api.Selector.order
    hosts = ['*']
    version = (0, 1, 0)

    def process(self, context):

        # accounting for preexiting data
        if "ftrackData" in context.data:
            data = context.data["ftrackData"]
            self.log.info('Found ftrack data: \n\n%s' % data)
            return

        # getting task id
        task_id = os.environ.get('FTRACK_TASKID', '')

        try:
            decoded_event_data = json.loads(
                base64.b64decode(
                    os.environ.get('FTRACK_CONNECT_EVENT')
                )
            )

            task_id = decoded_event_data.get('selection')[0]['entityId']
        except:
            pass

        if task_id:
            ftrack_data = self.get_data(task_id)

            # set ftrack data
            context.set_data('ftrackData', value=ftrack_data)

            self.log.info('Found ftrack data: \n\n%s' % ftrack_data)

    def get_data(self, task_id):

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
            task = ftrack.Task(id=task_id)
        except ValueError:
            task = None

        parents = task.getParents()
        project = ftrack.Project(task.get('showid'))
        task_type = task.getType().getName()
        entity_type = task.getObjectType()

        ctx = {
            'Project': {
                'name': project.get('fullname'),
                'code': project.get('name'),
                'id': task.get('showid'),
                'root': project.getRoot(),
            },
            entity_type: {
                'type': task_type,
                'name': task.getName(),
                'id': task.getId(),
                'code': task_codes.get(task_type, None)
            }
        }

        for parent in parents:
            tempdic = {}
            if parent.get('entityType') == 'task' and parent.getObjectType():
                object_type = parent.getObjectType()
                tempdic['name'] = parent.getName()
                tempdic['description'] = parent.getDescription()
                tempdic['id'] = parent.getId()
                if object_type == 'Asset Build':
                    tempdic['type'] = parent.getType().get('name')
                    object_type = object_type.replace(' ', '_')

                ctx[object_type] = tempdic

        return ctx
