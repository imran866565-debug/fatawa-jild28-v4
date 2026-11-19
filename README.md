# Fatawa Razviya — Jild 28 tashreeh v4 merge

Merge workspace: 14 leaf chunk files of the easy-Urdu tashreeh v4 for Fatawa Razviya Jild 28 (volume_id 32; 89 items, 636 pages) are merged into `jild-28.json` by GitHub Actions (`merge_jild28_v4.py`), then published as a v1.0 release asset.

Item order reproduces the v3 merged file exactly (first jild28-pesh-lafz, last jild28-zulal-latifa-baqillani). All 14 leaf chunks carry start_page == min(pages). The merge combines 5 two-part groups (shamama-4-nufha-3, shamama-4-nufha-14, shamama-4-nufha-21, zulal-shubha-1-muqaddimat, zalal-nqi-radd-abu-ubayda) and applies 16 rename-onlys (plain nafha-N ids of chunks 05/06 move to the shamama-4-nufha-N form; chunk 03 keeps plain nafha-1..10), then stable-sorts by start_page, matching the v3 merged file. No page markers are present in the chunks.
