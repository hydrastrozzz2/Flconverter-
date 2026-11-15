import zipfile
import xml.etree.ElementTree as ET
import pyflp
from pyflp import Project

def convert(flp_path, flm_path):
    try:
        try:
            project = pyflp.parse(flp_path)
        except AttributeError:
            project = Project(path=flp_path)
            
        root = ET.Element("FLMProject", version="4")
        
        chans = ET.SubElement(root, "Channels")
        for i, ch in enumerate(project.channels):
            c_name = getattr(ch, 'name', f"Channel {i+1}")
            c_id = getattr(ch, 'id', getattr(ch, 'index', i + 1))
            ET.SubElement(chans, "Channel", name=str(c_name), id=str(c_id))
            
        pats = ET.SubElement(root, "Patterns")
        for i, pat in enumerate(project.patterns):
            p_id = getattr(pat, 'id', getattr(pat, 'index', i + 1))
            p_name = getattr(pat, 'name', f"Pattern {p_id}")
            p = ET.SubElement(pats, "Pattern", name=str(p_name), id=str(p_id))
            notes = ET.SubElement(p, "Notes")
            
            try:
                for note in pat.notes:
                    ET.SubElement(notes, "Note", 
                                  time=str(getattr(note, 'position', getattr(note, 'time', 0))), 
                                  length=str(getattr(note, 'length', 0)), 
                                  pitch=str(getattr(note, 'key', 0)), 
                                  velocity=str(getattr(note, 'velocity', 0)), 
                                  channel=str(getattr(note, 'channel', getattr(note, 'rack_channel', 0))))
            except Exception:
                pass
                
        xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        
        with zipfile.ZipFile(flm_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr("project.xml", xml_str)
            
        return "Success"
    except Exception as e:
        return str(e)
