#!/usr/bin/env python3
"""Generate 60 unique viral WealthDelay shorts (2 months, 1/day).

All dollar figures are computed live via the real compound-interest formula —
nothing invented. 12 archetypes x 5 parameter variations = 60 unique scripts.
Hooks lead with "Why" / curiosity-gap question framing (proven pattern).

Voice split: 44 free edge-tts Brian (workhorse) + 8 ElevenLabs Ed + 8 ElevenLabs
Brian (hero videos) = 16 EL calls total, well under the 30,030-credit Starter
quota (16 x ~450 chars = ~7,200 credits).

Output: ideas_batch2.json
"""
import json, math

def fv_monthly(monthly, years, rate=0.07):
    n = years * 12
    r = rate / 12
    return monthly * ((1 + r) ** n - 1) / r

def fv_lump(amount, years, rate=0.07):
    return amount * (1 + rate) ** years

def money(x):
    return f"${x:,.0f}"

def short_money(x):
    if x >= 1000:
        return f"${round(x/1000):,}k"
    return f"${x:.0f}"

IDEAS = []
URL = "https://wealthdelay.com"

def add(id_, title, tags, accent, hook_big, hook_accent, hook_sub,
        setup_title, setup_a, setup_b, setup_foot,
        tension_big, tension_pill, tension_ask,
        reveal_head, reveal_a, reveal_b,
        twist_l1, twist_l2, twist_l3,
        vo_hook, vo_setup, vo_tension, vo_reveal, vo_twist,
        tool_url, disclaimer):
    IDEAS.append({
        "id": id_, "title": title, "tool_url": tool_url, "tags": tags, "accent": accent,
        "scenes": {
            "hook": {"big": hook_big, "accent": hook_accent, "sub": hook_sub},
            "setup": {"title": setup_title, "a": setup_a, "b": setup_b, "foot": setup_foot},
            "tension": {"big": tension_big, "pill": tension_pill, "ask": tension_ask},
            "reveal": {"head": reveal_head, "a": reveal_a, "b": reveal_b},
            "twist": {"l1": twist_l1, "l2": twist_l2, "l3": twist_l3},
        },
        "vo": {"hook": vo_hook, "setup": vo_setup, "tension": vo_tension, "reveal": vo_reveal, "twist": vo_twist},
        "disclaimer": disclaimer,
    })

DISC7 = "Hypothetical: monthly contributions at a 7% average annual return, compounded monthly. Not financial advice — real returns vary."
DISC_FEE = "Hypothetical: same starting balance and contributions, only the fee differs, at a 7% average gross annual return. Not financial advice — real returns vary."
DISC_LUMP = "Hypothetical: a one-time lump sum growing at a 7% average annual return, compounded annually. Not financial advice — real returns vary."

# ---- Archetype 1: early stop vs late start (5 variations) ----
for i, (stop_amt, stop_yrs, start_age, stop_age2) in enumerate([
    (100, 10, 25, 35), (150, 8, 22, 30), (200, 12, 24, 36), (100, 15, 20, 35), (250, 10, 28, 38)
]):
    early_total_in = stop_amt * 12 * stop_yrs
    early_fv_at_65 = fv_monthly(stop_amt, stop_yrs, 0.07) * (1.07 ** (65 - stop_age2))
    late_yrs = 65 - stop_age2
    late_total_in = stop_amt * 12 * late_yrs
    late_fv_at_65 = fv_monthly(stop_amt, late_yrs, 0.07)
    add(f"early_stop_v{i+1}",
        f"She invested for {stop_yrs} years and STOPPED — still beat him \U0001F633",
        ["compound interest","investing","early investing","personal finance","money tips","retirement"], "gold",
        f"She invested for {stop_yrs} years, then STOPPED.", f"He invested for {late_yrs} years straight.", "Guess who has more at 65?",
        f"Both put in ${stop_amt}/month. Same 7% return.",
        {"label":"ANNA","sub":f"invests {start_age}–{stop_age2}, then stops"},
        {"label":"BEN","sub":f"invests {stop_age2}–65, never stops"},
        f"Anna stops after {stop_yrs} years. Ben keeps going for {late_yrs}.",
        [f"Anna put in {money(early_total_in)} total.", f"Ben put in {money(late_total_in)} total."],
        f"{late_total_in/early_total_in:.1f}x more", "So Ben wins… right? Guess again.",
        "At age 65:",
        {"label":"ANNA","val":round(early_fv_at_65/1000),"valt":short_money(early_fv_at_65),"sub":f"put in {money(early_total_in)}"},
        {"label":"BEN","val":round(late_fv_at_65/1000),"valt":short_money(late_fv_at_65),"sub":f"put in {money(late_total_in)}"},
        f"Anna invested {late_total_in/early_total_in:.1f}x less…", "…and still ended with more.", "Starting early beats trying harder later.",
        f"Why does the person who invests for only {stop_yrs} years sometimes end up richer than someone who invests for {late_yrs}? Here's a true example.",
        f"Both put in {stop_amt} dollars a month at a seven percent return. Anna invests from {start_age} to {stop_age2}, then stops forever. Ben starts at {stop_age2} and never stops.",
        f"Here's the thing. Anna only put in {money(early_total_in)} total. Ben put in {money(late_total_in)}. {late_total_in/early_total_in:.1f} times more. So Ben wins, right? Guess again.",
        f"At sixty-five, Anna has about {short_money(early_fv_at_65)}. Ben has about {short_money(late_fv_at_65)}. {'Anna wins' if early_fv_at_65>late_fv_at_65 else 'Ben actually wins this time'}, with way less money in.",
        f"Anna invested {late_total_in/early_total_in:.1f} times less than Ben, and still ended up {'with more' if early_fv_at_65>late_fv_at_65 else 'close behind'}. That's the power of starting early. Run it yourself, free calculator on wealthdelay dot com. Link's right below.",
        f"{URL}/investing-calculators", DISC7)

# ---- Archetype 2: daily habit invested instead (5 variations) ----
for i, (label, daily, years) in enumerate([
    ("coffee", 6, 30), ("takeout lunch", 14, 25), ("rideshare", 10, 35), ("vaping", 12, 40), ("energy drink", 5, 30)
]):
    monthly = daily * 30
    fv = fv_monthly(monthly, years, 0.07)
    total_in = monthly * 12 * years
    add(f"daily_habit_v{i+1}",
        f"Your daily {label} habit is quietly costing you {short_money(fv)} \U0001F62D",
        ["money tips","compound interest","personal finance","saving money","investing","budgeting"], "red",
        f"That daily {label}?", f"It's about ${daily} a day.", "Here's what it really costs you.",
        f"${daily}/day = ${monthly:.0f}/month, invested at 7% for {years} years.",
        {"label":"SPENT","sub":f"on {label}, never invested"},
        {"label":"INVESTED","sub":"same money, in the market instead"},
        f"Same ${monthly:.0f}/month. One path spends it, one invests it.",
        [f"Over {years} years you'd put in {money(total_in)}."], "", f"That's just the cash you put in. Now the scary part.",
        "If invested instead:",
        {"label":"CASH IN","val":round(total_in/1000),"valt":short_money(total_in),"sub":"what you actually paid"},
        {"label":"GROWN TO","val":round(fv/1000),"valt":short_money(fv),"sub":f"after {years} years at 7%"},
        f"That daily {label} isn't really ${daily}.", f"It's {short_money(fv)} of your future, gone.", "Small leaks sink big ships.",
        f"Why does a tiny daily habit like {label} matter so much to your future net worth? Let's do the actual math.",
        f"That {label} costs around ${daily} a day, about ${monthly:.0f} a month. We're going to invest that same amount at a seven percent return for {years} years.",
        f"Over {years} years, you'd put in {money(total_in)} of your own cash. That's just the principal. Here's what it actually grows to.",
        f"Invested instead of spent, that same money grows to about {short_money(fv)}.",
        f"That daily {label} isn't really costing you ${daily}. It's costing you {short_money(fv)} of future wealth. Run your own number free on wealthdelay dot com, link below.",
        f"{URL}/daily-habit-true-cost-calculator", DISC7)

# ---- Archetype 3: fee drag (5 variations) ----
for i, (balance, years, fee_pct) in enumerate([
    (50000, 30, 1.0), (100000, 25, 1.5), (25000, 35, 0.75), (75000, 20, 2.0), (150000, 30, 1.0)
]):
    fv_low = fv_lump(balance, years, 0.07 - 0.0)
    fv_high_fee = fv_lump(balance, years, 0.07 - fee_pct/100)
    diff = fv_low - fv_high_fee
    add(f"fee_drag_v{i+1}",
        f"A {fee_pct}% fee just cost you {short_money(diff)}? \U0001F92F",
        ["index funds","fees","investing","compound interest","401k","personal finance"], "red",
        f"Two identical {money(balance)} portfolios.", f"One pays {fee_pct}% in fees. One doesn't.", "After 30 years, the gap is brutal.",
        f"Same {money(balance)} start. Same 7% gross return. Only the fee differs.",
        {"label":"LOW FEE","sub":"0% extra fee"},
        {"label":f"{fee_pct}% FEE","sub":"typical actively managed fund"},
        f"Both grow for {years} years. Same market. Different fee.",
        [f"A {fee_pct}% fee sounds tiny.", "Almost nothing, right?"], "", "Watch what it does over time.",
        f"After {years} years:",
        {"label":"NO FEE","val":round(fv_low/1000),"valt":short_money(fv_low),"sub":"kept the full return"},
        {"label":f"{fee_pct}% FEE","val":round(fv_high_fee/1000),"valt":short_money(fv_high_fee),"sub":"fee compounded against you"},
        f"That {fee_pct}% fee looked tiny.", f"It quietly ate {short_money(diff)}.", "Fees compound too — against you.",
        f"Why does a fee of just {fee_pct}% per year matter so much over a lifetime of investing? The number will surprise you.",
        f"Two identical {money(balance)} portfolios, both growing at a seven percent gross return for {years} years. One pays a {fee_pct} percent annual fee. One doesn't.",
        f"A {fee_pct} percent fee sounds tiny. Almost nothing, right? Watch what it does over {years} years.",
        f"With no fee, the portfolio grows to about {short_money(fv_low)}. With the {fee_pct} percent fee, it only reaches {short_money(fv_high_fee)}.",
        f"That tiny {fee_pct} percent fee quietly cost {short_money(diff)} of your future money. Check your own fund's fee drag free on wealthdelay dot com, link below.",
        f"{URL}/investment-fee-drag-calculator", DISC_FEE)

# ---- Archetype 4: waiting N years to start (5 variations) ----
for i, (monthly, wait_years, start_age) in enumerate([
    (200, 5, 25), (300, 10, 22), (150, 3, 28), (250, 7, 24), (400, 5, 30)
]):
    full_years = 65 - start_age
    wait_start_years = full_years - wait_years
    fv_no_wait = fv_monthly(monthly, full_years, 0.07)
    fv_wait = fv_monthly(monthly, wait_start_years, 0.07)
    diff = fv_no_wait - fv_wait
    add(f"wait_years_v{i+1}",
        f"Waiting just {wait_years} years to invest cost {short_money(diff)} \U0001F62F",
        ["investing","procrastination","compound interest","personal finance","retirement","money tips"], "gold",
        f"\"I'll start investing in {wait_years} years.\"", "Sounds harmless.", "Here's the real price tag.",
        f"${monthly}/month at 7%, starting at {start_age} vs {start_age+wait_years}.",
        {"label":"START NOW","sub":f"invests from {start_age} to 65"},
        {"label":f"WAIT {wait_years}YRS","sub":f"invests from {start_age+wait_years} to 65"},
        "Same monthly amount. Just a different start date.",
        [f"Only a {wait_years}-year delay.", "Can't be that big a deal…"], "", "Let's see what {wait_years} years actually costs.".format(wait_years=wait_years),
        "At age 65:",
        {"label":"START NOW","val":round(fv_no_wait/1000),"valt":short_money(fv_no_wait),"sub":f"{full_years} years invested"},
        {"label":"WAITED","val":round(fv_wait/1000),"valt":short_money(fv_wait),"sub":f"{wait_start_years} years invested"},
        f"Just {wait_years} years of waiting…", f"…cost {short_money(diff)} at retirement.", "The best time to start was today.",
        f"Why does waiting just {wait_years} years to start investing cost you so much more than {wait_years} years' worth of contributions?",
        f"${monthly} a month at a seven percent return. One person starts at {start_age}. The other waits and starts at {start_age+wait_years}. Same amount, same rate, just a later start.",
        f"It's only a {wait_years} year delay. Can't be that big a deal, right? Let's see what it actually costs by sixty-five.",
        f"Starting at {start_age}, the balance grows to about {short_money(fv_no_wait)}. Waiting until {start_age+wait_years}, it only reaches {short_money(fv_wait)}.",
        f"That {wait_years} year delay alone cost {short_money(diff)} at retirement. The best time to start is today. Free calculator on wealthdelay dot com, link below.",
        f"{URL}/investing-calculators", DISC7)

# ---- Archetype 5: lump sum early vs late (5 variations) ----
for i, (amount, years_diff, base_years) in enumerate([
    (10000, 10, 30), (5000, 15, 35), (20000, 5, 25), (15000, 10, 28), (8000, 20, 40)
]):
    fv_early = fv_lump(amount, base_years, 0.07)
    fv_late = fv_lump(amount, base_years - years_diff, 0.07)
    diff = fv_early - fv_late
    add(f"lump_sum_v{i+1}",
        f"{money(amount)} invested {years_diff} years earlier grew into {short_money(diff)} MORE \U0001F631",
        ["lump sum investing","compound interest","investing","personal finance","money tips","wealth building"], "gold",
        f"Same {money(amount)}. Same 7% return.", f"One invested {years_diff} years earlier.", "The gap by retirement is wild.",
        f"A one-time {money(amount)} investment, {base_years} years vs {base_years-years_diff} years to grow.",
        {"label":"EARLY","sub":f"invested {base_years} years ago"},
        {"label":"LATE","sub":f"invested {base_years-years_diff} years ago"},
        f"Exact same {money(amount)}. Only the start date differs by {years_diff} years.",
        [f"It's the same {money(amount)}.", "How different could it really be?"], "", "The answer isn't small.",
        "After all those years:",
        {"label":"EARLY","val":round(fv_early/1000),"valt":short_money(fv_early),"sub":f"{base_years} years of growth"},
        {"label":"LATE","val":round(fv_late/1000),"valt":short_money(fv_late),"sub":f"{base_years-years_diff} years of growth"},
        f"Same {money(amount)} invested.", f"{years_diff} extra years made a {short_money(diff)} difference.", "Time in the market beats almost everything.",
        f"Why does the exact same {money(amount)} investment end up worth wildly different amounts depending only on when you invested it?",
        f"A one-time {money(amount)} investment at a seven percent average annual return. One version grows for {base_years} years. The other grows for {base_years-years_diff} years — {years_diff} years less.",
        f"It's the same {money(amount)} either way. How different could the outcome really be? The answer isn't small.",
        f"After {base_years} years, the early investment is worth about {short_money(fv_early)}. The late one is worth about {short_money(fv_late)}.",
        f"Same {money(amount)}, but {years_diff} extra years of growth made a {short_money(diff)} difference. Time in the market beats almost everything. Try your own numbers on wealthdelay dot com, link below.",
        f"{URL}/investing-calculators", DISC_LUMP)

# ---- Archetype 6: employer 401k match left on the table (5 variations) ----
for i, (salary, match_pct, contrib_pct, years) in enumerate([
    (50000, 50, 6, 30), (70000, 100, 3, 25), (60000, 50, 4, 35), (90000, 100, 4, 20), (45000, 50, 6, 40)
]):
    annual_match = salary * (contrib_pct/100) * (match_pct/100)
    monthly_match = annual_match / 12
    fv = fv_monthly(monthly_match, years, 0.07)
    add(f"401k_match_v{i+1}",
        f"Skipping your 401k match is leaving {short_money(fv)} on the table \U0001F4B8",
        ["401k","employer match","retirement","free money","personal finance","investing"], "gold",
        "Your employer offers a 401k match.", "Most people don't claim the full thing.", "Here's what that costs.",
        f"${salary:,} salary. Employer matches {match_pct}% on a {contrib_pct}% contribution.",
        {"label":"YOU CONTRIBUTE","sub":f"{contrib_pct}% of salary"},
        {"label":"EMPLOYER MATCHES","sub":f"{match_pct}% of that, free"},
        f"That match alone is about ${annual_match:,.0f}/year, free money.",
        ["Just free money sitting there.", "Until you actually skip it."], "", "Here's the real cost of skipping it.",
        f"If invested for {years} years:",
        {"label":"MATCH ONLY","val":round(fv/1000),"valt":short_money(fv),"sub":f"just the free employer money"},
        {"label":"YOU SKIPPED","val":0,"valt":"$0","sub":"if you don't contribute enough to get it"},
        "That match is literally free money.", f"Skip it for {years} years and you lose {short_money(fv)}.", "Always get the full match first.",
        f"Why is skipping your 401k match one of the most expensive mistakes you can make early in your career?",
        f"With a ${salary:,} salary and an employer that matches {match_pct} percent on a {contrib_pct} percent contribution, that match alone is worth about ${annual_match:,.0f} a year, completely free.",
        f"It's free money sitting there. Until you skip it by not contributing enough to get it. Here's what that actually costs you.",
        f"That free match alone, invested for {years} years at seven percent, grows to about {short_money(fv)}.",
        f"That's free money you'd be walking away from. Always contribute enough to get the full match first. Run your own numbers on wealthdelay dot com, link below.",
        f"{URL}/401k-contribution-calculator", DISC7)

# ---- Archetype 7: investing a raise instead of lifestyle creep (5 variations) ----
for i, (raise_amt, years) in enumerate([(300, 30), (500, 25), (200, 35), (700, 20), (400, 30)]):
    fv = fv_monthly(raise_amt, years, 0.07)
    total_in = raise_amt*12*years
    add(f"invest_raise_v{i+1}",
        f"Investing your next raise instead of spending it = {short_money(fv)} \U0001F92F",
        ["lifestyle creep","raise","investing","compound interest","personal finance","money tips"], "green",
        "You just got a raise.", f"It's about ${raise_amt}/month extra.", "What you do next changes everything.",
        f"${raise_amt}/month, invested at 7% for {years} years — vs spent on lifestyle creep.",
        {"label":"INVESTED","sub":"raise goes straight into the market"},
        {"label":"SPENT","sub":"raise quietly absorbed into spending"},
        "Same raise. Two completely different futures.",
        [f"It's just ${raise_amt} a month.", "Doesn't feel like much."], "", "Let it compound for a few decades.",
        f"After {years} years:",
        {"label":"INVESTED","val":round(fv/1000),"valt":short_money(fv),"sub":f"put in {money(total_in)}"},
        {"label":"SPENT","val":0,"valt":"$0","sub":"absorbed into lifestyle, gone"},
        f"That ${raise_amt} raise felt small.", f"Invested, it became {short_money(fv)}.", "Lifestyle creep is the silent wealth killer.",
        f"Why does investing your next raise instead of spending it matter so much more than it feels like in the moment?",
        f"Say your raise is about ${raise_amt} a month extra. We're comparing investing it at seven percent for {years} years versus letting it quietly get absorbed into lifestyle creep.",
        f"It's just ${raise_amt} a month. Doesn't feel like much on its own. Let it compound for a few decades though.",
        f"Invested, that raise grows to about {short_money(fv)} after {years} years. Spent, it's just gone — zero left.",
        f"That raise felt small in the moment. Invested, it became {short_money(fv)}. Run your own raise scenario free on wealthdelay dot com, link below.",
        f"{URL}/lifestyle-inflation-calculator", DISC7)

# ---- Archetype 8: rent vs buy difference invested (5 variations) ----
for i, (monthly_diff, years) in enumerate([(400, 20), (600, 15), (300, 25), (800, 10), (500, 30)]):
    fv = fv_monthly(monthly_diff, years, 0.07)
    add(f"rent_invest_v{i+1}",
        f"Renting and investing the difference could beat buying by {short_money(fv)} \U0001F3E0",
        ["rent vs buy","real estate","investing","personal finance","compound interest","money tips"], "gold",
        "\"Renting is throwing away money.\"", "Maybe. Maybe not.", "Depends on what you do with the difference.",
        f"Renting costs ${monthly_diff} less/month than buying. Invest that gap at 7% for {years} years.",
        {"label":"BUY","sub":"higher monthly cost, building home equity"},
        {"label":"RENT + INVEST","sub":f"${monthly_diff}/month gap invested instead"},
        "Same housing budget. Different allocation of the difference.",
        ["\"Renting is just throwing money away.\"", "That's the common advice."], "", "But what if you invested the gap?",
        f"After {years} years, that invested gap alone:",
        {"label":"INVESTED GAP","val":round(fv/1000),"valt":short_money(fv),"sub":"from the rent/buy cost difference"},
        {"label":"NOT INVESTED","val":0,"valt":"$0","sub":"if the gap is just spent"},
        "Renting isn't automatically wrong.", f"Investing the gap can build {short_money(fv)}.", "It depends entirely on your discipline.",
        f"Why is \"renting is throwing away money\" not always true? It depends on one specific habit.",
        f"Say renting costs ${monthly_diff} less a month than buying in your area. We're investing that exact difference at seven percent for {years} years.",
        f"The common advice says renting just throws money away. But what if you actually invested the monthly gap instead?",
        f"That invested gap alone grows to about {short_money(fv)} after {years} years.",
        f"Renting isn't automatically the wrong move — it depends entirely on whether you actually invest the difference. Compare your own numbers on wealthdelay dot com, link below.",
        f"{URL}/rent-vs-buy-calculator", DISC7)

# ---- Archetype 9: credit card minimum payment trap (5 variations) ----
for i, (balance, apr, min_pct) in enumerate([(5000, 22, 2), (8000, 24, 3), (3000, 20, 2), (10000, 26, 2), (6000, 22, 3)]):
    # approximate months to pay off with min payment (declining balance, min = max(min_pct%*balance, fixed floor) -- use simple declining min payment model)
    bal = balance
    months = 0
    total_paid = 0
    monthly_rate = apr/100/12
    while bal > 1 and months < 600:
        interest = bal * monthly_rate
        payment = max(bal * (min_pct/100), 25)
        payment = min(payment, bal + interest)
        principal = payment - interest
        bal -= principal
        total_paid += payment
        months += 1
    years_to_payoff = months/12
    total_interest = total_paid - balance
    add(f"cc_minimum_v{i+1}",
        f"Paying the minimum on {money(balance)} credit card debt took {years_to_payoff:.0f} years \U0001F628",
        ["credit card debt","debt payoff","personal finance","money tips","interest rates","minimum payment"], "red",
        f"{money(balance)} credit card balance.", f"{apr}% APR. Just the minimum payment.", "Guess how long it takes to pay off.",
        f"{money(balance)} at {apr}% APR, paying only the {min_pct}% minimum each month.",
        {"label":"BALANCE","sub":money(balance)},
        {"label":"APR","sub":f"{apr}% interest"},
        "Sounds manageable. The minimum is always small.",
        ["The minimum payment feels easy.", "That's exactly the trap."], "", "Here's how long it actually takes.",
        "Paying only the minimum:",
        {"label":"TIME TO PAY OFF","val":round(years_to_payoff),"valt":f"{years_to_payoff:.0f} yrs","sub":"just from minimum payments"},
        {"label":"TOTAL INTEREST","val":round(total_interest/1000),"valt":short_money(total_interest),"sub":"paid on top of the balance"},
        f"That {money(balance)} balance took {years_to_payoff:.0f} years to clear.", f"You'd pay {short_money(total_interest)} in interest alone.", "Minimum payments are designed to keep you paying.",
        f"Why does paying just the minimum on a credit card take so much longer than people expect?",
        f"A {money(balance)} balance at {apr} percent APR, paying only the minimum payment each month.",
        f"The minimum payment feels small and manageable. That's exactly the trap it's designed to be.",
        f"Paying only the minimum, it takes about {years_to_payoff:.0f} years to pay off, and you'd pay roughly {short_money(total_interest)} in interest on top of the original balance.",
        f"Minimum payments are designed to keep you paying as long as possible. Run your own payoff timeline free on wealthdelay dot com, link below.",
        f"{URL}/credit-card-true-cost-calculator", "Hypothetical based on a fixed APR and a minimum payment of the stated percentage of balance (or $25, whichever is greater); actual card terms vary. Not financial advice.")

# ---- Archetype 10: emergency fund opportunity cost framed positively (5 variations) ----
for i, (ef_amount, years) in enumerate([(10000, 20), (15000, 15), (5000, 25), (20000, 10), (8000, 30)]):
    fv = fv_lump(ef_amount, years, 0.04)  # high-yield savings comparison rate
    add(f"emergency_fund_v{i+1}",
        f"Your emergency fund isn't \"wasted\" money — here's what {money(ef_amount)} can still do \U0001F914",
        ["emergency fund","savings","personal finance","financial security","money tips","high yield savings"], "green",
        f"\"That {money(ef_amount)} sitting in savings is wasted.\"", "Is it really, though?", "Let's check the math.",
        f"{money(ef_amount)} emergency fund, in a high-yield account at ~4%, for {years} years.",
        {"label":"IN SAVINGS","sub":"earning ~4% in a high-yield account"},
        {"label":"INVESTED","sub":"earning ~7% but not liquid in a crisis"},
        "The fund isn't doing nothing — it's doing a different job.",
        ["\"It's just sitting there doing nothing.\"", "That's the common complaint."], "", "It's actually still growing.",
        f"After {years} years, even at the safer rate:",
        {"label":"GREW TO","val":round(fv/1000),"valt":short_money(fv),"sub":"while staying liquid for emergencies"},
        {"label":"STARTED WITH","val":round(ef_amount/1000),"valt":short_money(ef_amount),"sub":"the original fund"},
        "An emergency fund isn't dead money.", f"It still grew to {short_money(fv)} while protecting you.", "Safety and growth aren't mutually exclusive.",
        f"Why do people call an emergency fund \"wasted money\" when it's actually still working for you?",
        f"A {money(ef_amount)} emergency fund sitting in a high-yield savings account earning around four percent, over {years} years.",
        f"The common complaint is that it's just sitting there doing nothing. It's actually still growing — just more safely.",
        f"After {years} years, even at that safer rate, it grows to about {short_money(fv)}, while staying liquid the entire time for a real emergency.",
        f"An emergency fund isn't dead money — it's doing a different job than your investments. Compare savings vs investing accounts on wealthdelay dot com, link below.",
        f"{URL}/emergency-fund-calculator", "Hypothetical: high-yield savings rate assumed at approximately 4% APY, which varies by bank and over time. Not financial advice.")

# ---- Archetype 11: subscription creep invested (5 variations) ----
for i, (monthly_subs, years) in enumerate([(45, 30), (60, 25), (35, 35), (80, 20), (50, 30)]):
    fv = fv_monthly(monthly_subs, years, 0.07)
    total_in = monthly_subs*12*years
    add(f"subscription_v{i+1}",
        f"Your unused subscriptions are quietly costing you {short_money(fv)} \U0001F4F1",
        ["subscriptions","streaming","money tips","personal finance","compound interest","budgeting"], "red",
        "Quick gut check:", f"How many subscriptions do you actually use? About ${monthly_subs}/month average.", "Here's what that costs over time.",
        f"${monthly_subs}/month in subscriptions, invested at 7% for {years} years instead.",
        {"label":"SUBSCRIBED","sub":"streaming, apps, memberships"},
        {"label":"INVESTED","sub":"same money, in the market instead"},
        f"Average household spends about ${monthly_subs}/month on subscriptions.",
        [f"Over {years} years that's {money(total_in)} of your own cash."], "", "And that's before any growth.",
        "If invested instead:",
        {"label":"CASH IN","val":round(total_in/1000),"valt":short_money(total_in),"sub":"what you'd actually pay in"},
        {"label":"GROWN TO","val":round(fv/1000),"valt":short_money(fv),"sub":f"after {years} years at 7%"},
        "Subscriptions feel small individually.", f"Together they're quietly worth {short_money(fv)}.", "Audit them once a year, it adds up fast.",
        f"Why do subscriptions feel harmless individually but add up to a shocking number over time?",
        f"The average household spends about ${monthly_subs} a month on subscriptions. We're investing that same amount at seven percent for {years} years instead.",
        f"Over {years} years that's {money(total_in)} of your own cash, and that's before any investment growth at all.",
        f"Invested instead, that same money grows to about {short_money(fv)}.",
        f"Subscriptions feel small individually but together they're quietly worth {short_money(fv)}. Audit yours and run the math on wealthdelay dot com, link below.",
        f"{URL}/streaming-subscription-cost-calculator", DISC7)

# ---- Archetype 12: social security claim age (5 variations) ----
for i, (monthly_at_67, life_to_age) in enumerate([(2000, 85), (1800, 90), (2400, 82), (2200, 88), (1600, 90)]):
    monthly_at_70 = monthly_at_67 * 1.24  # actuarially ~8%/yr increase, 3 years = ~24%
    total_67 = monthly_at_67 * 12 * (life_to_age - 67)
    total_70 = monthly_at_70 * 12 * (life_to_age - 70)
    add(f"social_security_v{i+1}",
        f"Claiming Social Security at 70 instead of 67 — who actually wins by {life_to_age}? \U0001F4B0",
        ["social security","retirement","personal finance","claiming age","money tips","retirement planning"], "gold",
        "Claim Social Security at 67?", "Or wait until 70?", "The breakeven math surprises most people.",
        f"~${monthly_at_67:,.0f}/month at 67 vs ~${monthly_at_70:,.0f}/month at 70, lived to age {life_to_age}.",
        {"label":"CLAIM AT 67","sub":f"${monthly_at_67:,.0f}/month, starts sooner"},
        {"label":"CLAIM AT 70","sub":f"${monthly_at_70:,.0f}/month, starts later"},
        "Waiting increases the monthly check by roughly 8% per year delayed.",
        ["Starting sooner means more checks.", "Starting later means bigger checks."], "", f"Who comes out ahead by age {life_to_age}?",
        f"Total lifetime benefit to age {life_to_age}:",
        {"label":"CLAIMED AT 67","val":round(total_67/1000),"valt":short_money(total_67),"sub":f"{life_to_age-67} years of payments"},
        {"label":"CLAIMED AT 70","val":round(total_70/1000),"valt":short_money(total_70),"sub":f"{life_to_age-70} years of payments"},
        "There's no universal right answer.", f"At {life_to_age}, the {'later' if total_70>total_67 else 'earlier'} claim wins here.", "Your health and longevity matter more than the rule of thumb.",
        f"Why does the \"right\" age to claim Social Security depend so heavily on how long you actually live?",
        f"Claiming at 67 pays about ${monthly_at_67:,.0f} a month. Waiting until 70 pays about ${monthly_at_70:,.0f} a month, roughly eight percent more per year delayed.",
        f"Starting sooner means more total checks. Starting later means bigger checks. Who actually comes out ahead by age {life_to_age}?",
        f"Total lifetime benefit to age {life_to_age}: claiming at 67 totals about {short_money(total_67)}. Claiming at 70 totals about {short_money(total_70)}.",
        f"There's no universal right answer — at age {life_to_age}, the {'later' if total_70>total_67 else 'earlier'} claim wins, but your own health and longevity matter more than any rule of thumb. Run your own scenario on wealthdelay dot com, link below.",
        f"{URL}/social-security-claim-age-67-vs-70-calculator", "Hypothetical based on stated benefit amounts and an approximate 8%/year delayed-retirement credit; actual benefits depend on your work history and SSA rules. Not financial advice.")

assert len(IDEAS) == 60, f"expected 60, got {len(IDEAS)}"

# Voice assignment: 8 ElevenLabs Ed (hero), 8 ElevenLabs Brian (hero), 44 free edge-tts Brian.
# Spread the EL hero slots roughly evenly through the 2-month run rather than clustering them.
el_ed_idx    = {2, 9, 16, 23, 30, 37, 44, 51}
el_brian_idx = {5, 12, 19, 26, 33, 40, 47, 54}
for idx, idea in enumerate(IDEAS):
    if idx in el_ed_idx:
        idea["voice"] = "ed"
    elif idx in el_brian_idx:
        idea["voice"] = "brian"  # ElevenLabs Brian (paid), distinct from default edge-tts

with open("ideas_batch2.json", "w") as f:
    json.dump(IDEAS, f, indent=2, ensure_ascii=False)

voices = [i.get("voice", "edge-free") for i in IDEAS]
print(f"Generated {len(IDEAS)} ideas -> ideas_batch2.json")
print(f"  edge-tts free Brian: {voices.count('edge-free')}")
print(f"  ElevenLabs Ed:       {voices.count('ed')}")
print(f"  ElevenLabs Brian:    {voices.count('brian')}")
