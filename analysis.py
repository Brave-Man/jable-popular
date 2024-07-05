import pandas as pd

pd.set_option("colheader_justify", "center")  # FOR TABLE <th>

html_string = """
<html>
  <head><title>Jable.tv Most Hot videos!</title></head>
  <link href="./table_style.css" rel="stylesheet" />
  <script src="./sortable.min.js"></script>    
  <body>
  <a href="all.html"><button>All data</button></a>
  <a href="most_like_200.html"><button>most_like_200</button></a>
  <a href="most_like_actors_200.html"><button>most_like_actors_200</button></a>
  <div>
    {table}
  </div>
  </body>
</html>
"""


def output(filename, df):
    print(df.head())
    with open(filename, "w", encoding="utf-8") as f:
        f.write(
            html_string.format(table=df.to_html(classes="sortable", render_links=True))
        )


df = pd.read_csv("data.csv")

output("docs/all.html", df)

most_like_200 = df.sort_values(by=["likes", "looks"], ascending=False).head(200)

output("docs/most_like_200.html", most_like_200)

most_like_actors_200 = (
    df.groupby(["actor"])
    .sum()
    .sort_values(by=["likes", "looks"], ascending=False)
    .head(200)
)

output("docs/most_like_actors_200.html", most_like_actors_200)
