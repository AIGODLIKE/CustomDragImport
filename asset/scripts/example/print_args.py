import bpy

cdi_tool = globals().get('cdi_tool')
from cdi_tool.debugLog import DebugLog

# each
filepath = globals().get('filepath')
index = globals().get('index')
selected_objects = globals().get('selected_objects')
selected_nodes = globals().get('selected_nodes')
# all
directory = globals().get('directory')
files = globals().get('files')

logger = DebugLog()
logger.debug("cdi_tool", filepath, index, selected_objects, selected_nodes, directory, files)
