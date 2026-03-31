"""Company engineering blog RSS feeds."""

RSS_FEEDS: list[dict[str, str]] = [
    {"name": "AWS Architecture Blog", "xmlUrl": "https://aws.amazon.com/blogs/architecture/feed/", "htmlUrl": "https://aws.amazon.com/blogs/architecture/"},
    {"name": "AWS Machine Learning Blog", "xmlUrl": "https://aws.amazon.com/blogs/machine-learning/feed/", "htmlUrl": "https://aws.amazon.com/blogs/machine-learning/"},
    {"name": "GitHub Engineering Blog", "xmlUrl": "https://github.blog/engineering.atom", "htmlUrl": "https://github.blog/category/engineering/"},
    {"name": "OpenAI Blog", "xmlUrl": "https://openai.com/blog/rss.xml", "htmlUrl": "https://openai.com/blog"},
    {"name": "Google DeepMind Blog", "xmlUrl": "https://deepmind.google/blog/rss.xml", "htmlUrl": "https://deepmind.google/blog"},
    {"name": "Meta Engineering Blog", "xmlUrl": "https://engineering.fb.com/feed/", "htmlUrl": "https://engineering.fb.com"},
    {"name": "Cloudflare Blog", "xmlUrl": "https://blog.cloudflare.com/rss/", "htmlUrl": "https://blog.cloudflare.com"},
    {"name": "Stripe Engineering Blog", "xmlUrl": "https://stripe.com/blog/feed.rss", "htmlUrl": "https://stripe.com/blog/engineering"},
    {"name": "Spotify Engineering", "xmlUrl": "https://engineering.atspotify.com/feed/", "htmlUrl": "https://engineering.atspotify.com"},
    {"name": "Dropbox Tech Blog", "xmlUrl": "https://dropbox.tech/feed", "htmlUrl": "https://dropbox.tech"},
]
