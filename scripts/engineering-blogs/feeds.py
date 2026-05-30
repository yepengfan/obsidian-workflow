"""Company engineering blog RSS feeds."""

RSS_FEEDS: list[dict[str, str]] = [
    # ── Cloud / Infra ──
    {"name": "AWS Architecture Blog", "xmlUrl": "https://aws.amazon.com/blogs/architecture/feed/", "htmlUrl": "https://aws.amazon.com/blogs/architecture/"},
    {"name": "AWS Machine Learning Blog", "xmlUrl": "https://aws.amazon.com/blogs/machine-learning/feed/", "htmlUrl": "https://aws.amazon.com/blogs/machine-learning/"},
    {"name": "Cloudflare Blog", "xmlUrl": "https://blog.cloudflare.com/rss/", "htmlUrl": "https://blog.cloudflare.com"},
    {"name": "HashiCorp Blog", "xmlUrl": "https://www.hashicorp.com/blog/feed.xml", "htmlUrl": "https://www.hashicorp.com/blog"},
    {"name": "Grafana Blog", "xmlUrl": "https://grafana.com/blog/index.xml", "htmlUrl": "https://grafana.com/blog"},
    {"name": "Fly.io Blog", "xmlUrl": "https://fly.io/blog/feed.xml", "htmlUrl": "https://fly.io/blog"},
    {"name": "Elastic Blog", "xmlUrl": "https://www.elastic.co/blog/feed", "htmlUrl": "https://www.elastic.co/blog"},
    # ── AI / Research ──
    {"name": "OpenAI Blog", "xmlUrl": "https://openai.com/blog/rss.xml", "htmlUrl": "https://openai.com/blog"},
    {"name": "Google DeepMind Blog", "xmlUrl": "https://deepmind.google/blog/rss.xml", "htmlUrl": "https://deepmind.google/blog"},
    # ── Big Tech Engineering ──
    {"name": "Meta Engineering Blog", "xmlUrl": "https://engineering.fb.com/feed/", "htmlUrl": "https://engineering.fb.com"},
    {"name": "GitHub Engineering Blog", "xmlUrl": "https://github.blog/engineering.atom", "htmlUrl": "https://github.blog/category/engineering/"},
    {"name": "Netflix Tech Blog", "xmlUrl": "https://netflixtechblog.com/feed", "htmlUrl": "https://netflixtechblog.com"},
    {"name": "Microsoft DevBlogs", "xmlUrl": "https://devblogs.microsoft.com/engineering-at-microsoft/feed/", "htmlUrl": "https://devblogs.microsoft.com/engineering-at-microsoft/"},
    # ── Unicorn Engineering ──
    {"name": "Canva Engineering", "xmlUrl": "https://www.canva.dev/blog/engineering/feed.xml", "htmlUrl": "https://www.canva.dev/blog/engineering"},
    {"name": "Lyft Engineering", "xmlUrl": "https://eng.lyft.com/feed", "htmlUrl": "https://eng.lyft.com"},
    {"name": "Instacart Engineering", "xmlUrl": "https://tech.instacart.com/feed", "htmlUrl": "https://tech.instacart.com"},
    {"name": "Etsy Engineering", "xmlUrl": "https://www.etsy.com/codeascraft/rss", "htmlUrl": "https://www.etsy.com/codeascraft"},
    {"name": "Square Engineering", "xmlUrl": "https://developer.squareup.com/blog/rss.xml", "htmlUrl": "https://developer.squareup.com/blog"},
    # ── DevTools ──
    {"name": "Vercel Blog", "xmlUrl": "https://vercel.com/atom", "htmlUrl": "https://vercel.com/blog"},
    {"name": "GitLab Blog", "xmlUrl": "https://about.gitlab.com/atom.xml", "htmlUrl": "https://about.gitlab.com/blog"},
    # ── Fintech / SaaS ──
    {"name": "Stripe Engineering Blog", "xmlUrl": "https://stripe.com/blog/feed.rss", "htmlUrl": "https://stripe.com/blog/engineering"},
    {"name": "Slack Engineering", "xmlUrl": "https://slack.engineering/feed/", "htmlUrl": "https://slack.engineering"},
    {"name": "Databricks Blog", "xmlUrl": "https://www.databricks.com/feed", "htmlUrl": "https://www.databricks.com/blog"},
    # ── Data / Storage ──
    {"name": "MongoDB Blog", "xmlUrl": "https://www.mongodb.com/company/blog/rss", "htmlUrl": "https://www.mongodb.com/blog"},
    {"name": "Spotify Engineering", "xmlUrl": "https://engineering.atspotify.com/feed/", "htmlUrl": "https://engineering.atspotify.com"},
    {"name": "Dropbox Tech Blog", "xmlUrl": "https://dropbox.tech/feed", "htmlUrl": "https://dropbox.tech"},
    # ── Security ──
    {"name": "Trail of Bits", "xmlUrl": "https://blog.trailofbits.com/index.xml", "htmlUrl": "https://blog.trailofbits.com"},
]
