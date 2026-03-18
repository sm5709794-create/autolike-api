from fastapi import FastAPI, Query
import httpx
import uvicorn

app = FastAPI()

MAIN_API = "https://autolike-twoin-one.vercel.app/debug"

@app.get("/")
def home():
    return {"status": "API is running"}

@app.get("/like")
async def like(uid: str = Query(...), server: str = Query(...)):
    try:
        url = f"{MAIN_API}?uid={uid}&server_name={server}"

        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)

        if response.status_code != 200:
            return {
                "error": "Main API not responding",
                "status": 0
            }

        data = response.json()
        api_reports = data.get("api_reports", [])

        if not api_reports:
            return {
                "error": "Empty API response",
                "status": 0
            }

        total_likes = 0
        nickname = "Unknown"
        uid_val = uid
        likes_before = 0
        likes_after = 0
        status = 0

        first = True  # 🔥 important fix

        for api in api_reports:
            d = api.get("data", {})

            if not d:
                continue

            total_likes += d.get("LikesGivenByAPI", 0)

            nickname = d.get("PlayerNickname", nickname)
            uid_val = d.get("UID", uid_val)

            # ✅ FIRST API → before
            if first:
                likes_before = d.get("LikesbeforeCommand", 0)
                first = False

            # ✅ LAST API → after
            likes_after = d.get("LikesafterCommand", likes_after)

            # ✅ status logic
            if d.get("status") == 1:
                status = 1
            elif d.get("status") == 2 and status != 1:
                status = 2

        # 🔥 FINAL RESPONSE (SAME STRUCTURE)
        return {
            "PlayerNickname": nickname,
            "UID": uid_val,
            "LikesbeforeCommand": likes_before,
            "LikesafterCommand": likes_after,
            "LikesGivenByAPI": total_likes,
            "status": status
        }

    except Exception as e:
        return {
            "error": str(e),
            "status": 0
        }


# 🔥 AUTO RUN
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=1148)