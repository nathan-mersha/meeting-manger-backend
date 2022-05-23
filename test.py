
parties = {
  "46f136f6-631b-46e9-9dd9-ad4adde6c57e": [
      {
        "fromDate": "2022-05-27T15:31:28.270000",
        "toDate": "2022-05-29T05:10:26.306000+00:00"
      },
      {
        "fromDate": "2022-05-24T15:31:28.270000",
        "toDate": "2022-05-25T15:31:28.270000"
      },
      {
        "fromDate": "2022-05-01T05:10:26.306000+00:00",
        "toDate": "2022-05-21T15:31:28.270000"
      },
      {
        "fromDate": "2022-05-22T15:31:28.270000",
        "toDate": "2022-05-23T15:31:28.270000"
      }
    ],

    "46f136f6-631b-46e9-9dd9-ad4adde6c57f": [
      {
        "fromDate": "2022-05-27T15:31:28.270000",
        "toDate": "2022-05-29T05:10:26.306000+00:00"
      },
      {
        "fromDate": "2022-05-24T15:31:28.270000",
        "toDate": "2022-05-25T15:31:28.270000"
      },
    ],

    "46f136f6-631b-46e9-9dd9-ad4adde6c57g": [
      {
        "fromDate": "2022-05-01T05:10:26.306000+00:00",
        "toDate": "2022-05-21T15:31:28.270000"
      },
      {
        "fromDate": "2022-05-24T15:31:28.270000",
        "toDate": "2022-05-26T15:31:28.270000"
      }
    ]
}

def getIntersectionDates(partyA, partyB):
    print("getting intersection ... ")
    print(f"party A : {partyA}")
    print(f"party B : {partyB}")
    intersections = []
    for partyAF in partyA:
        for partyBF in partyB:
            if partyAF["fromDate"] >= partyBF["fromDate"] and partyAF["toDate"] <= partyBF["toDate"]: # found my intersection of times
                print(f"found intersection : {partyAF}")
                intersections.append(partyAF)

            elif partyBF["fromDate"] >= partyAF["fromDate"] and partyBF["toDate"] <= partyAF["toDate"]: # found my intersection of times
                print(f"found intersection : {partyBF}")
                intersections.append(partyBF)

    print(f"intersection result : {intersections}")            
    return intersections


def getAllIntersection(parties):
    newParties = list(parties.values())
   
    # newParties = newParties + parties.values()

    # print(f"init new parties : {len(newParties)}")
    while len(newParties) > 1:
        print(f"running..... for len of {newParties}")
        
        p1 = newParties[0]
        p2 = newParties[1]
     
        intersectionResults = getIntersectionDates(p1, p2)
        # print(f"intersection results = {intersectionResults}")
        # print(f"p1 is : {p1}")
        newParties.remove(p1)
        newParties.remove(p2)

        print(f"len of intersection results : {len(intersectionResults)}")
        print(f"len of new parties before append : {len(newParties)}")        
        newParties.append(intersectionResults)
        print(f"len of new parties after append : {len(newParties)}")
        # print(f"new parties after append : {newParties}")


    print(f"final intesrsected result : {newParties}")
    return newParties

getAllIntersection(parties)

