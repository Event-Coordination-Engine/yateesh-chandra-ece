from fastapi import Request, HTTPException
from datetime import datetime
from http import HTTPStatus
from model import Api_Audit

def log_api(db, request: Request, response_code: int, message: str):
    status_message = HTTPStatus(response_code).phrase  # Get the standard message for the status code
    api_obj = Api_Audit(api_method = request.method, 
                    api_endpoint = request.url.path,
                    status_code = str(response_code) + " " + status_message,
                    response_message = message,
                    operation_timestamp = datetime.now())
    db.add(api_obj)
    db.commit()
    return {"message" : "log added"}

def raise_validation_error(db, request, message: str):
    log_api(db, request, 400, message)
    raise HTTPException(status_code=400, detail=message)

def unauthorised_access(db, request, message: str):
    log_api(db, request, 401, message)
    raise HTTPException(status_code=401, detail=message)

def email_trigger(subject, body, user_email):
    import smtplib
    from email.mime.text import MIMEText

    sender_email = "ece.operations01@gmail.com"
    sender_password = "qtyl axzc zpcr naix"

    html_message = MIMEText(body, 'html')
    html_message['Subject'] = subject
    html_message['From'] = sender_email
    html_message['To'] = user_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, user_email, html_message.as_string())

def registration_email(user_email, user_name):
    subject = "Yay, Welcome to ECE..!"
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
    email_trigger(subject, email_body, user_email)

def approval_email(user_name, event_name, date, time, location, description, user_email):
    subject = "Congratulations! Your Event Has Been Approved!"
    body = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background-color: #f9f9f9;
                    margin: 0;
                    padding: 0;
                }}
                .email-container {{
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
                    animation: slide-in 0.6s ease-out;
                    border-top: 5px solid #ffc107;
                }}
                @keyframes slide-in {{
                    from {{
                    opacity: 0;
                    transform: translateY(20px);
                    }}
                    to {{
                    opacity: 1;
                    transform: translateY(0);
                    }}
                }}
                .header {{
                    background: linear-gradient(135deg, #6a11cb, #2575fc);
                    padding: 20px;
                    text-align: center;
                    color: #ffffff;
                    border-radius: 12px 12px 0 0;
                }}
                .header img {{
                    width: 120px;
                    margin: 0 auto 15px;
                    display: block;
                    border-radius: 50%;
                }}
                .header h1 {{
                    font-size: 28px;
                    margin: 0;
                    font-weight: bold;
                    color: #ffd700;
                }}
                .content {{
                    padding: 20px;
                    text-align: left;
                    color: #333333;
                }}
                .content h2 {{
                    font-size: 24px;
                    color: #2575fc;
                    margin-bottom: 10px;
                }}
                .content p {{
                    font-size: 16px;
                    line-height: 1.8;
                    margin-bottom: 20px;
                    color: #555555;
                }}
                .content table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    background-color: #f3f4f6;
                    border-radius: 8px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                }}
                table, th, td {{
                    border: none;
                }}
                th, td {{
                    padding: 15px;
                    text-align: left;
                    font-size: 16px;
                    color: #333333;
                    border-bottom: 1px solid #e0e0e0;
                }}
                th {{
                    background-color: #ffc107;
                    color: #ffffff;
                }}
                td {{
                    background-color: #ffffff;
                }}
                .content .cta {{
                    text-align: center;
                    margin-top: 20px;
                }}
                .cta-button {{
                    background-color: #2575fc;
                    color: #ffffff;
                    padding: 15px 40px;
                    text-decoration: none;
                    border-radius: 50px;
                    font-size: 16px;
                    font-weight: bold;
                    display: inline-block;
                    transition: background 0.3s ease;
                }}
                .cta-button:hover {{
                    background-color: #6a11cb;
                }}
                .footer {{
                    background-color: #f3f4f6;
                    padding: 20px;
                    text-align: center;
                    font-size: 14px;
                    color: #999999;
                    border-top: 2px solid #ffc107;
                }}
                .footer a {{
                    color: #2575fc;
                    text-decoration: none;
                }}
                </style>
            </head>
            <body>
                <div class="email-container">
                <div class="header">
                    <img src="https://static.vecteezy.com/system/resources/previews/004/686/638/non_2x/approve-stickman-businessman-was-approved-and-very-happy-hand-drawn-outline-cartoon-illustration-free-vector.jpg" alt="Event Approved">
                    <h1>Event Approved!</h1>
                </div>

                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>We are excited to inform you that your event has been successfully approved by the admin! Below are the details of your approved event:</p>
                    <table>
                    <tr>
                        <th>Event Name</th>
                        <td>{event_name}</td>
                    </tr>
                    <tr>
                        <th>Date</th>
                        <td>{date}</td>
                    </tr>
                    <tr>
                        <th>Time</th>
                        <td>{time}</td>
                    </tr>
                    <tr>
                        <th>Location</th>
                        <td>{location}</td>
                    </tr>
                    <tr>
                        <th>Description</th>
                        <td>{description}</td>
                    </tr>
                    </table>

                    <p>You can now start promoting and preparing for your event. If you need any further assistance, feel free to reach out to us at any time!</p>
                </div>

                <div class="footer">
                    <p>Questions? <a href="mailto:ece.operations01@gmail.com">Contact Support</a></p>
                    <p>&copy; 2024 Your Event Platform. All rights reserved.</p>
                </div>
                </div>
            </body>
            </html>
            """
    email_trigger(subject, body, user_email)