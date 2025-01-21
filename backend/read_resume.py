from pypdf import PdfReader


def read_file(file):
    reader = PdfReader(file)

    fulltext = ""

    for p in reader.pages:
        fulltext += p.extract_text()
    
    return fulltext

if __name__ == "__main__":
    print("lets go")
    with open("C:/Users/Owner/Desktop/新しいフォルダー/files/resume.pdf","rb") as file:
        resume_text = read_file(file)
        print(resume_text)