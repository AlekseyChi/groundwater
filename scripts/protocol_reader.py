import os

from docx.api import Document

LABORATORY = 'ООО "ГИЦ ПВ"'
root_path = "examples"
files = os.listdir(root_path)

num_point = 1
num_row = 3
for file in files:
    if file.endswith(".docx"):
        doc = Document(os.path.join(root_path, file))
        data = []
        keys = tuple(cell.text for cell in doc.tables[0].rows[0].cells)
        well = doc.paragraphs[25].text.split(",")[-1].strip("скважина №").replace("x", "")
        date = doc.paragraphs[24].text.split(":")[-1].strip("x ")
        position = ",".join(doc.paragraphs[25].text.split(",")[:-1]).replace("Место отбора пробы: ", "")
        num_prot = f"{LABORATORY}, {doc.paragraphs[18].text} от {doc.paragraphs[19].text}"
        if "Дата отбора" in well:
            well = doc.paragraphs[26].text.split(",")[-1].strip("скважина №")
            date = doc.paragraphs[25].text.split(":")[-1].strip("x ")
            position = ",".join(doc.paragraphs[26].text.split(",")[:-1]).replace("Место отбора пробы: ", "")
            num_prot = f"{LABORATORY}, {doc.paragraphs[19].text} от {doc.paragraphs[20].text}"

        for row in doc.tables[0].rows[1:]:
            parameter = (cell.text for cell in row.cells)
            data = dict(zip(keys, parameter))
            values = float(data["Значение показателя"].replace("<", "").replace(">", "").split("±")[0])
