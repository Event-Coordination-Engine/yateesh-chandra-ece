def email_trigger(user_email, body, user_name):
    import smtplib
    from email.mime.text import MIMEText

    sender_email = "ece.operations01@gmail.com"
    sender_password = "qtyl axzc zpcr naix"
    subject = "Yay, Welcome to ECE..!"

    if body == "registration":
        email_body = f"""
        <html>
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <style>
        
        body {{
        margin: 0;
        padding: 0;
        background-color: #f4f4f4;
        font-family: Arial, sans-serif;
        }}

        .email-container {{
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
        background-color: #e7e7e7;
        padding: 20px;
        border-radius: 8px;
        }}

        .header {{
        background-color: #0dff05;
        padding: 20px;
        text-align: center;
        border-radius: 8px 8px 0 0;
        }}

        .header h1 {{
        margin: 0;
        color: #ffffff;
        font-size: 28px;
        }}

        .content {{
        padding: 20px;
        text-align: center;
        }}

        .content h2 {{
        font-size: 24px;
        margin-bottom: 10px;
        color: #333333;
        }}

        .content p {{
        font-size: 16px;
        color: #666666;
        margin-bottom: 20px;
        }}

        .cta-button {{
        display: inline-block;
        padding: 12px 25px;
        background-color: #0090a3;
        color: #ffffff;
        text-decoration: none;
        font-size: 16px;
        border-radius: 5px;
        }}

        .cta-button:hover {{
        background-color: #007a89;
        }}

        .footer {{
        padding: 20px;
        text-align: center;
        font-size: 14px;
        color: #999999;
        }}

        .content img {{
        width: 100%;
        max-width: 400px;
        height: auto;
        margin-bottom: 20px;
        border-radius: 8px;
        }}
        </style>
        </head>
        <body>
        <div class="email-container">
            <div class="header">
                <h1>Welcome to Our Platform!</h1>
            </div>
            <div class="content">
                <img src="https://blog.darwinbox.com/hubfs/Blog%20Image-2.png" alt="Welcome Image">
                <h2>Hi {user_name},</h2>
                <p>We're thrilled to have you on board! You have successfully registered on our platform.</p>
                <p>Start exploring the amazing features we offer.</p>
            </div>
            <div class="footer">
                <p>If you have any questions, feel free to <a href="mailto:support@yourplatform.com">contact us</a>.</p>
                <p>&copy; 2024 Your Platform. All rights reserved.</p>
            </div>
        </div>
        </body>
        </html>
        """

    html_message = MIMEText(email_body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = user_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, html_message.as_string())
