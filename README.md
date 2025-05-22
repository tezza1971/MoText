# MoText Blender Addon

MoText is a Blender addon designed to simplify the application of pre-configured Geometry Node setups (templates) to text objects or existing scene objects. It allows users to quickly create interesting motion graphics and object effects by selecting a template from a list.

## Features

*   Apply complex Geometry Node effects with a few clicks.
*   Supports text input directly within the addon panel.
*   Supports using existing scene objects as input for Geometry Node effects.
*   Dynamically scans a designated directory for compatible `.blend` templates.
*   Easy-to-use interface in the 3D View's N-Panel.
*   Refresh button to update the list of available templates.

## Installation

1.  Download the `MoText_addon` folder (or the entire repository as a ZIP and extract it).
2.  In Blender, go to `Edit > Preferences > Add-ons`.
3.  Click `Install...` and navigate to the directory where you saved the `MoText_addon` folder.
4.  Select the `MoText_addon` folder (or `__init__.py` within it if Blender requires a specific file). If you downloaded a ZIP, you might be able to install it directly.
5.  Enable the "Object: MoText" addon by checking the box next to its name.

The MoText panel will then be available in the 3D View Sidebar (press 'N' to open) under the "MoText" tab.

## Usage

1.  Open the 3D View Sidebar (N-Panel) and select the "MoText" tab.
2.  **Choose Input Type**:
    *   **Text**: Select this to generate an effect based on new text.
        *   **Text**: Enter the desired text in the input field.
    *   **Object**: Select this to apply an effect to an existing object.
        *   **Source Object**: Pick an object from your scene using the eyedropper or dropdown.
3.  **Select Template**:
    *   Choose a template from the "Template" dropdown menu. Templates are `.blend` files prefixed with `mograph_` located in the same directory as your currently saved Blender project file.
    *   If you add new templates to the directory while Blender is open, click the "Refresh Templates" button to update the list.
4.  **Apply Template**:
    *   Click the "Apply MoText Template" button.
    *   This will create a new Empty object named "MoText\_Output" (or similar) at the 3D cursor's location. This object will have a Geometry Nodes modifier containing the setup from the selected template, applied to your chosen text or object.

## Creating MoText Templates

To create your own `.blend` files that are compatible with the MoText addon, follow these requirements:

1.  **File Format**: Templates must be standard Blender `.blend` files.
2.  **Filename Prefix**: Template filenames **must** be prefixed with `mograph_`. For example, `mograph_my_cool_effect.blend`.
3.  **Location**: Template files **must** be placed in the same directory as your active (saved) main Blender project file. The addon scans this directory for templates.
4.  **Target Node Group**:
    *   Each template `.blend` file **must** contain a Geometry Node group named exactly `MoTextNodeTool`. This is the specific node group the addon will append and use.
5.  **Input Sockets in "MoTextNodeTool"**:
    *   The `MoTextNodeTool` group must have appropriately named input sockets for the addon to connect to, based on what your template is designed to process:
        *   For **Text Input**: If your template processes text, it needs an input socket named exactly `Input Text`. This socket should ideally be of type `String` in your Geometry Node group interface.
        *   For **Object Input**: If your template processes an existing Blender object, it needs an input socket named exactly `Input Object`. This socket should ideally be of type `Object` or `Geometry` in your Geometry Node group interface.
    *   Your node group can have other inputs, but these specific names are used by the addon to pass the primary data.
6.  **Scene Elements (Lighting, Camera)**:
    *   The MoText addon primarily focuses on applying the Geometry Node setup from the `MoTextNodeTool` group to a target object.
    *   If your template effect is intended to be a self-contained scene with specific lighting and camera setups, you should include these elements within the template `.blend` file. They can be part of the `MoTextNodeTool` (if appropriate for your node setup) or as separate objects in the template file that users would manually append or link if needed. The addon itself does not automatically handle scene-level elements beyond the Geometry Nodes modifier.

**Example Workflow for a Text Template:**

1.  Create a new `.blend` file.
2.  Go to the Geometry Nodes workspace.
3.  Create a new Geometry Node setup on any object (e.g., the default Cube).
4.  Design your node tree. Ensure it has an input socket for text (e.g., a "String" input node connected to a "String to Curves" node).
5.  In the "Group" tab of the Geometry Nodes editor (N-panel), name this input socket `Input Text`.
6.  Name the entire Geometry Node group `MoTextNodeTool`.
7.  Save the `.blend` file as `mograph_my_text_effect.blend` in the same directory as the project you'll be using the addon with.

## Author

Terence Kearns (with AI assistance)
