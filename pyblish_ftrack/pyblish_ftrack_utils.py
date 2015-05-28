import re
import ftrack

#   ====================
#   Task codes dictionary. This is needed to prevent file names and folders with full task type names.
#   Hopefully a temporary code until this is implemented in ftrack webUI. Change the code to your liking.

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
#   ====================


# Collect all ftrack data and store it in a dictionary
def getData(taskid):
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
                'id': task.get('showid')
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
            print parent
            objectType = parent.getObjectType()
            tempdic['name'] = parent.getName()
            tempdic['description'] = parent.getDescription()
            tempdic['id'] = parent.getId()
            if objectType == 'Asset Build':
                tempdic['type'] = parent.getType().get('name')
                objectType = objectType.replace(' ', '_')

            ctx[objectType] = tempdic

    return ctx


def version_up(string):
    try:
        (prefix, v) = version_get(string, 'v')
        v = int(v)
        file = version_set(string, prefix, v, v+1)
    except:
        raise ValueError, 'Unable to version up File'

    return file

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
