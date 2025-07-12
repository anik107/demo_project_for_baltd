"""
Database utilities for seeding location data (Divisions, Districts, Thanas)
This includes the major administrative divisions of Bangladesh
"""

from sqlalchemy.orm import Session
from models import Division, District, Thana

# Bangladesh administrative data
BANGLADESH_LOCATIONS = {
    "Dhaka": {
        "Dhaka": ["Dhanmondi", "Gulshan", "Ramna", "Tejgaon", "Wari", "Kotwali", "Lalbagh", "Motijheel", "Paltan", "Shah Ali"],
        "Gazipur": ["Gazipur Sadar", "Kaliakair", "Kapasia", "Sreepur", "Kaliganj"],
        "Kishoreganj": ["Kishoreganj Sadar", "Bajitpur", "Bhairab", "Hossainpur", "Itna", "Karimganj", "Katiadi", "Kuliarchar", "Mithamain", "Nikli", "Pakundia", "Tarail"],
        "Manikganj": ["Manikganj Sadar", "Daulatpur", "Ghior", "Harirampur", "Saturia", "Shivalaya", "Singair"],
        "Munshiganj": ["Munshiganj Sadar", "Gazaria", "Lohajang", "Sirajdikhan", "Sreenagar", "Tongibari"],
        "Narayanganj": ["Narayanganj Sadar", "Araihazar", "Bandar", "Rupganj", "Sonargaon"],
        "Narsingdi": ["Narsingdi Sadar", "Belabo", "Monohardi", "Palash", "Raipura", "Shibpur"],
        "Tangail": ["Tangail Sadar", "Basail", "Bhuapur", "Delduar", "Ghatail", "Gopalpur", "Kalihati", "Madhupur", "Mirzapur", "Nagarpur", "Sakhipur", "Dhanbari"]
    },
    "Chittagong": {
        "Chittagong": ["Chittagong City", "Anwara", "Banshkhali", "Boalkhali", "Chandanaish", "Fatikchhari", "Hathazari", "Lohagara", "Mirsharai", "Patiya", "Rangunia", "Raozan", "Sandwip", "Satkania", "Sitakunda"],
        "Cox's Bazar": ["Cox's Bazar Sadar", "Chakaria", "Kutubdia", "Maheshkhali", "Ramu", "Teknaf", "Ukhiya", "Pekua"],
        "Cumilla": ["Cumilla Sadar", "Barura", "Brahmanpara", "Burichang", "Chandina", "Chauddagram", "Daudkandi", "Debidwar", "Homna", "Laksam", "Meghna", "Muradnagar", "Nangalkot", "Titas"],
        "Feni": ["Feni Sadar", "Chhagalnaiya", "Daganbhuiyan", "Fulgazi", "Parshuram", "Sonagazi"],
        "Khagrachhari": ["Khagrachhari Sadar", "Dighinala", "Lakshmichhari", "Mahalchhari", "Manikchhari", "Matiranga", "Panchhari", "Ramgarh"],
        "Lakshmipur": ["Lakshmipur Sadar", "Kamalnagar", "Raipur", "Ramganj", "Ramgati"],
        "Noakhali": ["Noakhali Sadar", "Begumganj", "Chatkhil", "Companiganj", "Hatiya", "Kabir Hat", "Senbagh", "Sonaimuri", "Subarnachar"],
        "Rangamati": ["Rangamati Sadar", "Baghaichhari", "Barkal", "Belaichhari", "Kaptai", "Juraichhari", "Langadu", "Nannerchar", "Rajasthali", "Kaukhali"],
        "Bandarban": ["Bandarban Sadar", "Alikadam", "Lama", "Naikhongchhari", "Rowangchhari", "Ruma", "Thanchi"]
    },
    "Rajshahi": {
        "Rajshahi": ["Rajshahi City", "Bagha", "Bagmara", "Charghat", "Durgapur", "Godagari", "Mohanpur", "Paba", "Puthia", "Tanore"],
        "Bogura": ["Bogura Sadar", "Adamdighi", "Dhunat", "Dhupchanchia", "Gabtali", "Kahaloo", "Nandigram", "Sariakandi", "Shajahanpur", "Sherpur", "Shibganj", "Sonatala"],
        "Joypurhat": ["Joypurhat Sadar", "Akkelpur", "Kalai", "Khetlal", "Panchbibi"],
        "Naogaon": ["Naogaon Sadar", "Atrai", "Badalgachhi", "Dhamoirhat", "Manda", "Mahadebpur", "Niamatpur", "Patnitala", "Porsha", "Raninagar", "Sapahar"],
        "Natore": ["Natore Sadar", "Bagatipara", "Baraigram", "Gurudaspur", "Lalpur", "Singra"],
        "Nawabganj": ["Nawabganj Sadar", "Bholahat", "Gomastapur", "Nachole", "Shibganj"],
        "Pabna": ["Pabna Sadar", "Atgharia", "Bera", "Bhangura", "Chatmohar", "Faridpur", "Ishwardi", "Santhia", "Sujanagar"],
        "Sirajganj": ["Sirajganj Sadar", "Belkuchi", "Chowhali", "Kamarkhand", "Kazipur", "Raiganj", "Shahjadpur", "Tarash", "Ullahpara"]
    },
    "Khulna": {
        "Khulna": ["Khulna City", "Batiaghata", "Dacope", "Dumuria", "Dighalia", "Koyra", "Paikgachha", "Phultala", "Rupsa", "Terokhada"],
        "Bagerhat": ["Bagerhat Sadar", "Chitalmari", "Fakirhat", "Kachua", "Mollahat", "Mongla", "Morrelganj", "Rampal", "Sarankhola"],
        "Chuadanga": ["Chuadanga Sadar", "Alamdanga", "Damurhuda", "Jibannagar"],
        "Jessore": ["Jessore Sadar", "Abhaynagar", "Bagherpara", "Chaugachha", "Jhikargachha", "Keshabpur", "Manirampur", "Sharsha"],
        "Jhenaidah": ["Jhenaidah Sadar", "Harinakunda", "Kaliganj", "Kotchandpur", "Maheshpur", "Shailkupa"],
        "Kushtia": ["Kushtia Sadar", "Bheramara", "Daulatpur", "Khoksa", "Kumarkhali", "Mirpur"],
        "Magura": ["Magura Sadar", "Mohammadpur", "Salikha", "Sreepur"],
        "Meherpur": ["Meherpur Sadar", "Gangni", "Mujibnagar"],
        "Narail": ["Narail Sadar", "Kalia", "Lohagara"],
        "Satkhira": ["Satkhira Sadar", "Assasuni", "Debhata", "Kalaroa", "Kaliganj", "Patkelghata", "Shyamnagar"]
    },
    "Sylhet": {
        "Sylhet": ["Sylhet City", "Balaganj", "Beanibazar", "Bishwanath", "Companigonj", "Fenchuganj", "Golapganj", "Gowainghat", "Jaintiapur", "Kanaighat", "Osmani Nagar", "Zakiganj"],
        "Habiganj": ["Habiganj Sadar", "Ajmiriganj", "Bahubal", "Baniyachong", "Chunarughat", "Lakhai", "Madhabpur", "Nabiganj", "Sayestaganj"],
        "Moulvibazar": ["Moulvibazar Sadar", "Barlekha", "Juri", "Kamalganj", "Kulaura", "Rajnagar", "Sreemangal"],
        "Sunamganj": ["Sunamganj Sadar", "Bishwamvarpur", "Chhatak", "Derai", "Dharamapasha", "Dowarabazar", "Jagannathpur", "Jamalganj", "Sulla", "Tahirpur"]
    },
    "Rangpur": {
        "Rangpur": ["Rangpur City", "Badarganj", "Gangachhara", "Kaunia", "Mithapukur", "Pirgachha", "Pirganj", "Taraganj"],
        "Dinajpur": ["Dinajpur Sadar", "Birampur", "Birganj", "Biral", "Bochaganj", "Chirirbandar", "Fulbari", "Ghoraghat", "Hakimpur", "Kaharole", "Khansama", "Nawabganj", "Parbatipur"],
        "Gaibandha": ["Gaibandha Sadar", "Fulchhari", "Gobindaganj", "Palashbari", "Sadullapur", "Saghata", "Sundarganj"],
        "Kurigram": ["Kurigram Sadar", "Bhurungamari", "Char Rajibpur", "Chilmari", "Phulbari", "Nageshwari", "Rajarhat", "Raomari", "Ulipur"],
        "Lalmonirhat": ["Lalmonirhat Sadar", "Aditmari", "Hatibandha", "Kaliganj", "Patgram"],
        "Nilphamari": ["Nilphamari Sadar", "Dimla", "Domar", "Jaldhaka", "Kishoreganj", "Sayedpur"],
        "Panchagarh": ["Panchagarh Sadar", "Atwari", "Boda", "Debiganj", "Tetulia"],
        "Thakurgaon": ["Thakurgaon Sadar", "Baliadangi", "Haripur", "Pirganj", "Ranisankail"]
    },
    "Barisal": {
        "Barisal": ["Barisal City", "Agailjhara", "Babuganj", "Bakerganj", "Banari Para", "Gournadi", "Hizla", "Mehendiganj", "Muladi", "Wazirpur"],
        "Barguna": ["Barguna Sadar", "Amtali", "Betagi", "Bamna", "Pathorghata", "Taltali"],
        "Bhola": ["Bhola Sadar", "Burhanuddin", "Char Fasson", "Daulatkhan", "Lalmohan", "Manpura", "Tazumuddin"],
        "Jhalokati": ["Jhalokati Sadar", "Kathalia", "Nalchity", "Rajapur"],
        "Patuakhali": ["Patuakhali Sadar", "Bauphal", "Dashmina", "Dumki", "Galachipa", "Kalapara", "Mirzaganj", "Rangabali"],
        "Pirojpur": ["Pirojpur Sadar", "Bhandaria", "Kawkhali", "Mathbaria", "Nazirpur", "Nesarabad", "Zianagar"]
    },
    "Mymensingh": {
        "Mymensingh": ["Mymensingh City", "Bhaluka", "Dhobaura", "Fulbaria", "Gaffargaon", "Gouripur", "Haluaghat", "Ishwarganj", "Muktagachha", "Nandail", "Phulpur", "Trishal"],
        "Jamalpur": ["Jamalpur Sadar", "Baksiganj", "Dewanganj", "Islampur", "Madarganj", "Melandaha", "Sarishabari"],
        "Netrakona": ["Netrakona Sadar", "Atpara", "Barhatta", "Durgapur", "Kalmakanda", "Kendua", "Khaliajuri", "Madan", "Mohanganj", "Purbadhala"],
        "Sherpur": ["Sherpur Sadar", "Jhenaigati", "Nakla", "Nalitabari", "Sreebardi"]
    }
}

def seed_location_data(db: Session):
    """
    Seed the database with Bangladesh administrative divisions, districts, and thanas
    """
    try:
        # Check if data already exists
        existing_divisions = db.query(Division).count()
        if existing_divisions > 0:
            print("Location data already exists. Skipping seeding.")
            return

        for division_name, districts in BANGLADESH_LOCATIONS.items():
            # Create division
            division = Division(name=division_name)
            db.add(division)
            db.flush()  # Get the ID without committing

            for district_name, thanas in districts.items():
                # Create district
                district = District(name=district_name, division_id=division.id)
                db.add(district)
                db.flush()  # Get the ID without committing

                for thana_name in thanas:
                    # Create thana
                    thana = Thana(name=thana_name, district_id=district.id)
                    db.add(thana)

        db.commit()
        print("Successfully seeded location data!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding location data: {e}")
        raise

def get_districts_by_division(db: Session, division_id: int):
    """Get all districts for a specific division"""
    return db.query(District).filter(District.division_id == division_id).all()

def get_thanas_by_district(db: Session, district_id: int):
    """Get all thanas for a specific district"""
    return db.query(Thana).filter(Thana.district_id == district_id).all()

def get_all_divisions(db: Session):
    """Get all divisions"""
    return db.query(Division).all()
