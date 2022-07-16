import smtplib 
import os 
from dataclasses import dataclass
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

from email.mime.multipart import MIMEMultipart
from PyPDF2 import PdfFileReader, PdfFileWriter

@dataclass
class Mailer:
  
  email:str
  password:str
  name:str
  host:str
  port:str


  def encrypt_attachment(self, pdf:str, filename:str, password="M3na12345")->str:
    """
    Encrypt email attachment
    """

    with open(pdf, "rb") as file:
      reader = PdfFileReader(file)
      writer = PdfFileWriter()
      writer.appendPagesFromReader(reader)

      writer.encrypt(password, owner_pwd='M3na12345')

      encrypted_pdf = os.path.join(os.path.dirname(pdf),"encrypt",filename + ".pdf")

      with open(encrypted_pdf, 'wb') as output:
        writer.write(output)
    
    return encrypted_pdf


  def send(self, to:str, subject:str, attachment:str=""):
    """Send email"""
    
    # setup mail header
    message = MIMEMultipart()
    message["From"] = self.email
    message["To"] = to.lower()
    message["Cc"] = self.email
    message["Subject"] = subject

    # setup mail body
    with open(os.path.join(os.path.dirname(__file__),"body.html"),"r") as f:
      body = f.read()
    message.attach(MIMEText(body, "html"))

    # assign file name here
    filename = os.path.splitext(os.path.basename(attachment))[0]

    # check whether email attachment available
    if attachment != "":

      payload = MIMEBase("application","octet-stream")
      payload.set_payload(open(attachment,"rb").read())

      encoders.encode_base64(payload)
      payload.add_header("Content-Disposition",f"attachment; filename={filename}")
      message.attach(payload)

    # warped email message & attachment
    content = message.as_string()

    # send email
    print(self.email)
    print(to)
    try:
      server = smtplib.SMTP(self.host,self.port)
      server.starttls()
      server.login(self.email,self.password)
      server.send_message(from_addr=self.email, to_addrs=to, msg=content)
    except smtplib.SMTPResponseException as e:
      raise Exception(e)