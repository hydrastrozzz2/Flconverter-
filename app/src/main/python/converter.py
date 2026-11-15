import zipfile
import xml.etree.ElementTree as ET
import pyflp
from pyflp import Project

def convert(flp_path, flm_path):
    try:
        # Parse the FLP file using the updated pyflp API
        try:
            project = pyflp.parse(flp_path)
        except AttributeError:
            # Fallback for older versions
            project = Project(path=flp_path)
            
        # Build the FLM XML structure
        root = ET.Element("FLMProject", version="4")
        
        chans = ET.SubElement(root, "Channels")
        for i, ch in enumerate(project.channels):
            # Safe access to channel name
            c_name = getattr(ch, 'name', f"Channel {i+1}")
            ET.SubElement(chans, "Channel", name=str(c_name), id=str(i+1))
            
        pats = ET.SubElement(root, "Patterns")
        for pat in project.patterns:
            p_name = getattr(pat, 'name', f"Pattern {pat.id}")
            p = ET.SubElement(pats, "Pattern", name=str(p_name), id=str(pat.id))
            notes = ET.SubElement(p, "Notes")
            try:
                for note in pat.notes:
                    # Safe access to note attributes
                    ET.SubElement(notes, "Note", 
                                  time=str(getattr(note, 'position', 0)), 
                                  length=str(getattr(note, 'length', 0)), 
                                  pitch=str(getattr(note, 'key', 0)), 
                                  velocity=str(getattr(note, 'velocity', 0)), 
                                  channel=str(getattr(note, 'channel', 0)))
            except Exception:
                pass
                
        xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        
        # Save as .flm ZIP
        with zipfile.ZipFile(flm_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr("project.xml", xml_str)
            
        return "Success"
    except Exception as e:
        return str(e)
