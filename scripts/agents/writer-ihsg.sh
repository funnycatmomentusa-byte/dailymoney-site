#!/bin/sh
# DailyMoney Niche Agent: IHSG & Pasar Saham
export DM_NICHE=ihsg
cd /root/workspace/dailymoney-site
python3 scripts/dailymoney-niche-writer.py