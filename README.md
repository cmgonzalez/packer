README for Packer Tool
Overview
Packer is a Python tool designed for creating ZX Spectrum tap packs with a Basic menu. It enables users to bundle multiple .tap files into a single file with a custom menu for easier navigation and execution on a ZX Spectrum emulator or actual hardware.

Features
Create a single .tap file from multiple source .tap files.
Generate a Basic menu for the pack with a customizable title and program name.
Set various display attributes for the menu, like border, paper, and ink colors.
Requirements
Python 3.x
Basic understanding of ZX Spectrum .tap file structure and attributes.
Installation
Ensure Python 3.x is installed on your system.
Download the Packer.py script to your desired directory.
Usage
Run the script from the command line, providing the necessary arguments:

bash
Copy code
python Packer.py [path] [tap] [title] [program] [paper] [ink] [border] [sel_paper] [sel_ink] [title_paper] [title_ink]
Arguments
path: Path to the source .tap files.
tap: Name for the output .tap file.
title: Title for the Basic Menu.
program: Name of the Basic Menu program.
paper: Background color of the menu.
ink: Text color of the menu.
border: Border color of the menu.
sel_paper: Background color for selected menu item.
sel_ink: Text color for selected menu item.
title_paper: Background color for the menu title.
title_ink: Text color for the menu title.
Colors
Colors are specified as numbers ranging from 0 to 7, representing standard ZX Spectrum color codes.

Script Functions
create_header_block: Generates the header block for a tap file.
create_data_block: Creates a data block for the tap file.
create_tap_data_block: Generates the full tap data block, including length and data.
create_tap_header_block: Assembles the full tap header block.
Additional Information
Refer to the ZX Spectrum TAP format for details on the tap file structure and attributes.

Version
This documentation corresponds to Packer version 0.3.

License
Packer is distributed under a Copyleft license.

Author
Cristian Gonzalez

Disclaimer
This tool is provided "as is", with no warranty expressed or implied. The user assumes all responsibility for its use.
