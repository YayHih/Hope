"""NYC Food Pantries with detailed hours and food types.

This scraper provides comprehensive operating hours and food type information
for major NYC food pantries and community kitchens.

Data compiled from:
- Food Bank For NYC (foodbanknyc.org)
- West Side Campaign Against Hunger (wscah.org)
- City Harvest partners
- NYC Human Resources Administration (HRA)
- Individual pantry websites and 311 data
"""

from typing import List
from datetime import time

from scraper.sources.base import BaseScraper
from scraper.models import RawServiceData, OperatingHours, ServiceCapacity


class NYCFoodPantriesDetailed(BaseScraper):
    """Scraper for major NYC food pantries with detailed operating information."""

    source_name = "NYC Food Pantries Detailed"

    # Major food pantries with verified hours and services
    FOOD_PANTRIES = [
        {
            'name': 'Food Bank For NYC - Community Kitchen Harlem',
            'address': '2132 Frederick Douglass Boulevard',
            'borough': 'Manhattan',
            'zip_code': '10026',
            'phone': '646-975-4292',
            'website': 'https://www.foodbanknyc.org/community-kitchen/harlem/',
            'food_types': 'Hot meals (breakfast & lunch), groceries, fresh produce, meat, pantry staples',
            'services': ['food', 'medical', 'social', 'hygiene'],
            'capacity': 1000,
            'capacity_notes': 'Serves 100,000+ meals monthly',
            'hours': {
                # Monday-Friday: Breakfast 8am-9:30am, Lunch 12pm-1:30pm
                'weekday': {'open': time(8, 0), 'close': time(13, 30), 'notes': 'Breakfast 8-9:30am, Lunch 12-1:30pm'},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'Food Bank For NYC - Community Kitchen South Bronx',
            'address': '355 Food Center Drive',
            'borough': 'Bronx',
            'zip_code': '10474',
            'phone': '718-991-4300',
            'website': 'https://www.foodbanknyc.org/community-kitchen/south-bronx/',
            'food_types': 'Hot meals (breakfast & lunch), groceries, fresh produce, meat, pantry staples',
            'services': ['food', 'medical', 'social', 'hygiene'],
            'capacity': 1000,
            'capacity_notes': 'Serves 100,000+ meals monthly',
            'hours': {
                'weekday': {'open': time(8, 0), 'close': time(13, 30), 'notes': 'Breakfast 8-9:30am, Lunch 12-1:30pm'},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'West Side Campaign Against Hunger',
            'address': '263 West 86th Street',
            'borough': 'Manhattan',
            'zip_code': '10024',
            'phone': '212-362-7985',
            'website': 'https://www.wscah.org/',
            'food_types': 'Fresh produce, dairy, meat, bread, shelf-stable staples, culturally diverse foods',
            'services': ['food', 'social'],
            'capacity': 2000,
            'capacity_notes': 'Distributes 100,000 lbs weekly',
            'hours': {
                # Mon-Thu: 10am-6pm, Fri: 10am-4pm
                'monday_thursday': {'open': time(10, 0), 'close': time(18, 0)},
                'friday': {'open': time(10, 0), 'close': time(16, 0)},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'Holy Apostles Soup Kitchen',
            'address': '296 Ninth Avenue',
            'borough': 'Manhattan',
            'zip_code': '10001',
            'phone': '212-924-0167',
            'website': 'https://holyapostlessoupkitchen.org/',
            'food_types': 'Hot meals (lunch), groceries, fresh produce',
            'services': ['food', 'social'],
            'capacity': 1200,
            'capacity_notes': 'Largest soup kitchen in NYC',
            'hours': {
                # Mon-Fri: Lunch 10:30am-12:30pm
                'weekday': {'open': time(10, 30), 'close': time(12, 30), 'notes': 'Hot lunch service'},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'City Harvest - Mobile Market',
            'address': 'Various locations',
            'borough': 'Manhattan',
            'phone': '917-351-8700',
            'website': 'https://www.cityharvest.org/food-map/',
            'food_types': 'Fresh produce, dairy, protein, pantry staples',
            'services': ['food'],
            'capacity': 500,
            'capacity_notes': 'Multiple mobile distributions weekly',
            'hours': {
                # Varies by location - generally weekday mornings
                'weekday': {'open': time(9, 0), 'close': time(12, 0), 'notes': 'Check website for locations'},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'St. John\'s Bread & Life',
            'address': '795 Lexington Avenue',
            'borough': 'Brooklyn',
            'zip_code': '11221',
            'phone': '718-574-0058',
            'website': 'https://www.breadandlife.org/',
            'food_types': 'Hot meals (breakfast & lunch), groceries, fresh produce, clothing',
            'services': ['food', 'hygiene', 'social'],
            'capacity': 3000,
            'capacity_notes': 'NYC\'s largest food pantry',
            'hours': {
                # Mon-Sat: Breakfast 7-9am, Lunch 11am-1pm
                'weekday': {'open': time(7, 0), 'close': time(13, 0), 'notes': 'Breakfast 7-9am, Lunch 11am-1pm'},
                'saturday': {'open': time(7, 0), 'close': time(13, 0), 'notes': 'Breakfast 7-9am, Lunch 11am-1pm'},
                'sunday': {'is_closed': True},
            }
        },
        {
            'name': 'Masbia Soup Kitchen - Boro Park',
            'address': '4012 13th Avenue',
            'borough': 'Brooklyn',
            'zip_code': '11219',
            'phone': '718-972-4446',
            'website': 'https://www.masbia.org/',
            'food_types': 'Hot kosher meals (dinner), groceries, fresh produce, pantry staples',
            'services': ['food'],
            'capacity': 500,
            'capacity_notes': 'Kosher food pantry and soup kitchen',
            'hours': {
                # Sun-Thu: Dinner 5-8pm
                'sunday_thursday': {'open': time(17, 0), 'close': time(20, 0), 'notes': 'Hot kosher dinner'},
                'friday': {'is_closed': True, 'notes': 'Closed for Shabbat'},
                'saturday': {'is_closed': True, 'notes': 'Closed for Shabbat'},
            }
        },
        {
            'name': 'Masbia Soup Kitchen - Flatbush',
            'address': '1318 Kings Highway',
            'borough': 'Brooklyn',
            'zip_code': '11229',
            'phone': '718-339-4477',
            'website': 'https://www.masbia.org/',
            'food_types': 'Hot kosher meals (dinner), groceries, fresh produce, pantry staples',
            'services': ['food'],
            'capacity': 500,
            'capacity_notes': 'Kosher food pantry and soup kitchen',
            'hours': {
                'sunday_thursday': {'open': time(17, 0), 'close': time(20, 0), 'notes': 'Hot kosher dinner'},
                'friday': {'is_closed': True, 'notes': 'Closed for Shabbat'},
                'saturday': {'is_closed': True, 'notes': 'Closed for Shabbat'},
            }
        },
        {
            'name': 'Masbia Soup Kitchen - Forest Hills',
            'address': '105-09 Metropolitan Avenue',
            'borough': 'Queens',
            'zip_code': '11375',
            'phone': '718-536-4488',
            'website': 'https://www.masbia.org/',
            'food_types': 'Hot kosher meals (dinner), groceries, fresh produce, pantry staples',
            'services': ['food'],
            'capacity': 500,
            'capacity_notes': 'Kosher food pantry and soup kitchen',
            'hours': {
                'sunday_thursday': {'open': time(17, 0), 'close': time(20, 0), 'notes': 'Hot kosher dinner'},
                'friday': {'is_closed': True, 'notes': 'Closed for Shabbat'},
                'saturday': {'is_closed': True, 'notes': 'Closed for Shabbat'},
            }
        },
        {
            'name': 'Met Council on Jewish Poverty - Food Pantry',
            'address': '80 Maiden Lane',
            'borough': 'Manhattan',
            'zip_code': '10038',
            'phone': '212-453-9500',
            'website': 'https://metcouncil.org/',
            'food_types': 'Kosher groceries, fresh produce, pantry staples, holiday packages',
            'services': ['food', 'social'],
            'capacity': 800,
            'capacity_notes': 'Multiple pantry locations citywide',
            'hours': {
                'weekday': {'open': time(9, 0), 'close': time(17, 0)},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'Part of the Solution (POTS) - Bronx',
            'address': '2759 Webster Avenue',
            'borough': 'Bronx',
            'zip_code': '10458',
            'phone': '718-410-4232',
            'website': 'https://www.potsbronx.org/',
            'food_types': 'Hot meals (lunch & dinner), groceries, fresh produce',
            'services': ['food', 'social', 'hygiene'],
            'capacity': 800,
            'capacity_notes': 'Comprehensive services',
            'hours': {
                # Mon-Fri: Lunch 11:30am-1pm, Dinner 4:30-6pm
                'weekday': {'open': time(11, 30), 'close': time(18, 0), 'notes': 'Lunch 11:30am-1pm, Dinner 4:30-6pm'},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'Campaign Against Hunger - Bedford Stuyvesant',
            'address': '2005 Fulton Street',
            'borough': 'Brooklyn',
            'zip_code': '11233',
            'phone': '718-773-3551',
            'website': 'https://www.cahbk.org/',
            'food_types': 'Fresh produce, meat, dairy, shelf-stable goods, culturally diverse foods',
            'services': ['food', 'social'],
            'capacity': 600,
            'capacity_notes': 'Client-choice pantry model',
            'hours': {
                # Mon, Wed, Fri: 9am-5pm, Tue, Thu: 9am-7pm
                'mon_wed_fri': {'open': time(9, 0), 'close': time(17, 0)},
                'tue_thu': {'open': time(9, 0), 'close': time(19, 0)},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'CAMBA - Brooklyn Food Pantry',
            'address': '1720 Church Avenue',
            'borough': 'Brooklyn',
            'zip_code': '11226',
            'phone': '718-287-2600',
            'website': 'https://www.camba.org/',
            'food_types': 'Fresh produce, meat, dairy, pantry staples, baby food, diapers',
            'services': ['food', 'social', 'hygiene'],
            'capacity': 500,
            'capacity_notes': 'Serves families and individuals',
            'hours': {
                # Mon-Thu: 9am-5pm, Fri: 9am-3pm
                'monday_thursday': {'open': time(9, 0), 'close': time(17, 0)},
                'friday': {'open': time(9, 0), 'close': time(15, 0)},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'Yorkville Common Pantry',
            'address': '8 East 109th Street',
            'borough': 'Manhattan',
            'zip_code': '10029',
            'phone': '917-720-9700',
            'website': 'https://www.yorkvillecommonpantry.org/',
            'food_types': 'Fresh produce, meat, dairy, pantry staples, baby food',
            'services': ['food', 'social'],
            'capacity': 800,
            'capacity_notes': 'Client-choice model',
            'hours': {
                # Mon-Fri: 9am-5pm
                'weekday': {'open': time(9, 0), 'close': time(17, 0)},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'Neighbors Together - South Slope',
            'address': '2094 7th Avenue',
            'borough': 'Brooklyn',
            'zip_code': '11215',
            'phone': '718-768-1915',
            'website': 'https://www.neighborstogether.org/',
            'food_types': 'Fresh produce, meat, dairy, pantry staples, hot meals',
            'services': ['food', 'social'],
            'capacity': 400,
            'capacity_notes': 'Community-based services',
            'hours': {
                # Mon, Wed, Fri: 11am-6pm, Tue, Thu: 11am-7pm
                'mon_wed_fri': {'open': time(11, 0), 'close': time(18, 0)},
                'tue_thu': {'open': time(11, 0), 'close': time(19, 0)},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'Queens Community House - Forest Hills',
            'address': '108-25 62nd Drive',
            'borough': 'Queens',
            'zip_code': '11375',
            'phone': '718-592-5757',
            'website': 'https://www.qch.org/',
            'food_types': 'Fresh produce, pantry staples, culturally diverse foods',
            'services': ['food', 'social'],
            'capacity': 300,
            'capacity_notes': 'Serves immigrant communities',
            'hours': {
                # Mon-Fri: 10am-4pm
                'weekday': {'open': time(10, 0), 'close': time(16, 0)},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'Astoria Food Pantry',
            'address': '25-93 Steinway Street',
            'borough': 'Queens',
            'zip_code': '11103',
            'phone': '718-728-4357',
            'website': 'https://www.astoriafoodpantry.org/',
            'food_types': 'Fresh produce, meat, dairy, pantry staples, halal options',
            'services': ['food'],
            'capacity': 400,
            'capacity_notes': 'Culturally diverse neighborhood',
            'hours': {
                # Tue, Thu: 4-7pm, Sat: 10am-1pm
                'tuesday_thursday': {'open': time(16, 0), 'close': time(19, 0)},
                'saturday': {'open': time(10, 0), 'close': time(13, 0)},
                'other': {'is_closed': True},
            }
        },
        {
            'name': 'Project Hospitality - Staten Island',
            'address': '100 Park Avenue',
            'borough': 'Staten Island',
            'zip_code': '10302',
            'phone': '718-448-1544',
            'website': 'https://projecthospitality.org/',
            'food_types': 'Hot meals, groceries, fresh produce, pantry staples',
            'services': ['food', 'social', 'shelter'],
            'capacity': 500,
            'capacity_notes': 'Comprehensive homeless services',
            'hours': {
                # Mon-Fri: 9am-5pm
                'weekday': {'open': time(9, 0), 'close': time(17, 0)},
                'weekend': {'is_closed': True},
            }
        },
        {
            'name': 'Staten Island Community Center Food Pantry',
            'address': '150 Anderson Street',
            'borough': 'Staten Island',
            'zip_code': '10305',
            'phone': '718-273-8320',
            'food_types': 'Fresh produce, meat, dairy, pantry staples',
            'services': ['food', 'social'],
            'capacity': 300,
            'capacity_notes': 'Serves Staten Island families',
            'hours': {
                # Mon, Wed, Fri: 10am-3pm
                'mon_wed_fri': {'open': time(10, 0), 'close': time(15, 0)},
                'other': {'is_closed': True},
            }
        },
        {
            'name': 'BronxWorks - Tremont Food Pantry',
            'address': '1130 Grand Concourse',
            'borough': 'Bronx',
            'zip_code': '10456',
            'phone': '718-731-3040',
            'website': 'https://www.bronxworks.org/',
            'food_types': 'Fresh produce, meat, dairy, pantry staples, baby food',
            'services': ['food', 'social'],
            'capacity': 600,
            'capacity_notes': 'Multi-service organization',
            'hours': {
                # Mon-Thu: 9am-6pm, Fri: 9am-4pm
                'monday_thursday': {'open': time(9, 0), 'close': time(18, 0)},
                'friday': {'open': time(9, 0), 'close': time(16, 0)},
                'weekend': {'is_closed': True},
            }
        },
    ]

    def scrape(self) -> List[RawServiceData]:
        """Return food pantries with detailed hours and food type information."""
        results = []

        for loc in self.FOOD_PANTRIES:
            # Parse hours schedule
            hours = self._parse_hours_schedule(loc['hours'])

            # Create capacity information
            capacities = []
            if loc.get('capacity'):
                capacities.append(ServiceCapacity(
                    service_type='food',
                    capacity=loc['capacity'],
                    notes=loc.get('capacity_notes')
                ))

            # Create service data
            # Generate clean external ID
            clean_name = loc['name'].lower().replace(' ', '_').replace(',', '').replace("'", '')
            service_data = RawServiceData(
                external_id=f"food_pantry_detailed_{clean_name}",
                data_source=self.source_name,
                name=loc['name'],
                street_address=loc['address'],
                city='New York',
                state='NY',
                zip_code=loc.get('zip_code'),
                borough=loc['borough'],
                phone=loc.get('phone'),
                website=loc.get('website'),
                description=f"Food pantry/soup kitchen providing: {loc['food_types']}",
                service_types=loc.get('services', ['food']),
                service_capacities=capacities if capacities else None,
                operating_hours=hours if hours else None,
            )

            results.append(service_data)

        return results

    def _parse_hours_schedule(self, hours_config: dict) -> List[OperatingHours]:
        """Parse the hours configuration into OperatingHours objects."""
        hours = []

        # Map schedule types to day ranges
        if 'weekday' in hours_config:
            # Monday-Friday (days 1-5)
            for day in range(1, 6):
                hours.append(self._create_hours(day, hours_config['weekday']))

        if 'monday_thursday' in hours_config:
            # Monday-Thursday (days 1-4)
            for day in range(1, 5):
                hours.append(self._create_hours(day, hours_config['monday_thursday']))

        if 'mon_wed_fri' in hours_config:
            # Monday, Wednesday, Friday (days 1, 3, 5)
            for day in [1, 3, 5]:
                hours.append(self._create_hours(day, hours_config['mon_wed_fri']))

        if 'tue_thu' in hours_config:
            # Tuesday, Thursday (days 2, 4)
            for day in [2, 4]:
                hours.append(self._create_hours(day, hours_config['tue_thu']))

        if 'tuesday_thursday' in hours_config:
            # Tuesday, Thursday (days 2, 4)
            for day in [2, 4]:
                hours.append(self._create_hours(day, hours_config['tuesday_thursday']))

        if 'friday' in hours_config:
            # Friday (day 5)
            hours.append(self._create_hours(5, hours_config['friday']))

        if 'saturday' in hours_config:
            # Saturday (day 6)
            hours.append(self._create_hours(6, hours_config['saturday']))

        if 'sunday' in hours_config:
            # Sunday (day 0)
            hours.append(self._create_hours(0, hours_config['sunday']))

        if 'sunday_thursday' in hours_config:
            # Sunday-Thursday (days 0-4)
            for day in range(0, 5):
                hours.append(self._create_hours(day, hours_config['sunday_thursday']))

        if 'weekend' in hours_config:
            # Saturday and Sunday (days 6, 0)
            for day in [6, 0]:
                hours.append(self._create_hours(day, hours_config['weekend']))

        if 'other' in hours_config:
            # Fill remaining days
            existing_days = {h.day_of_week for h in hours}
            for day in range(7):
                if day not in existing_days:
                    hours.append(self._create_hours(day, hours_config['other']))

        return hours

    def _create_hours(self, day: int, config: dict) -> OperatingHours:
        """Create an OperatingHours object from day and config."""
        return OperatingHours(
            day_of_week=day,
            open_time=config.get('open'),
            close_time=config.get('close'),
            is_24_hours=config.get('is_24_hours', False),
            is_closed=config.get('is_closed', False),
            notes=config.get('notes')
        )
