import zipfile
import xml.etree.ElementTree as ET
import os

docx_path = r"c:\Users\Shravan\OneDrive\Desktop\arun\Internship Report Keerthi & Irfan.docx"
output_path = r"c:\Users\Shravan\OneDrive\Desktop\arun\report_text.txt"

def extract_text_from_docx(docx_file):
    try:
        with zipfile.ZipFile(docx_file) as docx:
            # Check files in zip
            file_list = docx.namelist()
            print("Files inside docx zip:", len(file_list))
            
            # Read document.xml
            xml_content = docx.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # Namespace map
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            paragraphs = []
            for p in root.findall('.//w:p', ns):
                texts = [t.text for t in p.findall('.//w:t', ns) if t.text]
                if texts:
                    paragraphs.append(''.join(texts))
            
            return '\n'.join(paragraphs)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(f"Extracting from {docx_path}...")
    if os.path.exists(docx_path):
        text = extract_text_from_docx(docx_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Extraction complete! Extracted {len(text)} characters to {output_path}")
    else:
        print("Docx file not found!")
