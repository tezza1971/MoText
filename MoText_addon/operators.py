# operators.py
import bpy
import os

# --- Conventions for MoText Template Files ---
# These constants define the specific naming conventions that users MUST follow
# when creating their .blend files to be used as templates by the MoText addon.
# Adherence to these conventions is CRUCIAL for the addon to correctly identify
# and utilize the Geometry Node setups within the template files.

# TARGET_NODE_GROUP_NAME:
#   - Purpose: Specifies the exact name of the Geometry Node group that the MoText
#     addon will look for and apply from the template .blend file.
#   - Convention: Template creators MUST name their main Geometry Node group
#     (intended for use by MoText) exactly as defined by this constant.
#   - Example: "MoTextNodeTool"
TARGET_NODE_GROUP_NAME = "MoTextNodeTool"

# TEXT_INPUT_SOCKET_NAME:
#   - Purpose: Defines the name of the input socket within the TARGET_NODE_GROUP_NAME
#     that the addon will use to pass text data (if the user selects 'Text' input type).
#   - Convention: If a template is designed to work with text input, its
#     TARGET_NODE_GROUP_NAME must have an input socket with this exact name.
#     This socket should typically be of type String.
#   - Example: "Input Text"
TEXT_INPUT_SOCKET_NAME = "Input Text"

# OBJECT_INPUT_SOCKET_NAME:
#   - Purpose: Defines the name of the input socket within the TARGET_NODE_GROUP_NAME
#     that the addon will use to pass an existing Blender object (if the user
#     selects 'Object' input type).
#   - Convention: If a template is designed to work with an existing object as input,
#     its TARGET_NODE_GROUP_NAME must have an input socket with this exact name.
#     This socket should typically be of type Object or Geometry.
#   - Example: "Input Object"
OBJECT_INPUT_SOCKET_NAME = "Input Object"


class MOTEXT_OT_apply_template(bpy.types.Operator):
    bl_idname = "motext.apply_template"
    bl_label = "Apply MoText Template"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Check if a template is selected and inputs are valid
        motext_props = context.scene.motext_props
        if not motext_props.template_file:
            return False
        if motext_props.input_type == 'TEXT' and not motext_props.text_input:
            return False
        if motext_props.input_type == 'OBJECT' and not motext_props.object_input:
            return False
        return True

    def execute(self, context):
        motext_props = context.scene.motext_props
        template_blend_path = motext_props.template_file # This is the full path from EnumProperty

        if not os.path.exists(template_blend_path):
            self.report({'ERROR'}, f"Template file not found: {template_blend_path}")
            return {'CANCELLED'}

        # 1. Create a new target object (e.g., an Empty or a Mesh Cube)
        #    For simplicity, let's create an Empty at the cursor
        bpy.ops.object.empty_add(location=context.scene.cursor.location)
        target_object = context.active_object
        target_object.name = "MoText_Output"

        # 2. Append the Node Group from the template .blend file
        try:
            with bpy.data.libraries.load(template_blend_path, link=False) as (data_from, data_to):
                # Check if TARGET_NODE_GROUP_NAME exists in the template file
                if TARGET_NODE_GROUP_NAME in data_from.node_groups:
                    data_to.node_groups = [TARGET_NODE_GROUP_NAME]
                else:
                    self.report({'ERROR'}, f"Node group '{TARGET_NODE_GROUP_NAME}' not found in {os.path.basename(template_blend_path)}")
                    bpy.data.objects.remove(target_object, do_unlink=True) # Clean up created empty
                    return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load template: {str(e)}")
            if target_object and target_object.name == "MoText_Output": # check if it was created
                 bpy.data.objects.remove(target_object, do_unlink=True)
            return {'CANCELLED'}

        appended_node_group = bpy.data.node_groups.get(TARGET_NODE_GROUP_NAME)
        if not appended_node_group:
            self.report({'ERROR'}, f"Failed to append node group '{TARGET_NODE_GROUP_NAME}'.")
            bpy.data.objects.remove(target_object, do_unlink=True)
            return {'CANCELLED'}

        # 3. Add Geometry Nodes modifier to the target object
        gn_modifier = target_object.modifiers.new(name="MoTextEffect", type='NODES')
        gn_modifier.node_group = appended_node_group

        # 4. Set inputs on the Geometry Nodes modifier.
        # This section relies HEAVILY on the naming conventions defined at the top of this file:
        # TARGET_NODE_GROUP_NAME: The name of the Geometry Node group within your .blend template.
        # TEXT_INPUT_SOCKET_NAME: The name of the input socket for text data in that node group.
        # OBJECT_INPUT_SOCKET_NAME: The name of the input socket for object data in that node group.
        
        # Get the inputs from the instanced node group on the modifier.
        node_inputs = gn_modifier.node_group.inputs

        if motext_props.input_type == 'TEXT':
            # Check if the conventional text input socket name exists in the node group.
            if TEXT_INPUT_SOCKET_NAME in node_inputs:
                try:
                    # Assign the user's text to the specified input socket.
                    # Blender's Python API for Geometry Nodes allows direct assignment
                    # to modifier inputs by their socket name (for Blender 3.3+).
                    gn_modifier[TEXT_INPUT_SOCKET_NAME] = motext_props.text_input
                    self.report({'INFO'}, f"Set text input '{TEXT_INPUT_SOCKET_NAME}' to: '{motext_props.text_input}'")
                except Exception as e:
                    # Report error if assignment fails (e.g., type mismatch if the socket isn't a string input).
                    self.report({'WARNING'}, f"Could not set text input socket '{TEXT_INPUT_SOCKET_NAME}': {e}. Verify the socket type in the node group.")
            else:
                # Report warning if the conventional text input socket is not found.
                self.report({'WARNING'}, f"Node group '{appended_node_group.name}' does not have the expected text input socket: '{TEXT_INPUT_SOCKET_NAME}'.")
        
        elif motext_props.input_type == 'OBJECT':
            # Check if the conventional object input socket name exists in the node group.
            if OBJECT_INPUT_SOCKET_NAME in node_inputs:
                try:
                    # Assign the user's selected object to the specified input socket.
                    gn_modifier[OBJECT_INPUT_SOCKET_NAME] = motext_props.object_input
                    self.report({'INFO'}, f"Set object input '{OBJECT_INPUT_SOCKET_NAME}' to: '{motext_props.object_input.name}'")
                except Exception as e:
                    # Report error if assignment fails (e.g., type mismatch if the socket isn't an object/geometry input).
                    self.report({'WARNING'}, f"Could not set object input socket '{OBJECT_INPUT_SOCKET_NAME}': {e}. Verify the socket type in the node group.")
            else:
                # Report warning if the conventional object input socket is not found.
                self.report({'WARNING'}, f"Node group '{appended_node_group.name}' does not have the expected object input socket: '{OBJECT_INPUT_SOCKET_NAME}'.")
        
        self.report({'INFO'}, f"MoText applied using template: {os.path.basename(template_blend_path)}")
        return {'FINISHED'}

class MOTEXT_OT_refresh_templates(bpy.types.Operator):
    """Refresh the list of available MoText templates"""
    bl_idname = "motext.refresh_templates"
    bl_label = "Refresh MoText Templates"
    bl_options = {'REGISTER'} # No undo needed

    def execute(self, context):
        # This simply triggers the update mechanism for the EnumProperty
        # by re-running its items callback.
        # A more robust way might involve a custom property to store the list
        # and updating that, then telling UI to redraw.
        # For EnumProperty, simply accessing it or the panel redrawing might be enough
        # after utils.template_files_list is updated.
        from . import utils # ensure utils is imported
        utils.update_template_list_on_load(force_refresh=True) # Add a force_refresh if needed
        self.report({'INFO'}, "Template list refreshed.")
        # Force UI update if necessary
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'UI':
                            region.tag_redraw()
        return {'FINISHED'}
