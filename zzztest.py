import redis
import json
import redis.asyncio as redis
import asyncio


async def get_redis():
    r =  redis.from_url("redis://localhost")
    yield r
    await r.aclose()


async def main():
    r = await get_redis()
    await r.set("ttt", 5)
    t = await r.get("ttt")
    print(t)



if __name__ == "__main__":
    asyncio.run(main())













#r = redis.Redis(decode_responses=True)
#r.mset({"a": 1, "b": 2})
#t = r.get("a").decode("utf-8")
#t = r.hgetall()
#with r.pipeline() as pipe:
#    pipe.hset("testd", mapping={"a": 1, "b": 2})
#    pipe.setex("testd", 10)
#    pipe.execute()
#template = {"a": 1, "b": 2}
#
#j_template = json.dumps(template)
#
#r.set("21", j_template)
#r.set("21:22", j_template)
#r.set("21:22:23", j_template)
#t = r.get("test")

#r.bgsave()

#print(t)