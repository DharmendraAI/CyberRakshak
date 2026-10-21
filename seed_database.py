from backend.app.database import SessionLocal
from backend.app.models import FraudCase
from Data.frauds_seed import frauds


def seed_frauds():
    db = SessionLocal()

    try:
        inserted = 0
        updated = 0

        for fraud_data in frauds:

            existing_fraud = (
                db.query(FraudCase)
                .filter(FraudCase.name == fraud_data["name"])
                .first()
            )

            if existing_fraud:
                for field, value in fraud_data.items():
                    setattr(existing_fraud, field, value)

                updated += 1

            else:
                fraud = FraudCase(**fraud_data)

                db.add(fraud)
                inserted += 1

        db.commit()

        print("=" * 50)
        print("CyberRakshak AI - Fraud Seed")
        print("=" * 50)
        print(f"Inserted : {inserted}")
        print(f"Updated  : {updated}")
        print("Seed completed successfully.")
        print("=" * 50)

    except Exception as e:
        db.rollback()

        print("=" * 50)
        print("Seed failed!")
        print("Error:", e)
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    seed_frauds()