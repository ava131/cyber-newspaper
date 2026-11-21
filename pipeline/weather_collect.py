import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

from sample_collect import LOCAL, ROOT


def condition(code):
    labels = {0:"晴",1:"晴间多云",2:"多云",3:"阴",45:"雾",48:"雾凇",51:"小毛毛雨",53:"毛毛雨",55:"较强毛毛雨",56:"冻毛毛雨",57:"冻毛毛雨",61:"小雨",63:"中雨",65:"大雨",66:"冻雨",67:"冻雨",71:"小雪",73:"中雪",75:"大雪",77:"雪粒",80:"阵雨",81:"阵雨",82:"强阵雨",85:"阵雪",86:"强阵雪",95:"雷雨",96:"雷雨伴冰雹",99:"强雷雨伴冰雹"}
    return labels.get(int(code), "天气代码"+str(code))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--edition", required=True)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    config = json.loads((ROOT / "config/weather.json").read_text())
    day = datetime.strptime(args.edition, "%Y-%m-%d")
    params = {"latitude":config["latitude"], "longitude":config["longitude"], "timezone":config["timezone"],
              "current":"temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m",
              "daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_speed_10m_max,sunrise,sunset",
              "start_date":args.edition, "end_date":(day+timedelta(days=2)).strftime("%Y-%m-%d")}
    url = config["endpoint"] + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent":"CyberDaily/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
    payload = json.loads(raw)
    current = payload["current"]
    daily = payload["daily"]
    if current["time"][:10] != args.edition or daily["time"][0] != args.edition:
        raise ValueError("Weather response date does not match the edition")
    if payload["timezone"] != "Asia/Shanghai" or payload["utc_offset_seconds"] != 28800:
        raise ValueError("Weather response timezone mismatch")
    direction = ["北","东北","东","东南","南","西南","西","西北"][int((current["wind_direction_10m"]+22.5)//45)%8]
    forecast = [{"date":date,"condition":condition(daily["weather_code"][index]),"weather_code":daily["weather_code"][index],
                 "low":daily["temperature_2m_min"][index],"high":daily["temperature_2m_max"][index],
                 "rain_probability":daily["precipitation_probability_max"][index],"max_wind_kmh":daily["wind_speed_10m_max"][index],
                 "sunrise":daily["sunrise"][index],"sunset":daily["sunset"][index]} for index,date in enumerate(daily["time"])]
    today = forecast[0]
    tips = []
    if today["rain_probability"]>=50:
        tips.append("出门带伞")
    if today["low"]<10:
        tips.append("早晚添衣")
    if today["max_wind_kmh"]>=30:
        tips.append("湖边留意风")
    if not tips:
        tips.append("出门前看一眼天空")
    result = {"location":config["location"],"point_label":config["point_label"],"latitude":config["latitude"],"longitude":config["longitude"],
              "forecast_grid":{"latitude":payload["latitude"],"longitude":payload["longitude"]}, "timezone":payload["timezone"],
              "provider":config["provider"],"source_id":"weather_fenhu","url":url,"fetched_at":datetime.now(LOCAL).isoformat(),
              "current":{"time":current["time"],"temperature":current["temperature_2m"],"feels_like":current["apparent_temperature"],
                         "condition":condition(current["weather_code"]),"weather_code":current["weather_code"],"wind_kmh":current["wind_speed_10m"],"wind_direction":direction},
              "forecast":forecast,"tip":" · ".join(tips),"tip_origin":"deterministic_rules","units":{"temperature":"°C","wind":"km/h","rain_probability":"%"}}
    edition = ROOT / "data/editions" / args.edition
    raw_path = edition / "raw/weather_open_meteo.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(raw)
    (edition / "weather.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    collection_path = edition / "collection.json"
    collection = json.loads(collection_path.read_text())
    collection["documents"] = [document for document in collection["documents"] if document["id"] != result["source_id"]]
    collection["documents"].append({"id":result["source_id"],"title":"Open-Meteo：吴江汾湖定点天气","url":url,"category":"weather","status":"ok",
                                     "fetched_at":result["fetched_at"],"raw_path":str(raw_path.relative_to(ROOT)),"sha256":hashlib.sha256(raw).hexdigest(),"response_bytes":len(raw)})
    collection_path.write_text(json.dumps(collection, ensure_ascii=False, indent=2))
    print(json.dumps({"weather":result["location"],"forecast_date":today["date"],"status":"ok"} if args.quiet else result, ensure_ascii=False, indent=None if args.quiet else 2))


if __name__ == "__main__":
    main()
