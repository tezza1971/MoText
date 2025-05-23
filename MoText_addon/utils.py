# utils.py
import bpy
import os

_template_files_cache = []

def get_blend_filepath():
    """
    Factory method to safely get the current .blend filepath.
    Returns None if no file is loaded or if bpy.data is not properly initialized.
    """
    try:
        return bpy.data.filepath if hasattr(bpy.data, 'filepath') else None
    except (AttributeError, TypeError):
        return None

def get_project_directory():
    """Returns the directory of the currently open .blend file."""
    current_blend_filepath = get_blend_filepath()
    if not current_blend_filepath:
        return None  # No .blend file saved/opened
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
    
    if not _template_files_cache:
        # Do NOT call update_template_list_on_load() here.
        # Return a placeholder if the cache is empty.
        # The cache will be populated by file load/save handlers or the refresh button.
        return [("NONE", "No Templates Loaded", "Save your .blend file and click 'Refresh Templates', or load a project.")]

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
def on_blend_file_changed(dummy):
    print("MoText: Blender file loaded/saved. Refreshing template list.")
    update_template_list_on_load(force_refresh=True) # Force refresh of cache
    # This will be called when a new .blend file is loaded or saved.
# Register the handler
bpy.app.handlers.load_post.append(on_blend_file_changed)
# Register the handler
bpy.app.handlers.save_post.append(on_blend_file_changed)
# This will be called when a new .blend file is saved.
# Note: You may want to unregister these handlers when the addon is disabled.
# Unregister the handlers when the addon is disabled
def unregister_handlers():
    if on_blend_file_changed in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_blend_file_changed)
    if on_blend_file_changed in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(on_blend_file_changed)
# Call this function when the addon is disabled to clean up.
