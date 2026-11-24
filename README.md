# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/yiw8551/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/yiw8551/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

`main.py` is a self-contained Python 3 program (standard library only, fully
deterministic, no network or external files) that renders a newspaper-style
front page summarising the world news of Tuesday 24 November 2026 in a single
1024x1024 PNG. It implements its own PNG encoder and its own 5x7 bitmap font,
then lays out a bold masthead ("THE DAY IN ONE IMAGE"), six numbered story
tiles, and a sources footer. The six stories are: (1) Dmitry Medvedev floats a
preventive nuclear strike in a journal article, saying Ukraine and NATO crossed
lines that could justify a first strike and that the decision rests with Putin;
(2) Nvidia's board brings back co-founder Jensen Huang as CEO 11 days after he
resigned, with Trump backing his return and shares jumping about 30%;
(3) Sanofi agrees to buy US biotech Insmed for $41 billion ($175 a share in
cash), the biggest biotech deal in nearly three years; (4) the UK recognises
the Rohingya genocide after the ICJ ruling, sanctioning five senior Myanmar
officers and planning a jet-fuel ban; (5) Virginia and Oregon sue Musk's
SpaceX, alleging Grok's "spicy mode" produced sexualised images, including of
children, after safeguards were stripped out; and (6) Mediazona and Meduza's
analysis of leaked Russian registry data puts registered Russian military
deaths at about 490,000, with the true total modelled above 700,000, which
Rosstat denies.

## Run it

```
python3 main.py
```

This writes `entry.png` to `/output/` if that directory exists, otherwise to
`./output/`. Running it twice produces byte-identical output.

<sub>Entered on [make.fun](https://make.fun/?ref=azfjxkfk&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
