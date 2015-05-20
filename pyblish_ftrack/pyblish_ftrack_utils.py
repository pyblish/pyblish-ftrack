import re
import ftrack

task_codes = {
    'Animation': 'anim',
    'Layout': 'layout',
    'FX': 'fx',
    'Compositing': 'comp',
    'Motion Graphics': 'mograph',
    'Lighting': 'light',
}


def version_up(string):
    try:
        (prefix, v) = version_get(string, 'v')
        v = int(v)
        file = version_set(string, prefix, v, v+1)
    except:
        raise ValueError, 'Unable to version up File'

    return file


def getData(taskid):
    try:
        task = ftrack.Task(id=taskid)
    except:
        task = None

    parents = task.getParents()
    project = ftrack.Project(task.get('showid'))
    stepName = task.getType().getName()
    directParent = parents[0]

    episodeDesc = episodeName = sequenceName = sequenceDesc = shotName = assetName = assetCategory = None

    for parent in parents:

        if parent.get('entityType') == 'task':
            objectType = parent.getObjectType()
            if objectType == 'Shot':
                shotName = parent.getName()
                shotDesc = parent.getDescription()
                shot_id = parent.getId()
            elif objectType == 'Sequence':
                sequenceName = parent.getName()
                sequenceDesc = parent.getDescription()
                sequence_id = parent.getId()
            elif objectType == 'Episode':
                episodeName = parent.getName()
                episodeDesc = parent.getDescription()
                episode_id = parent.getId()
            elif objectType == 'Asset Build':
                assetName = parent.getName()
                assetCategory = parent.getType().get('name')
                asset_id = parent.getId()


    if directParent.getObjectType() in ['Shot', 'Sequence', 'Episode']:
        ctx = {
            'project': {
                # 'scode': project.get('scode'),
                'name': project.get('fullname'),
                'code': project.get('name'),
                'id': task.get('showid')
            },
            'shot': {
                'name': shotName,
                'description': shotDesc,
                'id': shot_id
            },
            'sequence': {
                'name': sequenceName,
                'description': sequenceDesc,
                'id': sequence_id
            },
            'task': {
                'type': stepName,
                'name': task.getName(),
                'id': task.getId(),
                'code': task_codes.get(stepName, None)
            }
        }
        if episodeName:
            ctx['episode'] = {
                'name': episodeName,
                'description': episodeDesc,
                'id': episode_id
            }
    else :
        ctx = {
            'project': {
                # 'scode': project.get('scode'),
                'name': project.get('fullname'),
                'code': project.get('name'),
                'id': task.get('showid')
            },
            'asset': {
                'name': assetName,
                'type': assetCategory,
                'id': asset_id
            },
            'task': {
                'type': stepName,
                'name': task.getName(),
                'id': task.getId(),
                'code': task_codes.get(stepName, None)
            }
        }

    return ctx


def version_get(string, prefix, suffix = None):
    """Extract version information from filenames.  Code from Foundry's nukescripts.version_get()"""

    if string is None:
       raise ValueError, "Empty version string - no match"

    regex = "[/_.]"+prefix+"\d+"
    matches = re.findall(regex, string, re.IGNORECASE)
    if not len(matches):
        msg = "No \"_"+prefix+"#\" found in \""+string+"\""
        raise ValueError, msg
    return (matches[-1:][0][1], re.search("\d+", matches[-1:][0]).group())


def version_set(string, prefix, oldintval, newintval):
    """Changes version information from filenames. Code from Foundry's nukescripts.version_set()"""

    regex = "[/_.]"+prefix+"\d+"
    matches = re.findall(regex, string, re.IGNORECASE)
    if not len(matches):
        return ""

    # Filter to retain only version strings with matching numbers
    matches = filter(lambda s: int(s[2:]) == oldintval, matches)

    # Replace all version strings with matching numbers
    for match in matches:
        # use expression instead of expr so 0 prefix does not make octal
        fmt = "%%(#)0%dd" % (len(match) - 2)
        newfullvalue = match[0] + prefix + str(fmt % {"#": newintval})
        string = re.sub(match, newfullvalue, string)
    return string
