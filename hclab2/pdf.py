import os
from PyPDF2 import PdfFileReader, PdfFileWriter

def encrypt(file:str,pswd:str,dest:str=''):

    if pswd == '':
        pswd = 'M3na12345'

    if dest == '':
        dest = os.path.join(os.path.dirname(file),'encrypt')
   
    with open(file, "rb") as in_file:
        input_pdf = PdfFileReader(in_file)
        
        output_pdf = PdfFileWriter()
        output_pdf.appendPagesFromReader(input_pdf)
        
        output_pdf.encrypt(pswd,'M3na12345')

        encrypted_pdf = os.path.join(dest,os.path.basename(file))
        with open(encrypted_pdf, 'wb') as out_file:
                output_pdf.write(out_file)
    
    return encrypted_pdf
