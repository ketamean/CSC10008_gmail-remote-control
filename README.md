## How to use?
1. Choose an empty folder on your device, right-click a choose Open in Terminal.
2. Paste this to terminal:
    ```
    git clone https://github.com/ketamean/CSC10008_gmail-remote-control.git
    ```
3. Double click `init.cmd` to invoke the innitial process.
4. Open the folder
5. ..... to be continued
- Run `init.cmd` to automatically initialize virtual environment and install all essential packages
- Run `run.cmd` to run the client-side application
- Open the given link on your web browser (or Ctrl + click on the link) to open the app.

## Instruction
- Use can use the app either anonymously or not
- If you use the app anonymously, you will be ***prohibited*** from invoking some of the following commands:
  - Shut down server.
  - Log out server.
  - Start an application on server.
  - Close an application on server.
- If you log in with your gmail before using the app, please note that:
  - We ***do not collect your password*** as we use gmail api for authentication and authorization. Moreover, we only read mails that match our specialized keyword ("PCRC") and do not access to others.
  - You need to register first (click on *Register* button). You can skip this step if you have done it before. After that, you can use it normally with full accessibility to all the commands.

## FYI
### A message object
```py
{
    'id': '18c218f77a3e3d06',
    'threadId': '18c218f77a3e3d06',
    'labelIds': ['UNREAD', 'SENT', 'INBOX'],
    'snippet': '[screen_capture]',
    'payload':
        {
            'partId': '',
            'mimeType': 'multipart/alternative',
            'filename': '',
            'headers': [
                {'name': 'Received', 'value': 'from 275361750661 named unknown by gmailapi.google.com with HTTPREST; Thu, 30 Nov 2023 12:48:19 -0600'},
                {'name': 'Content-Type', 'value': 'multipart/alternative; boundary="===============3918266203360981644=="'},
                {'name': 'MIME-Version', 'value': '1.0'},
                {'name': 'To', 'value': 'chiemthoica@gmail.com'},
                {'name': 'From', 'value': 'chiemthoica@gmail.com'},
                {'name': 'Subject', 'value': 'PCRC'},
                {'name': 'Date', 'value': 'Thu, 30 Nov 2023 12:48:19 -0600'},
                {'name': 'Message-Id', 'value': '<CANDETt=R3sZWpco9KMafrRdxQgyVTPLksP9uBCS-HpHs4zt=ew@mail.gmail.com>'}
            ],
            'body': {'size': 0},
            'parts': [
                {
                    'partId': '0', 'mimeType': 'text/plain', 'filename': '',
                    'headers': [
                        {'name': 'Content-Type', 'value': 'text/plain; charset="us-ascii"'},
                        {'name': 'MIME-Version', 'value': '1.0'}, {'name': 'Content-Transfer-Encoding', 'value': '7bit'}
                    ],
                    'body': {'size': 16, 'data': 'W3NjcmVlbl9jYXB0dXJlXQ=='}
                },
                {
                    'partId': '1', 'mimeType': 'application/octet-stream', 'filename': 'graph.png',
                    'headers': [
                        {'name': 'Content-Type', 'value': 'application/octet-stream; Name="graph.png"'},
                        {'name': 'MIME-Version', 'value': '1.0'},
                        {'name': 'Content-Transfer-Encoding', 'value': 'base64'},
                        {'name': 'Content-Disposition', 'value': 'attachment; filename="graph.png"'}
                    ],
                    'body': {'attachmentId': 'ANGjdJ_iokCVRR3TbOzt3_DvC4coujmzTRXVKSbsXf__A09Vq3WHop97bUomf4nmEi0o8n9nv69EiMNlrNhayR1vg9C-RSNaBvguoTH_Q5YZud9w1m-Pz7TEURfCo2YpJ0ZDMrqwmHh-UoAHqGVL7D6W54DjEJZNmCBRhVtl-uWa3xat-BCq9Mrnih7YN0rXL-nOWi70IURLAw8wKXMmZjaXMMen0_fex7PqFbU2SqcHXuDvFJAhhozVtcR7Tf2_femcZeoMKI94rFgSW2D9fWxQVLIWNzzm9b8gQufrU3eJhbnI-P3Wxwm6mE_eEz0h0xisrdm__h1FSOF3GBtBlmpabqvCVkDFVo-jr79MjtCS9xa5i-N5-H1Vc4wXM3n78kOCCjn8goM-DyGSwRV2', 'size': 27383}
                }
            ]
        },
    'sizeEstimate': 615,
    'historyId': '48182',
    'internalDate': '1701370099000'
}
```