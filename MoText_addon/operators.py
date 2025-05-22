# operators.py
import bpy
import os

# --- Convention for Node Groups in Template Files ---
# It's CRUCIAL that your mograph_*.blend files have a Geometry Node group
# with a consistent name that this addon can target.
TARGET_NODE_GROUP_NAME = "MoTextNodeTool" # e.g., the main GN group in your templates

# Also, this node group needs specific input names the addon can set:
TEXT_INPUT_SOCKET_NAME = "Input Text"       # For string input
OBJECT_INPUT_SOCKET_NAME = "Input Object" # For geometry/object input


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

        # 4. Set inputs on the Geometry Nodes modifier
        # This relies on the convention that your template node groups have specific input names.
        
        # Check if inputs exist before trying to set them
        node_inputs = gn_modifier.node_group.inputs

        if motext_props.input_type == 'TEXT':
            if TEXT_INPUT_SOCKET_NAME in node_inputs:
                # For Blender 3.x, direct assignment might work if input type is string
                # For some versions/types, you might need to assign to the default_value of the socket
                # on the node_group itself before assigning the group, or ensure type matching.
                # This is often the trickiest part with GN via Python.
                try:
                    # Blender 3.3+ way:
                    gn_modifier[TEXT_INPUT_SOCKET_NAME] = motext_props.text_input
                    self.report({'INFO'}, f"Set text input to: '{motext_props.text_input}'")
                except Exception as e:
                    self.report({'WARNING'}, f"Could not set text input '{TEXT_INPUT_SOCKET_NAME}': {e}. Check node group input type.")
            else:
                self.report({'WARNING'}, f"Node group missing text input: '{TEXT_INPUT_SOCKET_NAME}'")
        
        elif motext_props.input_type == 'OBJECT':
            if OBJECT_INPUT_SOCKET_NAME in node_inputs:
                try:
                    gn_modifier[OBJECT_INPUT_SOCKET_NAME] = motext_props.object_input
                    self.report({'INFO'}, f"Set object input to: '{motext_props.object_input.name}'")
                except Exception as e:
                    self.report({'WARNING'}, f"Could not set object input '{OBJECT_INPUT_SOCKET_NAME}': {e}. Check node group input type.")
            else:
                self.report({'WARNING'}, f"Node group missing object input: '{OBJECT_INPUT_SOCKET_NAME}'")
        
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
