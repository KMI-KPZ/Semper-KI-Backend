import sys
import numpy as np
import asyncio
import time
import aiohttp
from django.http import HttpResponse

# BenchyMcMarkface is a script that can be used to benchmark a website
# Needed as parameters: 
# The main url of the website
# A file containing suburls, one per line
# Number of async calls to be made randomly to the suburls
#
# Created by: Silvio Weging, 2023

#############################################
async def request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()

#############################################
async def runLoop(url, paths):
    start = time.time()
    path = np.random.choice(paths)
    await request(url + path)
    end = time.time()
    return (path, end-start)

#############################################
async def main(argv):
    url = argv[0]
    paths = open(argv[1]).read().splitlines()
    numOfCalls = int(argv[2])

    await asyncio.gather(*[runLoop(url, paths) for i in range(numOfCalls)])
    
#############################################
async def mainDjango(argv):
    url = argv[0]
    paths = argv[1].read().decode("UTF-8").splitlines()
    numOfCalls = int(argv[2])

    start = time.time()
    results = await asyncio.gather(*[runLoop(url, paths) for i in range(numOfCalls)])
    end = time.time()
    timediff = (end-start) * 10**3
    resDict = {}
    for entry in results:
        path = entry[0]
        resTime = entry[1]
        if path in resDict:
            resDict[path][0] += resTime
            resDict[path][1] += 1
        else:
            resDict[path] = [resTime, 1]
    
    resList = list(resDict.items())
    sorted(resList, reverse=True, key=lambda elem: elem[0])

    outStr = "Results:\nTime in total: " + str(timediff) + " ms\n Paths and average times:\n"
    for elem in resList:
        print(elem)
        outStr += elem[0] + " " + str(elem[1][0]/elem[1][1] * 10**3) + " ms\n"
    return outStr
    
#############################################
def startFromDjango(request):
    numOfCalls = request.POST["NumberOfCalls"]
    url = request.POST["URL"]
    paths = request.FILES.get("PathFile")

    outStr = asyncio.run(mainDjango([url, paths, numOfCalls]))
    return HttpResponse(outStr,content_type="text/plain")


#############################################
#start = time.time()
#asyncio.run(main(sys.argv[1:]))
#end = time.time()
#print("TOE:", (end-start) * 10**3, "ms")
