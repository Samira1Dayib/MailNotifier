import imaplib
import requests
import email
from email.header import decode_header


EMAIL = "samiradayib1@gmail.com"           
APP_PASSWORD = "my 16 char gmail imap password"  
KEYWORDS = ["interview", "offer", "follow-up", "assessment"]

def connect_inbox():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("inbox")  # open mailbox in read only mode
    return mail
def get_email_body(msg):
    """Extracts and returns the email body as plain text."""
    if msg.is_multipart():
        # walk through the parts to find text/plain
        for part in msg.walk():
            content_type = part.get_content_type()
            content_dispo = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_dispo:
                # decode email body
                body = part.get_payload(decode=True)
                charset = part.get_content_charset()
                if charset:
                    body = body.decode(charset, errors="replace")
                else:
                    body = body.decode(errors="replace")
                return body
    else:

        body = msg.get_payload(decode=True)
        charset = msg.get_content_charset()
        if charset:
            body = body.decode(charset, errors="replace")
        else:
            body = body.decode(errors="replace")
        return body
    return ""  # if no body found



def search_unread_emails(mail):
    status, message_ids = mail.search(None, '(UNSEEN SINCE "10-Apr-2025")')

    if status != "OK":
        print("Error searching mailbox.")
        return []

    matches = []

    for num in message_ids[0].split():
        status, msg_data = mail.fetch(num, "(RFC822)")
        if status != "OK":
            continue

        raw_msg = msg_data[0][1]
        msg = email.message_from_bytes(raw_msg)

        # decode subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        # extract body text
        body = get_email_body(msg)

        # check keywords in subject or body (case-insensitive)
        combined_text = (subject + " " + body).lower()

        for keyword in KEYWORDS:
            if keyword.lower() in combined_text:
                matches.append(subject)
                break  # no need to check other keywords

    return matches

def send_zapier_alert(subjects):
    webhook_url = "https://hooks.zapier.com/hooks/catch/my complete link here"  # replace 

    payload = {
        "count": len(subjects),
        "subjects": "\n".join(f"- {subject}" for subject in subjects)
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("Zapier webhook sent successfully!")
        else:
            print(f"Zapier webhook failed. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending webhook: {e}")

def main():
    print("Checking for important unread emails...")
    try:
        mail = connect_inbox()
        print("Connected to mailbox.")
        matched_subjects = search_unread_emails(mail)

        if matched_subjects:
            print(f"\n Found {len(matched_subjects)} important unread email(s):")
            for subject in matched_subjects:
                print(f" - {subject}")

            send_zapier_alert(matched_subjects)
        else:
            print("No matching unread emails found.")

        mail.logout()
    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    main()
