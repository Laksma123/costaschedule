#!/usr/bin/env python3
"""
Costa Smeralda / Serena Restaurant Schedule Exporter
CLI & Standalone Python tool for converting Excel schedules into WhatsApp smart payloads.
"""

import sys
import os
import json
import base64
import subprocess
import argparse
import openpyxl

def copy_to_clipboard(text):
    """Copy text to clipboard cross-platform (Mac, Windows, Linux)"""
    try:
        if sys.platform == 'darwin':
            p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE, close_fds=True)
            p.communicate(input=text.encode('utf-8'))
            return True
        elif sys.platform.startswith('win'):
            p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, close_fds=True)
            p.communicate(input=text.encode('utf-8'))
            return True
        else:
            p = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE, close_fds=True)
            p.communicate(input=text.encode('utf-8'))
            return True
    except Exception as e:
        print(f"[Warning] Failed to copy to clipboard automatically: {e}")
        return False

def parse_schedule_excel(file_path, shift_override=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    wb = openpyxl.load_workbook(file_path, data_only=True)
    
    ship_name = "COSTA SMERALDA"
    port_name = "KAOHSIUNG"
    date_val = "August 23, 2026"
    shift_val = "LUNCH REPORT 11:00"
    meal_val = "LUNCH"

    venues = []
    buffet_venues = []
    side_duties = []
    special_events = []
    sick_leave = []

    # Sheet 1: Main Dining
    ws1 = wb.worksheets[0]
    
    r1 = str(ws1.cell(row=1, column=1).value or '').strip()
    if r1: date_val = r1

    r2 = str(ws1.cell(row=2, column=1).value or '').strip()
    if r2: port_name = r2

    r4 = str(ws1.cell(row=4, column=1).value or '').strip()
    if r4:
        shift_val = r4
        if "LUNCH" in r4.upper(): meal_val = "LUNCH"
        elif "DINNER" in r4.upper(): meal_val = "DINNER"
        elif "BREAKFAST" in r4.upper(): meal_val = "BREAKFAST"
    
    if shift_override:
        meal_val = shift_override.upper()
        shift_val = f"{meal_val} REPORT"

    # Main Ceres Table (Stations 1-14)
    ceres_assignments = []
    for r in range(7, 21):
        stn = str(ws1.cell(row=r, column=1).value or '').strip()
        w_name = str(ws1.cell(row=r, column=3).value or '').strip()
        tbl = str(ws1.cell(row=r, column=6).value or '').strip()
        
        if stn and w_name:
            ceres_assignments.append({
                "station": stn,
                "waiterName": w_name,
                "attendantName": "",
                "tables": tbl
            })

    if ceres_assignments:
        venues.append({
            "name": "Ceres Restaurant Main (Deck 5)",
            "reportTime": "11:00",
            "assignments": ceres_assignments
        })

    # Ceres Sub-Teams: Refilling & Resetting
    refill_a = []
    refill_b = []
    reset_team = []
    
    for r in range(22, 32):
        name_a = str(ws1.cell(row=r, column=2).value or '').strip()
        if name_a: refill_a.append({"name": name_a})

        name_b = str(ws1.cell(row=r, column=4).value or '').strip()
        if name_b: refill_b.append({"name": name_b})

        name_r = str(ws1.cell(row=r, column=6).value or '').strip()
        if name_r: reset_team.append({"name": name_r})

    if refill_a:
        side_duties.append({"name": "Ceres — Refilling Team A (Report at 10:45)", "timing": "10:45", "crew": refill_a})
    if refill_b:
        side_duties.append({"name": "Ceres — Refilling Team B (Report at 11:00)", "timing": "11:00", "crew": refill_b})
    if reset_team:
        side_duties.append({"name": "Ceres — Resetting Team (Report at 11:30)", "timing": "11:30", "crew": reset_team})

    # Ceres Upper
    cu_assignments = []
    for r in range(35, 43):
        stn = str(ws1.cell(row=r, column=1).value or '').strip()
        cname = str(ws1.cell(row=r, column=3).value or '').strip()
        if cname:
            cu_assignments.append({
                "station": stn or f"Stn {r}",
                "waiterName": cname,
                "attendantName": "",
                "tables": f"Upper Station {stn}"
            })
    if cu_assignments:
        venues.append({
            "name": "Ceres Upper (Deck 6)",
            "reportTime": "11:00",
            "assignments": cu_assignments
        })

    # Vesta Upper
    vu_assignments = []
    for r in range(44, 54):
        stn = str(ws1.cell(row=r, column=1).value or '').strip()
        wname = str(ws1.cell(row=r, column=3).value or '').strip()
        aname = str(ws1.cell(row=r, column=5).value or '').strip()
        if wname:
            vu_assignments.append({
                "station": stn or f"Stn {r}",
                "waiterName": wname,
                "attendantName": aname,
                "tables": f"Vesta {stn}"
            })
    if vu_assignments:
        venues.append({
            "name": "Vesta Upper (Deck 6)",
            "reportTime": "11:00",
            "assignments": vu_assignments
        })

    # Parse Sheet 2 (Buffet & Side Duties) if exists
    if len(wb.worksheets) > 1:
        ws2 = wb.worksheets[1]
        
        # Buffet 32 crew grid (Rows 4 to 13)
        buffet_crew = []
        for r in range(4, 14):
            for c_pair in [(1, 2), (3, 4), (5, 6)]:
                cname = str(ws2.cell(row=r, column=c_pair[1]).value or '').strip()
                if cname:
                    buffet_crew.append({"name": cname})

        if buffet_crew:
            buffet_venues.append({
                "name": "Buffet Deck 9 (Main)",
                "timing": "07:00-10:00 / 11:00-14:00",
                "lead": "SRS LI ZHI",
                "crew": buffet_crew
            })

        # DRS 07:00-13:00 (RAMANDA LAKSMANA DIAN)
        drs_crew = []
        drs_name = str(ws2.cell(row=19, column=2).value or '').strip()
        if drs_name:
            drs_crew.append({"name": drs_name})
            side_duties.append({
                "name": "DRS 07:00-13:00",
                "timing": "07:00-13:00",
                "crew": drs_crew
            })

        # Office Disposition
        off_crew = []
        for r in [16, 17]:
            cname = str(ws2.cell(row=r, column=2).value or '').strip()
            if cname: off_crew.append({"name": cname})
        if off_crew:
            side_duties.append({"name": "Office Disposition (07:00-13:00)", "timing": "07:00-13:00", "crew": off_crew})

        # Reservation Call & Doors
        res_name = str(ws2.cell(row=16, column=4).value or '').strip()
        if res_name:
            side_duties.append({"name": "Reservation Call", "timing": "Shift Duty", "crew": [{"name": res_name}]})

        vu_door_name = str(ws2.cell(row=16, column=6).value or '').strip()
        if vu_door_name:
            side_duties.append({"name": "Vesta Upper by the Door (11:00)", "timing": "11:00", "crew": [{"name": vu_door_name}]})

        vl_door_name = str(ws2.cell(row=19, column=6).value or '').strip()
        if vl_door_name:
            side_duties.append({"name": "Vesta Lower by the Door (11:15-14:15)", "timing": "11:15-14:15", "crew": [{"name": vl_door_name}]})

        # Outlets & Specialty Lounges
        outlets_crew = []
        noodle_name = str(ws2.cell(row=21, column=2).value or '').strip()
        if noodle_name: outlets_crew.append({"name": noodle_name, "role": "Noodle Bar 12:30-15:30/16:30-24:30"})

        for r in [21, 22, 23]:
            pname = str(ws2.cell(row=r, column=4).value or '').strip()
            if pname: outlets_crew.append({"name": pname, "role": "Pizzeria"})

        for r in [21, 22]:
            sname = str(ws2.cell(row=r, column=6).value or '').strip()
            if sname: outlets_crew.append({"name": sname, "role": "Salty Beach"})

        # Sushino, Casanova, Steakhouse
        sush_name = str(ws2.cell(row=35, column=2).value or '').strip()
        if sush_name: outlets_crew.append({"name": sush_name, "role": "Sushino (Report 11:00)"})

        sush2_name = str(ws2.cell(row=36, column=2).value or '').strip()
        if sush2_name: outlets_crew.append({"name": sush2_name, "role": "Sushino (Report 11:00)"})

        cas_name = str(ws2.cell(row=35, column=4).value or '').strip()
        if cas_name: outlets_crew.append({"name": cas_name, "role": "Casanova (Report 11:00)"})

        stk_name = str(ws2.cell(row=35, column=6).value or '').strip()
        if stk_name: outlets_crew.append({"name": stk_name, "role": "Steakhouse (Report 11:00)"})

        stk2_name = str(ws2.cell(row=36, column=6).value or '').strip()
        if stk2_name: outlets_crew.append({"name": stk2_name, "role": "Steakhouse (Report 11:00)"})

        for r in range(38, 42):
            hname = str(ws2.cell(row=r, column=2).value or '').strip()
            if hname: outlets_crew.append({"name": hname, "role": "Hot Pot Team (10:00-14:00)"})

        if outlets_crew:
            buffet_venues.append({
                "name": "Specialty Restaurants & Lounges",
                "timing": "Per Shift Roster",
                "crew": outlets_crew
            })

        # Linen Incharge
        lin_name = str(ws2.cell(row=25, column=2).value or '').strip()
        if lin_name: side_duties.append({"name": "Linen Incharge (08:00-14:00)", "timing": "08:00-14:00", "crew": [{"name": lin_name}]})

        # Cleaning
        cln_crew = []
        for r in [27, 28, 29]:
            cname = str(ws2.cell(row=r, column=2).value or '').strip()
            if cname: cln_crew.append({"name": cname})
        if cln_crew:
            side_duties.append({"name": "Cleaning After Breakfast (13:00)", "timing": "13:00", "crew": cln_crew})

        # Buffet 9 Report with SRS Li Zhi
        rep_crew = []
        for r in [27, 28]:
            name1 = str(ws2.cell(row=r, column=4).value or '').strip()
            if name1: rep_crew.append({"name": name1})
            name2 = str(ws2.cell(row=r, column=6).value or '').strip()
            if name2: rep_crew.append({"name": name2})
        if rep_crew:
            side_duties.append({"name": "Buffet Deck 9 Report with SRS Li Zhi", "timing": "07:00-10:00 / 11:00-14:00", "crew": rep_crew})

        # Magazinero
        mag_crew = []
        for r in [31, 32]:
            cname = str(ws2.cell(row=r, column=2).value or '').strip()
            if cname: mag_crew.append({"name": cname})
        if mag_crew:
            side_duties.append({"name": "Magazinero Report (08:00-14:00)", "timing": "08:00-14:00", "crew": mag_crew})

        # Folding Napkin
        nap_crew = []
        for r in [31, 32]:
            cname = str(ws2.cell(row=r, column=4).value or '').strip()
            if cname: nap_crew.append({"name": cname})
        if nap_crew:
            side_duties.append({"name": "Folding Napkin Deck 10", "timing": "07:00-10:00 / 11:00-14:00", "crew": nap_crew})

        # Crew Mess
        mess_crew = []
        for r in [31, 32, 33]:
            cname = str(ws2.cell(row=r, column=6).value or '').strip()
            if cname: mess_crew.append({"name": cname})
        if mess_crew:
            side_duties.append({"name": "Check Crew Mess Schedule", "timing": "Shift Duty", "crew": mess_crew})

        # Sick Leave
        for r in range(38, 42):
            cname = str(ws2.cell(row=r, column=4).value or '').strip()
            if cname: sick_leave.append({"name": cname})

    special_events = [
        {
            "title": "TRAVEL TALK — 05 NOVEMBER 2024 AT 10:40",
            "location": "Stand by in front of Theater Deck 3",
            "participants": [
                {"name": "CONCEPCION ILOGON ANNE JENESSE", "uniform": "Day Uniform"},
                {"name": "GU YUAN", "uniform": "Day Uniform"},
                {"name": "SEMERTI NI MADE DIAN BUDI", "uniform": "Dinner Uniform"},
                {"name": "SOFYAN HELMI", "uniform": "Dinner Uniform"},
                {"name": "CHEOK PEI YAN", "uniform": "Hot Pot Uniform"},
                {"name": "LI CHUN YUN", "uniform": "Hot Pot Uniform"},
                {"name": "YI KE", "uniform": "Day Uniform"}
            ]
        }
    ]

    schedule_data = {
        "ship": ship_name,
        "port": port_name,
        "date": date_val,
        "shift": shift_val,
        "meal": meal_val,
        "venues": venues,
        "buffetAndVenues": buffet_venues,
        "sideDuties": side_duties,
        "specialEvents": special_events,
        "sickLeave": sick_leave
    }

    return schedule_data

def generate_payload(schedule_data):
    json_str = json.dumps(schedule_data, separators=(',', ':'))
    b64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    wa_message = (
        f"🚢 {schedule_data['ship']} — RESTAURANT SCHEDULE\n"
        f"📅 Date    : {schedule_data['date']}\n"
        f"🍽️ Shift   : {schedule_data['shift']}\n"
        f"--------------------------------------------\n"
        f"[COSTA-DATA-START]\n"
        f"{b64_str}\n"
        f"[COSTA-DATA-END]"
    )
    return wa_message, b64_str

def main():
    parser = argparse.ArgumentParser(description="Costa Smeralda Schedule Exporter to WhatsApp")
    parser.add_argument("file", nargs="?", default="/Users/dianjulie/Documents/Schedule Costa/sample/Costa_Serena_Schedule_Sample.xlsx", help="Path to Excel schedule (.xlsx)")
    parser.add_argument("--shift", choices=["BREAKFAST", "LUNCH", "DINNER"], help="Override meal shift")
    parser.add_argument("--gui", action="store_true", help="Launch Desktop GUI mode")
    args = parser.parse_args()

    if args.gui:
        import app_desktop
        app_desktop.launch_gui()
        return

    print("=" * 60)
    print("🚢 COSTA SMERALDA — RESTAURANT SCHEDULE EXPORTER")
    print("=" * 60)

    try:
        print(f"📖 Reading Excel file: {args.file}")
        data = parse_schedule_excel(args.file, args.shift)
        
        wa_msg, b64 = generate_payload(data)
        
        print(f"✅ Successfully parsed {data['ship']} schedule!")
        print(f"   📅 Date : {data['date']}")
        print(f"   📍 Port : {data['port']}")
        print(f"   🍽️ Shift: {data['shift']}")
        print(f"   👥 Total Venues & Sections: {len(data['venues']) + len(data['buffetAndVenues']) + len(data['sideDuties'])}")
        print("-" * 60)
        
        copied = copy_to_clipboard(wa_msg)
        if copied:
            print("🎉 [SUCCESS] The schedule message has been COPIED TO YOUR CLIPBOARD!")
            print("👉 Open WhatsApp and press Ctrl+V to paste the message to your crew group.\n")
        else:
            print("\n📋 Below is your WhatsApp Message (Copy manually):\n")
            print(wa_msg)
            
    except Exception as err:
        print(f"❌ Error: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
