"""Tests for Whop clipping campaigns integration and earnings tracking."""
import os, sys, tempfile
os.environ["PEAKCUT_DATA"] = tempfile.mkdtemp(prefix="pc-whop-")
sys.path.insert(0, ".")
from studio import db, whop, creators, auth, ctx
db.init()

fails = []
def check(n, got, want=True):
    ok = want(got) if callable(want) else got == want
    print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"   got {got!r}"))
    ok or fails.append(n)

# 1. Directory of campaigns
camps = whop.list_campaigns()
check("campaigns loaded", len(camps) >= 6, True)
adin = whop.get_campaign("whop_adin_ross")
check("adin ross campaign found", adin is not None, True)
check("adin ross cpm", adin["cpm"], 8.50)
check("adin ross platforms", "tiktok" in adin["platforms"], True)

# Filter by category
fitness = whop.list_campaigns(category="Fitness & Gym")
check("category filter", any(c["id"] == "whop_sam_sulek" for c in fitness), True)
check("category filter excludes other", all(c["category"] == "Fitness & Gym" for c in fitness), True)

# Filter by query
query_match = whop.list_campaigns(query="Speed")
check("query search", any(c["id"] == "whop_ishowspeed" for c in query_match), True)

# 2. 1-Click start clipping campaign
user = auth.local_user().id
ctx.set_uid(user)
res = whop.start_clipping_campaign("whop_adin_ross", user=user)
check("creator created", bool(res.get("creator_id")), True)
cr = creators.get(res["creator_id"])
check("creator name matches", cr["name"], "Adin Ross")
check("rate per 1k set from cpm", float(cr["rate_per_1k"]), 8.50)
check("post footer set from campaign", "Whop Rewards" in cr["post_footer"], True)

# 3. Earnings summary
# Add simulated views to creator
creators.update(cr["id"], {"total_views": 100_000})
summary = whop.earnings_summary(user=user)
check("active campaigns count", summary["active_campaigns"] >= 1, True)
check("total views tracked", summary["total_views"], 100_000)
# 100k views @ $8.50 CPM = $850.00
check("estimated earnings calculated", summary["estimated_earnings"], 850.00)

print("ALL PASSED" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
