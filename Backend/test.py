import smtplib
from email.mime.text import MIMEText

sender_email = "ece.operations01@gmail.com"
sender_password = "qtyl axzc zpcr naix"
recipient_email = "yateed1437@gmail.com"
subject = "Hello from Python"
body = """
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Palmplate</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .palmplate {
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            padding: 20px;
            text-align: center;
        }
        .palmplate img {
            border-radius: 50%;
            width: 100px;
            height: 100px;
            object-fit: cover;
        }
        .palmplate h1 {
            font-size: 24px;
            margin: 10px 0;
        }
        .palmplate p {
            color: #777777;
            font-size: 16px;
            margin: 5px 0;
        }
        .palmplate button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            border-radius: 5px;
            margin-top: 15px;
            cursor: pointer;
        }
        .palmplate button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="palmplate">
        <img src="https://via.placeholder.com/100" alt="Profile Picture">
        <h1>John Doe</h1>
        <p>Event Coordinator</p>
        <p>john.doe@example.com</p>
        <button>Contact</button>
    </div>
</body>
</html>
"""
html_message = MIMEText(body, 'html')
html_message['Subject'] = subject
html_message['From'] = sender_email
html_message['To'] = recipient_email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
   server.login(sender_email, sender_password)
   server.sendmail(sender_email, recipient_email, html_message.as_string())