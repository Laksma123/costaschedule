/**
 * Costa Cruises — Restaurant Schedule Exporter
 * Desktop Edition — Web Implementation
 * 100% Client-Side, Zero Network Dependencies, Ship IT Compliant
 */

// ─────────────────────────────────────────────────────────────
// DESIGN SYSTEM TOKENS & CONSTANTS
// ─────────────────────────────────────────────────────────────
const TK = {
  bg_base:        '#FFFFFF',
  surface_card:   '#FFFFFF',
  surface_inner:  '#F8FAFC',
  surface_hover:  '#F1F5F9',
  border_card:    '#CBD5E1',
  border_inner:   '#E2E8F0',
  accent:         '#0071A3',
  gold_accent:    '#F9B000',
  gold_hover:     '#E09E00',
  good_ink:       '#1F7A54',
  good_bg:        '#F1F9F5',
  warn_ink:       '#6B4E00',
  bad_ink:        '#B3402E',
  bad_bg:         '#FCF2F0',
  bad_border:     '#EFCFC8',
  fg_primary:     '#0A2A38',
  fg_secondary:   '#5F7079',
  fg_subtle:      '#94A6AE',
};

// Key minification map matching exporter.py
const _KEY_MIN = {
  'waiterName': 'w', 'attendantName': 'a', 'station': 's',
  'tables': 't', 'name': 'n', 'role': 'r', 'crew': 'c',
  'assignments': 'as', 'reportTime': 'rt', 'timing': 'ti',
  'lead': 'ld', 'title': 'tt', 'location': 'lo',
  'participants': 'pa', 'uniform': 'un',
  'venues': 'v', 'buffetAndVenues': 'bv', 'sideDuties': 'sd',
  'specialEvents': 'se', 'sickLeave': 'sl',
  'ship': 'sh', 'date': 'dt', 'port': 'po', 'meal': 'ml', 'shift': 'sf',
};

// Default embedded sample data
const DEFAULT_SAMPLE_DATA = {"ship": "COSTA SMERALDA", "port": "KAOHSIUNG", "date": "August 23, 2026", "shift": "LUNCH REPORT", "meal": "LUNCH", "venues": [{"name": "Ceres Restaurant Main (Deck 5)", "reportTime": "11:00", "assignments": [{"station": "1", "waiterName": "WIBOWO ANDRI -BS", "attendantName": "", "tables": "302, 304, 306, 362, 364"}, {"station": "2", "waiterName": "PUTRA DUWI LAKSANA -BS", "attendantName": "", "tables": "308, 310, 312, 366, 368"}, {"station": "3", "waiterName": "SETIOBUDI NIDZAR DICKY -TR -CT", "attendantName": "", "tables": "314, 316, 370, 372, 374"}, {"station": "4", "waiterName": "WIJAYA I GEDE ARIK -TR CT", "attendantName": "", "tables": "318, 320, 322, 324, 344, 346"}, {"station": "5", "waiterName": "WIDYANTARA I GUSTI NGURAH -TR", "attendantName": "", "tables": "326, 328, 330, 338, 340, 342"}, {"station": "6", "waiterName": "HUSEN MUSTAFA AHMAD", "attendantName": "", "tables": "331, 332, 333, 334, 335, 336, 337"}, {"station": "7", "waiterName": "ROHMAN FADILI", "attendantName": "", "tables": "325, 327, 329, 339, 341, 343, 345"}, {"station": "8", "waiterName": "HAIRUDIN EXDA -CT", "attendantName": "", "tables": "317, 319, 321, 323, 347, 349"}, {"station": "9", "waiterName": "SHARMA VICKY CHANDESWAR", "attendantName": "", "tables": "313, 315, 351, 373, 375, 377"}, {"station": "10", "waiterName": "HALANKAR SACHIN SHAM -LINEN", "attendantName": "", "tables": "307, 309, 311, 357, 359"}, {"station": "11", "waiterName": "THAKUR AKSHAY VISHNU -LINEN", "attendantName": "", "tables": "301, 303, 305, 365, 367"}, {"station": "12", "waiterName": "SARMADI KEVIN TEGUH -DIRECTIONE", "attendantName": "", "tables": "376, 378, 380, 382, 410, 379, 381, 383, 385, 413"}, {"station": "13", "waiterName": "CAMBA GHIEMER PAUL -CT", "attendantName": "", "tables": "403, 405, 407, 427"}, {"station": "14", "waiterName": "JOSHI PREM", "attendantName": "", "tables": "400, 402, 404, 424"}]}, {"name": "Ceres Upper (Deck 6)", "reportTime": "11:00", "assignments": [{"station": "28", "waiterName": "RAHI AKASH", "attendantName": "", "tables": "Upper Station 28"}, {"station": "30", "waiterName": "SIPAHUTAR DOLY CRISTIAN", "attendantName": "", "tables": "Upper Station 30"}, {"station": "32", "waiterName": "DSOUZA RITHESHA", "attendantName": "", "tables": "Upper Station 32"}, {"station": "34", "waiterName": "MANNA MANOJ", "attendantName": "", "tables": "Upper Station 34"}, {"station": "36", "waiterName": "MALE ASHISH ANTHONY", "attendantName": "", "tables": "Upper Station 36"}, {"station": "37", "waiterName": "TEMAJA MADE SINGA", "attendantName": "", "tables": "Upper Station 37"}, {"station": "39", "waiterName": "PRABOWO AJI SURYA", "attendantName": "", "tables": "Upper Station 39"}]}, {"name": "Vesta Upper (Deck 6)", "reportTime": "11:00", "assignments": [{"station": "62", "waiterName": "SUSILA PUTU PANDE", "attendantName": "WARDANA WAYAN ADI WISNU", "tables": "Vesta 62"}, {"station": "63", "waiterName": "LAUAN MARY", "attendantName": "SATYAMA I KADEK", "tables": "Vesta 63"}, {"station": "64", "waiterName": "RAMESH KUMAR", "attendantName": "THAPA SAURABH", "tables": "Vesta 64"}, {"station": "65", "waiterName": "KARMAKAR SUDIP", "attendantName": "RAFLI RIFKI -TR", "tables": "Vesta 65"}, {"station": "66", "waiterName": "KALE SAGAR", "attendantName": "PRADHAN SAYANTA RABIN", "tables": "Vesta 66"}, {"station": "67", "waiterName": "DARMAWAN I GUSTI PUTU ERI -CC", "attendantName": "LAZAGA MARIA", "tables": "Vesta 67"}, {"station": "68", "waiterName": "KUMAR ABHIJEET", "attendantName": "WASIUN MOHAMMAD ROHIB", "tables": "Vesta 68"}, {"station": "69", "waiterName": "INDRAWAN SALEH ARIF", "attendantName": "CATINDIG MATAWARAN HEIDEE", "tables": "Vesta 69"}, {"station": "70", "waiterName": "PRAWIRA EDWIN -BS", "attendantName": "ALPHONSO MICHAEL PAUL", "tables": "Vesta 70"}]}], "buffetAndVenues": [{"name": "Buffet Deck 9 (Main)", "timing": "07:00-10:00 / 11:00-14:00", "lead": "SRS LI ZHI", "crew": [{"name": "SHANMUGAM KARTHICK KUMAR"}, {"name": "DINGANKAR RITESH"}, {"name": "PRAMADYA FIKRYAN SURYA"}, {"name": "PRABU TAMA"}, {"name": "RAJ AMAN"}, {"name": "WAFA MUHAMMAD HILMI"}, {"name": "DEWI PUTU AYU RISTIANA"}, {"name": "FRANSISKA OCTAVIA MELIANA"}, {"name": "UMAM DAVID NUR"}, {"name": "DWIATMO JOKO"}, {"name": "YULIASTUTI EKA"}, {"name": "KESUMA SANG NYOMAN ARDIKA"}, {"name": "JAMALUDDIN XXX"}, {"name": "SETIAWAN MUKLIS"}, {"name": "WIDIARTA I PUTU HENDRA"}, {"name": "MUMAR BALONGA ZISKA"}, {"name": "CARDOZO BENZY FRANKLLIN"}, {"name": "BITUIN JOHN HOWEN"}, {"name": "ARTHA WIGUNA GEDE KOMANG"}, {"name": "GEORGE PETER SEBASTIAN"}, {"name": "SHAHI VIKRANT"}, {"name": "SAPUTRA I WAYAN SUMADI ADI"}, {"name": "SHAABAN ALI"}, {"name": "SEJATI MUHAMMAD AGUS WAHYU"}, {"name": "SOMBILON TACANG SHEENA LOU"}, {"name": "FLORES LENNY JOY"}, {"name": "TOGNI JUDY ANN"}, {"name": "NANDA JUILTA ARIA"}, {"name": "JASMINE IVANA"}]}, {"name": "Specialty Restaurants & Lounges", "timing": "Per Shift Roster", "crew": [{"name": "RAJBHAR RAHUL MEGHNATH", "role": "Noodle Bar 12:30-15:30/16:30-24:30"}, {"name": "PERMANA EPRIN OKTAVIAN 12:30-15:30 /18:30-02:30", "role": "Pizzeria"}, {"name": "CHHETRI SHUBHAM 12:15-15:15/18:15-02:15", "role": "Pizzeria"}, {"name": "BHADALE SIDDHANT 12:30-15:30 /18:30-02:30", "role": "Pizzeria"}, {"name": "CHEN SUIYAN 13:00-16:30/19:30-01:00/02:30-04:30", "role": "Salty Beach"}, {"name": "WIJAYA KETUT PUTRA 17:00-19:30/20:30-02:30/04:00-06:30", "role": "Salty Beach"}, {"name": "SADEWA BENYAMIN BENY", "role": "Sushino (Report 11:00)"}, {"name": "MUYCO VILLA ABRILLE JAN CLOYDE", "role": "Sushino (Report 11:00)"}, {"name": "NEGARA I KOMANG ABDI", "role": "Casanova (Report 11:00)"}, {"name": "ERON DIONSON SAMUEL", "role": "Steakhouse (Report 11:00)"}, {"name": "MAHENDRA PRATAMA I PUTU GEDE DEVA", "role": "Steakhouse (Report 11:00)"}, {"name": "GENG YANAN -SELLING HOTPOT AREA", "role": "Hot Pot Team (10:00-14:00)"}, {"name": "DEGUNE JASPAL -SELLING HOTPOT AREA", "role": "Hot Pot Team (10:00-14:00)"}, {"name": "KURNIA TEGAR", "role": "Hot Pot Team (10:00-14:00)"}, {"name": "PANGESTU PANJI FAJAR", "role": "Hot Pot Team (10:00-14:00)"}]}], "sideDuties": [{"name": "Ceres — Refilling Team A (Report at 10:45)", "timing": "10:45", "crew": [{"name": "ARYANTO I PUTU AGUS"}, {"name": "SUARJANA MADE"}, {"name": "ABADI SULASTOMO"}, {"name": "GADIANO PAICA APRILLE JANE"}, {"name": "ERYANTO XXX"}, {"name": "ANATHASYA PRILY"}]}, {"name": "Ceres — Refilling Team B (Report at 11:00)", "timing": "11:00", "crew": [{"name": "DARSANA I NYOMAN"}, {"name": "MUKHI ROSHAN"}, {"name": "NEMIS BENEDICT"}, {"name": "FALLADO CARREL"}]}, {"name": "Ceres — Resetting Team (Report at 11:30)", "timing": "11:30", "crew": [{"name": "HERMAWAN WAWAN"}, {"name": "SANTIAGO ANDREW"}, {"name": "PRABANGKARA IDA BAGUS PUTU KRISNA -SG"}]}, {"name": "DRS 07:00-13:00", "timing": "07:00-13:00", "crew": [{"name": "RAMANDA LAKSMANA DIAN"}]}, {"name": "Office Disposition (07:00-13:00)", "timing": "07:00-13:00", "crew": [{"name": "RAMOS LESLIE"}, {"name": "JUANILLO USOG MAE RUSELLE -HANDOVER RECEIVER"}]}, {"name": "Reservation Call", "timing": "Shift Duty", "crew": [{"name": "LU YANLING"}]}, {"name": "Vesta Upper by the Door (11:00)", "timing": "11:00", "crew": [{"name": "ANTARI NI WAYAN DESI -FRONT"}]}, {"name": "Vesta Lower by the Door (11:15-14:15)", "timing": "11:15-14:15", "crew": [{"name": "LU YANLING -FRONT"}]}, {"name": "Linen Incharge (08:00-14:00)", "timing": "08:00-14:00", "crew": [{"name": "DJODI ACHMAD SETIA"}]}, {"name": "Cleaning After Breakfast (13:00)", "timing": "13:00", "crew": [{"name": "BURHANUDIN MUHAMAD RIZKI -CT"}, {"name": "PUTRA ERICHO ALLAM FAQIHSYAH -CT"}, {"name": "SETIAWAN HERU -CT"}]}, {"name": "Buffet Deck 9 Report with SRS Li Zhi", "timing": "07:00-10:00 / 11:00-14:00", "crew": [{"name": "PRATAMA WILY -DECK 3 FWD ELEVATOR & LOBBY"}, {"name": "NUGRAHA PUTU WIRA - DECK 3 CERES & LOUNGES"}, {"name": "ENDANG SAHIDIN -DECK 5 ALL LOUNGES"}, {"name": "ASEO GLADY'S -BUFFET DECK 9"}]}, {"name": "Magazinero Report (08:00-14:00)", "timing": "08:00-14:00", "crew": [{"name": "BAPTISTA WILSON AUSTIN"}, {"name": "SYAMSI KHAERUL"}]}, {"name": "Folding Napkin Deck 10", "timing": "07:00-10:00 / 11:00-14:00", "crew": [{"name": "KRENDANA ANGGRA -07:00-10:00/11:00-14:00"}, {"name": "HIDAYAH SHOHIBUL -07:00-10:00/11:00-14:00"}]}, {"name": "Check Crew Mess Schedule", "timing": "Shift Duty", "crew": [{"name": "DSOUZA YORICK ROQUE JOHNSON"}, {"name": "XXX EI EI HTAR"}, {"name": "XXX CHIT KO KO ZAW"}]}], "specialEvents": [{"title": "TRAVEL TALK — 05 NOVEMBER 2024 AT 10:40", "location": "Stand by in front of Theater Deck 3", "participants": [{"name": "CONCEPCION ILOGON ANNE JENESSE", "uniform": "Day Uniform"}, {"name": "GU YUAN", "uniform": "Day Uniform"}, {"name": "SEMERTI NI MADE DIAN BUDI", "uniform": "Dinner Uniform"}, {"name": "SOFYAN HELMI", "uniform": "Dinner Uniform"}, {"name": "CHEOK PEI YAN", "uniform": "Hot Pot Uniform"}, {"name": "LI CHUN YUN", "uniform": "Hot Pot Uniform"}, {"name": "YI KE", "uniform": "Day Uniform"}]}], "sickLeave": [{"name": "MOHANTY DEEPAK RAJ"}, {"name": "SHEIKH AMIR SULEMAN"}, {"name": "SALVADOR JOMEL"}, {"name": "KUMBHAR AJAY PANDURANG"}]};

// ─────────────────────────────────────────────────────────────
// GLOBAL APPLICATION STATE
// ─────────────────────────────────────────────────────────────
const state = {
  currentFileName: 'Costa_Serena_Schedule_Sample.xlsx',
  rawWorkbook: null,
  scheduleData: null,
  payload: '',
  b64Data: '',
  qrSegments: [],
  qrCompressedB64: '',
  mealShift: 'LUNCH',
  activeFilter: 'ALL',
  searchQuery: '',
  currentModalIdx: 0,
  cachedCrewCount: 0,
  cachedSectionCount: 0,
  searchDebounceTimer: null,
  toastTimer: null,
};

// ─────────────────────────────────────────────────────────────
// VECTOR ICON GENERATOR
// ─────────────────────────────────────────────────────────────
function getIconSvg(name, color = 'currentColor', size = 16) {
  const icons = {
    search: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    clear: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    zoom: '<polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><polyline points="21 15 21 21 15 21"/><polyline points="3 9 3 3 9 3"/>',
    ship: '<path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.5 0 2.5 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M19.38 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9.94 5.34 2.81 7.76"/><path d="M19 13V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6"/><line x1="12" y1="2" x2="12" y2="5"/>',
    calendar: '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    map_pin: '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    copy: '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    check: '<polyline points="20 6 9 17 4 12"/>',
    folder: '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    refresh: '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
    save: '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>',
    export: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    external: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>',
    users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    utensils: '<path d="M18 2v20M2 2v8a4 4 0 0 0 4 4h0a4 4 0 0 0 4-4V2M6 2v20"/>',
    qr: '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="3" height="3"/><rect x="18" y="18" width="3" height="3"/>',
  };
  const body = icons[name] || '';
  return '<svg class="v-icon" style="width:' + size + 'px; height:' + size + 'px; stroke:' + color + ';" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>';
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ─────────────────────────────────────────────────────────────
// EXCEL PARSING ENGINE (1:1 with exporter.py)
// ─────────────────────────────────────────────────────────────
function getCell(ws, r, c) {
  if (!ws) return '';
  const addr = XLSX.utils.encode_cell({ r: r - 1, c: c - 1 });
  const cell = ws[addr];
  return (cell && cell.v !== undefined && cell.v !== null) ? String(cell.v).trim() : '';
}

function parseScheduleWorkbook(wb, shiftOverride = null) {
  if (!wb || !wb.SheetNames || !wb.SheetNames.length) {
    throw new Error('Invalid Excel file or no sheets found.');
  }

  const ws1 = wb.Sheets[wb.SheetNames[0]];

  let shipName = 'COSTA SMERALDA';
  let portName = 'KAOHSIUNG';
  let dateVal = 'August 23, 2026';
  let shiftVal = 'LUNCH REPORT 11:00';
  let mealVal = 'LUNCH';

  const venues = [];
  const buffetVenues = [];
  const sideDuties = [];
  const specialEvents = [];
  const sickLeave = [];

  const r1 = getCell(ws1, 1, 1);
  if (r1) dateVal = r1;

  const r2 = getCell(ws1, 2, 1);
  if (r2) portName = r2;

  const r4 = getCell(ws1, 4, 1);
  if (r4) {
    shiftVal = r4;
    const up = r4.toUpperCase();
    if (up.includes('LUNCH')) mealVal = 'LUNCH';
    else if (up.includes('DINNER')) mealVal = 'DINNER';
    else if (up.includes('BREAKFAST')) mealVal = 'BREAKFAST';
  }

  if (shiftOverride) {
    mealVal = shiftOverride.toUpperCase();
    shiftVal = mealVal + ' REPORT';
  }

  // Main Ceres Table (Stations 1-14)
  const ceresAssignments = [];
  for (let r = 7; r <= 20; r++) {
    const stn = getCell(ws1, r, 1);
    const wName = getCell(ws1, r, 3);
    const tbl = getCell(ws1, r, 6);
    if (stn && wName) {
      ceresAssignments.push({
        station: stn,
        waiterName: wName,
        attendantName: '',
        tables: tbl,
      });
    }
  }

  if (ceresAssignments.length) {
    venues.push({
      name: 'Ceres Restaurant Main (Deck 5)',
      reportTime: '11:00',
      assignments: ceresAssignments,
    });
  }

  // Ceres Sub-Teams: Refilling & Resetting
  const refillA = [];
  const refillB = [];
  const resetTeam = [];

  for (let r = 22; r <= 31; r++) {
    const nameA = getCell(ws1, r, 2);
    if (nameA) refillA.push({ name: nameA });

    const nameB = getCell(ws1, r, 4);
    if (nameB) refillB.push({ name: nameB });

    const nameR = getCell(ws1, r, 6);
    if (nameR) resetTeam.push({ name: nameR });
  }

  if (refillA.length) sideDuties.push({ name: 'Ceres — Refilling Team A (Report at 10:45)', timing: '10:45', crew: refillA });
  if (refillB.length) sideDuties.push({ name: 'Ceres — Refilling Team B (Report at 11:00)', timing: '11:00', crew: refillB });
  if (resetTeam.length) sideDuties.push({ name: 'Ceres — Resetting Team (Report at 11:30)', timing: '11:30', crew: resetTeam });

  // Ceres Upper
  const cuAssignments = [];
  for (let r = 35; r <= 42; r++) {
    const stn = getCell(ws1, r, 1);
    const cname = getCell(ws1, r, 3);
    if (cname) {
      cuAssignments.push({
        station: stn || ('Stn ' + r),
        waiterName: cname,
        attendantName: '',
        tables: 'Upper Station ' + stn,
      });
    }
  }
  if (cuAssignments.length) {
    venues.push({
      name: 'Ceres Upper (Deck 6)',
      reportTime: '11:00',
      assignments: cuAssignments,
    });
  }

  // Vesta Upper
  const vuAssignments = [];
  for (let r = 44; r <= 53; r++) {
    const stn = getCell(ws1, r, 1);
    const wname = getCell(ws1, r, 3);
    const aname = getCell(ws1, r, 5);
    if (wname) {
      vuAssignments.push({
        station: stn || ('Stn ' + r),
        waiterName: wname,
        attendantName: aname,
        tables: 'Vesta ' + stn,
      });
    }
  }
  if (vuAssignments.length) {
    venues.push({
      name: 'Vesta Upper (Deck 6)',
      reportTime: '11:00',
      assignments: vuAssignments,
    });
  }

  // Sheet 2: Buffet & Side Duties
  if (wb.SheetNames.length > 1) {
    const ws2 = wb.Sheets[wb.SheetNames[1]];

    // Buffet 32 crew grid (Rows 4 to 13)
    const buffetCrew = [];
    for (let r = 4; r <= 13; r++) {
      for (const col of [2, 4, 6]) {
        const cname = getCell(ws2, r, col);
        if (cname) buffetCrew.push({ name: cname });
      }
    }
    if (buffetCrew.length) {
      buffetVenues.push({
        name: 'Buffet Deck 9 (Main)',
        timing: '07:00-10:00 / 11:00-14:00',
        lead: 'SRS LI ZHI',
        crew: buffetCrew,
      });
    }

    // DRS 07:00-13:00
    const drsName = getCell(ws2, 19, 2);
    if (drsName) {
      sideDuties.push({
        name: 'DRS 07:00-13:00',
        timing: '07:00-13:00',
        crew: [{ name: drsName }],
      });
    }

    // Office Disposition
    const offCrew = [];
    for (const r of [16, 17]) {
      const cname = getCell(ws2, r, 2);
      if (cname) offCrew.push({ name: cname });
    }
    if (offCrew.length) {
      sideDuties.push({ name: 'Office Disposition (07:00-13:00)', timing: '07:00-13:00', crew: offCrew });
    }

    // Reservation Call & Doors
    const resName = getCell(ws2, 16, 4);
    if (resName) {
      sideDuties.push({ name: 'Reservation Call', timing: 'Shift Duty', crew: [{ name: resName }] });
    }

    const vuDoorName = getCell(ws2, 16, 6);
    if (vuDoorName) {
      sideDuties.push({ name: 'Vesta Upper by the Door (11:00)', timing: '11:00', crew: [{ name: vuDoorName }] });
    }

    const vlDoorName = getCell(ws2, 19, 6);
    if (vlDoorName) {
      sideDuties.push({ name: 'Vesta Lower by the Door (11:15-14:15)', timing: '11:15-14:15', crew: [{ name: vlDoorName }] });
    }

    // Outlets & Specialty Lounges
    const outletsCrew = [];
    const noodleName = getCell(ws2, 21, 2);
    if (noodleName) outletsCrew.push({ name: noodleName, role: 'Noodle Bar 12:30-15:30/16:30-24:30' });

    for (const r of [21, 22, 23]) {
      const pname = getCell(ws2, r, 4);
      if (pname) outletsCrew.push({ name: pname, role: 'Pizzeria' });
    }

    for (const r of [21, 22]) {
      const sname = getCell(ws2, r, 6);
      if (sname) outletsCrew.push({ name: sname, role: 'Salty Beach' });
    }

    const sushName = getCell(ws2, 35, 2);
    if (sushName) outletsCrew.push({ name: sushName, role: 'Sushino (Report 11:00)' });
    const sush2Name = getCell(ws2, 36, 2);
    if (sush2Name) outletsCrew.push({ name: sush2Name, role: 'Sushino (Report 11:00)' });

    const casName = getCell(ws2, 35, 4);
    if (casName) outletsCrew.push({ name: casName, role: 'Casanova (Report 11:00)' });

    const stkName = getCell(ws2, 35, 6);
    if (stkName) outletsCrew.push({ name: stkName, role: 'Steakhouse (Report 11:00)' });
    const stk2Name = getCell(ws2, 36, 6);
    if (stk2Name) outletsCrew.push({ name: stk2Name, role: 'Steakhouse (Report 11:00)' });

    for (let r = 38; r <= 41; r++) {
      const hname = getCell(ws2, r, 2);
      if (hname) outletsCrew.push({ name: hname, role: 'Hot Pot Team (10:00-14:00)' });
    }

    if (outletsCrew.length) {
      buffetVenues.push({
        name: 'Specialty Restaurants & Lounges',
        timing: 'Per Shift Roster',
        crew: outletsCrew,
      });
    }

    // Linen Incharge
    const linName = getCell(ws2, 25, 2);
    if (linName) sideDuties.push({ name: 'Linen Incharge (08:00-14:00)', timing: '08:00-14:00', crew: [{ name: linName }] });

    // Cleaning After Breakfast
    const clnCrew = [];
    for (const r of [27, 28, 29]) {
      const cname = getCell(ws2, r, 2);
      if (cname) clnCrew.push({ name: cname });
    }
    if (clnCrew.length) {
      sideDuties.push({ name: 'Cleaning After Breakfast (13:00)', timing: '13:00', crew: clnCrew });
    }

    // Buffet 9 Report with SRS Li Zhi
    const repCrew = [];
    for (const r of [27, 28]) {
      const name1 = getCell(ws2, r, 4);
      if (name1) repCrew.push({ name: name1 });
      const name2 = getCell(ws2, r, 6);
      if (name2) repCrew.push({ name: name2 });
    }
    if (repCrew.length) {
      sideDuties.push({ name: 'Buffet Deck 9 Report with SRS Li Zhi', timing: '07:00-10:00 / 11:00-14:00', crew: repCrew });
    }

    // Magazinero
    const magCrew = [];
    for (const r of [31, 32]) {
      const cname = getCell(ws2, r, 2);
      if (cname) magCrew.push({ name: cname });
    }
    if (magCrew.length) {
      sideDuties.push({ name: 'Magazinero Report (08:00-14:00)', timing: '08:00-14:00', crew: magCrew });
    }

    // Folding Napkin Deck 10
    const napCrew = [];
    for (const r of [31, 32]) {
      const cname = getCell(ws2, r, 4);
      if (cname) napCrew.push({ name: cname });
    }
    if (napCrew.length) {
      sideDuties.push({ name: 'Folding Napkin Deck 10', timing: '07:00-10:00 / 11:00-14:00', crew: napCrew });
    }

    // Crew Mess
    const messCrew = [];
    for (const r of [31, 32, 33]) {
      const cname = getCell(ws2, r, 6);
      if (cname) messCrew.push({ name: cname });
    }
    if (messCrew.length) {
      sideDuties.push({ name: 'Check Crew Mess Schedule', timing: 'Shift Duty', crew: messCrew });
    }

    // Sick Leave
    for (let r = 38; r <= 41; r++) {
      const cname = getCell(ws2, r, 4);
      if (cname) sickLeave.push({ name: cname });
    }
  }

  // Special Events
  specialEvents.push({
    title: 'TRAVEL TALK — 05 NOVEMBER 2024 AT 10:40',
    location: 'Stand by in front of Theater Deck 3',
    participants: [
      { name: 'CONCEPCION ILOGON ANNE JENESSE', uniform: 'Day Uniform' },
      { name: 'GU YUAN', uniform: 'Day Uniform' },
      { name: 'SEMERTI NI MADE DIAN BUDI', uniform: 'Dinner Uniform' },
      { name: 'SOFYAN HELMI', uniform: 'Dinner Uniform' },
      { name: 'CHEOK PEI YAN', uniform: 'Hot Pot Uniform' },
      { name: 'LI CHUN YUN', uniform: 'Hot Pot Uniform' },
      { name: 'YI KE', uniform: 'Day Uniform' },
    ],
  });

  return {
    ship: shipName,
    port: portName,
    date: dateVal,
    shift: shiftVal,
    meal: mealVal,
    venues: venues,
    buffetAndVenues: buffetVenues,
    sideDuties: sideDuties,
    specialEvents: specialEvents,
    sickLeave: sickLeave,
  };
}

// ─────────────────────────────────────────────────────────────
// ENCODING & COMPRESSION (1:1 with exporter.py)
// ─────────────────────────────────────────────────────────────
function minifyKeys(obj) {
  if (Array.isArray(obj)) return obj.map(minifyKeys);
  if (obj && typeof obj === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      out[_KEY_MIN[k] || k] = minifyKeys(v);
    }
    return out;
  }
  return obj;
}

function uint8ToBase64(bytes) {
  let binary = '';
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function generatePayload(scheduleData) {
  const jsonStr = JSON.stringify(scheduleData);
  const b64Str = btoa(unescape(encodeURIComponent(jsonStr)));
  const waMessage = [
    '🚢 ' + scheduleData.ship + ' — RESTAURANT SCHEDULE',
    '📅 Date    : ' + scheduleData.date,
    '🍽️ Shift   : ' + scheduleData.shift,
    '--------------------------------------------',
    '[COSTA-DATA-START]',
    b64Str,
    '[COSTA-DATA-END]'
  ].join('\n');
  return { waMessage, b64Str };
}

function generateCompressedPayload(scheduleData, numSegments = 2) {
  const minified = minifyKeys(scheduleData);
  const miniJson = JSON.stringify(minified);
  const compressed = pako.deflate(miniJson, { level: 9 });
  const fullB64 = uint8ToBase64(compressed);

  const segSize = Math.ceil(fullB64.length / numSegments);
  const segments = [];
  for (let i = 0; i < numSegments; i++) {
    const start = i * segSize;
    const end = Math.min((i + 1) * segSize, fullB64.length);
    const chunk = fullB64.slice(start, end);
    segments.push('[COSTA-PART ' + (i + 1) + '/' + numSegments + ']\n' + chunk);
  }
  return { segments, fullB64 };
}

// ─────────────────────────────────────────────────────────────
// CREW & SECTION COUNTING
// ─────────────────────────────────────────────────────────────
function calculateStats(d) {
  if (!d) return { crewCount: 0, sectionCount: 0, totalStations: 0, totalVenues: 0 };
  const names = new Set();
  let totalStations = 0;

  (d.venues || []).forEach(v => {
    (v.assignments || []).forEach(a => {
      totalStations++;
      if (a.waiterName) names.add(a.waiterName);
      if (a.attendantName) names.add(a.attendantName);
    });
  });

  (d.buffetAndVenues || []).forEach(b => {
    (b.crew || []).forEach(c => {
      if (c.name) names.add(c.name);
    });
  });

  (d.sideDuties || []).forEach(s => {
    (s.crew || []).forEach(c => {
      if (c.name) names.add(c.name);
    });
  });

  (d.sickLeave || []).forEach(sk => {
    if (sk.name) names.add(sk.name);
  });

  const totalVenues = (d.venues || []).length;
  const sectionCount = totalVenues + (d.buffetAndVenues || []).length + (d.sideDuties || []).length;

  return {
    crewCount: names.size,
    sectionCount,
    totalStations,
    totalVenues,
  };
}

// ─────────────────────────────────────────────────────────────
// QR CODE RENDERING
// ─────────────────────────────────────────────────────────────
function renderQR(container, text, size) {
  if (!container) return;
  container.innerHTML = '';
  try {
    new QRCode(container, {
      text: text,
      width: size,
      height: size,
      colorDark: '#000000',
      colorLight: '#FFFFFF',
      correctLevel: QRCode.CorrectLevel.L,
    });
  } catch (err) {
    console.error('QR code generation failed:', err);
  }
}

function updateQRPopups() {
  if (!state.scheduleData) return;

  try {
    const res = generateCompressedPayload(state.scheduleData, 2);
    state.qrSegments = res.segments;
    state.qrCompressedB64 = res.fullB64;

    const box1 = document.getElementById('qr-box-1');
    const box2 = document.getElementById('qr-box-2');

    if (res.segments.length >= 1 && box1) {
      renderQR(box1, res.segments[0], 110);
    }
    if (res.segments.length >= 2 && box2) {
      renderQR(box2, res.segments[1], 110);
    }

    const desc = document.getElementById('airgap-desc');
    if (desc) {
      desc.innerHTML =
        '1. Point phone camera at QR preview or click &quot;ENLARGE QR CODE&quot;.<br>' +
        '2. Tap &quot;Copy text&quot; on phone, then paste into WhatsApp.<br>' +
        '3. Repeat for Part 2 to transfer complete encrypted roster.';
    }
  } catch (e) {
    console.error('Failed to generate QR codes:', e);
  }
}

// ─────────────────────────────────────────────────────────────
// CARD RENDERING (Newspaper Editorial Style, Zero Emojis)
// ─────────────────────────────────────────────────────────────
function renderCards() {
  const container = document.getElementById('cards-container');
  if (!container) return;

  const d = state.scheduleData;
  if (!d) {
    container.innerHTML = '<div class="empty-state-label">No schedule loaded. Click Browse to select an Excel roster file.</div>';
    return;
  }

  const q = state.searchQuery.toLowerCase();
  const filt = state.activeFilter;
  let html = '';

  // 1. Main Dining
  if (filt === 'ALL' || filt === 'MAIN DINING') {
    (d.venues || []).forEach(venue => {
      const assignments = venue.assignments || [];
      const filtered = assignments.filter(a => {
        if (!q) return true;
        return (
          String(a.station || '').toLowerCase().includes(q) ||
          String(a.waiterName || '').toLowerCase().includes(q) ||
          String(a.attendantName || '').toLowerCase().includes(q) ||
          String(a.tables || '').toLowerCase().includes(q)
        );
      });

      if (filtered.length || !q) {
        html += '<article class="r-card">';
        html += '<div class="r-card-header">';
        html += '<h3 class="r-card-title">' + escapeHtml(venue.name) + '</h3>';
        html += '<span class="r-card-meta">Report: ' + escapeHtml(venue.reportTime || '—') + '  •  ' + filtered.length + ' stations</span>';
        html += '</div>';
        html += '<div class="r-card-divider"></div>';
        html += '<div class="r-card-body">';

        filtered.forEach(a => {
          html += '<div class="venue-row">';
          html += '<span class="station-badge">' + escapeHtml(a.station || '—') + '</span>';
          html += '<span class="waiter-name">' + escapeHtml(a.waiterName || '—') + '</span>';
          if (a.attendantName) {
            html += '<span class="attendant-name">/ ' + escapeHtml(a.attendantName) + '</span>';
          }
          if (a.tables) {
            html += '<span class="table-numbers">' + escapeHtml(a.tables) + '</span>';
          }
          html += '</div>';
        });

        html += '</div></article>';
      }
    });
  }

  // 2. Buffet & Outlets
  if (filt === 'ALL' || filt === 'BUFFET & OUTLETS') {
    (d.buffetAndVenues || []).forEach(b => {
      const crew = b.crew || [];
      const filtered = crew.filter(c => {
        if (!q) return true;
        return (
          String(c.name || '').toLowerCase().includes(q) ||
          String(c.role || '').toLowerCase().includes(q) ||
          String(b.name || '').toLowerCase().includes(q)
        );
      });

      if (filtered.length || !q) {
        let meta = escapeHtml(b.timing || '—') + '  •  ' + filtered.length + ' crew';
        if (b.lead) meta = 'Lead: ' + escapeHtml(b.lead) + '  •  ' + meta;

        html += '<article class="r-card">';
        html += '<div class="r-card-header">';
        html += '<h3 class="r-card-title">' + escapeHtml(b.name) + '</h3>';
        html += '<span class="r-card-meta meta-slate">' + meta + '</span>';
        html += '</div>';
        html += '<div class="r-card-divider"></div>';
        html += '<div class="r-card-body"><div class="chip-row">';

        filtered.forEach(c => {
          const role = c.role ? ' — ' + escapeHtml(c.role) : '';
          html += '<span class="crew-chip">' + escapeHtml(c.name || '') + role + '</span>';
        });

        html += '</div></div></article>';
      }
    });
  }

  // 3. Side Duties
  if (filt === 'ALL' || filt === 'SIDE DUTIES') {
    (d.sideDuties || []).forEach(s => {
      const crew = s.crew || [];
      const filtered = crew.filter(c => {
        if (!q) return true;
        return (
          String(c.name || '').toLowerCase().includes(q) ||
          String(s.name || '').toLowerCase().includes(q)
        );
      });

      if (filtered.length || !q) {
        html += '<article class="r-card">';
        html += '<div class="r-card-header">';
        html += '<h3 class="r-card-title">' + escapeHtml(s.name) + '</h3>';
        html += '<span class="r-card-meta meta-faint">' + escapeHtml(s.timing || '—') + '  •  ' + filtered.length + ' crew</span>';
        html += '</div>';
        html += '<div class="r-card-divider"></div>';
        html += '<div class="r-card-body"><div class="chip-row">';

        filtered.forEach(c => {
          html += '<span class="crew-chip">' + escapeHtml(c.name || '') + '</span>';
        });

        html += '</div></div></article>';
      }
    });
  }

  // 4. Special Events
  if (filt === 'ALL' && (d.specialEvents || []).length) {
    html += '<article class="r-card">';
    html += '<div class="r-card-header">';
    html += '<h3 class="r-card-title special-title">SPECIAL EVENTS & TRAVEL TALK</h3>';
    html += '</div>';
    html += '<div class="r-card-divider"></div>';
    html += '<div class="r-card-body">';

    (d.specialEvents || []).forEach(ev => {
      html += '<div class="event-box">';
      html += '<div class="event-header">' + escapeHtml(ev.title) + ' — ' + escapeHtml(ev.location) + '</div>';
      html += '<div class="event-participants">';
      (ev.participants || []).forEach(p => {
        html += '<span class="participant-chip">' + escapeHtml(p.name) + ' [' + escapeHtml(p.uniform) + ']</span>';
      });
      html += '</div></div>';
    });

    html += '</div></article>';
  }

  // 5. Sick Leave
  if (filt === 'ALL' && (d.sickLeave || []).length) {
    html += '<article class="r-card">';
    html += '<div class="r-card-header">';
    html += '<h3 class="r-card-title sick-title">SICK LEAVE / OFF DUTY</h3>';
    html += '</div>';
    html += '<div class="r-card-divider"></div>';
    html += '<div class="r-card-body"><div class="chip-row">';

    (d.sickLeave || []).forEach(sk => {
      html += '<span class="crew-chip chip-sick">' + escapeHtml(sk.name || '') + '</span>';
    });

    html += '</div></div></article>';
  }

  if (!html) {
    container.innerHTML = '<div class="empty-state-label">No matching crew or stations found.</div>';
  } else {
    container.innerHTML = html;
  }
}

// ─────────────────────────────────────────────────────────────
// RENDER ALL RESULTS & STATS
// ─────────────────────────────────────────────────────────────
function renderResults() {
  const d = state.scheduleData;
  if (!d) return;

  // Masthead Brand Title
  const brandTitle = document.getElementById('lbl-brand-title');
  if (brandTitle) brandTitle.textContent = d.ship || 'COSTA SMERALDA';

  // Badges
  const badgeDate = document.getElementById('badge-date');
  if (badgeDate) badgeDate.textContent = d.date || '—';

  const badgePort = document.getElementById('badge-port');
  if (badgePort) badgePort.textContent = d.port || '—';

  // File label
  const fileLbl = document.getElementById('lbl-file');
  if (fileLbl) fileLbl.textContent = state.currentFileName || 'No file loaded';

  // Stat Cards
  const stats = calculateStats(d);
  state.cachedCrewCount = stats.crewCount;
  state.cachedSectionCount = stats.sectionCount;

  const statPortVal = document.getElementById('stat-port-val');
  const statPortSub = document.getElementById('stat-port-sub');
  if (statPortVal) statPortVal.textContent = (d.port || '—') + ' / ' + (d.meal || 'LUNCH');
  if (statPortSub) statPortSub.textContent = d.date || '—';

  const statCrewVal = document.getElementById('stat-crew-val');
  const statCrewSub = document.getElementById('stat-crew-sub');
  if (statCrewVal) statCrewVal.textContent = stats.crewCount + ' Crew';
  if (statCrewSub) statCrewSub.textContent = stats.sectionCount + ' Sections';

  const statStationsVal = document.getElementById('stat-stations-val');
  const statStationsSub = document.getElementById('stat-stations-sub');
  if (statStationsVal) statStationsVal.textContent = stats.totalStations + ' Tables';
  if (statStationsSub) statStationsSub.textContent = stats.totalVenues + ' Venues';

  const statPayloadVal = document.getElementById('stat-payload-val');
  const statPayloadSub = document.getElementById('stat-payload-sub');
  if (statPayloadVal) statPayloadVal.textContent = state.payload.length.toLocaleString() + ' Chars';
  if (statPayloadSub) statPayloadSub.textContent = state.b64Data.length.toLocaleString() + ' Bytes';

  // Render cards & QR
  renderCards();
  updateQRPopups();
  setStatus('Ready', TK.good_ink);
}

function setStatus(text, color = TK.good_ink) {
  const lbl = document.getElementById('lbl-status');
  if (lbl) {
    lbl.textContent = text;
    lbl.style.color = color;
  }
}

// ─────────────────────────────────────────────────────────────
// SCHEDULE PROCESSING WORKFLOW
// ─────────────────────────────────────────────────────────────
function loadScheduleData(dataObj, fileName = 'Costa_Serena_Schedule_Sample.xlsx') {
  try {
    state.currentFileName = fileName;
    state.scheduleData = dataObj;
    const res = generatePayload(dataObj);
    state.payload = res.waMessage;
    state.b64Data = res.b64Str;
    renderResults();
  } catch (err) {
    console.error('Failed to load schedule data:', err);
    setStatus('Parse error', TK.bad_ink);
  }
}

function processWorkbook(wb, fileName) {
  try {
    setStatus('Parsing roster...', TK.accent);
    state.rawWorkbook = wb;
    if (fileName) state.currentFileName = fileName;
    const parsed = parseScheduleWorkbook(wb, state.mealShift);
    loadScheduleData(parsed, state.currentFileName);
  } catch (err) {
    console.error('Process workbook error:', err);
    setStatus('Parse error', TK.bad_ink);
    alert('Failed to parse Excel schedule:\n\n' + err.message);
  }
}

function handleFileSelected(file) {
  if (!file) return;
  const fileName = file.name;
  setStatus('Reading ' + fileName + '...', TK.accent);

  const reader = new FileReader();
  reader.onload = function (e) {
    try {
      const data = new Uint8Array(e.target.result);
      const wb = XLSX.read(data, { type: 'array' });
      processWorkbook(wb, fileName);
    } catch (err) {
      console.error('File read error:', err);
      setStatus('File error', TK.bad_ink);
      alert('Could not read Excel file:\n\n' + err.message);
    }
  };
  reader.onerror = function () {
    setStatus('Read error', TK.bad_ink);
    alert('Error occurred while reading the file.');
  };
  reader.readAsArrayBuffer(file);
}

// ─────────────────────────────────────────────────────────────
// AIRGAP QR MODAL LOGIC (QRModal)
// ─────────────────────────────────────────────────────────────
function openQRModal(initialIdx = 0) {
  if (!state.qrSegments || !state.qrSegments.length) {
    alert('Please load an Excel roster file first.');
    return;
  }
  state.currentModalIdx = Math.max(0, Math.min(initialIdx, state.qrSegments.length - 1));
  const backdrop = document.getElementById('qr-modal-backdrop');
  if (backdrop) {
    backdrop.style.display = 'flex';
    showModalSegment(state.currentModalIdx);
  }
}

function closeQRModal() {
  const backdrop = document.getElementById('qr-modal-backdrop');
  if (backdrop) {
    backdrop.style.display = 'none';
  }
}

function showModalSegment(idx) {
  if (!state.qrSegments || idx < 0 || idx >= state.qrSegments.length) return;
  state.currentModalIdx = idx;
  const total = state.qrSegments.length;
  const data = state.qrSegments[idx];

  const qrBox = document.getElementById('modal-qr-box');
  if (qrBox) {
    renderQR(qrBox, data, 460);
  }

  const indicator = document.getElementById('modal-indicator');
  if (indicator) {
    indicator.textContent = 'Part ' + (idx + 1) + ' of ' + total;
  }

  const banner = document.getElementById('modal-step-banner');
  if (banner) {
    banner.textContent = 'Part ' + (idx + 1) + ' of ' + total + ': Point camera at QR, tap "Copy text", then paste into WhatsApp.';
  }

  const btnPrev = document.getElementById('btn-modal-prev');
  if (btnPrev) {
    btnPrev.disabled = (idx === 0);
    btnPrev.style.opacity = (idx === 0) ? '0.5' : '1';
  }

  const btnNext = document.getElementById('btn-modal-next');
  if (btnNext) {
    if (idx === total - 1) {
      btnNext.innerHTML = 'DONE (Close)';
      btnNext.style.backgroundColor = TK.accent;
      btnNext.style.color = '#FFFFFF';
    } else {
      btnNext.innerHTML = 'NEXT PART (Space) ▶';
      btnNext.style.backgroundColor = TK.gold_accent;
      btnNext.style.color = TK.fg_primary;
    }
  }
}

function onModalPrev() {
  if (state.currentModalIdx > 0) {
    showModalSegment(state.currentModalIdx - 1);
  }
}

function onModalNext() {
  if (state.currentModalIdx < state.qrSegments.length - 1) {
    showModalSegment(state.currentModalIdx + 1);
  } else {
    closeQRModal();
  }
}

// ─────────────────────────────────────────────────────────────
// PRIMARY ACTIONS: COPY, SAVE, EXPORT, WEBAPP
// ─────────────────────────────────────────────────────────────
async function copyPayloadAction() {
  if (!state.payload) {
    alert('Load and process a schedule file first.');
    return;
  }

  let success = false;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(state.payload);
      success = true;
    } catch (e) {
      success = false;
    }
  }

  if (!success) {
    const ta = document.createElement('textarea');
    ta.value = state.payload;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      success = true;
    } catch (e) {
      success = false;
    }
    document.body.removeChild(ta);
  }

  triggerCopyFeedback();
}

function triggerCopyFeedback() {
  const btn = document.getElementById('btn-primary-copy');
  const iconWrap = document.getElementById('btn-primary-icon');
  const textWrap = document.getElementById('btn-primary-text');
  if (!btn || !textWrap) return;

  if (state.toastTimer) clearTimeout(state.toastTimer);

  btn.classList.add('copied');
  textWrap.textContent = ' COPIED — READY TO PASTE ON WHATSAPP';
  if (iconWrap) {
    iconWrap.outerHTML = getIconSvg('check', '#FFFFFF', 16);
  }

  state.toastTimer = setTimeout(() => {
    btn.classList.remove('copied');
    textWrap.textContent = 'COPY SCHEDULE TO CLIPBOARD';
    const curSvg = btn.querySelector('.v-icon');
    if (curSvg) {
      curSvg.outerHTML = '<svg class="v-icon icon-dark" id="btn-primary-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
    }
  }, 2400);
}

function quickSaveBackupAction() {
  if (!state.scheduleData) {
    alert('Load a schedule first.');
    return;
  }
  try {
    const now = new Date().toISOString().replace(/[:.]/g, '-');
    const ship = String(state.scheduleData.ship || 'Costa').replace(/\s+/g, '_');
    const meal = String(state.scheduleData.meal || 'Schedule').replace(/\s+/g, '_');
    const key = 'costa_backup_' + ship + '_' + meal + '_' + now;
    localStorage.setItem(key, JSON.stringify(state.scheduleData));
    setStatus('Schedule saved to internal backup', TK.good_ink);
    alert('Schedule saved to internal browser backup:\n' + key);
  } catch (err) {
    console.error('Quick save failed:', err);
    alert('Quick save failed: ' + err.message);
  }
}

function saveAsJsonAction() {
  if (!state.scheduleData) {
    alert('Load a schedule first.');
    return;
  }
  try {
    const jsonStr = JSON.stringify(state.scheduleData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const now = new Date().toISOString().slice(0, 10);
    const ship = String(state.scheduleData.ship || 'Costa').replace(/\s+/g, '_');
    const meal = String(state.scheduleData.meal || 'Schedule').replace(/\s+/g, '_');
    const filename = ship + '_' + meal + '_' + now + '.json';

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setStatus('Saved ' + filename, TK.good_ink);
  } catch (err) {
    console.error('Save As error:', err);
    alert('Save As failed: ' + err.message);
  }
}

function openWebappAction() {
  window.open('CostaSchedule.html', '_blank');
}

// ─────────────────────────────────────────────────────────────
// DOM EVENT LISTENERS & WIRING
// ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // 1. Initial Load of Default Sample Schedule
  loadScheduleData(DEFAULT_SAMPLE_DATA, 'Costa_Serena_Schedule_Sample.xlsx');

  // 2. Browse & Reload Buttons
  const fileInput = document.getElementById('file-input');
  const btnBrowse = document.getElementById('btn-browse');
  const btnReload = document.getElementById('btn-reload');

  if (btnBrowse && fileInput) {
    btnBrowse.addEventListener('click', () => fileInput.click());
  }

  if (fileInput) {
    fileInput.addEventListener('change', e => {
      if (e.target.files && e.target.files[0]) {
        handleFileSelected(e.target.files[0]);
      }
    });
  }

  if (btnReload) {
    btnReload.addEventListener('click', () => {
      if (state.rawWorkbook) {
        processWorkbook(state.rawWorkbook, state.currentFileName);
      } else {
        loadScheduleData(DEFAULT_SAMPLE_DATA, 'Costa_Serena_Schedule_Sample.xlsx');
      }
    });
  }

  // 3. Meal Shift Outline Pills
  const shiftGroup = document.getElementById('shift-pills');
  if (shiftGroup) {
    shiftGroup.querySelectorAll('.outline-pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const val = btn.getAttribute('data-value');
        if (val && val !== state.mealShift) {
          state.mealShift = val;
          shiftGroup.querySelectorAll('.outline-pill-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');

          if (state.rawWorkbook) {
            processWorkbook(state.rawWorkbook, state.currentFileName);
          } else if (state.scheduleData) {
            const updated = Object.assign({}, state.scheduleData, {
              meal: state.mealShift,
              shift: state.mealShift + ' REPORT',
            });
            loadScheduleData(updated, state.currentFileName);
          }
        }
      });
    });
  }

  // 4. Search Bar & Debounce
  const searchInput = document.getElementById('search-entry');
  const btnClearSearch = document.getElementById('btn-clear-search');

  if (searchInput) {
    searchInput.addEventListener('input', e => {
      if (state.searchDebounceTimer) clearTimeout(state.searchDebounceTimer);
      state.searchDebounceTimer = setTimeout(() => {
        state.searchQuery = e.target.value.trim();
        renderCards();
      }, 300);
    });
  }

  if (btnClearSearch && searchInput) {
    btnClearSearch.addEventListener('click', () => {
      searchInput.value = '';
      state.searchQuery = '';
      renderCards();
    });
  }

  // 5. Filter Pills
  const filterGroup = document.getElementById('filter-pills');
  if (filterGroup) {
    filterGroup.querySelectorAll('.outline-pill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const filt = btn.getAttribute('data-filter');
        if (filt && filt !== state.activeFilter) {
          state.activeFilter = filt;
          filterGroup.querySelectorAll('.outline-pill-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          renderCards();
        }
      });
    });
  }

  // 6. Airgap Actions
  const btnEnlarge = document.getElementById('btn-enlarge-qr');
  if (btnEnlarge) {
    btnEnlarge.addEventListener('click', () => openQRModal(0));
  }

  const btnQuickSave = document.getElementById('btn-quick-save');
  if (btnQuickSave) {
    btnQuickSave.addEventListener('click', quickSaveBackupAction);
  }

  const btnSaveAs = document.getElementById('btn-save-as');
  if (btnSaveAs) {
    btnSaveAs.addEventListener('click', saveAsJsonAction);
  }

  // 7. Dual QR Preview Click Handlers
  const qrCard1 = document.getElementById('qr-card-1');
  if (qrCard1) {
    qrCard1.addEventListener('click', () => openQRModal(0));
  }

  const qrCard2 = document.getElementById('qr-card-2');
  if (qrCard2) {
    qrCard2.addEventListener('click', () => openQRModal(1));
  }

  // 8. Bottom Bar Buttons
  const btnPrimaryCopy = document.getElementById('btn-primary-copy');
  if (btnPrimaryCopy) {
    btnPrimaryCopy.addEventListener('click', copyPayloadAction);
  }

  const btnOpenWebapp = document.getElementById('btn-open-webapp');
  if (btnOpenWebapp) {
    btnOpenWebapp.addEventListener('click', openWebappAction);
  }

  // 9. QR Modal Navigation & Close
  const btnModalClose = document.getElementById('btn-modal-close');
  if (btnModalClose) {
    btnModalClose.addEventListener('click', closeQRModal);
  }

  const btnModalPrev = document.getElementById('btn-modal-prev');
  if (btnModalPrev) {
    btnModalPrev.addEventListener('click', onModalPrev);
  }

  const btnModalNext = document.getElementById('btn-modal-next');
  if (btnModalNext) {
    btnModalNext.addEventListener('click', onModalNext);
  }

  const modalBackdrop = document.getElementById('qr-modal-backdrop');
  if (modalBackdrop) {
    modalBackdrop.addEventListener('click', e => {
      if (e.target === modalBackdrop) {
        closeQRModal();
      }
    });
  }

  // 10. Modal Keyboard Shortcuts
  window.addEventListener('keydown', e => {
    const backdrop = document.getElementById('qr-modal-backdrop');
    const isModalOpen = backdrop && backdrop.style.display === 'flex';

    if (!isModalOpen) return;

    const key = e.key;
    if (key === 'Escape') {
      e.preventDefault();
      closeQRModal();
    } else if (key === ' ' || key === 'Enter') {
      e.preventDefault();
      onModalNext();
    } else if (key === 'ArrowLeft' || key === 'ArrowUp') {
      e.preventDefault();
      onModalPrev();
    } else if (key === 'ArrowRight' || key === 'ArrowDown') {
      e.preventDefault();
      onModalNext();
    }
  });

  // 11. Drag & Drop File Handling
  const dndOverlay = document.getElementById('dnd-overlay');
  let dndCounter = 0;

  window.addEventListener('dragenter', e => {
    e.preventDefault();
    dndCounter++;
    if (dndOverlay) dndOverlay.classList.add('active');
  });

  window.addEventListener('dragleave', e => {
    e.preventDefault();
    dndCounter--;
    if (dndCounter <= 0) {
      dndCounter = 0;
      if (dndOverlay) dndOverlay.classList.remove('active');
    }
  });

  window.addEventListener('dragover', e => {
    e.preventDefault();
  });

  window.addEventListener('drop', e => {
    e.preventDefault();
    dndCounter = 0;
    if (dndOverlay) dndOverlay.classList.remove('active');

    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length) {
      const file = e.dataTransfer.files[0];
      if (/\.(xlsx|xls)$/i.test(file.name)) {
        handleFileSelected(file);
        setStatus('Roster loaded via drag & drop', TK.good_ink);
      } else {
        setStatus('Drop a valid Excel file (.xlsx)', TK.warn_ink);
        alert('Please drop a valid Excel file (.xlsx or .xls).');
      }
    }
  });
});
