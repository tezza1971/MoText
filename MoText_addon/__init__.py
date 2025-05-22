# __init__.py

bl_info = {
    "name": "MoText",
    "author": "Terence Kearns (with AI assistance)",
    "version": (1, 0, 0),
    "blender": (4, 0, 0), # Minimum Blender version
    "location": "3D View > Sidebar (N-Panel) > MoText Tab",
    "description": "Applies Geometry Node tools from .blend templates to text or objects.",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
from . import ui
from . import operators
from . import utils # If you have a utils.py

# --- Properties for the Addon (can be stored in scene or addon preferences) ---
# These properties will be accessible by the panel and operator.

class MoTextProperties(bpy.types.PropertyGroup):
    input_type: bpy.props.EnumProperty(
        name="Input Type",
        description="Choose input type for the MoText effect",
        items=[
            ('TEXT', "Text", "Use custom text input"),
            ('OBJECT', "Object", "Use an existing scene object"),
        ],
        default='TEXT',
        update=lambda self, context: MoTextProperties.clear_other_input(self, context) # Optional: clear other input on change
    )
    
    text_input: bpy.props.StringProperty(
        name="Text",
        description="Text to be processed by the MoText template",
        default="Hello Blender",
    )

    object_input: bpy.props.PointerProperty(
        name="Source Object",
        description="Object to be processed by the MoText template",
        type=bpy.types.Object,
    )

    # template_files will be populated dynamically
    # The EnumProperty items callback will use a function from utils.py
    template_file: bpy.props.EnumProperty(
        name="Template",
        description="Select a MoText template (.blend file prefixed with 'mograph_')",
        items=utils.get_template_files_enum_items # This function needs to be defined in utils.py
    )
    
    @classmethod
    def clear_other_input(cls, self, context):
        # Optional: When switching input_type, clear the irrelevant field
        # For instance, if switching to 'TEXT', you might want to clear 'object_input'
        # This requires careful handling if you want to preserve previous selections
        pass


# --- Registration ---

# TODO (Inside __init__.py)
# ... other imports ...
#from .utils import on_blend_file_changed # Import the handler

# ... inside register() ...
    #bpy.app.handlers.load_post.append(on_blend_file_changed)
    #bpy.app.handlers.save_post.append(on_blend_file_changed)
    #update_template_list_on_load() # Initial scan

# ... inside unregister() ...
    #if on_blend_file_changed in bpy.app.handlers.load_post:
    #    bpy.app.handlers.load_post.remove(on_blend_file_changed)
    #if on_blend_file_changed in bpy.app.handlers.save_post:
    #    bpy.app.handlers.save_post.remove(on_blend_file_changed)

#classes_to_register = (
    #MoTextProperties,
    #ui.MoTextPanel,
    #operators.MOTEXT_OT_apply_template,
    # Add other classes if you create more
#)

def register():
    for cls in classes_to_register:
        bpy.utils.register_class(cls)
    
    # Store properties in the scene (could also be addon preferences)
    bpy.types.Scene.motext_props = bpy.props.PointerProperty(type=MoTextProperties)
    
    # Refresh template list on registration (and potentially on file load)
    utils.update_template_list_on_load()


def unregister():
    del bpy.types.Scene.motext_props
    
    for cls in reversed(classes_to_register):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
