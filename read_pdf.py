import fitz
doc = fitz.open(r'C:\Users\MADHAV\Downloads\NLP Lab Examination – Guidelines, Deliverables & Assessment Rubrics (2).pdf')
for i, page in enumerate(doc):
    text = page.get_text()
    if text.strip():
        print(f'--- PAGE {i+1} ---')
        # Replace problematic characters
        text = text.replace('\u200b', '').replace('\u2013', '-').replace('\u2014', '--').replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u25cf', '*')
        print(text)
doc.close()