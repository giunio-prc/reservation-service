from database import engine, Base, SessionLocal, Availability

def init_database():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        existing_count = db.query(Availability).count()
        if existing_count == 0:
            print("Initializing default availability slots...")
            for day in range(7):  # 0=Monday to 6=Sunday
                for hour in range(24):  # 0-23 hours
                    availability = Availability(
                        day_of_week=day,
                        hour=hour,
                        is_available=True if 9 <= hour <= 17 else False
                    )
                    db.add(availability)
            
            db.commit()
            print("Database initialized with business hours (9 AM - 5 PM) availability.")
        else:
            print(f"Database already contains {existing_count} availability records.")
    
    finally:
        db.close()

if __name__ == "__main__":
    init_database()