from app.database import SessionLocal
from app.models import FraudCase


NEW_FRAUDS = [
    {
        "name": "Phishing Scam",
        "category": "Cyber Fraud",
        "keywords": "phishing, fake link, suspicious link, login, password, bank account",
        "description": "A scam where criminals use fake websites, messages, emails, or links to steal sensitive information.",
        "how_it_happens": "The victim receives a fake message or link that looks like it belongs to a bank, company, or government service. The victim is asked to enter login details, passwords, card information, or other sensitive data.",
        "warning_signs": "Unknown links, urgent messages, fake websites, requests for passwords or banking information.",
        "prevention": "Do not open suspicious links. Verify the website address and never share passwords or banking credentials.",
        "what_to_do": "Stop interacting with the sender, change compromised passwords, contact the concerned bank or service provider, and report the incident.",
        "risk_level": "High",
        "active": True
    },
    {
        "name": "Remote Access Scam",
        "category": "Cyber Fraud",
        "keywords": "remote access, screen sharing, AnyDesk, TeamViewer, app install, bank account, OTP",
        "description": "A scam where criminals convince victims to install remote-access software and then control or observe their device.",
        "how_it_happens": "The scammer pretends to be customer support or a service representative and asks the victim to install a remote-access application.",
        "warning_signs": "Requests to install remote-access apps, screen sharing requests, requests to reveal OTP or banking information.",
        "prevention": "Never install remote-access applications at the request of unknown callers and never share OTPs or banking credentials.",
        "what_to_do": "Immediately disconnect the remote session, uninstall suspicious software, contact your bank if financial information was exposed, and report the incident.",
        "risk_level": "Critical",
        "active": True
    },
    {
        "name": "Courier/Parcel Scam",
        "category": "Cyber Fraud",
        "keywords": "courier, parcel, package, customs, police, illegal parcel, arrest, payment",
        "description": "A scam in which criminals falsely claim that a parcel linked to the victim contains illegal or suspicious items.",
        "how_it_happens": "The victim receives a call claiming that a courier or parcel is associated with illegal activity. The scammer may impersonate police, customs, or courier officials and demand money.",
        "warning_signs": "Unexpected parcel calls, threats of arrest, fake police or customs officials, demands for immediate payment.",
        "prevention": "Verify courier information independently and never transfer money because of threats made during an unexpected call.",
        "what_to_do": "Disconnect the call, preserve messages and caller information, verify the parcel through the official courier channel, and report suspected fraud.",
        "risk_level": "High",
        "active": True
    },
    {
        "name": "Electricity Bill Scam",
        "category": "Cyber Fraud",
        "keywords": "electricity bill, power cut, electricity department, bill payment, payment, UPI, link",
        "description": "A scam where criminals pretend to be electricity department employees and threaten disconnection unless an immediate payment is made.",
        "how_it_happens": "The victim receives an SMS or call claiming that their electricity bill is unpaid and that the connection will be disconnected. A payment link or UPI request is then provided.",
        "warning_signs": "Urgent payment demands, threats of immediate power disconnection, unknown payment links, requests for UPI payment.",
        "prevention": "Check electricity bills only through the official electricity provider's website or application and avoid unknown payment links.",
        "what_to_do": "Do not make the requested payment, verify the bill through the official electricity provider, and report the suspicious message or call.",
        "risk_level": "High",
        "active": True
    },
    {
        "name": "SIM/KYC Deactivation Scam",
        "category": "Cyber Fraud",
        "keywords": "SIM, KYC, deactivation, mobile number, verification, OTP, link, telecom",
        "description": "A scam where criminals falsely claim that a mobile SIM or number will be deactivated due to incomplete KYC verification.",
        "how_it_happens": "The victim receives a call or message claiming that their SIM will be blocked. The scammer asks for OTPs, personal information, or directs the victim to a suspicious link.",
        "warning_signs": "Threats of SIM deactivation, urgent KYC requests, unknown links, requests for OTP or personal information.",
        "prevention": "Complete telecom verification only through the official telecom provider's channels and never share OTPs with callers.",
        "what_to_do": "Do not share OTP or personal information, avoid suspicious links, contact the telecom provider through its official channel, and report suspected fraud.",
        "risk_level": "High",
        "active": True
    }
]


def seed_frauds():
    db = SessionLocal()

    try:
        inserted = 0
        skipped = 0

        for fraud_data in NEW_FRAUDS:
            existing = db.query(FraudCase).filter(
                FraudCase.name == fraud_data["name"]
            ).first()

            if existing:
                skipped += 1
                print(f"SKIPPED: {fraud_data['name']}")
                continue

            fraud = FraudCase(**fraud_data)

            db.add(fraud)
            inserted += 1

        db.commit()

        print("\n------------------------------")
        print("Fraud Knowledge Base Seeding")
        print("------------------------------")
        print(f"Inserted : {inserted}")
        print(f"Skipped  : {skipped}")
        print(f"Total New: {len(NEW_FRAUDS)}")
        print("------------------------------")

    except Exception as e:
        db.rollback()
        print("ERROR:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_frauds()