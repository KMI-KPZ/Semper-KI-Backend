import sys
import numpy as np
import asyncio
import time
import aiohttp

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
    return await request(url + np.random.choice(paths))

#############################################
async def main(argv):
    url = argv[0]
    paths = open(argv[1]).read().splitlines()
    numOfCalls = int(argv[2])

    await asyncio.gather(*[runLoop(url, paths) for i in range(numOfCalls)])
    
#############################################
start = time.time()
asyncio.run(main(sys.argv[1:]))
end = time.time()
print("TOE:", (end-start) * 10**3, "ms")
