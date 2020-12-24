from typing import Dict


stateAbbreviations: Dict[str, str] = {
    "ALABAMA": "AL",
    "ALASKA": "AK",
    "AMERICAN SAMOA": "AS",
    "ARIZONA": "AZ",
    "ARKANSAS": "AR",
    "CALIFORNIA": "CA",
    "COLORADO": "CO",
    "CONNECTICUT": "CT",
    "DELAWARE": "DE",
    "DISTRICT OF COLUMBIA": "DC",
    "FLORIDA": "FL",
    "GEORGIA": "GA",
    "GUAM": "GU",
    "HAWAII": "HI",
    "IDAHO": "ID",
    "ILLINOIS": "IL",
    "INDIANA": "IN",
    "IOWA": "IA",
    "KANSAS": "KS",
    "KENTUCKY": "KY",
    "LOUISIANA": "LA",
    "MAINE": "ME",
    "MARYLAND": "MD",
    "MASSACHUSETTS": "MA",
    "MICHIGAN": "MI",
    "MINNESOTA": "MN",
    "MISSISSIPPI": "MS",
    "MISSOURI": "MO",
    "MONTANA": "MT",
    "NEBRASKA": "NE",
    "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH",
    "NEW JERSEY": "NJ",
    "NEW MEXICO": "NM",
    "NEW YORK": "NY",
    "NORTH CAROLINA": "NC",
    "NORTH DAKOTA": "ND",
    "NORTHERN MARIANA IS": "MP",
    "OHIO": "OH",
    "OKLAHOMA": "OK",
    "OREGON": "OR",
    "PENNSYLVANIA": "PA",
    "PUERTO RICO": "PR",
    "RHODE ISLAND": "RI",
    "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD",
    "TENNESSEE": "TN",
    "TEXAS": "TX",
    "UTAH": "UT",
    "VERMONT": "VT",
    "VIRGINIA": "VA",
    "VIRGIN ISLANDS": "VI",
    "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI",
    "WYOMING": "WY"
}

codes: Dict[str, Dict[str, str]] = {
    'population': {
        'total': 'B01003_001E'
    },
    'education': {
        'total': 'B29002_001E',
        'lessThanHighSchool': 'B29002_002E',
        'highSchoolNoGrad': 'B29002_003E',
        'highSchoolGrad': 'B29002_004E',
        'someCollegeNoDegree': 'B29002_005E',
        'associatesDegree': 'B29002_006E',
        'bachelorsDegree': 'B29002_007E',
        'graduateDegree': 'B29002_008E',
    },
    'educationByInternetAccess': {
        # EDUCATIONAL ATTAINMENT BY PRESENCE OF A COMPUTER AND TYPES OF INTERNET SUBSCRIPTION IN HOUSEHOLD
        'total': 'B28006_001E',

        'lessThanHighSchoolTotal': 'B28006_002E',
        'lessThanHighSchoolWithComputer': 'B28006_003E',
        'lessThanHighSchoolWithComputerWithDialUpOnly': 'B28006_004E',
        'lessThanHighSchoolWithComputerWithBroadband': 'B28006_005E',
        'lessThanHighSchoolWithComputerNoInternet': 'B28006_006E',
        'lessThanHighSchoolNoComputer': 'B28006_007E',

        'highSchoolSomeCollegeTotal': 'B28006_008E',
        'highSchoolSomeCollegeWithComputer': 'B28006_009E',
        'highSchoolSomeCollegeWithComputerDialUpOnly': 'B28006_010E',
        'highSchoolSomeCollegeWithComputerWithBroadband': 'B28006_011E',
        'highSchoolSomeCollegeWithComputerNoInternet': 'B28006_012E',
        'highSchoolSomeCollegeNoComputer': 'B28006_013E',

        "bachelorsTotal": 'B28006_014E',
        "bachelorsWithComputer": 'B28006_015E',
        "bachelorsWithComputerWithDialUpOnly": 'B28006_016E',
        "bachelorsWithComputerWithBroadband": 'B28006_017E',
        "bachelorsWithComputerNoInternet": 'B28006_018E',
        "bachelorsNoComputer": 'B28006_019E',
    },
    'homeOwnershipByEducation': {
        'total': 'B25013_001E',

        'homeOwner': 'B25013_002E',
        'homeOwnerLessThanHighSchool': 'B25013_003E',
        'homeOwnerHighSchoolGrad': 'B25013_004E',
        'homeOwnerSomeCollege': 'B25013_005E',
        'homeOwnerBachelorsOrMore': 'B25013_006E',

        'renter': 'B25013_007E',
        'renterLessThanHighSchool': 'B25013_008E',
        'renterHighSchoolGrad': 'B25013_009E',
        'renterSomeCollege': 'B25013_010E',
        'renterBachelorsOrMore': 'B25013_011E',

    },
    'healthInsuranceCoverageByEducation':
    {
        'total': 'B27019_001E',

        '26to64Total': 'B27019_002E',

        '26to64NoHighSchoolGrad': 'B27019_003E',
        '26to64NoHighSchoolGradCoverage': 'B27019_004E',
        '26to64NoHighSchoolGradCoveragePrivate': 'B27019_005E',
        '26to64NoHighSchoolGradCoveragePublic': 'B27019_006E',
        '26to64NoHighSchoolGradNoCoverage': 'B27019_007E',

        '26to64HighSchoolGrad': 'B27019_008E',
        '26to64HighSchoolGradCoverage': 'B27019_009E',
        '26to64HighSchoolGradCoveragePrivate': 'B27019_010E',
        '26to64HighSchoolGradCoveragePublic': 'B27019_011E',
        '26to64HighSchoolGradNoCoverage': 'B27019_012E',

        '26to64SomeCollege': 'B27019_013E',
        '26to64SomeCollegeCoverage': 'B27019_014E',
        '26to64SomeCollegeCoveragePrivate': 'B27019_015E',
        '26to64SomeCollegeCoveragePublic': 'B27019_016E',
        '26to64SomeCollegeNoCoverage': 'B27019_017E',

        '26to64BachelorsOrHigher': 'B27019_018E',
        '26to64BachelorsOrHigherCoverage': 'B27019_019E',
        '26to64BachelorsOrHigherCoveragePrivate': 'B27019_020E',
        '26to64BachelorsOrHigherCoveragePublic': 'B27019_021E',
        '26to64BachelorsOrHigherNoCoverage': 'B27019_022E',


        '65plus': 'B27019_023E',

        '65plusNoHighSchoolGradCoverage': 'B27019_024E',
        '65plusNoHighSchoolGradCoverage': 'B27019_025E',
        '65plusNoHighSchoolGradPrivate': 'B27019_026E',
        '65plusNoHighSchoolGradCoveragePublic': 'B27019_027E',
        '65plusNoHighSchoolGradNoCoverage': 'B27019_028E',

        '65plusHighSchoolGrad': 'B27019_029E',
        '65plusHighSchoolGradCoverage': 'B27019_030E',
        '65plusHighSchoolGradCoveragePrivate': 'B27019_031E',
        '65plusHighSchoolGradCoveragePublic': 'B27019_032E',
        '65plusHighSchoolGradNoCoverage': 'B27019_033E',

        '65plusSomeCollege': 'B27019_034E',
        '65plusSomeCollegeCoverage': 'B27019_035E',
        '65plusSomeCollegeCoveragePrivate': 'B27019_036E',
        '65plusSomeCollegeCoveragePublic': 'B27019_037E',
        '65plusSomeCollegeNoCoverage': 'B27019_038E',

        '65plusBachelorsOrHigher': 'B27019_039E',
        '65plusBachelorsOrHigherCoverage': 'B27019_040E',
        '65plusBachelorsOrHigherCoveragePrivate': 'B27019_042E',
        '65plusBachelorsOrHigherCoveragePublic': 'B27019_042E',
        '65plusBachelorsOrHigherNoCoverage': 'B27019_043E',
    },
    'veteranStatusByEducation': {
        'total': 'B21003_001E',

        'veteran': 'B21003_002E',

        'veteranNoHighSchoolGrad': 'B21003_003E',
        'veteranHighSchoolGrad': 'B21003_004E',
        'veteranSomeCollege': 'B21003_005E',
        'veteranBachelorsOrHigher': 'B21003_006E',

        'nonVeteran': 'B21003_007E',

        'nonVeteranNoHighSchoolGrad': 'B21003_008E',
        'nonVeteranHighSchoolGrad': 'B21003_009E',
        'nonVeteranSomeCollege': 'B21003_010E',
        'nonVeteranBachelorsOrHigher': 'B21003_011E'
    },
    'educationByEmploymentStatus': {
        'total': 'B23006_001E',

        'noHighSchoolGrad': 'B23006_002E',
        'noHighSchoolGradInLaborForce': 'B23006_003E',
        'noHighSchoolGradInLaborForceInArmy': 'B23006_004E',
        'noHighSchoolGradInLaborForceCivilian': 'B23006_005E',
        'noHighSchoolGradInLaborForceCivilianEmployed': 'B23006_006E',
        'noHighSchoolGradInLaborForceCivilianUnemployed': 'B23006_007E',
        'noHighSchoolGradNotInLaborForce': 'B23006_008E',

        'highSchoolGrad': 'B23006_009E',
        'highSchoolGradInLaborForce': 'B23006_010E',
        'highSchoolGradInLaborForceInArmy': 'B23006_011E',
        'highSchoolGradInLaborForceCivilian': 'B23006_012E',
        'highSchoolGradInLaborForceCivilianEmployed': 'B23006_013E',
        'highSchoolGradInLaborForceCivilianUnemployed': 'B23006_014E',
        'highSchoolGradNotInLaborForce': 'B23006_015E',

        'someCollege': 'B23006_016E',
        'someCollegeInLaborForce': 'B23006_017E',
        'someCollegeInLaborForceInArmy': 'B23006_018E',
        'someCollegeInLaborForceCivilian': 'B23006_019E',
        'someCollegeInLaborForceCivilianEmployed': 'B23006_020E',
        'someCollegeInLaborForceCivilianUnemployed': 'B23006_021E',
        'someCollegeNotInLaborForce': 'B23006_022E',

        'bachelorsOrHigher': 'B23006_023E',
        'bachelorsOrHigherInLaborForce': 'B23006_024E',
        'bachelorsOrHigherInLaborForceInArmy': 'B23006_025E',
        'bachelorsOrHigherInLaborForceCivilian': 'B23006_026E',
        'bachelorsOrHigherInLaborForceCivilianEmployed': 'B23006_027E',
        'bachelorsOrHigherInLaborForceCivilianUnemployed': 'B23006_028E',
        'bachelorsOrHigherNotInLaborForce': 'B23006_029E',
    },
    'povertyStatusByEducation':  {
        'total': 'B17018_001E',

        'belowPovertyLevel': 'B17018_002E',

        'belowPovertyLevelMarried': 'B17018_003E',
        'belowPovertyLevelMarriedNoHighSchoolGrad': 'B17018_004E',
        'belowPovertyLevelMarriedHighSchoolGrad': 'B17018_005E',
        'belowPovertyLevelMarriedSomeCollege': 'B17018_006E',
        'belowPovertyLevelMarriedBachelorsOrHigher': 'B17018_007E',

        'belowPovertyLevelSingleParent': 'B17018_008E',
        'belowPovertyLevelSingleParentDad': 'B17018_009E',
        'belowPovertyLevelSingleParentDadNoHighSchoolGrad': 'B17018_010E',
        'belowPovertyLevelSingleParentDadHighSchoolGrad': 'B17018_011E',
        'belowPovertyLevelSingleParentDadSomeCollege': 'B17018_012E',
        'belowPovertyLevelSingleParentDadBachelorsOrHigher': 'B17018_013E',

        'belowPovertyLevelSingleParentMom': 'B17018_014E',
        'belowPovertyLevelSingleParentMomNoHighSchoolGrad': 'B17018_015E',
        'belowPovertyLevelSingleParentMomHighSchoolGrad': 'B17018_016E',
        'belowPovertyLevelSingleParentMomSomeCollege': 'B17018_017E',
        'belowPovertyLevelSingleParentMomBachelorsOrHigher': 'B17018_018E',

        'atOrAbovePovertyLevel': 'B17018_019E',

        'atOrAbovePovertyLevelMarried': 'B17018_020E',
        'atOrAbovePovertyLevelMarriedNoHighSchoolGrad': 'B17018_021E',
        'atOrAbovePovertyLevelMarriedHighSchoolGrad': 'B17018_022E',
        'atOrAbovePovertyLevelMarriedSomeCollege': 'B17018_023E',
        'atOrAbovePovertyLevelMarriedBachelorsOrHigher': 'B17018_024E',

        'atOrAbovePovertyLevelSingleParent': 'B17018_025E',
        'atOrAbovePovertyLevelSingleParentDad': 'B17018_026E',
        'atOrAbovePovertyLevelSingleParentDadNoHighSchoolGrad': 'B17018_027E',
        'atOrAbovePovertyLevelSingleParentDadHighSchoolGrad': 'B17018_028E',
        'atOrAbovePovertyLevelSingleParentDadSomeCollege': 'B17018_029E',
        'atOrAbovePovertyLevelSingleParentDadBachelorsOrHigher': 'B17018_030E',

        'atOrAbovePovertyLevelSingleParentMom': 'B17018_031E',
        'atOrAbovePovertyLevelSingleParentMomNoHighSchoolGrad': 'B17018_032E',
        'atOrAbovePovertyLevelSingleParentMomHighSchoolGrad': 'B17018_033E',
        'atOrAbovePovertyLevelSingleParentMomSomeCollege': 'B17018_034E',
        'atOrAbovePovertyLevelSingleParentMomBachelorsOrHigher': 'B17018_035E',

    },
    'povertyLevel': {
        'total': 'B29003_001E',
        'below': 'B29003_002E',
        'atOrAbove': 'B29003_003E',
    },
    'internetSubscription': {
        'total': 'B28002_001E',
        'hasInternet': 'B28002_002E',
        'dialUp': 'B28002_003E',
        'anyBroadband': 'B28002_004E',
        'cellPlanTotal': 'B28002_005E',
        'cellPlanOnly': 'B28002_006E',
        'cableFiberOpticOrDslTotal': 'B28002_007E',
        'cableFiberOpticOrDslOnly': 'B28002_008E',
        'satelliteTotal': 'B28002_009E',
        'satelliteOnly': 'B28002_010E',
        'otherNoOtherService': 'B28002_011E',
        'internetNoSubscription': 'B28002_012E',
        'noInternet': 'B28002_013E'
    },
    'income': {
        'total': 'B07010_001E',
        'noIncome': 'B07010_002E',
        '$1-9k': 'B07010_004E',
        '$10-15k': 'B07010_005E',
        '$15-25k': 'B07010_006E',
        '$25-35k': 'B07010_007E',
        '$35-50k': 'B07010_008E',
        '$50-65k': 'B07010_009E',
        '$65-75k': 'B07010_010E',
        '$75k-more': 'B07010_011E',
    }
}


# EDUCATIONAL ATTAINMENT AND EMPLOYMENT STATUS BY LANGUAGE SPOKEN AT HOME FOR THE POPULATION 25 YEARS AND OVER
