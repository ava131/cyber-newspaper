from render_sample import escape

CSS = """
.weather-strip{display:grid;grid-template-columns:1fr auto 1.45fr;align-items:center;gap:12px 18px;border-top:1px solid var(--ink);border-bottom:1px solid var(--ink);padding:15px 0 11px;margin:-4px 0 25px;font-family:var(--sans)}.weather-place b{display:block;font-family:var(--serif);font-size:19px;letter-spacing:.08em}.weather-place span{display:block;font-size:9px;line-height:1.8;color:var(--muted);margin-top:7px}.weather-now{display:grid;grid-template-columns:30px auto;gap:2px 9px;align-items:center}.weather-now svg{width:30px;height:30px;grid-row:1/3;color:#9d7d3e}.weather-now strong{font:31px Georgia,serif;white-space:nowrap;line-height:1}.weather-now strong small{font-size:14px;margin-left:3px}.weather-now>span{font-size:10px;margin-top:5px;color:var(--muted)}.weather-details{font-size:10px;line-height:1.9}.weather-details b{font-size:12px;display:block;font-weight:500}.weather-details span{display:block}.weather-foot{grid-column:1/-1;display:flex;justify-content:space-between;align-items:baseline;gap:12px;font-size:9px;line-height:1.6;color:var(--muted);border-top:1px solid var(--line);padding-top:8px}.weather-foot strong{color:var(--accent);font-weight:500}.weather-foot a{text-decoration:none;border-bottom:1px solid var(--line)}
@media(max-width:650px){.weather-strip{grid-template-columns:1fr auto;gap:10px 14px;padding-top:15px}.weather-place b{font-size:21px}.weather-now strong{font-size:35px}.weather-details{grid-column:1/-1;display:flex;gap:4px 12px;flex-wrap:wrap;font-size:11px}.weather-details b{font-size:12px;width:100%}.weather-foot{align-items:flex-start}.weather-foot span{text-align:right}.weather-place span{font-size:10px}.section-mark{display:block}.section-mark strong{display:block;white-space:nowrap}.section-mark span{display:block;margin-top:10px}}
@media print{.weather-strip{padding:8px 0;margin-bottom:14px}.weather-now strong{font-size:24px}.weather-place b{font-size:16px}}
"""


def render(weather):
    current = weather["current"]
    today = weather["forecast"][0]
    tomorrow = weather["forecast"][1]
    sun = '<circle cx="20" cy="20" r="7"/>' + ''.join(f'<path d="M20 3v4" transform="rotate({angle} 20 20)"/>' for angle in range(0,360,45))
    cloud = '<path d="M10 28h19a7 7 0 0 0 0-14 10 10 0 0 0-18-2 8 8 0 0 0-1 16Z"/>'
    icon = f'<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">{sun if current["weather_code"]<=1 else cloud}</svg>'
    updated = current["time"][11:16]
    return f'''<section class="weather-strip" aria-label="吴江汾湖天气" data-origin="program-weather" data-date="{today['date']}">
<div class="weather-place"><b>{escape(weather['location'])}</b><span>今日天气 · 汾湖（黎里）预报点</span></div>
<div class="weather-now">{icon}<strong>{current['temperature']:.1f}<small>℃</small></strong><span>{escape(current['condition'])} · 当前预报</span></div>
<div class="weather-details"><b>今日 {today['low']:.0f}—{today['high']:.0f}℃ · {escape(today['condition'])}</b><span>体感 {current['feels_like']:.0f}℃ · {escape(current['wind_direction'])}风 {current['wind_kmh']:.0f} km/h</span><span>降水概率 {today['rain_probability']:.0f}% · 日落 {today['sunset'][11:16]}</span></div>
<div class="weather-foot"><strong>{escape(weather['tip'])} · 明日{escape(tomorrow['condition'])} {tomorrow['low']:.0f}—{tomorrow['high']:.0f}℃</strong><span><a href="{escape(weather['url'])}" target="_blank" rel="noopener noreferrer">Open-Meteo</a> · {updated} 北京时间</span></div></section>'''
