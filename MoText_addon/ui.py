# ui.py
import bpy

class MoTextPanel(bpy.types.Panel):
    bl_label = "MoText"
    bl_idname = "OBJECT_PT_motext_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'MoText' # Tab name in the N-Panel

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        motext_props = scene.motext_props # Get properties from scene

        layout.label(text="Input Source:")
        row = layout.row(align=True)
        row.prop(motext_props, "input_type", expand=True)

        if motext_props.input_type == 'TEXT':
            layout.prop(motext_props, "text_input")
        elif motext_props.input_type == 'OBJECT':
            layout.prop(motext_props, "object_input")
            if not motext_props.object_input:
                layout.label(text="Select a source object.", icon='ERROR')
        
        layout.separator()
        
        layout.label(text="Select Template:")
        layout.prop(motext_props, "template_file", text="") # text="" to use EnumProperty's item names as labels
        if not motext_props.template_file:
             layout.label(text="No 'mograph_*.blend' files found", icon='INFO')
             layout.label(text="Place templates in the same folder as this .blend file.")


        layout.separator()
        
        op_row = layout.row()
        op_row.scale_y = 1.5 # Make button bigger
        op_row.operator(operators.MOTEXT_OT_apply_template.bl_idname, text="Apply MoText", icon='PLAY')

        op_row_refresh = layout.row()
        op_row_refresh.operator(operators.MOTEXT_OT_refresh_templates.bl_idname, text="Refresh Templates", icon='FILE_REFRESH')
