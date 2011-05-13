# allows to send email to a list of people with attachments
# and inline/embedded image

import os
import re
import smtplib
import mimetypes
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Encoders import encode_base64
from getpass import getpass

NAME = 0
EMAIL = 1

def getNamesEmails():
    h = []
    f = open('namesEmails.csv', 'r')
    for line in f:
        name, email = line.split(',')
        h.append((name, email.strip()))

    return h


def getText():
    text = ''

    f = open('text.txt')
    for l in f:
        text += l
    return text


def sendMails(h, text):
    gotError = False
    p = re.compile('^.*@.*$')
    gmailUser = raw_input("What's your full email or user name (default is @movein.to)? ")
    m = p.search(gmailUser)
    if m:
        gmailUser = gmailUser
    else:
        gmailUser += '@movein.to'

    print gmailUser

    gmailPassword = getpass()
    recipient = ''
    subject = raw_input("Please enter the subject line: ")
    greeting = raw_input("Please enter your greeting (e.g. Dear, Hi,...): ")
    fromStr = raw_input("Please enter your name: ")
    attachmentDirPath = raw_input("Please directory with files to attach: ")

    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)

    for t in h:
        personal_text = greeting + " " + t[NAME] + ",\n"
        personal_text += text + "\n"
        recipient = t[EMAIL]
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['To'] = recipient
        msg['From'] = fromStr
        msg.attach(MIMEText(personal_text))
	getAttachments(msg,attachmentDirPath)
        try:
            mailServer.sendmail(gmailUser, recipient, msg.as_string())
            print('Sent email to %s at %s' % (t[NAME],recipient))
        except Exception, e:
            gotError = True
            print '\nIf you read this then email me the text below!\n'
            print e


    mailServer.close()
    print("Done!\n")
    if gotError:
        print 'Some error(s) occured. Please see the text generated above!\n'

def getAttachments(msg,attachmentDirPath):
    #default to current directory
    if not attachmentDirPath:
        attachmentDirPath = '.'

    for filename in os.listdir(attachmentDirPath):
        path = os.path.join(attachmentDirPath, filename)
        if not os.path.isfile(path):
            continue

        contentType, encoding = mimetypes.guess_type(path)
        if contentType is None or encoding is not None:
            contentType = 'application/octet-stream'
        mainType, subType = contentType.split('/', 1)

        fp = open(path, 'rb')

        if mainType == 'text':
            attachment = MIMEText(fp.read())
        elif mainType == 'image':
            attachment = MIMEImage(fp.read(),_subType=subType)
        elif mainType == 'audio':
            attachment = MIMEAudio(fp.read(),_subType=subType)
        else:
            attachment = MIMEBase(mainType, subType)
            attachment.set_payload(fp.read())
            encode_base64(attachment)
            fp.close()

        attachment.add_header('Content-Disposition', 'attachment', 
                                  filename=os.path.basename(path))
        msg.attach(attachment)

if __name__ == "__main__":
    print "Please make sure there is 'namesEmails.csv' and 'text.txt' fps in the script folder before proceeding."
    print "CSV file format must be 'name, email_address' per line. [Press Enter to Continue]"
    raw_input()
    text = getText()
    namesEmails = getNamesEmails()
    sendMails(namesEmails, text)
