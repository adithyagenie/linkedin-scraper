import requests

url = lambda x: f"https://www.linkedin.com/voyager/api/graphql?variables=(start:0,origin:FACETED_SEARCH,query:(flagshipSearchIntent:ORGANIZATIONS_PEOPLE_ALUMNI,queryParameters:List((key:resultType,value:List(ORGANIZATION_ALUMNI)),(key:schoolFilter,value:List(15103020))),includeFiltersInResponse:true),count:{x})&queryId=voyagerSearchDashClusters.37920f17209f22c510dd410658abc540"

requests.get(url(12))