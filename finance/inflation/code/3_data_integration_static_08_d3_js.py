import pandas as pd
from sklearn.cluster import KMeans
import json

# === PARAMETRY ===
YEAR_START = 1977
YEAR_END = 2024
ROLLING_WINDOW = 10

# === WCZYTANIE I INTEGRACJA DANYCH ===
df_gus = pd.read_csv("data/gus/all.csv")
df_gus["date"] = pd.to_datetime(df_gus["date"])
df_gus = df_gus.sort_values("date")

df_nbp = pd.read_csv("data/nbp/all.csv")
df_nbp["date"] = pd.to_datetime(df_nbp["date"])
df_nbp = df_nbp.sort_values("date")

df = pd.merge_asof(
    df_gus.sort_values("date"),
    df_nbp.sort_values("date"),
    on="date",
    direction="nearest",
    tolerance=pd.Timedelta("30D")
)

df["year"] = df["date"].dt.year
df["cpi"] = df["cpi_avg_wiki"].fillna(df["cpi_avg_gus"])
df["usd"] = df["USD_PLN"]
df = df.dropna(subset=["cpi", "usd"])

# === FILTROWANIE ===
df_range = df[(df["year"] >= YEAR_START) & (df["year"] <= YEAR_END)].copy()

window_days = int(ROLLING_WINDOW * 365)
df_range["corr"] = df_range["cpi"].rolling(window=window_days, min_periods=50).corr(df_range["usd"])

df_seg = df_range.dropna(subset=["cpi", "usd"]).copy()
if len(df_seg) >= 3:
    X = df_seg[["cpi", "usd"]].to_numpy()
    kmeans = KMeans(n_clusters=3, random_state=42, n_init="auto")
    df_seg["cluster"] = kmeans.fit_predict(X)
else:
    df_seg["cluster"] = 0

# === PRZYGOTOWANIE DANYCH JSON ===
data_json = df_range[["date", "cpi", "usd", "corr"]].copy()
data_json["date"] = data_json["date"].dt.strftime("%Y-%m-%d")
data_json = data_json.to_dict(orient="records")

seg_json = df_seg[["cpi", "usd", "cluster"]].copy()
seg_json["cluster"] = seg_json["cluster"].astype(int)
seg_json = seg_json.to_dict(orient="records")

# === GENEROWANIE HTML Z D3.js ===
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Dashboard D3.js</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .chart {{ margin-bottom: 40px; }}
        svg {{ border: 1px solid #ccc; }}
    </style>
</head>
<body>
    <h1>Dashboard: Inflacja CPI vs USD/PLN ({YEAR_START}-{YEAR_END})</h1>
    <div id="chart1" class="chart"></div>
    <div id="chart2" class="chart"></div>
    <div id="chart3" class="chart"></div>
    
    <script>
        const data = {json.dumps(data_json)};
        const segData = {json.dumps(seg_json)};
        
        // Wykres 1: CPI
        const margin = {{top: 20, right: 30, bottom: 30, left: 50}};
        const width = 800 - margin.left - margin.right;
        const height = 200 - margin.top - margin.bottom;
        
        const svg1 = d3.select("#chart1").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
        
        const parseDate = d3.timeParse("%Y-%m-%d");
        data.forEach(d => {{ d.date = parseDate(d.date); }});
        
        const x1 = d3.scaleTime().domain(d3.extent(data, d => d.date)).range([0, width]);
        const y1 = d3.scaleLinear().domain([0, d3.max(data, d => d.cpi)]).range([height, 0]);
        
        svg1.append("path")
            .datum(data)
            .attr("fill", "none")
            .attr("stroke", "red")
            .attr("stroke-width", 1.5)
            .attr("d", d3.line().x(d => x1(d.date)).y(d => y1(d.cpi)));
        
        svg1.append("g").attr("transform", `translate(0,${{height}})`).call(d3.axisBottom(x1));
        svg1.append("g").call(d3.axisLeft(y1));
        svg1.append("text").attr("x", width/2).attr("y", -5).text("Inflacja CPI [%]");
        
        // Wykres 2: USD
        const svg2 = d3.select("#chart2").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
        
        const y2 = d3.scaleLinear().domain([0, d3.max(data, d => d.usd)]).range([height, 0]);
        
        svg2.append("path")
            .datum(data)
            .attr("fill", "none")
            .attr("stroke", "blue")
            .attr("stroke-width", 1.5)
            .attr("d", d3.line().x(d => x1(d.date)).y(d => y2(d.usd)));
        
        svg2.append("g").attr("transform", `translate(0,${{height}})`).call(d3.axisBottom(x1));
        svg2.append("g").call(d3.axisLeft(y2));
        svg2.append("text").attr("x", width/2).attr("y", -5).text("Kurs USD/PLN");
        
        // Wykres 3: Scatter
        const svg3 = d3.select("#chart3").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", 300)
            .append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
        
        const x3 = d3.scaleLinear().domain([0, d3.max(segData, d => d.cpi)]).range([0, width]);
        const y3 = d3.scaleLinear().domain([0, d3.max(segData, d => d.usd)]).range([250, 0]);
        const colors = ["#FF5733", "#33C3FF", "#33FF77"];
        
        svg3.selectAll("circle")
            .data(segData)
            .enter().append("circle")
            .attr("cx", d => x3(d.cpi))
            .attr("cy", d => y3(d.usd))
            .attr("r", 4)
            .attr("fill", d => colors[d.cluster])
            .attr("opacity", 0.7);
        
        svg3.append("g").attr("transform", "translate(0,250)").call(d3.axisBottom(x3));
        svg3.append("g").call(d3.axisLeft(y3));
        svg3.append("text").attr("x", width/2).attr("y", 290).text("CPI [%]");
    </script>
</body>
</html>"""

# === EKSPORT ===
with open("dashboard_08_d3_js.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✓ Zapisano: dashboard_08_d3_js.html")
print("⚠ D3.js wymaga przeglądarki do wyświetlenia")
print("  Dla PNG/PDF użyj narzędzi jak puppeteer/playwright")
