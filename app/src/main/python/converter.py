import zipfile
import xml.etree.ElementTree as ET
from pyflp import Project

def convert(flp_path, flm_path):
    try:
        project = Project.load(flp_path)
        root = ET.Element("FLMProject", version="4")
        
        chans = ET.SubElement(root, "Channels")
        for i, ch in enumerate(project.channels):
            ET.SubElement(chans, "Channel", name=str(ch.name), id=str(i+1))
            
        pats = ET.SubElement(root, "Patterns")
        for pat in project.patterns:
            p = ET.SubElement(pats, "Pattern", name=pat.name, id=str(pat.id))
            notes = ET.SubElement(p, "Notes")
            try:
                for note in pat.notes:
                    ET.SubElement(notes, "Note", 
                                  time=str(note.position), 
                                  length=str(note.length), 
                                  pitch=str(note.key), 
                                  velocity=str(note.velocity), 
                                  channel=str(note.channel))
            except AttributeError:
                pass
                
        xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        
        with zipfile.ZipFile(flm_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr("project.xml", xml_str)
            
        return "Success"
    except Exception as e:
        return str(e)
