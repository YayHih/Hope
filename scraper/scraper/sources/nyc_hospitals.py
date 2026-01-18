"""NYC Hospitals scraper - medical facilities data source."""
from typing import List
from datetime import datetime

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData


class NYCHospitalsScraper(BaseScraper):
    """Scrape major NYC public hospitals."""

    # Major NYC Health + Hospitals facilities
    NYC_HOSPITALS = [
        {
            "name": "Bellevue Hospital Center",
            "address": "462 First Avenue",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10016",
            "phone": "(212) 562-4141"
        },
        {
            "name": "NYC Health + Hospitals/Metropolitan",
            "address": "1901 First Avenue",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10029",
            "phone": "(212) 423-6262"
        },
        {
            "name": "NYC Health + Hospitals/Harlem",
            "address": "506 Lenox Avenue",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10037",
            "phone": "(212) 939-1000"
        },
        {
            "name": "NYC Health + Hospitals/Lincoln",
            "address": "234 East 149th Street",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10451",
            "phone": "(718) 579-5000"
        },
        {
            "name": "NYC Health + Hospitals/Jacobi",
            "address": "1400 Pelham Parkway South",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10461",
            "phone": "(718) 918-5000"
        },
        {
            "name": "NYC Health + Hospitals/North Central Bronx",
            "address": "3424 Kossuth Avenue",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10467",
            "phone": "(718) 519-5000"
        },
        {
            "name": "NYC Health + Hospitals/Kings County",
            "address": "451 Clarkson Avenue",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11203",
            "phone": "(718) 245-3131"
        },
        {
            "name": "NYC Health + Hospitals/Woodhull",
            "address": "760 Broadway",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11206",
            "phone": "(718) 963-8000"
        },
        {
            "name": "NYC Health + Hospitals/Coney Island",
            "address": "2601 Ocean Parkway",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11235",
            "phone": "(718) 616-3000"
        },
        {
            "name": "NYC Health + Hospitals/Elmhurst",
            "address": "79-01 Broadway",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11373",
            "phone": "(718) 334-4000"
        },
        {
            "name": "NYC Health + Hospitals/Queens",
            "address": "82-68 164th Street",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11432",
            "phone": "(718) 883-3000"
        },
        {
            "name": "Mount Sinai Hospital",
            "address": "1 Gustave L. Levy Place",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10029",
            "phone": "(212) 241-6500"
        },
        {
            "name": "NewYork-Presbyterian/Weill Cornell Medical Center",
            "address": "525 East 68th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10065",
            "phone": "(212) 746-5454"
        },
        {
            "name": "NYU Langone Health - Tisch Hospital",
            "address": "550 First Avenue",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10016",
            "phone": "(212) 263-7300"
        },
        {
            "name": "Mount Sinai Beth Israel",
            "address": "First Avenue at 16th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10003",
            "phone": "(212) 420-2000"
        },
        {
            "name": "Montefiore Medical Center - Moses Campus",
            "address": "111 East 210th Street",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10467",
            "phone": "(718) 920-4321"
        },
        {
            "name": "Maimonides Medical Center",
            "address": "4802 10th Avenue",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11219",
            "phone": "(718) 283-6000"
        },
        {
            "name": "Brooklyn Hospital Center",
            "address": "121 DeKalb Avenue",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11201",
            "phone": "(718) 250-8000"
        },
        {
            "name": "Jamaica Hospital Medical Center",
            "address": "8900 Van Wyck Expressway",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11418",
            "phone": "(718) 206-6000"
        },
        {
            "name": "Staten Island University Hospital - North",
            "address": "475 Seaview Avenue",
            "city": "Staten Island",
            "borough": "Staten Island",
            "zip": "10305",
            "phone": "(718) 226-9000"
        },
        # Additional Major Hospitals
        {
            "name": "NewYork-Presbyterian/Columbia University Irving Medical Center",
            "address": "622 West 168th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10032",
            "phone": "(212) 305-2500"
        },
        {
            "name": "Lenox Hill Hospital",
            "address": "100 East 77th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10075",
            "phone": "(212) 434-2000"
        },
        {
            "name": "Mount Sinai West",
            "address": "1000 Tenth Avenue",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10019",
            "phone": "(212) 523-4000"
        },
        {
            "name": "Mount Sinai Morningside",
            "address": "1111 Amsterdam Avenue",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10025",
            "phone": "(212) 523-4000"
        },
        {
            "name": "NYU Langone Brooklyn",
            "address": "150 55th Street",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11220",
            "phone": "(718) 630-7000"
        },
        {
            "name": "Montefiore Medical Center - Weiler Hospital",
            "address": "1825 Eastchester Road",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10461",
            "phone": "(718) 904-2000"
        },
        {
            "name": "Bronx-Lebanon Hospital Center",
            "address": "1650 Grand Concourse",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10457",
            "phone": "(718) 590-1800"
        },
        {
            "name": "Wyckoff Heights Medical Center",
            "address": "374 Stockholm Street",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11237",
            "phone": "(718) 963-7272"
        },
        {
            "name": "Brookdale Hospital Medical Center",
            "address": "One Brookdale Plaza",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11212",
            "phone": "(718) 240-5000"
        },
        {
            "name": "Kingsbrook Jewish Medical Center",
            "address": "585 Schenectady Avenue",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11203",
            "phone": "(718) 604-5000"
        },
        {
            "name": "Interfaith Medical Center",
            "address": "1545 Atlantic Avenue",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11213",
            "phone": "(718) 613-4000"
        },
        {
            "name": "NYC Health + Hospitals/Bellevue",
            "address": "462 First Avenue",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10016",
            "phone": "(212) 562-4141"
        },
        {
            "name": "Mount Sinai Queens",
            "address": "25-10 30th Avenue",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11102",
            "phone": "(718) 267-4000"
        },
        {
            "name": "NewYork-Presbyterian Queens",
            "address": "56-45 Main Street",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11355",
            "phone": "(718) 670-1231"
        },
        {
            "name": "Forest Hills Hospital",
            "address": "102-01 66th Road",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11375",
            "phone": "(718) 830-4000"
        },
        {
            "name": "Flushing Hospital Medical Center",
            "address": "4500 Parsons Boulevard",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11355",
            "phone": "(718) 670-5000"
        },
        {
            "name": "Long Island Jewish Medical Center",
            "address": "270-05 76th Avenue",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11040",
            "phone": "(718) 470-7000"
        },
        {
            "name": "Staten Island University Hospital - South",
            "address": "375 Seguine Avenue",
            "city": "Staten Island",
            "borough": "Staten Island",
            "zip": "10309",
            "phone": "(718) 226-2000"
        },
        {
            "name": "Richmond University Medical Center",
            "address": "355 Bard Avenue",
            "city": "Staten Island",
            "borough": "Staten Island",
            "zip": "10310",
            "phone": "(718) 818-1234"
        },
        {
            "name": "NYU Langone Orthopedic Hospital",
            "address": "301 East 17th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10003",
            "phone": "(212) 598-6000"
        },
        {
            "name": "Hospital for Special Surgery",
            "address": "535 East 70th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10021",
            "phone": "(212) 606-1000"
        },
        {
            "name": "Memorial Sloan Kettering Cancer Center",
            "address": "1275 York Avenue",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10065",
            "phone": "(212) 639-2000"
        },
        {
            "name": "Mount Sinai Brooklyn",
            "address": "3131 Kings Highway",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11234",
            "phone": "(718) 252-3000"
        },
        {
            "name": "Coney Island Hospital",
            "address": "2601 Ocean Parkway",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11235",
            "phone": "(718) 616-3000"
        },
        {
            "name": "BronxCare Health System",
            "address": "1276 Fulton Avenue",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10456",
            "phone": "(718) 960-1234"
        },
        {
            "name": "St. Barnabas Hospital",
            "address": "4422 Third Avenue",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10457",
            "phone": "(718) 960-9000"
        },
        {
            "name": "SBH Health System",
            "address": "4487 Third Avenue",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10458",
            "phone": "(718) 960-6151"
        },
        # Additional Manhattan Hospitals
        {
            "name": "NYU Langone Health - Kimmel Pavilion",
            "address": "240 East 38th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10016",
            "phone": "(646) 929-7800"
        },
        {
            "name": "Mount Sinai St. Luke's",
            "address": "1111 Amsterdam Avenue",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10025",
            "phone": "(212) 523-4000"
        },
        {
            "name": "NewYork-Presbyterian Lower Manhattan Hospital",
            "address": "170 William Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10038",
            "phone": "(212) 312-5000"
        },
        {
            "name": "Mount Sinai Union Square",
            "address": "10 Union Square East",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10003",
            "phone": "(212) 844-8000"
        },
        {
            "name": "Hospital for Joint Diseases",
            "address": "301 East 17th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10003",
            "phone": "(212) 598-6000"
        },
        {
            "name": "Manhattan Eye, Ear and Throat Hospital",
            "address": "210 East 64th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10065",
            "phone": "(212) 838-9200"
        },
        {
            "name": "NYU Langone Hospital - Brooklyn",
            "address": "150 55th Street",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11220",
            "phone": "(718) 630-7000"
        },
        # Additional Brooklyn Hospitals
        {
            "name": "Woodhull Medical Center",
            "address": "760 Broadway",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11206",
            "phone": "(718) 963-8000"
        },
        {
            "name": "Cobble Hill Health Center",
            "address": "380 Henry Street",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11201",
            "phone": "(718) 855-3800"
        },
        {
            "name": "NYU Langone Hospital - Sunset Park",
            "address": "4220 9th Avenue",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11232",
            "phone": "(718) 567-1234"
        },
        {
            "name": "Victory Memorial Hospital",
            "address": "792 Bushwick Avenue",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11221",
            "phone": "(718) 574-4000"
        },
        {
            "name": "NewYork-Presbyterian Brooklyn Methodist Hospital",
            "address": "506 6th Street",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11215",
            "phone": "(718) 780-3000"
        },
        {
            "name": "SUNY Downstate Medical Center University Hospital",
            "address": "450 Clarkson Avenue",
            "city": "Brooklyn",
            "borough": "Brooklyn",
            "zip": "11203",
            "phone": "(718) 270-1000"
        },
        # Additional Queens Hospitals
        {
            "name": "Queens Hospital Center",
            "address": "82-68 164th Street",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11432",
            "phone": "(718) 883-3000"
        },
        {
            "name": "Elmhurst Hospital Center",
            "address": "79-01 Broadway",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11373",
            "phone": "(718) 334-4000"
        },
        {
            "name": "Long Island Jewish Forest Hills",
            "address": "102-01 66th Road",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11375",
            "phone": "(718) 830-4000"
        },
        {
            "name": "St. John's Episcopal Hospital",
            "address": "327 Beach 19th Street",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11691",
            "phone": "(718) 869-7000"
        },
        {
            "name": "Cohen Children's Medical Center",
            "address": "269-01 76th Avenue",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11040",
            "phone": "(718) 470-3000"
        },
        {
            "name": "Jamaica Medical Center",
            "address": "8900 Van Wyck Expressway",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11418",
            "phone": "(718) 206-6000"
        },
        {
            "name": "Peninsula Hospital Center",
            "address": "51-15 Beach Channel Drive",
            "city": "Queens",
            "borough": "Queens",
            "zip": "11691",
            "phone": "(718) 734-7000"
        },
        # Additional Bronx Hospitals
        {
            "name": "Montefiore Medical Center - Wakefield Campus",
            "address": "600 East 233rd Street",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10466",
            "phone": "(718) 920-9000"
        },
        {
            "name": "Montefiore New Rochelle",
            "address": "16 Guion Place",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10801",
            "phone": "(914) 632-5000"
        },
        {
            "name": "NYC Health + Hospitals/Gotham Health Morrisania",
            "address": "1225 Gerard Avenue",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10452",
            "phone": "(718) 960-1234"
        },
        {
            "name": "Westchester Medical Center - Bronx",
            "address": "1250 Waters Place",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10461",
            "phone": "(914) 493-7000"
        },
        {
            "name": "James J. Peters VA Medical Center",
            "address": "130 West Kingsbridge Road",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10468",
            "phone": "(718) 584-9000"
        },
        {
            "name": "Calvary Hospital",
            "address": "1740 Eastchester Road",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10461",
            "phone": "(718) 518-2000"
        },
        # Additional Staten Island Hospitals
        {
            "name": "Staten Island University Hospital - Prince's Bay",
            "address": "375 Seguine Avenue",
            "city": "Staten Island",
            "borough": "Staten Island",
            "zip": "10309",
            "phone": "(718) 226-2000"
        },
        {
            "name": "Richmond University Medical Center - South Campus",
            "address": "355 Bard Avenue",
            "city": "Staten Island",
            "borough": "Staten Island",
            "zip": "10310",
            "phone": "(718) 818-1234"
        },
        # Specialty and Children's Hospitals
        {
            "name": "Children's Hospital at Montefiore",
            "address": "3415 Bainbridge Avenue",
            "city": "Bronx",
            "borough": "Bronx",
            "zip": "10467",
            "phone": "(718) 741-2450"
        },
        {
            "name": "Morgan Stanley Children's Hospital",
            "address": "3959 Broadway",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10032",
            "phone": "(212) 305-2500"
        },
        {
            "name": "Hassenfeld Children's Hospital at NYU Langone",
            "address": "240 East 38th Street",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10016",
            "phone": "(212) 263-7300"
        },
        {
            "name": "Kravis Children's Hospital at Mount Sinai",
            "address": "1 Gustave L. Levy Place",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10029",
            "phone": "(212) 241-6500"
        },
        {
            "name": "NewYork-Presbyterian Morgan Stanley Children's Hospital",
            "address": "3959 Broadway",
            "city": "New York",
            "borough": "Manhattan",
            "zip": "10032",
            "phone": "(212) 305-5437"
        },
    ]

    async def scrape(self) -> List[RawServiceData]:
        """Return hardcoded list of major NYC hospitals."""
        results = []

        print(f"  Loading {len(self.NYC_HOSPITALS)} major NYC hospitals")

        for hospital in self.NYC_HOSPITALS:
            try:
                results.append(RawServiceData(
                    name=hospital["name"],
                    organization_name="NYC Hospital",
                    description="Major hospital facility providing emergency and medical services.",
                    street_address=hospital["address"],
                    city=hospital["city"],
                    zip_code=hospital["zip"],
                    borough=hospital["borough"],
                    phone=hospital["phone"],
                    service_types=["hospitals"],
                    external_id=f"nyc-hospital-{hospital['name'].lower().replace(' ', '-').replace('/', '-')}",
                    data_source="NYC Major Hospitals",
                    scraped_at=datetime.now(),
                ))
            except Exception as e:
                print(f"  ⚠️  Error adding hospital {hospital['name']}: {e}")
                continue

        return results
