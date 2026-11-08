# Contributing to NexPrice

Rules: no emoji anywhere (code, docs, commits). No AI co-author trailers in commits. Run git config core.hooksPath .githooks after cloning.

Work on develop. Tests must pass offline (pytest), ruff clean, and python scripts/check_no_emoji.py clean. Only fetch pages the user asked for; respect robots.txt and rate limits; prefer official price APIs; never bypass captchas.

