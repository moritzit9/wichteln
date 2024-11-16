import smtplib
from flask import Flask, request, render_template
import random

app = Flask(__name__)
participants = []  # Liste der Teilnehmer mit ihren Präferenzen
max_participants = 8  # Maximale Anzahl von Teilnehmern

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_email():
    if len(participants) >= max_participants:
        return "Anmeldung geschlossen: Maximale Teilnehmerzahl erreicht!", 400

    first_name = request.form['first_name']
    email = request.form['email']
    dislikes = request.form.get('dislikes', '').strip()
    
    if email and email not in [p['email'] for p in participants]:
        participants.append({'first_name': first_name, 'email': email, 'dislikes': dislikes})
        position = len(participants)
        if position == 1:
            return f"Du bist der Erste {position}/{max_participants}."
        elif position == max_participants:
            return f"Du warst der Letzte {position}/{max_participants}."
        else:
            return f"Bereits eingetragen: {position}/{max_participants}."
    return "E-Mail wurde bereits hinzugefügt oder ist ungültig.", 400

@app.route('/assign')
def assign():
    if len(participants) < 2:
        return "Zu wenige Teilnehmer!"
    pairs = assign_secret_santa(participants)
    if pairs is None:
        return "Fehler bei der Zuweisung. Bitte erneut versuchen."
    send_emails(pairs)
    return "Zuweisung abgeschlossen und E-Mails gesendet!"

def assign_secret_santa(participants):
    for _ in range(100):  # Maximal 100 Versuche, eine gültige Zuordnung zu finden
        givers = participants[:]
        receivers = participants[:]
        random.shuffle(receivers)
        
        pairs = {}
        valid = True
        for giver in givers:
            for receiver in receivers:
                if receiver != giver:
                    pairs[giver['email']] = receiver
                    receivers.remove(receiver)
                    break
            else:
                valid = False
                break
        if valid:
            return pairs
    return None  # Keine gültige Zuordnung gefunden

def send_emails(pairs):
    smtp_server = "smtp.example.com"
    smtp_user = "your-email@example.com"
    smtp_password = "your-password"
    sender_email = "your-email@example.com"
    
    with smtplib.SMTP(smtp_server, 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        for giver_email, receiver in pairs.items():
            receiver_name = receiver['first_name']
            receiver_email = receiver['email']
            dislikes = receiver['dislikes'] if receiver['dislikes'] else "Keine speziellen Angaben."
            
            message = f"""\
Subject: Dein Wichtel-Partner

Du schenkst etwas an: {receiver_name} ({receiver_email})
Was die Person nicht mag: {dislikes}
"""
            server.sendmail(sender_email, giver_email, message)

if __name__ == '__main__':
    app.run(debug=True)
