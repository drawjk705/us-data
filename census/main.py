# from census.models import GeoDomain
# from census.utils.configureLogger import configureLogger
# from census.variableRetrieval.variableRetriever import VariableRetriever


# configureLogger("census.log")

# c = VariableRetriever(2019, shouldLoadFromExistingCache=True)
# supportedGeos = c.getSupportedGeographies()

# c.getGeographyCodes(
#     forDomain=GeoDomain("county"), inDomains=[GeoDomain("state", "01"), GeoDomain("us")]
# )


from pprint import pprint

from census.api.models import GeographyClauseSet, GeographyItem


gi1 = GeographyItem.makeItem(
    name="congressional district",
    hierarchy="500",
    clauses=[
        GeographyClauseSet.makeSet(forClause="congressional district:*", inClauses=[]),
        GeographyClauseSet.makeSet(
            forClause="congressional district:*",
            inClauses=["state:*"],
        ),
        GeographyClauseSet.makeSet(
            forClause="congressional district:CODE",
            inClauses=["state:CODE"],
        ),
    ],
)

gi2 = GeographyItem.makeItem(
    name="congressional district",
    hierarchy="500",
    clauses=[
        GeographyClauseSet.makeSet(
            forClause="congressional district:*",
            inClauses=["state:*"],
        ),
        GeographyClauseSet.makeSet(
            forClause="congressional district:CODE",
            inClauses=["state:CODE"],
        ),
        GeographyClauseSet.makeSet(forClause="congressional district:*", inClauses=[]),
    ],
)

print("ONE")
print("-------------")
pprint(gi1)
print("\nTWO")
print("-------------")
pprint(gi1)