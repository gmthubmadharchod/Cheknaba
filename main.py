from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def main():
    url = request.args.get("url")
    token = request.args.get("token")  # 👈 user ka token

    if not url:
        return jsonify({"status": False, "error": "URL missing"}), 400

    if not token:
        return jsonify({"status": False, "error": "Token missing"}), 400

    try:
        # ✅ Classplus / Testbook handler
        if (
            'classplusapp' in url
            or "testbook.com" in url
            or "classplusapp.com/drm" in url
            or "media-cdn.classplusapp.com/drm" in url
        ):
            # 🔧 contentId extract
            parts = url.split('&')
            contentId = None

            for p in parts:
                if "contentId=" in p:
                    contentId = p.split("contentId=")[-1]

            if not contentId:
                return jsonify({"status": False, "error": "contentId not found"})

            headers = {
                'x-access-token': token,  # 👈 USER TOKEN
                'accept-language': 'EN',
                'api-version': '18',
                'app-version': '1.4.73.2',
                'build-number': '35',
                'connection': 'Keep-Alive',
                'content-type': 'application/json',
                'device-details': 'Xiaomi_Redmi 7_SDK-32',
                'device-id': 'c28d3cb16bbdac01',
                'region': 'IN',
                'user-agent': 'Mobile-Android',
                'accept-encoding': 'gzip'
            }

            params = {
                'contentId': contentId,
                'offlineDownload': "false"
            }

            res = requests.get(
                "https://api.classplusapp.com/cams/uploader/video/jw-signed-url",
                params=params,
                headers=headers,
                timeout=15
            ).json()

            final_url = res.get("url")

            if not final_url:
                return jsonify({
                    "status": False,
                    "error": "Failed to fetch signed URL",
                    "response": res
                })

            return jsonify({
                "status": True,
                "type": "classplus",
                "url": final_url
            })

        # 🌐 Default handler
        else:
            r = requests.get(url, timeout=10)

            return jsonify({
                "status": True,
                "code": r.status_code,
                "length": len(r.text)
            })

    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500


# ✅ Render port setup
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
