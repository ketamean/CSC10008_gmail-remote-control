# CSC10008_gmail-remote-control
- Create .venv folder: `python -m venv .venv`
- Activate vir env: `.venv/scripts/activate`
- Install packages: `pip install -r requirements.txt`
- Run: `flask --app client run` (in order to run `client.py` file using `flask`).

## Notes
- Time limit after sending mails: 60s.
- If being exceeded, the session will be coercively terminated
- Message object retrieved from a thread data object `thread["messages"]` with attachments:
- Response
```python
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

## Flow after clicking Send button
- Right after Send button is clicked, loading view "Sending" will be displayed until the mail is successfully sent.
- Afterwards, loading view "Processing" will be displayed within a certain time period. The length of this time period is determined via some of the following criterion:
  - If a valid `[key_logger]` command exists, let $T_0$ be key logger time; otherwise, $T_0 = 0$
  - Time to wait = $T_0$ + 30sec