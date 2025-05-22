# utils.py
import bpy
import os

# --- Global list to store template files, simplifies EnumProperty items callback ---
# This list will be populated by get_template_files_enum_items
# Storing it globally avoids re-scanning the directory every time the UI draws,
# but it needs to be updated when Blender starts or when the user changes the current .blend file's directory.
_template_files_cache = [] 

def get_project_directory():
    """Returns the directory of the currently open .blend file."""
    current_blend_filepath = bpy.data.filepath
    if not current_blend_filepath:
        return None # No .blend file saved/opened
    return os.path.dirname(current_blend_filepath)

def find_mograph_templates(directory):
    """Scans a directory for .blend files prefixed with 'mograph_'."""
    templates = []
    if not directory or not os.path.isdir(directory):
        return templates
        
    for filename in os.listdir(directory):
        if filename.startswith("mograph_") and filename.endswith(".blend"):
            full_path = os.path.join(directory, filename)
            # Clean name for display: remove "mograph_" and ".blend"
            display_name = filename.replace("mograph_", "").replace(".blend", "").replace("_", " ").title()
            templates.append((full_path, display_name, f"Uses template: {filename}"))
    return templates

def get_template_files_enum_items(self, context):
    """
    Callback for the EnumProperty to list template files.
    Uses the _template_files_cache.
    """
    global _template_files_cache
    
    # Check if the cache is valid or needs updating
    # A simple check could be if the project directory changed,
    # but for dynamic updates, a manual refresh button is better.
    # The `update_template_list_on_load` function handles initial population.
    
    if not _template_files_cache: # If cache is empty, try to populate it
        update_template_list_on_load()

    if not _template_files_cache:
         return [("NONE", "No Templates Found", "Place 'mograph_*.blend' files in project dir")]

    enum_items = []
    for full_path, display_name, description in _template_files_cache:
        # EnumProperty item: (identifier, name, description, icon, number)
        enum_items.append((full_path, display_name, description))
    return enum_items

def update_template_list_on_load(force_refresh=False):
    """
    Updates the global _template_files_cache.
    Call this on addon registration and potentially via a refresh button.
    """
    global _template_files_cache
    # TODO: Add logic to check if project directory changed if not force_refresh
    # For now, always refreshes if called.
    
    project_dir = get_project_directory()
    if project_dir:
        print(f"MoText: Scanning for templates in {project_dir}")
        _template_files_cache = find_mograph_templates(project_dir)
        if not _template_files_cache:
            print("MoText: No 'mograph_*.blend' template files found.")
        else:
            print(f"MoText: Found {_template_files_cache.__len__()} templates.")
    else:
        _template_files_cache = []
        print("MoText: Current .blend file is not saved. Cannot find templates.")


# --- Handler to update template list when a new .blend file is loaded or saved ---
# This ensures the template list is relevant to the current project's directory.
@bpy.app.handlers.load_post
@bpy.app.handlers.save_post
def on_blend_file_changed(dummy):
    print("MoText: Blender file loaded/saved. Refreshing template list.")
    update_template_list_on_load(force_refresh=True) # Force refresh of cache

# Make sure to register these handlers in your main register() function
# and unregister them in unregister()
# In __init__.py:
# def register():
# ...
#   bpy.app.handlers.load_post.append(on_blend_file_changed)
#   bpy.app.handlers.save_post.append(on_blend_file_changed)
# ...
# def unregister():
# ...
#   bpy.app.handlers.load_post.remove(on_blend_file_changed)
#   bpy.app.handlers.save_post.remove(on_blend_file_changed)
# ...
