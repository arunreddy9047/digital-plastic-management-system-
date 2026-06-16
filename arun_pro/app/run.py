from app import create_app, db
from app.models import User, Location, PlasticType, Event
from werkzeug.security import generate_password_hash

app = create_app()

KARNATAKA_DISTRICTS = [
    ("Bagalkot", "Bagalkot"),
    ("Ballari", "Ballari"),
    ("Belagavi", "Belagavi"),
    ("Bengaluru Rural", "Bengaluru"),
    ("Bengaluru Urban", "Bengaluru"),
    ("Bidar", "Bidar"),
    ("Chamarajanagar", "Chamarajanagar"),
    ("Chikballapur", "Chikballapur"),
    ("Chikkamagaluru", "Chikkamagaluru"),
    ("Chitradurga", "Chitradurga"),
    ("Dakshina Kannada", "Mangaluru"),
    ("Davanagere", "Davanagere"),
    ("Dharwad", "Dharwad"),
    ("Gadag", "Gadag-Betageri"),
    ("Hassan", "Hassan"),
    ("Haveri", "Haveri"),
    ("Kalaburagi", "Kalaburagi"),
    ("Kodagu", "Madikeri"),
    ("Kolar", "Kolar"),
    ("Koppal", "Koppal"),
    ("Mandya", "Mandya"),
    ("Mysuru", "Mysuru"),
    ("Raichur", "Raichur"),
    ("Ramanagara", "Ramanagara"),
    ("Shivamogga", "Shivamogga"),
    ("Tumakuru", "Tumakuru"),
    ("Udupi", "Udupi"),
    ("Uttara Kannada", "Karwar"),
    ("Vijayapura", "Vijayapura"),
    ("Vijayanagara", "Hosapete"),
    ("Yadgir", "Yadgir"),
]

def seed_database():
    with app.app_context():
        db.create_all()
        
        # 1. Seed Default Admin User if none exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password=generate_password_hash('admin123'),
                role='admin',
                is_superuser=True
            )
            db.session.add(admin_user)
            print("Seeded default admin user: admin / admin123")

        if not User.query.filter_by(username='user').first():
            basic_user = User(
                username='user',
                password=generate_password_hash('user123'),
                role='user',
                is_superuser=False
            )
            db.session.add(basic_user)
            print("Seeded default user account: user / user123")
            
        # 2. Sync Locations to Karnataka districts only
        existing_locations = Location.query.all()
        desired_names = {district for district, _ in KARNATAKA_DISTRICTS}
        location_by_name = {location.name: location for location in existing_locations}

        fallback_location = location_by_name.get("Bengaluru Urban") or location_by_name.get("Karnataka")
        if fallback_location is None:
            fallback_location = Location(name="Bengaluru Urban", city="Bengaluru", state="Karnataka")
            db.session.add(fallback_location)
            db.session.flush()

        for district_name, headquarters in KARNATAKA_DISTRICTS:
            location = location_by_name.get(district_name)
            if location is None and district_name == "Bengaluru Urban" and fallback_location is not None:
                location = fallback_location

            if location is None:
                location = Location(name=district_name, city=headquarters, state="Karnataka")
                db.session.add(location)
            else:
                location.name = district_name
                location.city = headquarters
                location.state = "Karnataka"

        db.session.flush()
        fallback_location = Location.query.filter_by(name="Bengaluru Urban").first()

        for location in Location.query.all():
            if location.name in desired_names:
                continue

            for team in location.teams:
                team.location = fallback_location
            for record in location.waste_records:
                record.location = fallback_location
            db.session.delete(location)

        print(f"Synced {len(KARNATAKA_DISTRICTS)} Karnataka districts.")
            
        # 3. Seed Plastic Types (12 categories from report)
        plastic_categories = [
            ("PET Bottles", True),
            ("HDPE Milk Jugs", True),
            ("PVC Pipes & Cable Sheaths", False),
            ("LDPE Shopping Bags", True),
            ("PP Bottle Caps & Straws", False),
            ("PS Disposable Cups", False),
            ("ABS Electronic Enclosures", True),
            ("Polycarbonate Sheets", False),
            ("Acrylic Panels", False),
            ("Polyurethane Foam", False),
            ("Multi-Layer Packaging", False),
            ("Nylon Monofilaments", False)
        ]
        
        if PlasticType.query.count() == 0:
            for name, recyclable in plastic_categories:
                pt = PlasticType(name=name, recyclable=recyclable)
                db.session.add(pt)
            print(f"Seeded {len(plastic_categories)} plastic type categories.")
            
        # 4. Seed Official Fixed Environmental Events
        fixed_events = [
            ("World Earth Day Campaign", "22nd April 2026", "A global call to protect our planet. NSS teams host plastic-free pledge drives and regional garbage cleanup campaigns.", True),
            ("World Environment Day", "5th June 2026", "Focus on beating plastic pollution. Community garbage mapping, sorting, and awareness programs.", True),
            ("World Oceans Day Drive", "8th June 2026", "Beach cleanups and riverine protection drives targeting plastic wrappers and floating debris.", True),
            ("International Coastal Cleanup", "19th September 2026", "Largest volunteer effort for ocean health. NSS team coastal waste tracking audits.", True)
        ]
        
        if Event.query.filter_by(is_fixed=True).count() == 0:
            for name, date, desc, fixed in fixed_events:
                ev = Event(name=name, event_date=date, description=desc, is_fixed=fixed)
                db.session.add(ev)
            print(f"Seeded {len(fixed_events)} official global events.")
            
        db.session.commit()
        print("Database initialization and seeding complete!")

if __name__ == '__main__':
    seed_database()
    app.run(debug=True, port=5000)
