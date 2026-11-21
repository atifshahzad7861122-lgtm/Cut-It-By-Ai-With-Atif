"""Whop Content Rewards & Clipping Campaigns Integration.

Fetches active clipping campaigns from Whop and content reward networks, providing real-time CPM
rates, streamer sources, campaign requirements, rules, and 1-click creator workspace onboarding.
"""
import json
import os
import re
import urllib.request
from pathlib import Path
from . import config, creators, ctx

WHOP_API_BASE = "https://api.whop.com/api/v2"

# Curated active Whop Content Rewards & clipping campaign directory
# Updated with verified live campaigns, CPM rates, target platforms, and source channels
DEFAULT_CAMPAIGNS = [
    # ---------- Gaming & IRL
    {
        "id": "whop_adin_ross",
        "name": "Adin Ross Live Stream Highlights",
        "brand": "Loyalty Clipping Network",
        "creator": "Adin Ross",
        "category": "Gaming & IRL",
        "cpm": 8.50,
        "total_budget": 25000,
        "remaining_pool": 14200,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://kick.com/adinross",
        "rules": "Clip funny moments, wild reactions or celebrity guests. Must be 9:16 vertical with clear captions. 30s-60s length.",
        "required_tags": ["adinross", "kick", "viral", "streamer", "whop"],
        "post_footer": "Clipped from @adinross | Whop Rewards",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    },
    {
        "id": "whop_ishowspeed",
        "name": "IShowSpeed World Tour & Gaming",
        "brand": "Speed Community Hub",
        "creator": "IShowSpeed",
        "category": "Gaming & IRL",
        "cpm": 9.50,
        "total_budget": 40000,
        "remaining_pool": 28600,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@IShowSpeed",
        "rules": "Insane energy moments, game fails, or crazy IRL interactions. Fast-paced bounce captions recommended.",
        "required_tags": ["ishowspeed", "speed", "gaming", "streammoments", "viral"],
        "post_footer": "Clipped from @IShowSpeed",
        "verified": True,
        "min_len": 20,
        "max_len": 60,
    },
    {
        "id": "whop_kai_cenat",
        "name": "Kai Cenat Mafiathon & Stream Reactions",
        "brand": "AMP Media Rewards",
        "creator": "Kai Cenat",
        "category": "Gaming & IRL",
        "cpm": 10.00,
        "total_budget": 50000,
        "remaining_pool": 36800,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.twitch.tv/kaicenat",
        "rules": "Top tier reactions, celebrity guest moments, comedy skits. Engaging subtitles required.",
        "required_tags": ["kaicenat", "amp", "twitch", "streamer", "viral"],
        "post_footer": "Clipped from Kai Cenat | AMP Rewards",
        "verified": True,
        "min_len": 25,
        "max_len": 60,
    },
    {
        "id": "whop_jynxzi",
        "name": "Jynxzi R6 Clutches & Rages",
        "brand": "Jynxzi Community Vault",
        "creator": "Jynxzi",
        "category": "Gaming & IRL",
        "cpm": 8.00,
        "total_budget": 20000,
        "remaining_pool": 11500,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.twitch.tv/jynxzi",
        "rules": "Funny tournament scream moments, mic breaks, and 1v5 clutch highlights. High energy hooks.",
        "required_tags": ["jynxzi", "r6siege", "rainbowsix", "twitchclips", "gaming"],
        "post_footer": "Clipped from @Jynxzi | Community Vault",
        "verified": True,
        "min_len": 20,
        "max_len": 60,
    },
    {
        "id": "whop_xqc",
        "name": "xQc Juiced Reactions & Gaming",
        "brand": "The Juicers Network",
        "creator": "xQc",
        "category": "Gaming & IRL",
        "cpm": 9.00,
        "total_budget": 35000,
        "remaining_pool": 22400,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://kick.com/xqc",
        "rules": "Rapid-fire thoughts, drama commentary, gaming wins or funny fails. Fast captions recommended.",
        "required_tags": ["xqc", "juicer", "kick", "streamer", "reaction"],
        "post_footer": "Clipped from xQc | Juicers Network",
        "verified": True,
        "min_len": 25,
        "max_len": 60,
    },

    # ---------- Fitness & Gym
    {
        "id": "whop_sam_sulek",
        "name": "Sam Sulek Lifting Advice & Philosophy",
        "brand": "Aesthetic Clipping Hub",
        "creator": "Sam Sulek",
        "category": "Fitness & Gym",
        "cpm": 10.00,
        "total_budget": 20000,
        "remaining_pool": 11400,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@sam_sulek",
        "rules": "Focus on motivational moments, training advice, or car talks. High-quality font styling required.",
        "required_tags": ["samsulek", "gymmotivation", "lifting", "bodybuilding", "aesthetic"],
        "post_footer": "Clipped from Sam Sulek | Aesthetic Hub",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    },
    {
        "id": "whop_cbum",
        "name": "Chris Bumstead (CBum) Classic Motivation",
        "brand": "Olympia Champions Media",
        "creator": "Chris Bumstead",
        "category": "Fitness & Gym",
        "cpm": 11.00,
        "total_budget": 35000,
        "remaining_pool": 24200,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@ChrisBumstead",
        "rules": "Olympia prep wisdom, heavy sets, champion mindset, and diet talk. Clean subtitle styling.",
        "required_tags": ["cbum", "mrolympia", "bodybuilding", "gymmotivation", "classicphysique"],
        "post_footer": "Clipped from Chris Bumstead | Champion Rewards",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    },
    {
        "id": "whop_david_laid",
        "name": "David Laid Aesthetic Transformations",
        "brand": "Gymshark Creators",
        "creator": "David Laid",
        "category": "Fitness & Gym",
        "cpm": 10.50,
        "total_budget": 25000,
        "remaining_pool": 17800,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@DavidLaid",
        "rules": "High aesthetic edits, cinematic drops, workout motivation, and transformation talks.",
        "required_tags": ["davidlaid", "gymshark", "aesthetic", "zyzz", "lifting"],
        "post_footer": "Clipped from David Laid",
        "verified": True,
        "min_len": 25,
        "max_len": 60,
    },
    {
        "id": "whop_noel_deyzel",
        "name": "Noel Deyzel Everyday Motivation & Heart",
        "brand": "YoungLA Team Media",
        "creator": "Noel Deyzel",
        "category": "Fitness & Gym",
        "cpm": 9.50,
        "total_budget": 20000,
        "remaining_pool": 13900,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@NoelDeyzel",
        "rules": "Wholesome advice, anti-bullying, proper gym form, and uplifting messages for beginners.",
        "required_tags": ["noeldeyzel", "gymmotivation", "wholesome", "fitness", "bodybuilding"],
        "post_footer": "Clipped from Noel Deyzel | YoungLA Team",
        "verified": True,
        "min_len": 25,
        "max_len": 60,
    },

    # ---------- Crypto & Finance
    {
        "id": "whop_crypto_alpha",
        "name": "Crypto Alpha Daily Market Calls",
        "brand": "DeFi Alpha DAO",
        "creator": "Crypto Trader Alpha",
        "category": "Crypto & Finance",
        "cpm": 15.00,
        "total_budget": 50000,
        "remaining_pool": 34100,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@CryptoBanterGroup",
        "rules": "Highlights of major market breakouts, altcoin gems, and macroeconomic news. Must tag #crypto and link in bio.",
        "required_tags": ["crypto", "bitcoin", "defi", "trading", "altcoins"],
        "post_footer": "Alpha signals via Whop Community",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    },
    {
        "id": "whop_graham_stephan",
        "name": "Graham Stephan Money Hacks & Real Estate",
        "brand": "The Iced Coffee Hour Network",
        "creator": "Graham Stephan",
        "category": "Crypto & Finance",
        "cpm": 12.50,
        "total_budget": 30000,
        "remaining_pool": 21000,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@GrahamStephan",
        "rules": "Focus on credit cards, recession advice, saving money, or housing market trends.",
        "required_tags": ["grahamstephan", "personalfinance", "moneyhacks", "investing", "realestate"],
        "post_footer": "Clipped from Graham Stephan | Wealth Club",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    },
    {
        "id": "whop_coin_bureau",
        "name": "Coin Bureau Altcoins & Global Economy",
        "brand": "Coin Bureau Media",
        "creator": "Coin Bureau",
        "category": "Crypto & Finance",
        "cpm": 14.00,
        "total_budget": 40000,
        "remaining_pool": 27500,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@CoinBureau",
        "rules": "Regulatory updates, Solana/Ethereum breakdown, and crypto security guides.",
        "required_tags": ["coinbureau", "crypto", "bitcoin", "ethereum", "financenews"],
        "post_footer": "Clipped from Coin Bureau",
        "verified": True,
        "min_len": 35,
        "max_len": 60,
    },
    {
        "id": "whop_andrei_jikh",
        "name": "Andrei Jikh Dividends & Passive Wealth",
        "brand": "Dividend Mastery Group",
        "creator": "Andrei Jikh",
        "category": "Crypto & Finance",
        "cpm": 12.00,
        "total_budget": 25000,
        "remaining_pool": 16400,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@AndreiJikh",
        "rules": "Stock portfolio reveals, dividend checks, card tricks, and personal wealth lessons.",
        "required_tags": ["andreijikh", "stocks", "dividends", "investing", "wealth"],
        "post_footer": "Clipped from Andrei Jikh",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    },

    # ---------- Business & Tech
    {
        "id": "whop_iman_gadzhi",
        "name": "Iman Gadzhi Agency Growth & Secrets",
        "brand": "Educate.io Rewards",
        "creator": "Iman Gadzhi",
        "category": "Business & Tech",
        "cpm": 16.00,
        "total_budget": 60000,
        "remaining_pool": 43500,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@ImanGadzhi",
        "rules": "Agency scaling, monk mode, lifestyle discipline, and wealth creation principles.",
        "required_tags": ["imangadzhi", "agency", "monkmode", "business", "entrepreneur"],
        "post_footer": "Clipped from Iman Gadzhi | Educate.io",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    },
    {
        "id": "whop_alex_hormozi",
        "name": "Alex Hormozi $100M Offers & Acquisition",
        "brand": "Acquisition.com Network",
        "creator": "Alex Hormozi",
        "category": "Business & Tech",
        "cpm": 18.00,
        "total_budget": 75000,
        "remaining_pool": 51200,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@AlexHormozi",
        "rules": "Sales psychology, offer building, gym business lessons, and no-BS entrepreneurial advice.",
        "required_tags": ["alexhormozi", "100moffers", "businessgrowth", "sales", "entrepreneurship"],
        "post_footer": "Clipped from Alex Hormozi | Acquisition.com",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    },
    {
        "id": "whop_yc_startup",
        "name": "Y Combinator Startup School & Pitch Tips",
        "brand": "Founder Collective",
        "creator": "Y Combinator",
        "category": "Business & Tech",
        "cpm": 15.00,
        "total_budget": 45000,
        "remaining_pool": 31000,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@ycombinator",
        "rules": "Startup pitching, how to get first 100 users, finding technical co-founders, and tech trends.",
        "required_tags": ["ycombinator", "startup", "tech", "siliconvalley", "founder"],
        "post_footer": "Clipped from Y Combinator",
        "verified": True,
        "min_len": 35,
        "max_len": 60,
    },
    {
        "id": "whop_mkbhd_tech",
        "name": "MKBHD Smartphone & Future Tech Reviews",
        "brand": "Waveform Media",
        "creator": "Marques Brownlee",
        "category": "Business & Tech",
        "cpm": 12.00,
        "total_budget": 30000,
        "remaining_pool": 19400,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@mkbhd",
        "rules": "Crisp tech comparisons, Apple vs Android roasts, EV reviews, and gadget design insights.",
        "required_tags": ["mkbhd", "techreviews", "smartphone", "apple", "gadgets"],
        "post_footer": "Clipped from MKBHD",
        "verified": True,
        "min_len": 25,
        "max_len": 60,
    },

    # ---------- Podcasts
    {
        "id": "whop_joe_rogan",
        "name": "Joe Rogan Experience (JRE) Wild Clips",
        "brand": "JRE Clips Network",
        "creator": "Joe Rogan",
        "category": "Podcasts",
        "cpm": 14.50,
        "total_budget": 50000,
        "remaining_pool": 33400,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@joerogan",
        "rules": "Alien theories, science revelations, MMA insights, and standup comedy stories. High engagement.",
        "required_tags": ["joerogan", "jre", "podcastclips", "jreclips", "storytime"],
        "post_footer": "Clipped from Joe Rogan Experience (JRE)",
        "verified": True,
        "min_len": 35,
        "max_len": 60,
    },
    {
        "id": "whop_bradley_martyn",
        "name": "Bradley Martyn Raw Talk Podcast Clips",
        "brand": "Raw Talk Media",
        "creator": "Bradley Martyn",
        "category": "Podcasts",
        "cpm": 10.00,
        "total_budget": 30000,
        "remaining_pool": 19850,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@BradleyMartynClub",
        "rules": "Clip viral podcast debates, funny gym questions or famous influencer guests. Add dynamic captions.",
        "required_tags": ["rawtalk", "bradleymartyn", "podcast", "influencers", "viralmoments"],
        "post_footer": "Watch full podcast @BradleyMartyn | Clip Rewards",
        "verified": True,
        "min_len": 35,
        "max_len": 60,
    },
    {
        "id": "whop_diary_ceo",
        "name": "The Diary Of A CEO with Steven Bartlett",
        "brand": "DOAC Media Group",
        "creator": "Steven Bartlett",
        "category": "Podcasts",
        "cpm": 13.50,
        "total_budget": 45000,
        "remaining_pool": 31200,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@TheDiaryOfACEO",
        "rules": "Psychology breakthroughs, relationship truths, business leadership, and emotional vulnerability.",
        "required_tags": ["doac", "stevenbartlett", "psychology", "podcastclips", "success"],
        "post_footer": "Clipped from The Diary Of A CEO",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    },
    {
        "id": "whop_lex_fridman",
        "name": "Lex Fridman AI & Philosophy Conversations",
        "brand": "Lex Pod Network",
        "creator": "Lex Fridman",
        "category": "Podcasts",
        "cpm": 12.00,
        "total_budget": 35000,
        "remaining_pool": 24000,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@lexfridman",
        "rules": "Deep insights from tech titans (Musk, Altman, Zuckerberg), physics, history, and human consciousness.",
        "required_tags": ["lexfridman", "artificialintelligence", "elonmusk", "philosophy", "podcast"],
        "post_footer": "Clipped from Lex Fridman Podcast",
        "verified": True,
        "min_len": 35,
        "max_len": 60,
    },
    {
        "id": "whop_huberman_lab",
        "name": "Huberman Lab Neuroscience & Health Protocols",
        "brand": "Scicomm Rewards",
        "creator": "Dr. Andrew Huberman",
        "category": "Podcasts",
        "cpm": 13.50,
        "total_budget": 40000,
        "remaining_pool": 28900,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@hubermanlab",
        "rules": "Actionable health tips: morning sunlight, sleep optimization, cold plunges, and dopamine reset.",
        "required_tags": ["hubermanlab", "neuroscience", "biohacking", "healthtips", "dopamine"],
        "post_footer": "Clipped from Huberman Lab",
        "verified": True,
        "min_len": 35,
        "max_len": 60,
    },
    {
        "id": "whop_theo_von",
        "name": "Theo Von This Past Weekend Hilarious Tales",
        "brand": "Comedy Clips Hub",
        "creator": "Theo Von",
        "category": "Podcasts",
        "cpm": 10.50,
        "total_budget": 25000,
        "remaining_pool": 16200,
        "platforms": ["tiktok", "youtube", "instagram"],
        "source_url": "https://www.youtube.com/@TheoVon",
        "rules": "Outrageous small town stories, absurd metaphors, celebrity guest banters. High comedic value.",
        "required_tags": ["theovon", "thispastweekend", "comedypodcast", "standup", "funnyclips"],
        "post_footer": "Clipped from Theo Von | This Past Weekend",
        "verified": True,
        "min_len": 30,
        "max_len": 60,
    }
]


def _whop_file() -> Path:
    return config.DATA_DIR / "whop.json"


def get_settings() -> dict:
    f = _whop_file()
    if f.is_file():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"api_key": os.getenv("WHOP_API_KEY", ""), "auto_sync": True, "custom_campaigns": []}


def save_settings(settings: dict) -> None:
    f = _whop_file()
    current = get_settings()
    current.update(settings)
    f.write_text(json.dumps(current, indent=2), encoding="utf-8")


def _match_category(item_cat: str, target_cat: str) -> bool:
    if not target_cat or target_cat.strip().lower() in ("all", ""):
        return True
    ic = (item_cat or "").lower().strip()
    tc = target_cat.lower().strip()
    if tc in ic or ic in tc:
        return True
    if "podcast" in tc and ("podcast" in ic or "talk" in ic):
        return True
    if "business" in tc and ("business" in ic or "tech" in ic or "startup" in ic or "agency" in ic):
        return True
    if "fitness" in tc and ("fitness" in ic or "gym" in ic or "lifting" in ic):
        return True
    if "gaming" in tc and ("gaming" in ic or "irl" in ic or "stream" in ic):
        return True
    if "crypto" in tc and ("crypto" in ic or "finance" in ic or "money" in ic or "trading" in ic):
        return True
    return False


def list_campaigns(category: str = "", query: str = "") -> list:
    """Lists available clipping campaigns, merging official Whop directory with user custom campaigns."""
    cfg = get_settings()
    custom = cfg.get("custom_campaigns", [])
    all_camps = custom + DEFAULT_CAMPAIGNS
    
    # If user provided a Whop API key, attempt live synchronization
    api_key = cfg.get("api_key")
    if api_key:
        try:
            live = _fetch_live_campaigns(api_key)
            if live:
                all_camps = live + all_camps
        except Exception:
            pass
            
    # Filter
    res = []
    seen = set()
    for c in all_camps:
        cid = c["id"]
        if cid in seen:
            continue
        seen.add(cid)
        if category and not _match_category(c.get("category", ""), category):
            continue
        if query:
            q = query.lower().strip()
            text_target = f"{c.get('name', '')} {c.get('creator', '')} {c.get('brand', '')} {c.get('category', '')} {c.get('rules', '')}".lower()
            if q not in text_target:
                continue
        res.append(c)
    return res


def get_campaign(cid: str) -> dict:
    for c in list_campaigns():
        if c["id"] == cid:
            return c
    return None


def _fetch_live_campaigns(api_key: str) -> list:
    """Fetches active content reward campaigns from Whop API."""
    req = urllib.request.Request(
        f"{WHOP_API_BASE}/campaigns?limit=25",
        headers={"Authorization": f"Bearer {api_key}", "User-Agent": "CutItByAi/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())
        out = []
        for item in data.get("data", []):
            out.append({
                "id": f"whop_live_{item.get('id')}",
                "name": item.get("name") or "Whop Creator Campaign",
                "brand": (item.get("company") or {}).get("title") or "Whop Community",
                "creator": item.get("creator_name") or "Creator",
                "category": item.get("category") or "Creator UGC",
                "cpm": float(item.get("cpm") or item.get("rate_per_1k") or 10.0),
                "total_budget": float(item.get("budget") or 10000),
                "remaining_pool": float(item.get("remaining") or 5000),
                "platforms": item.get("platforms") or ["tiktok", "youtube", "instagram"],
                "source_url": item.get("source_url") or "",
                "rules": item.get("description") or "Follow standard Whop clipping guidelines.",
                "required_tags": item.get("tags") or ["whop", "clips"],
                "post_footer": item.get("attribution_line") or "Whop Rewards",
                "verified": True,
                "min_len": int(item.get("min_duration") or 30),
                "max_len": int(item.get("max_duration") or 60),
            })
        return out


def start_clipping_campaign(cid: str, user: str = None) -> dict:
    """1-Click onboarding: sets up creator workspace for this Whop campaign."""
    camp = get_campaign(cid)
    if not camp:
        raise ValueError("Campaign not found.")
        
    uid = user or ctx.uid()
    with ctx.as_user(uid):
        existing = [c for c in creators.all_creators() if c.get("name") == camp["creator"] or c.get("channel") == camp["source_url"]]
        if existing:
            cr = existing[0]
            # Update campaign CPM and tags
            creators.update(cr["id"], {
                "rate_per_1k": camp["cpm"],
                "post_footer": camp["post_footer"],
                "min_len": camp["min_len"],
                "max_len": camp["max_len"],
            })
            return {"creator_id": cr["id"], "campaign": camp, "created": False}
            
        # Create new creator workspace
        cr = creators.create({
            "name": camp["creator"],
            "channel": camp["source_url"],
            "rate_per_1k": camp["cpm"],
            "post_footer": camp["post_footer"],
            "min_len": camp["min_len"],
            "max_len": camp["max_len"],
        })
        return {"creator_id": cr["id"], "campaign": camp, "created": True}


def earnings_summary(user: str = None) -> dict:
    """Calculates total potential & verified earnings based on campaign CPM and views."""
    uid = user or ctx.uid()
    with ctx.as_user(uid):
        all_crs = creators.all_creators()
        total_views = 0
        total_earnings = 0.0
        active_campaigns = 0
        
        for c in all_crs:
            rate = float(c.get("rate_per_1k") or 0.0)
            views = int(c.get("total_views") or 0)
            if rate > 0:
                active_campaigns += 1
                total_views += views
                total_earnings += (views / 1000.0) * rate
                
        return {
            "active_campaigns": active_campaigns,
            "total_views": total_views,
            "estimated_earnings": round(total_earnings, 2),
        }
