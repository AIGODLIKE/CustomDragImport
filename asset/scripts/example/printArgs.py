import bpy

from cdi_tool.debugLog import DebugLog

event = globals().get('event')
# each
filepath = globals().get('filepath')
index = globals().get('index')
selected_objects = globals().get('selected_objects')
selected_nodes = globals().get('selected_nodes')
# all
directory = globals().get('directory')
files = globals().get('files')

logger = DebugLog()
logger.debug(f'event:{event}\n'
             f'filepath:{filepath}\n'
             f'index:{index}\n'
             f'selected_objects:{selected_objects}\n'
             f'selected_nodes:{selected_nodes}\n'
             f'directory:{directory}\n'
             f'files:{files}\n')
