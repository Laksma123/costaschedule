/**
 * Costa Smeralda Restaurant Schedule System - Client App
 * 100% Offline Progressive Web App
 */

// Service Worker Registration for Offline Caching
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch(err => {
      console.log('SW registration skipped:', err);
    });
  });
}

// App State
const state = {
  currentDay: 'today',       // 'today' | 'yesterday'
  currentMeal: 'LUNCH',     // 'BREAKFAST' | 'LUNCH' | 'DINNER'
  searchQuery: '',
  profile: {
    name: localStorage.getItem('costa_user_name') || ''
  },
  alarm: {
    enabled: localStorage.getItem('costa_alarm_enabled') !== 'false', // default: true
    option: localStorage.getItem('costa_alarm_option') || '60',       // '60' | '30' | 'custom'
    customHours: parseInt(localStorage.getItem('costa_alarm_custom_h') || '1', 10),
    customMinutes: parseInt(localStorage.getItem('costa_alarm_custom_m') || '0', 10)
  },
  schedules: loadStoredSchedules(),
  allExpanded: false,
  bedside: {
    timer: null,
    wakeLock: null,
    active: false,
    isRinging: false,
    targetHour: 0,
    targetMin: 0
  }
};

// ==========================================
// REAL SAMPLE DATA (Costa Smeralda Schedule Format)
// ==========================================
const SAMPLE_SCHEDULE = {
  ship: "COSTA SMERALDA",
  port: "KAOHSIUNG",
  date: "August 23, 2026",
  shift: "LUNCH REPORT 11:00",
  meal: "LUNCH",
  timestamp: Date.now(),
  venues: [
    {
      name: "Ceres Restaurant Main (Deck 5)",
      reportTime: "11:00",
      assignments: [
        { station: "1", waiterName: "WIBOWO ANDRI -BS", attendantName: "", tables: "302, 304, 306, 362, 364" },
        { station: "2", waiterName: "PUTRA DUWI LAKSANA -BS", attendantName: "", tables: "308, 310, 312, 366, 368" },
        { station: "3", waiterName: "SETIOBUDI NIDZAR DICKY -TR -CT", attendantName: "", tables: "314, 316, 370, 372, 374" },
        { station: "4", waiterName: "WIJAYA I GEDE ARIK -TR CT", attendantName: "", tables: "318, 320, 322, 324, 344, 346" },
        { station: "5", waiterName: "WIDYANTARA I GUSTI NGURAH -TR", attendantName: "", tables: "326, 328, 330, 338, 340, 342" },
        { station: "6", waiterName: "HUSEN MUSTAFA AHMAD", attendantName: "", tables: "331, 332, 333, 334, 335, 336, 337" },
        { station: "7", waiterName: "ROHMAN FADILI", attendantName: "", tables: "325, 327, 329, 339, 341, 343, 345" },
        { station: "8", waiterName: "HAIRUDIN EXDA -CT", attendantName: "", tables: "317, 319, 321, 323, 347, 349" },
        { station: "9", waiterName: "SHARMA VICKY CHANDESWAR", attendantName: "", tables: "313, 315, 351, 373, 375, 377" },
        { station: "10", waiterName: "HALANKAR SACHIN SHAM -LINEN", attendantName: "", tables: "307, 309, 311, 357, 359" },
        { station: "11", waiterName: "THAKUR AKSHAY VISHNU -LINEN", attendantName: "", tables: "301, 303, 305, 365, 367" },
        { station: "12", waiterName: "SARMADI KEVIN TEGUH -DIRECTIONE", attendantName: "", tables: "376, 378, 380, 382, 410, 379, 381, 383, 385, 413" },
        { station: "13", waiterName: "CAMBA GHIEMER PAUL -CT", attendantName: "", tables: "403, 405, 407, 427" },
        { station: "14", waiterName: "JOSHI PREM", attendantName: "", tables: "400, 402, 404, 424" }
      ]
    },
    {
      name: "Ceres Upper (Deck 6)",
      reportTime: "11:00",
      assignments: [
        { station: "28", waiterName: "RAHI AKASH", attendantName: "", tables: "Upper Station 28" },
        { station: "30", waiterName: "SIPAHUTAR DOLY CRISTIAN", attendantName: "", tables: "Upper Station 30" },
        { station: "32", waiterName: "DSOUZA RITHESHA", attendantName: "", tables: "Upper Station 32" },
        { station: "34", waiterName: "MANNA MANOJ", attendantName: "", tables: "Upper Station 34" },
        { station: "36", waiterName: "MALE ASHISH ANTHONY", attendantName: "", tables: "Upper Station 36" },
        { station: "37", waiterName: "TEMAJA MADE SINGA", attendantName: "", tables: "Upper Station 37" },
        { station: "39", waiterName: "PRABOWO AJI SURYA", attendantName: "", tables: "Upper Station 39" }
      ]
    },
    {
      name: "Vesta Upper (Deck 6)",
      reportTime: "11:00",
      assignments: [
        { station: "62", waiterName: "SUSILA PUTU PANDE", attendantName: "WARDANA WAYAN ADI WISNU", tables: "Vesta 62" },
        { station: "63", waiterName: "LAUAN MARY", attendantName: "SATYAMA I KADEK", tables: "Vesta 63" },
        { station: "64", waiterName: "RAMESH KUMAR", attendantName: "THAPA SAURABH", tables: "Vesta 64" },
        { station: "65", waiterName: "KARMAKAR SUDIP", attendantName: "RAFLI RIFKI -TR", tables: "Vesta 65" },
        { station: "66", waiterName: "KALE SAGAR", attendantName: "PRADHAN SAYANTA RABIN", tables: "Vesta 66" },
        { station: "67", waiterName: "DARMAWAN I GUSTI PUTU ERI -CC", attendantName: "LAZAGA MARIA", tables: "Vesta 67" },
        { station: "68", waiterName: "KUMAR ABHIJEET", attendantName: "WASIUN MOHAMMAD ROHIB", tables: "Vesta 68" },
        { station: "69", waiterName: "INDRAWAN SALEH ARIF", attendantName: "CATINDIG MATAWARAN HEIDEE", tables: "Vesta 69" },
        { station: "70", waiterName: "PRAWIRA EDWIN -BS", attendantName: "ALPHONSO MICHAEL PAUL", tables: "Vesta 70" }
      ]
    },
    {
      name: "Suite Elite",
      reportTime: "11:00",
      assignments: [
        { station: "SE-1", waiterName: "NINGAMLA RAGUI", attendantName: "", tables: "Suite VIP Section" }
      ]
    }
  ],
  buffetAndVenues: [
    {
      name: "Buffet Deck 9 (Main - 32 Crew)",
      timing: "07:00-10:00 / 11:00-14:00",
      lead: "SRS LI ZHI",
      crew: [
        { name: "SHANMUGAM KARTHICK KUMAR" },
        { name: "DINGANKAR RITESH" },
        { name: "PRAMADYA FIKRYAN SURYA" },
        { name: "PRABU TAMA" },
        { name: "RAJ AMAN" },
        { name: "WAFA MUHAMMAD HILMI" },
        { name: "DEWI PUTU AYU RISTIANA" },
        { name: "FRANSISKA OCTAVIA MELIANA" },
        { name: "UMAM DAVID NUR" },
        { name: "DWIATMO JOKO" },
        { name: "YULIASTUTI EKA" },
        { name: "KESUMA SANG NYOMAN ARDIKA" },
        { name: "JAMALUDDIN XXX" },
        { name: "SETIAWAN MUKLIS" },
        { name: "WIDIARTA I PUTU HENDRA" },
        { name: "MUMAR BALONGA ZISKA" },
        { name: "CARDOZO BENZY FRANKLLIN" },
        { name: "BITUIN JOHN HOWEN" },
        { name: "ARTHA WIGUNA GEDE KOMANG" },
        { name: "GEORGE PETER SEBASTIAN" },
        { name: "SHAHI VIKRANT" },
        { name: "SAPUTRA I WAYAN SUMADI ADI" },
        { name: "SHAABAN ALI" },
        { name: "SEJATI MUHAMMAD AGUS WAHYU" },
        { name: "SOMBILON TACANG SHEENA LOU" },
        { name: "FLORES LENNY JOY" },
        { name: "TOGNI JUDY ANN" },
        { name: "NANDA JUILTA ARIA" },
        { name: "JASMINE IVANA" }
      ]
    },
    {
      name: "Specialty Restaurants & Lounges",
      timing: "Per Shift Roster",
      crew: [
        { name: "RAJBHAR RAHUL MEGHNATH", role: "Noodle Bar 12:30-15:30/16:30-24:30" },
        { name: "PERMANA EPRIN OKTAVIAN", role: "Pizzeria 12:30-15:30/18:30-02:30" },
        { name: "CHHETRI SHUBHAM", role: "Pizzeria 12:15-15:15/18:15-02:15" },
        { name: "BHADALE SIDDHANT", role: "Pizzeria 12:30-15:30/18:30-02:30" },
        { name: "CHEN SUIYAN", role: "Salty Beach 13:00-16:30/19:30-01:00/02:30-04:30" },
        { name: "WIJAYA KETUT PUTRA", role: "Salty Beach 17:00-19:30/20:30-02:30/04:00-06:30" },
        { name: "SADEWA BENYAMIN BENY", role: "Sushino (Report 11:00)" },
        { name: "MUYCO VILLA ABRILLE JAN CLOYDE", role: "Sushino (Report 11:00)" },
        { name: "NEGARA I KOMANG ABDI", role: "Casanova (Report 11:00)" },
        { name: "ERON DIONSON SAMUEL", role: "Steakhouse (Report 11:00)" },
        { name: "MAHENDRA PRATAMA I PUTU GEDE DEVA", role: "Steakhouse (Report 11:00)" },
        { name: "GENG YANAN", role: "Hot Pot Team (Selling Area 10:00-14:00)" },
        { name: "DEGUNE JASPAL", role: "Hot Pot Team (Selling Area 10:00-14:00)" },
        { name: "KURNIA TEGAR", role: "Hot Pot Team (Selling Area 10:00-14:00)" },
        { name: "PANGESTU PANJI FAJAR", role: "Hot Pot Team (Selling Area 10:00-14:00)" }
      ]
    }
  ],
  sideDuties: [
    {
      name: "DRS 07:00-13:00",
      timing: "07:00-13:00",
      crew: [
        { name: "RAMANDA LAKSMANA DIAN" }
      ]
    },
    {
      name: "Office Disposition (07:00-13:00)",
      timing: "07:00-13:00",
      crew: [
        { name: "RAMOS LESLIE" },
        { name: "JUANILLO USOG MAE RUSELLE -HANDOVER RECEIVER" }
      ]
    },
    {
      name: "Reservation Call",
      timing: "Shift Duty",
      crew: [
        { name: "LU YANLING" }
      ]
    },
    {
      name: "Vesta Upper by the Door (11:00)",
      timing: "11:00",
      crew: [
        { name: "ANTARI NI WAYAN DESI -FRONT" }
      ]
    },
    {
      name: "Vesta Lower by the Door (11:15-14:15)",
      timing: "11:15-14:15",
      crew: [
        { name: "LU YANLING -FRONT" }
      ]
    },
    {
      name: "Linen Incharge (08:00-14:00)",
      timing: "08:00-14:00",
      crew: [
        { name: "DJODI ACHMAD SETIA" }
      ]
    },
    {
      name: "Cleaning After Breakfast (13:00)",
      timing: "13:00",
      crew: [
        { name: "BURHANUDIN MUHAMAD RIZKI -CT" },
        { name: "PUTRA ERICHO ALLAM FAQIHSYAH -CT" },
        { name: "SETIAWAN HERU -CT" }
      ]
    },
    {
      name: "Buffet Deck 9 Report with SRS Li Zhi",
      timing: "07:00-10:00 / 11:00-14:00",
      crew: [
        { name: "PRATAMA WILY -DECK 3 FWD ELEVATOR & LOBBY" },
        { name: "ENDANG SAHIDIN -DECK 5 ALL LOUNGES" },
        { name: "NUGRAHA PUTU WIRA -DECK 3 CERES & LOUNGES" },
        { name: "ASEO GLADY'S -BUFFET DECK 9" }
      ]
    },
    {
      name: "Magazinero Report (08:00-14:00)",
      timing: "08:00-14:00",
      crew: [
        { name: "BAPTISTA WILSON AUSTIN" },
        { name: "SYAMSI KHAERUL" }
      ]
    },
    {
      name: "Folding Napkin Deck 10",
      timing: "07:00-10:00 / 11:00-14:00",
      crew: [
        { name: "KRENDANA ANGGRA -07:00-10:00/11:00-14:00" },
        { name: "HIDAYAH SHOHIBUL -07:00-10:00/11:00-14:00" }
      ]
    },
    {
      name: "Check Crew Mess Schedule",
      timing: "Shift Duty",
      crew: [
        { name: "DSOUZA YORICK ROQUE JOHNSON" },
        { name: "XXX EI EI HTAR" },
        { name: "XXX CHIT KO KO ZAW" }
      ]
    },
    {
      name: "Ceres — Refilling Team A (Report at 10:45)",
      timing: "10:45",
      crew: [
        { name: "ARYANTO I PUTU AGUS" },
        { name: "SUARJANA MADE" },
        { name: "ABADI SULASTOMO" },
        { name: "GADIANO PAICA APRILLE JANE" },
        { name: "ERYANTO XXX" },
        { name: "ANATHASYA PRILY" }
      ]
    },
    {
      name: "Ceres — Refilling Team B (Report at 11:00)",
      timing: "11:00",
      crew: [
        { name: "DARSANA I NYOMAN" },
        { name: "MUKHI ROSHAN" },
        { name: "NEMIS BENEDICT" },
        { name: "FALLADO CARREL" }
      ]
    },
    {
      name: "Ceres — Resetting Team (Report at 11:30)",
      timing: "11:30",
      crew: [
        { name: "HERMAWAN WAWAN" },
        { name: "SANTIAGO ANDREW" },
        { name: "PRABANGKARA IDA BAGUS PUTU KRISNA -SG" }
      ]
    }
  ],
  specialEvents: [
    {
      title: "TRAVEL TALK — 05 NOVEMBER 2024 AT 10:40",
      location: "Stand by in front of Theater Deck 3",
      participants: [
        { name: "CONCEPCION ILOGON ANNE JENESSE", uniform: "Day Uniform" },
        { name: "GU YUAN", uniform: "Day Uniform" },
        { name: "SEMERTI NI MADE DIAN BUDI", uniform: "Dinner Uniform" },
        { name: "SOFYAN HELMI", uniform: "Dinner Uniform" }
      ]
    }
  ],
  sickLeave: [
    { name: "MOHANTY DEEPAK RAJ" },
    { name: "SHEIKH AMIR SULEMAN" },
    { name: "SALVADOR JOMEL" },
    { name: "KUMBHAR AJAY PANDURANG" }
  ]
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  
  // Set sample as default for today lunch if empty
  if (!state.schedules.today[state.currentMeal]) {
    state.schedules.today[state.currentMeal] = SAMPLE_SCHEDULE;
    saveStoredSchedules();
  }
  
  renderSchedule();

  // Smoothly dismiss splash loading & validation overlay
  setTimeout(() => {
    const splash = document.getElementById('splashOverlay');
    if (splash) {
      splash.classList.add('fade-out');
      setTimeout(() => splash.remove(), 400);
    }
  }, 400);
});

// ==========================================
// STORAGE & RETENTION MANAGEMENT (2 DAYS / 6 SLOTS)
// ==========================================
function loadStoredSchedules() {
  const defaultStructure = {
    today: { BREAKFAST: null, LUNCH: null, DINNER: null },
    yesterday: { BREAKFAST: null, LUNCH: null, DINNER: null },
    lastUpdated: Date.now()
  };

  try {
    const raw = localStorage.getItem('costa_schedules');
    if (!raw) return defaultStructure;
    const data = JSON.parse(raw);

    const now = Date.now();
    const oneDayMs = 24 * 60 * 60 * 1000;
    if (data.lastUpdated && (now - data.lastUpdated > oneDayMs)) {
      data.yesterday = data.today;
      data.today = { BREAKFAST: null, LUNCH: null, DINNER: null };
      data.lastUpdated = now;
      localStorage.setItem('costa_schedules', JSON.stringify(data));
    }
    return data;
  } catch (e) {
    console.error('Failed to load storage:', e);
    return defaultStructure;
  }
}

function saveStoredSchedules() {
  state.schedules.lastUpdated = Date.now();
  localStorage.setItem('costa_schedules', JSON.stringify(state.schedules));
}

// ==========================================
// PAYLOAD PARSER & DECODER
// ==========================================
function parseWhatsAppPayload(text) {
  if (!text || typeof text !== 'string') {
    throw new Error('Empty message received.');
  }

  let rawEncoded = text.trim();

  const startTag = '[COSTA-DATA-START]';
  const endTag = '[COSTA-DATA-END]';
  
  const startIndex = text.indexOf(startTag);
  const endIndex = text.indexOf(endTag);

  if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
    rawEncoded = text.substring(startIndex + startTag.length, endIndex).trim();
  }

  rawEncoded = rawEncoded.replace(/[\*\_\s]/g, '');

  let jsonString = '';

  if (rawEncoded.startsWith('{') && rawEncoded.endsWith('}')) {
    jsonString = rawEncoded;
  } else {
    try {
      jsonString = decodeURIComponent(escape(atob(rawEncoded)));
    } catch (e1) {
      try {
        jsonString = atob(rawEncoded);
      } catch (e2) {
        throw new Error('Failed to decode Base64 data. Ensure the full message was copied.');
      }
    }
  }

  let scheduleObj;
  try {
    scheduleObj = JSON.parse(jsonString);
  } catch (err) {
    throw new Error('Invalid schedule format: ' + err.message);
  }

  if (!scheduleObj || !scheduleObj.meal) {
    throw new Error('Incomplete schedule structure.');
  }

  scheduleObj.timestamp = Date.now();
  return scheduleObj;
}

// ==========================================
// USER PROFILE & SMART NAME MATCHING
// ==========================================
function hasUserProfile() {
  return Boolean((state.profile.name || '').trim());
}

function cleanNameString(str) {
  if (!str) return '';
  return str.toString().toUpperCase()
    .replace(/-(BS|TR|CT|LINEN|DIRECTIONE|SG|CC|FRONT|D|PZ|HANDOVER RECEIVER|SELLING HOTPOT AREA)\b/g, '')
    .replace(/XXX\b/g, '')
    .replace(/[^\w\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function isCurrentUser(name) {
  const myFullName = cleanNameString(state.profile.name || '');
  if (!myFullName || !name) return false;

  const targetClean = cleanNameString(name);
  if (!targetClean) return false;

  if (myFullName === targetClean) return true;

  const myTokens = myFullName.split(' ').filter(t => t.length >= 2);
  const targetTokens = targetClean.split(' ').filter(t => t.length >= 2);

  if (myTokens.length === 0 || targetTokens.length === 0) return false;

  // Check if at least 2 tokens match or all user tokens match
  const matchingTokens = myTokens.filter(token => targetTokens.includes(token));
  if (matchingTokens.length >= 2 || (myTokens.length === 1 && matchingTokens.length === 1 && targetTokens.includes(myTokens[0]))) {
    return true;
  }

  if (myTokens.every(token => targetTokens.includes(token))) return true;
  if (targetTokens.length >= 2 && targetTokens.every(token => myTokens.includes(token))) return true;

  return false;
}

function matchesSearchQuery(query, name, extra1, extra2, extra3) {
  if (!query) return true;
  const q = query.trim().toLowerCase();
  if (name && name.toLowerCase().includes(q)) return true;
  if (extra1 && extra1.toLowerCase().includes(q)) return true;
  if (extra2 && extra2.toLowerCase().includes(q)) return true;
  if (extra3 && extra3.toLowerCase().includes(q)) return true;

  // Multi-token matching (e.g. searching "Laksmana Dian" or "Ramanda Dian" matches "RAMANDA LAKSMANA DIAN")
  const qTokens = q.split(/\s+/).filter(t => t.length >= 2);
  if (qTokens.length > 1 && name) {
    const nameClean = cleanNameString(name).toLowerCase();
    const nameTokens = nameClean.split(/\s+/).filter(t => t.length >= 2);
    const matchCount = qTokens.filter(t => nameTokens.includes(t)).length;
    if (matchCount >= 2 || matchCount === qTokens.length) {
      return true;
    }
  }

  // Also if query matches current profile, check isCurrentUser
  if (state.profile.name && q === state.profile.name.toLowerCase()) {
    if (isCurrentUser(name)) return true;
  }

  return false;
}

// ==========================================
// RENDER ENGINE (Newspaper Editorial System)
// ==========================================
function renderSchedule() {
  const schedule = state.schedules[state.currentDay][state.currentMeal];
  const query = (state.searchQuery || '').trim().toLowerCase();

  const emptyState = document.getElementById('emptyState');
  const scheduleContent = document.getElementById('scheduleContent');
  const overviewWrap = document.getElementById('scheduleOverviewSection');

  // Update Profile & Alarm Button Visibility
  updateUserProfilePill();
  updateAlarmButtonVisibility();

  if (!schedule) {
    if (emptyState) emptyState.classList.remove('hidden');
    if (scheduleContent) scheduleContent.classList.add('hidden');
    if (overviewWrap) overviewWrap.classList.add('hidden');
    const dDate = document.getElementById('displayDate');
    if (dDate) dDate.innerText = 'No Date';
    const dPortName = document.getElementById('displayPortName');
    if (dPortName) dPortName.innerText = 'AT SEA';
    const bPort = document.getElementById('briefingPort');
    if (bPort) bPort.innerText = 'AT SEA';
    const bDuty = document.getElementById('briefingDuty');
    if (bDuty) bDuty.innerText = hasUserProfile() ? `Not Scheduled for ${state.currentMeal}` : 'Tap Profile in More tab';
    const bStn = document.getElementById('briefingStation');
    if (bStn) bStn.innerText = '—';
    const spotlight = document.getElementById('personalDutySpotlight');
    if (spotlight) spotlight.classList.add('hidden');
    updatePillDisplay(null);
    return;
  }

  if (emptyState) emptyState.classList.add('hidden');
  if (scheduleContent) scheduleContent.classList.remove('hidden');
  if (overviewWrap) overviewWrap.classList.remove('hidden');

  // Update Newspaper Masthead & Port Headline
  const portUpper = (schedule.port || 'KAOHSIUNG').toUpperCase();
  const dDate = document.getElementById('displayDate');
  if (dDate) dDate.innerText = schedule.date || 'Today';
  const dPortName = document.getElementById('displayPortName');
  if (dPortName) dPortName.innerText = portUpper;
  const dPort = document.getElementById('displayPort');
  if (dPort) dPort.innerText = '📍 ' + portUpper;
  const bPort = document.getElementById('briefingPort');
  if (bPort) bPort.innerText = portUpper;

  // Find User Assigned Duty & Update Personal Shift Spotlight
  const userDuty = findUserDuty(schedule);
  updatePillDisplay(userDuty, schedule.shift);
  updatePersonalBriefingAndSpotlight(userDuty, schedule);
  renderQuickVenuesOverview(schedule);

  // Render Sections with Search Query Filter
  let matchCount = 0;
  matchCount += renderMainDining(schedule.venues || [], query);
  matchCount += renderBuffetAndVenues(schedule.buffetAndVenues || [], query);
  matchCount += renderSideDuties(schedule.sideDuties || [], query);
  matchCount += renderSpecialEvents(schedule.specialEvents || [], query);
  matchCount += renderSickLeave(schedule.sickLeave || [], query);

  // Update Search Counter
  const countEl = document.getElementById('searchCount');
  if (countEl) {
    if (query) {
      countEl.innerHTML = `Found ${matchCount} matches <span id="searchJumpVenuesLink" style="cursor:pointer;color:var(--costa-blue);text-decoration:underline;font-weight:600;margin-left:4px;">(View &rarr;)</span>`;
      const jumpLink = document.getElementById('searchJumpVenuesLink');
      if (jumpLink) {
        jumpLink.onclick = () => switchTab('tabVenues');
      }
      autoExpandOnSearch(true);
    } else {
      countEl.innerText = '';
      if (!state.allExpanded) {
        applyDefaultCollapseState();
      }
    }
  }
}

function updatePersonalBriefingAndSpotlight(userDuty, schedule) {
  const bDuty = document.getElementById('briefingDuty');
  const bStn = document.getElementById('briefingStation');
  const spotlight = document.getElementById('personalDutySpotlight');
  const sTime = document.getElementById('spotlightReportTime');
  const sVenue = document.getElementById('spotlightVenueName');
  const sDetails = document.getElementById('spotlightDetailsText');

  if (!hasUserProfile()) {
    if (bDuty) bDuty.innerText = 'Tap Profile to Set Name';
    if (bStn) bStn.innerText = '—';
    if (spotlight) spotlight.classList.add('hidden');
    return;
  }

  if (userDuty) {
    const venueName = userDuty.venue || userDuty.sideDuty || 'Assigned Duty';
    const reportTime = formatDutyTimeForPill(userDuty.time) || userDuty.time || '11:00';
    if (bDuty) bDuty.innerText = `${venueName} at ${reportTime}`;

    let stnText = '—';
    if (userDuty.station) {
      stnText = `STN ${userDuty.station}` + (userDuty.tables ? ` • Tables: ${userDuty.tables}` : '');
    } else if (userDuty.lead) {
      stnText = `Lead: ${userDuty.lead}`;
    } else if (userDuty.sideDuty) {
      stnText = `Side Duty Assignment`;
    }
    if (bStn) bStn.innerText = stnText;

    if (spotlight) {
      spotlight.classList.remove('hidden');
      if (sTime) sTime.innerText = reportTime;
      if (sVenue) sVenue.innerText = venueName;
      if (sDetails) {
        if (userDuty.station) {
          sDetails.innerHTML = `Station: <strong>STN ${userDuty.station}</strong> &bull; Tables: <strong>${userDuty.tables || 'Assigned'}</strong>`;
        } else if (userDuty.lead) {
          sDetails.innerHTML = `Team Lead: <strong>${userDuty.lead}</strong>`;
        } else {
          sDetails.innerHTML = `Operation: <strong>${userDuty.sideDuty || 'Scheduled Task'}</strong>`;
        }
      }
    }
  } else {
    if (bDuty) bDuty.innerText = `Not scheduled for ${state.currentMeal}`;
    if (bStn) bStn.innerText = 'Standby / Off Duty';
    if (spotlight) spotlight.classList.add('hidden');
  }
}

function renderQuickVenuesOverview(schedule) {
  const listEl = document.getElementById('overviewVenuesList');
  if (!listEl) return;
  listEl.innerHTML = '';

  const allVenues = [
    ...(schedule.venues || []).map(v => ({ name: v.name, time: v.reportTime, count: (v.assignments || []).length })),
    ...(schedule.buffetAndVenues || []).map(b => ({ name: b.name, time: b.timing, count: (b.crew || []).length }))
  ];

  if (allVenues.length === 0) {
    listEl.innerHTML = '<div style="font-size:0.82rem; color:var(--costa-slate); padding:10px 0;">No active venues for this meal shift.</div>';
    return;
  }

  allVenues.slice(0, 5).forEach(v => {
    const card = document.createElement('div');
    card.className = 'overview-venue-card';
    card.innerHTML = `
      <div>
        <div class="overview-venue-name">${escapeHtml(v.name)}</div>
        <div class="overview-venue-meta">Report Time: <strong>${escapeHtml(v.time || 'Standard')}</strong></div>
      </div>
      <span class="overview-badge">${v.count} Crew</span>
    `;
    card.onclick = () => {
      switchTab('tabVenues');
      const cat = document.getElementById('catMainDining');
      if (cat) {
        cat.classList.remove('collapsed');
        const b = document.getElementById('bodyMainDining');
        if (b) b.classList.remove('hidden');
      }
    };
    listEl.appendChild(card);
  });
}

function getShortVenueName(userDuty) {
  if (!userDuty) return 'ON DUTY';

  if (userDuty.sideDuty) {
    const sd = userDuty.sideDuty;
    if (/^DRS/i.test(sd)) return 'DRS';
    if (/Refilling Team A/i.test(sd)) return 'REFILLING A';
    if (/Refilling Team B/i.test(sd)) return 'REFILLING B';
    if (/Resetting Team/i.test(sd)) return 'RESETTING';
    if (/Office Disposition/i.test(sd)) return 'OFFICE';
    if (/Reservation Call/i.test(sd)) return 'RESERVATION';
    if (/Vesta Upper by the Door|Vesta Lower by the Door|Vesta Door/i.test(sd)) return 'VESTA DOOR';
    if (/Linen Incharge/i.test(sd)) return 'LINEN';
    if (/Cleaning/i.test(sd)) return 'CLEANING';
    if (/Magazinero/i.test(sd)) return 'MAGAZINERO';
    if (/Folding Napkin/i.test(sd)) return 'FOLDING NAPKIN';
    if (/Crew Mess/i.test(sd)) return 'CREW MESS';
    if (/Travel Talk/i.test(sd)) return 'TRAVEL TALK';
  }

  const v = userDuty.venue || '';
  if (/Ceres.*Main/i.test(v)) return 'CERES MAIN';
  if (/Ceres.*Upper/i.test(v)) return 'CERES UPPER';
  if (/Vesta.*Upper/i.test(v)) return 'VESTA UPPER';
  if (/Suite Elite/i.test(v)) return 'SUITE ELITE';
  if (/Noodle Bar/i.test(v)) return 'NOODLE BAR';
  if (/Pizzeria/i.test(v)) return 'PIZZERIA';
  if (/Salty Beach/i.test(v)) return 'SALTY BEACH';
  if (/Sushino/i.test(v)) return 'SUSHINO';
  if (/Casanova/i.test(v)) return 'CASANOVA';
  if (/Steakhouse/i.test(v)) return 'STEAKHOUSE';
  if (/Hot Pot/i.test(v)) return 'HOT POT';
  if (/Buffet/i.test(v)) return 'BUFFET DECK 9';
  if (/Theater/i.test(v)) return 'TRAVEL TALK';

  return v.replace(/Restaurant/i, '').replace(/\(.*\)/g, '').trim().toUpperCase() || 'ON DUTY';
}

function formatDutyTimeForPill(timeStr) {
  if (!timeStr) return '';
  let cleaned = timeStr.replace(/^(Report\s*(at)?\s*|Stand\s*by\s*(at)?\s*)/i, '').trim();
  if (/^(Shift Duty|Scheduled Shift)$/i.test(cleaned)) {
    return '';
  }
  return cleaned;
}

// Update Top Right Yellow Shift Pill (Supports start time AND end time)
function updatePillDisplay(userDuty, defaultShiftText) {
  const pill = document.getElementById('displayShift');
  const pillText = document.getElementById('shiftPillText');

  if (!hasUserProfile()) {
    pill.className = 'shift-pill pill-empty';
    pillText.innerText = 'TAP PROFILE TO SET';
    return;
  }

  if (userDuty) {
    pill.className = 'shift-pill';
    const shortVenue = getShortVenueName(userDuty);
    const timeFormatted = formatDutyTimeForPill(userDuty.time);
    if (timeFormatted) {
      pillText.innerText = `${shortVenue} • ${timeFormatted}`;
    } else {
      pillText.innerText = shortVenue;
    }
  } else {
    pill.className = 'shift-pill pill-empty';
    pillText.innerText = 'NOT SCHEDULED';
  }
}

// Update User Profile Pill in Header & More Screen
function updateUserProfilePill() {
  const pill = document.getElementById('userProfilePill');
  const nameEl = document.getElementById('userPillName');
  const avatarEl = document.getElementById('userAvatarCircle');
  const headerAvatar = document.getElementById('headerAvatarCircle');
  const moreSubtext = document.getElementById('moreProfileSubtext');

  const fullName = state.profile.name ? state.profile.name.toUpperCase().trim() : 'CREW MEMBER';
  const words = fullName.split(/\s+/).filter(Boolean);
  let initials = 'CR';
  if (words.length >= 2) {
    initials = (words[0][0] + words[words.length - 1][0]).toUpperCase();
  } else if (words.length === 1 && words[0].length >= 2) {
    initials = words[0].substring(0, 2).toUpperCase();
  }

  if (headerAvatar) headerAvatar.innerText = initials;
  if (avatarEl) avatarEl.innerText = initials;
  if (nameEl) nameEl.innerText = fullName;
  if (moreSubtext) {
    moreSubtext.innerHTML = hasUserProfile() 
      ? `<strong>${escapeHtml(fullName)}</strong> &bull; Settings and personal data`
      : `Tap to configure your full name & alarms`;
  }

  if (pill) {
    pill.classList.remove('hidden'); // Always visible in Tab 4 More so crew can configure
  }
}

// Find User Duty across all tables and duties
function findUserDuty(schedule) {
  if (!hasUserProfile()) return null;

  // 1. Check Side Duties first (DRS, Office, Linen, Refilling, Resetting, etc.)
  for (const d of schedule.sideDuties || []) {
    for (const c of d.crew || []) {
      if (isCurrentUser(c.name)) {
        let dutyTime = d.timing || '';
        if (!dutyTime || dutyTime === 'Shift Duty') {
          const m = d.name.match(/\d{1,2}:\d{2}(?:\s*-\s*\d{1,2}:\d{2})?/);
          if (m) dutyTime = m[0];
        }
        const crewTimeMatch = (c.name || '').match(/\d{1,2}:\d{2}(?:-\d{1,2}:\d{2})?(?:\/\d{1,2}:\d{2}-\d{1,2}:\d{2})?/);
        if (crewTimeMatch && (!dutyTime || dutyTime === 'Shift Duty')) {
          dutyTime = crewTimeMatch[0];
        }

        return {
          name: c.name,
          venue: d.name.startsWith('DRS') ? 'DRS (Deck Operations)' : 'Side Duties & Operations',
          station: d.name,
          time: dutyTime || '07:00-13:00',
          tables: d.name.startsWith('DRS') ? 'Deck Operations' : 'Assigned Operation',
          sideDuty: d.name,
          uniform: null
        };
      }
    }
  }

  // 2. Check Main Dining
  for (const v of schedule.venues || []) {
    for (const a of v.assignments || []) {
      if (isCurrentUser(a.waiterName)) {
        return {
          name: a.waiterName,
          venue: v.name,
          station: 'Station ' + a.station,
          time: v.reportTime || '11:00',
          tables: a.tables || 'Assigned Section',
          sideDuty: null,
          uniform: null
        };
      }
      if (isCurrentUser(a.attendantName)) {
        return {
          name: a.attendantName,
          venue: v.name,
          station: 'Station ' + a.station + ' (Assistant)',
          time: v.reportTime || '11:00',
          tables: a.tables || 'Assigned Section',
          sideDuty: null,
          uniform: null
        };
      }
    }
  }

  // 3. Check Buffet & Venues
  for (const bv of schedule.buffetAndVenues || []) {
    for (const c of bv.crew || []) {
      if (isCurrentUser(c.name)) {
        let timing = bv.timing || '';
        let roleVenue = bv.name;
        if (c.role) {
          const timeMatch = c.role.match(/\d{1,2}:\d{2}(?:-\d{1,2}:\d{2})?(?:\/\d{1,2}:\d{2}-\d{1,2}:\d{2})?/);
          if (timeMatch) timing = timeMatch[0];
          
          if (/noodle\s*bar/i.test(c.role)) roleVenue = 'Noodle Bar';
          else if (/pizzeria/i.test(c.role)) roleVenue = 'Pizzeria';
          else if (/salty\s*beach/i.test(c.role)) roleVenue = 'Salty Beach';
          else if (/sushino/i.test(c.role)) roleVenue = 'Sushino';
          else if (/casanova/i.test(c.role)) roleVenue = 'Casanova';
          else if (/steakhouse/i.test(c.role)) roleVenue = 'Steakhouse';
          else if (/hot\s*pot/i.test(c.role)) roleVenue = 'Hot Pot Team';
        }

        return {
          name: c.name,
          venue: roleVenue,
          station: c.role || 'Buffet Station',
          time: timing || 'Scheduled Shift',
          tables: 'Buffet Service Area',
          sideDuty: null,
          uniform: null
        };
      }
    }
  }

  // 4. Check Special Events (Travel Talk)
  for (const ev of schedule.specialEvents || []) {
    for (const p of ev.participants || []) {
      if (isCurrentUser(p.name)) {
        return {
          name: p.name,
          venue: ev.location,
          station: ev.title,
          time: '10:40',
          tables: '-',
          sideDuty: ev.title,
          uniform: p.uniform
        };
      }
    }
  }

  return null;
}

// 1. Render Main Dining Rooms
function renderMainDining(venues, query) {
  const container = document.getElementById('bodyMainDining');
  const countBadge = document.getElementById('countMainDining');
  container.innerHTML = '';
  let count = 0;

  venues.forEach((venue, vIdx) => {
    const filteredAssignments = venue.assignments.filter(item => {
      if (!query) return true;
      return (
        matchesSearchQuery(query, item.waiterName, item.station, item.tables) ||
        matchesSearchQuery(query, item.attendantName, item.station, item.tables) ||
        venue.name.toLowerCase().includes(query)
      );
    });

    if (filteredAssignments.length > 0) {
      count += filteredAssignments.length;
      const group = document.createElement('div');
      group.className = 'venue-group' + (query || state.allExpanded ? '' : ' sub-collapsed');
      group.innerHTML = `
        <div class="venue-header" data-sub-toggle="venue_md_${vIdx}">
          <span>${escapeHtml(venue.name)} &bull; ${escapeHtml(venue.reportTime || '11:00')}</span>
          <span class="sub-chevron">▼</span>
        </div>
        <table class="schedule-table">
          <thead>
            <tr>
              <th style="width: 45px;">Stn</th>
              <th>Waiter / Crew</th>
              <th>Assistant / Attendant</th>
              <th>Tables</th>
            </tr>
          </thead>
          <tbody>
            ${filteredAssignments.map(item => {
              const isMe = isCurrentUser(item.waiterName) || isCurrentUser(item.attendantName);
              const isHighlighted = isMe || Boolean(query);
              return `
                <tr class="${isHighlighted ? 'highlight-my-row' : ''}">
                  <td><span class="station-badge">${escapeHtml(item.station)}</span></td>
                  <td>
                    <strong>${escapeHtml(item.waiterName)}</strong>
                  </td>
                  <td>
                    ${item.attendantName ? `<strong>${escapeHtml(item.attendantName)}</strong>` : '<span style="color:#94a3b8;">-</span>'}
                  </td>
                  <td><span class="tables-list">${escapeHtml(item.tables || '-')}</span></td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      `;
      container.appendChild(group);
    }
  });

  countBadge.innerText = count;
  document.getElementById('catMainDining').style.display = count === 0 && query ? 'none' : 'block';
  return count;
}

// 2. Render Buffet & Specialty Venues
function renderBuffetAndVenues(list, query) {
  const container = document.getElementById('bodyBuffet');
  const countBadge = document.getElementById('countBuffet');
  container.innerHTML = '';
  let count = 0;

  list.forEach((v, vIdx) => {
    const filteredCrew = (v.crew || []).filter(c => {
      if (!query) return true;
      return matchesSearchQuery(query, c.name, c.role, v.name);
    });

    if (filteredCrew.length > 0) {
      count += filteredCrew.length;
      const group = document.createElement('div');
      group.className = 'venue-group' + (query || state.allExpanded ? '' : ' sub-collapsed');
      group.innerHTML = `
        <div class="venue-header" data-sub-toggle="venue_bf_${vIdx}">
          <span>${escapeHtml(v.name)} &bull; ${escapeHtml(v.timing || (v.lead ? 'Lead: ' + v.lead : ''))}</span>
          <span class="sub-chevron">▼</span>
        </div>
        <table class="schedule-table">
          <thead>
            <tr>
              <th>Crew Name</th>
              <th>Role / Assignment</th>
            </tr>
          </thead>
          <tbody>
            ${filteredCrew.map(c => {
              const isMe = isCurrentUser(c.name);
              const isHighlighted = isMe || Boolean(query);
              return `
                <tr class="${isHighlighted ? 'highlight-my-row' : ''}">
                  <td><strong>${escapeHtml(c.name)}</strong></td>
                  <td><span class="duty-pill">${escapeHtml(c.role || v.timing || 'On Duty')}</span></td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      `;
      container.appendChild(group);
    }
  });

  countBadge.innerText = count;
  document.getElementById('catBuffet').style.display = count === 0 && query ? 'none' : 'block';
  return count;
}

// 3. Render Side Duties & Operations (including DRS, Office, Linen, Refilling, Resetting)
function renderSideDuties(duties, query) {
  const container = document.getElementById('bodyDuties');
  const countBadge = document.getElementById('countDuties');
  container.innerHTML = '';
  let count = 0;

  duties.forEach((d, dIdx) => {
    const filteredCrew = (d.crew || []).filter(c => {
      if (!query) return true;
      return matchesSearchQuery(query, c.name, c.role, d.name);
    });

    if (filteredCrew.length > 0) {
      count += filteredCrew.length;
      const isDrs = d.name.startsWith('DRS');
      const group = document.createElement('div');
      group.className = 'venue-group' + (query || state.allExpanded ? '' : ' sub-collapsed');
      group.innerHTML = `
        <div class="venue-header" style="border-left-color: ${isDrs ? 'var(--costa-yellow)' : 'var(--costa-gold)'};" data-sub-toggle="venue_sd_${dIdx}">
          <span>${escapeHtml(d.name)} &bull; ${escapeHtml(d.timing || '')}</span>
          <span class="sub-chevron">▼</span>
        </div>
        <table class="schedule-table">
          <thead>
            <tr>
              <th>Crew Name</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            ${filteredCrew.map(c => {
              const isMe = isCurrentUser(c.name);
              const isHighlighted = isMe || Boolean(query);
              return `
                <tr class="${isHighlighted ? 'highlight-my-row' : ''}">
                  <td><strong>${escapeHtml(c.name)}</strong></td>
                  <td><span class="duty-pill">${escapeHtml(c.role || d.timing || 'Assigned')}</span></td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      `;
      container.appendChild(group);
    }
  });

  countBadge.innerText = count;
  document.getElementById('catDuties').style.display = count === 0 && query ? 'none' : 'block';
  return count;
}

// 4. Render Special Events & Uniforms
function renderSpecialEvents(events, query) {
  const container = document.getElementById('bodySpecialEvents');
  const countBadge = document.getElementById('countSpecialEvents');
  container.innerHTML = '';
  let count = 0;

  events.forEach((ev, eIdx) => {
    const filteredParticipants = (ev.participants || []).filter(p => {
      if (!query) return true;
      return matchesSearchQuery(query, p.name, p.uniform, ev.title);
    });

    if (filteredParticipants.length > 0) {
      count += filteredParticipants.length;
      const group = document.createElement('div');
      group.className = 'venue-group' + (query || state.allExpanded ? '' : ' sub-collapsed');
      group.innerHTML = `
        <div class="venue-header" style="border-left-color: var(--purple); background:#faf5ff;" data-sub-toggle="venue_ev_${eIdx}">
          <div>
            <strong>${escapeHtml(ev.title)}</strong><br>
            <small style="font-size:0.75rem; color:#6b21a8;">📍 ${escapeHtml(ev.location)}</small>
          </div>
          <span class="sub-chevron">▼</span>
        </div>
        <table class="schedule-table">
          <thead>
            <tr>
              <th>Crew Name</th>
              <th>Required Uniform</th>
            </tr>
          </thead>
          <tbody>
            ${filteredParticipants.map(p => {
              const isMe = isCurrentUser(p.name);
              const isHighlighted = isMe || Boolean(query);
              return `
                <tr class="${isHighlighted ? 'highlight-my-row' : ''}">
                  <td><strong>${escapeHtml(p.name)}</strong></td>
                  <td><span class="uniform-tag">${escapeHtml(p.uniform || 'Standard')}</span></td>
                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      `;
      container.appendChild(group);
    }
  });

  countBadge.innerText = count;
  document.getElementById('catSpecialEvents').style.display = count === 0 && query ? 'none' : 'block';
  return count;
}

// 5. Render Sick Leave
function renderSickLeave(list, query) {
  const container = document.getElementById('bodySickLeave');
  const countBadge = document.getElementById('countSickLeave');
  container.innerHTML = '';
  let count = 0;

  const filtered = list.filter(item => {
    if (!query) return true;
    return matchesSearchQuery(query, item.name);
  });

  count = filtered.length;
  if (count > 0) {
    container.innerHTML = filtered.map(c => {
      const isMe = isCurrentUser(c.name);
      const isHighlighted = isMe || Boolean(query);
      return `
        <div class="sick-leave-item ${isHighlighted ? 'highlight-my-row' : ''}">
          <span><strong>${escapeHtml(c.name)}</strong></span>
        </div>
      `;
    }).join('');
  } else {
    container.innerHTML = '<p style="color:#64748b; font-size:0.82rem;">No personnel recorded on sick leave.</p>';
  }

  countBadge.innerText = count;
  document.getElementById('catSickLeave').style.display = count === 0 && query ? 'none' : 'block';
  return count;
}

// ==========================================
// ACCORDION TOGGLE FUNCTIONS & MULTI-TAB CONTROLLER
// ==========================================
function setCardExpansion(card, expand) {
  const body = card.querySelector('.category-body');
  if (expand) {
    card.classList.remove('collapsed');
    if (body) body.classList.remove('hidden');
  } else {
    card.classList.add('collapsed');
    if (body) body.classList.add('hidden');
  }
}

function updateToggleBtnLabels() {
  // Check Tab 2 (Venues)
  const venuesCards = document.querySelectorAll('#tabVenues .category-card');
  const venuesCollapsed = Array.from(venuesCards).some(c => c.classList.contains('collapsed'));
  const btnVenues = document.getElementById('toggleVenuesAccordionBtn');
  if (btnVenues) {
    btnVenues.innerText = venuesCollapsed ? 'Expand All' : 'Collapse All';
  }

  // Check Tab 3 (Operations)
  const opsCards = document.querySelectorAll('#tabOperations .category-card');
  const opsCollapsed = Array.from(opsCards).some(c => c.classList.contains('collapsed'));
  const btnOps = document.getElementById('toggleOperationsAccordionBtn');
  if (btnOps) {
    btnOps.innerText = opsCollapsed ? 'Expand All' : 'Collapse All';
  }

  // Check Tab 1 / Global
  const allCards = document.querySelectorAll('.category-card');
  const anyCollapsed = Array.from(allCards).some(c => c.classList.contains('collapsed'));
  const btnAll = document.getElementById('toggleAllAccordionBtn');
  if (btnAll) {
    btnAll.innerText = anyCollapsed ? 'Expand All' : 'Collapse All';
  }
  state.allExpanded = !anyCollapsed;
}

function applyDefaultCollapseState() {
  document.querySelectorAll('.category-card').forEach(card => {
    card.classList.add('collapsed');
    const body = card.querySelector('.category-body');
    if (body) body.classList.add('hidden');
  });
  document.querySelectorAll('.venue-group').forEach(grp => {
    grp.classList.add('sub-collapsed');
  });
  updateToggleBtnLabels();
}

function autoExpandOnSearch(shouldExpand) {
  document.querySelectorAll('.category-card').forEach(card => {
    const body = card.querySelector('.category-body');
    if (shouldExpand) {
      card.classList.remove('collapsed');
      if (body) body.classList.remove('hidden');
    }
  });
  document.querySelectorAll('.venue-group').forEach(grp => {
    if (shouldExpand) {
      grp.classList.remove('sub-collapsed');
    }
  });
}

// ==========================================
// ALARM LOGIC & HELPERS
// ==========================================
function updateAlarmButtonVisibility() {
  const alarmBtn = document.getElementById('alarmBtn');
  if (alarmBtn) {
    // Alarm button is visible ONLY IF Alarm toggle is ON AND User Profile is configured
    const shouldShow = Boolean(state.alarm.enabled && hasUserProfile());
    if (shouldShow) {
      alarmBtn.classList.remove('hidden');
    } else {
      alarmBtn.classList.add('hidden');
    }
  }
}

function extractDutyStartTime(timeStr, defaultMeal) {
  if (timeStr) {
    // If multiple shift timings like "07:00-10:00 / 11:00-14:00" and defaultMeal is known:
    if (timeStr.includes('/')) {
      const parts = timeStr.split('/');
      if (defaultMeal === 'BREAKFAST' && parts[0]) {
        const m = parts[0].match(/(\d{1,2}):(\d{2})/);
        if (m) return { hour: parseInt(m[1], 10), minute: parseInt(m[2], 10) };
      } else if (defaultMeal === 'LUNCH' && parts[1]) {
        const m = parts[1].match(/(\d{1,2}):(\d{2})/);
        if (m) return { hour: parseInt(m[1], 10), minute: parseInt(m[2], 10) };
      } else if (defaultMeal === 'DINNER' && (parts[2] || parts[1])) {
        const p = parts[2] || parts[1];
        const m = p.match(/(\d{1,2}):(\d{2})/);
        if (m) return { hour: parseInt(m[1], 10), minute: parseInt(m[2], 10) };
      }
    }

    const m = timeStr.match(/(\d{1,2}):(\d{2})/);
    if (m) {
      return {
        hour: parseInt(m[1], 10),
        minute: parseInt(m[2], 10)
      };
    }
  }

  // Fallbacks based on Meal Shift
  if (defaultMeal === 'BREAKFAST') return { hour: 6, minute: 30 };
  if (defaultMeal === 'LUNCH') return { hour: 11, minute: 0 };
  if (defaultMeal === 'DINNER') return { hour: 17, minute: 30 };
  return { hour: 11, minute: 0 };
}

function calculate3Alarms(dutyHour, dutyMinute) {
  let offsetMinutes = 60;
  if (state.alarm.option === '30') {
    offsetMinutes = 30;
  } else if (state.alarm.option === 'custom') {
    offsetMinutes = (state.alarm.customHours * 60) + state.alarm.customMinutes;
    if (isNaN(offsetMinutes) || offsetMinutes < 0) offsetMinutes = 60;
  }

  const dutyTotalMinutes = dutyHour * 60 + dutyMinute;
  
  let a1Mins = (dutyTotalMinutes - offsetMinutes) % 1440;
  if (a1Mins < 0) a1Mins += 1440;
  const h1 = Math.floor(a1Mins / 60) % 24;
  const m1 = a1Mins % 60;

  let a2Mins = (a1Mins + 5) % 1440;
  const h2 = Math.floor(a2Mins / 60) % 24;
  const m2 = a2Mins % 60;

  let a3Mins = (a1Mins + 10) % 1440;
  const h3 = Math.floor(a3Mins / 60) % 24;
  const m3 = a3Mins % 60;

  const pad = (n) => String(n).padStart(2, '0');

  return {
    h1, m1, h2, m2, h3, m3,
    str1: `${pad(h1)}:${pad(m1)}`,
    str2: `${pad(h2)}:${pad(m2)}`,
    str3: `${pad(h3)}:${pad(m3)}`,
    offsetMinutes
  };
}

function getAlarmConfigLabel() {
  if (state.alarm.option === '30') {
    return '⚙️ Config: 30 Min Before Duty';
  } else if (state.alarm.option === 'custom') {
    const h = state.alarm.customHours || 0;
    const m = state.alarm.customMinutes || 0;
    const parts = [];
    if (h > 0) parts.push(`${h} hr`);
    if (m > 0 || parts.length === 0) parts.push(`${m} min`);
    return `⚙️ Config: Custom (${parts.join(' ')}) Before Duty`;
  }
  return '⚙️ Config: 1 Hour Before Duty';
}

function handleAlarmButtonClick() {
  if (!hasUserProfile()) {
    showToast('⚠️ Please configure your Crew Profile in Settings first.');
    openSettingsModal();
    return;
  }

  const schedule = state.schedules[state.currentDay][state.currentMeal];
  if (!schedule) {
    showToast(`⚠️ No ${state.currentMeal} schedule loaded.`);
    return;
  }

  const userDuty = findUserDuty(schedule);
  if (!userDuty) {
    const profileLabel = (state.profile.name || state.profile.id).toUpperCase();
    showToast(`⚠️ ${profileLabel} is NOT scheduled for ${state.currentMeal} duty.`);
    return;
  }

  const startTime = extractDutyStartTime(userDuty.time, state.currentMeal);
  const alarms = calculate3Alarms(startTime.hour, startTime.minute);

  const pad = (n) => String(n).padStart(2, '0');
  const reportFormatted = `${pad(startTime.hour)}:${pad(startTime.minute)}`;
  const venueTitle = userDuty.station || userDuty.venue || userDuty.sideDuty || 'Costa Duty';

  // Directly launch the dedicated Bedside Nightstand Alarm
  openBedsideNightstandAlarm(venueTitle, reportFormatted, startTime.hour, startTime.minute, alarms);
}

// ==========================================
// DEDICATED BEDSIDE NIGHTSTAND ALARM CONTROLLER
// ==========================================
function openBedsideNightstandAlarm(venueTitle, reportFormatted, dutyHour, dutyMin, alarms) {
  state.bedside.active = true;
  state.bedside.targetHour = alarms.h1;
  state.bedside.targetMin = alarms.m1;
  state.bedside.isRinging = false;

  // 1. Populate Target Duty Details
  const venueEl = document.getElementById('bedsideTargetVenue');
  if (venueEl) venueEl.innerText = venueTitle.toUpperCase();

  const reportEl = document.getElementById('bedsideTargetReport');
  if (reportEl) reportEl.innerText = `Report Time: ${reportFormatted}`;

  const configChip = document.getElementById('bedsideConfigChip');
  if (configChip) configChip.innerText = getAlarmConfigLabel().replace('⚙️ Config: ', '');

  const targetTimeEl = document.getElementById('bedsideTargetTime');
  if (targetTimeEl) targetTimeEl.innerText = alarms.str1;

  const s1 = document.getElementById('bedsideStep1');
  const s2 = document.getElementById('bedsideStep2');
  const s3 = document.getElementById('bedsideStep3');
  if (s1) s1.innerText = alarms.str1;
  if (s2) s2.innerText = alarms.str2;
  if (s3) s3.innerText = alarms.str3;

  const ringVenueEl = document.getElementById('bedsideRingingVenue');
  if (ringVenueEl) ringVenueEl.innerText = `Report to ${venueTitle.toUpperCase()} at ${reportFormatted}`;

  // Reset Control Views
  const standbyWrap = document.getElementById('bedsideStandbyControls');
  const ringingWrap = document.getElementById('bedsideRingingControls');
  if (standbyWrap) standbyWrap.classList.remove('hidden');
  if (ringingWrap) ringingWrap.classList.add('hidden');

  // 2. Enable Screen Always ON (Overrides Phone 5-Min Screen Timeout)
  enableScreenAlwaysOn();

  // 3. Start Live Clock & Countdown
  startBedsideClockCountdown(alarms.h1, alarms.m1);

  // 4. Wire Action Buttons
  const testBtn = document.getElementById('testAlarmSoundBtn');
  if (testBtn) testBtn.onclick = testAlarmRingtone;

  const dismissBtn = document.getElementById('dismissAlarmBtn');
  if (dismissBtn) dismissBtn.onclick = stopBedsideAlarmRinging;

  const snoozeBtn = document.getElementById('snoozeAlarmBtn');
  if (snoozeBtn) snoozeBtn.onclick = snoozeBedsideAlarm;

  // 5. Open Modal View
  document.getElementById('bedsideAlarmModal').classList.remove('hidden');
}

// ==========================================
// SCREEN ALWAYS ON ENGINE (OVERRIDE SCREEN LOCK)
// ==========================================
let screenWakeLock = null;
let dummyVideoEl = null;

async function enableScreenAlwaysOn() {
  let success = false;

  // 1. W3C Screen Wake Lock API (Standard for Chrome on Android, Safari iOS 16.4+, Edge)
  if ('wakeLock' in navigator) {
    try {
      screenWakeLock = await navigator.wakeLock.request('screen');
      screenWakeLock.addEventListener('release', () => {
        console.log('Screen Wake Lock was released');
      });
      state.bedside.wakeLock = screenWakeLock;
      success = true;
    } catch (err) {
      console.warn('Screen Wake Lock request:', err);
    }
  }

  // 2. Universal Mobile Fallback: Invisible Looping Video
  // Keeps screen awake on older Android & iOS browsers even with strict screen timeout settings
  try {
    if (!dummyVideoEl) {
      dummyVideoEl = document.createElement('video');
      dummyVideoEl.setAttribute('playsinline', '');
      dummyVideoEl.setAttribute('webkit-playsinline', '');
      dummyVideoEl.setAttribute('loop', '');
      dummyVideoEl.setAttribute('muted', '');
      dummyVideoEl.muted = true;
      dummyVideoEl.style.position = 'fixed';
      dummyVideoEl.style.top = '-9999px';
      dummyVideoEl.style.left = '-9999px';
      dummyVideoEl.style.width = '1px';
      dummyVideoEl.style.height = '1px';
      dummyVideoEl.style.opacity = '0.01';
      dummyVideoEl.style.pointerEvents = 'none';

      // 1x1 base64 transparent MP4
      dummyVideoEl.src = 'data:video/mp4;base64,AAAAHGZ0eXBtcDQyAAAAAW1wNDJpc29tYXZjMQAAAAhmcmVlAAAAGG1kYXQAAAEAAQAAAABkYXRhAAAAAA==';
      document.body.appendChild(dummyVideoEl);
    }
    dummyVideoEl.play().catch(() => {});
  } catch (e) {}

  // 3. Native APK Window Flag (when running inside Android APK)
  if (window.AndroidBridge && typeof window.AndroidBridge.setKeepScreenOn === 'function') {
    try {
      window.AndroidBridge.setKeepScreenOn(true);
      success = true;
    } catch (e) {}
  }

  // Update Visual Status Badge
  const dot = document.getElementById('bedsideWakeLockDot');
  const status = document.getElementById('bedsideWakeLockStatus');
  if (dot) dot.classList.add('active');
  if (status) status.innerText = 'Screen Always ON (Lock Screen Bypassed)';

  return success;
}

function disableScreenAlwaysOn() {
  if (screenWakeLock) {
    screenWakeLock.release().catch(() => {});
    screenWakeLock = null;
    state.bedside.wakeLock = null;
  }
  if (dummyVideoEl) {
    dummyVideoEl.pause();
  }
  if (window.AndroidBridge && typeof window.AndroidBridge.setKeepScreenOn === 'function') {
    try {
      window.AndroidBridge.setKeepScreenOn(false);
    } catch (e) {}
  }
  const dot = document.getElementById('bedsideWakeLockDot');
  const status = document.getElementById('bedsideWakeLockStatus');
  if (dot) dot.classList.remove('active');
  if (status) status.innerText = 'Screen Sleep Allowed';
}

// Automatically re-acquire screen wake lock if user briefly leaves and returns to tab
document.addEventListener('visibilitychange', async () => {
  if (state.bedside.active && document.visibilityState === 'visible') {
    await enableScreenAlwaysOn();
  }
});

// ==========================================
// REALISTIC MOBILE PHONE ALARM SOUND ENGINE
// ==========================================
let mobileAlarmAudioCtx = null;
let mobileAlarmLoopTimer = null;
let isMobileAlarmPlaying = false;
let testSoundTimeout = null;

function playMobileAlarmLoop() {
  if (isMobileAlarmPlaying) return;
  isMobileAlarmPlaying = true;

  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) return;
  if (!mobileAlarmAudioCtx || mobileAlarmAudioCtx.state === 'closed') {
    mobileAlarmAudioCtx = new AudioContextClass();
  }
  if (mobileAlarmAudioCtx.state === 'suspended') {
    mobileAlarmAudioCtx.resume();
  }

  function playNote(freq, startOffset, duration, volume) {
    if (!mobileAlarmAudioCtx) return;
    const now = mobileAlarmAudioCtx.currentTime + startOffset;

    // Osc1: Fundamental tone (Sine wave for warm body)
    const osc1 = mobileAlarmAudioCtx.createOscillator();
    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(freq, now);

    // Osc2: Harmonic overtone (Triangle wave for crisp mobile marimba/chime attack)
    const osc2 = mobileAlarmAudioCtx.createOscillator();
    osc2.type = 'triangle';
    osc2.frequency.setValueAtTime(freq * 2, now);

    // Osc3: Subtle high overtone for realistic metal bell ring
    const osc3 = mobileAlarmAudioCtx.createOscillator();
    osc3.type = 'sine';
    osc3.frequency.setValueAtTime(freq * 2.76, now);

    const gainNode = mobileAlarmAudioCtx.createGain();
    const gain3 = mobileAlarmAudioCtx.createGain();
    gain3.gain.setValueAtTime(0.25, now);

    gainNode.gain.setValueAtTime(0.0001, now);
    gainNode.gain.exponentialRampToValueAtTime(volume, now + 0.012);
    gainNode.gain.exponentialRampToValueAtTime(0.0001, now + duration);

    osc1.connect(gainNode);
    osc2.connect(gainNode);
    osc3.connect(gain3);
    gain3.connect(gainNode);
    gainNode.connect(mobileAlarmAudioCtx.destination);

    osc1.start(now);
    osc2.start(now);
    osc3.start(now);
    osc1.stop(now + duration + 0.05);
    osc2.stop(now + duration + 0.05);
    osc3.stop(now + duration + 0.05);
  }

  function scheduleMelodyCycle() {
    if (!isMobileAlarmPlaying || !mobileAlarmAudioCtx) return;

    // 12-Tone Smartphone Alarm Melody (Crescendo marimba + urgent pulse)
    // Notes: D5 (587Hz), F#5 (740Hz), A5 (880Hz), D6 (1175Hz), E6 (1318Hz), F#6 (1480Hz), A6 (1760Hz)
    const pattern = [
      // Phrase 1: Ascending Morning Chime
      { freq: 587.33, offset: 0.00, dur: 0.22, vol: 0.70 },
      { freq: 739.99, offset: 0.22, dur: 0.22, vol: 0.75 },
      { freq: 880.00, offset: 0.44, dur: 0.22, vol: 0.80 },
      { freq: 1174.66, offset: 0.66, dur: 0.35, vol: 0.88 },

      // Phrase 2: Melodic Uplift
      { freq: 880.00, offset: 1.10, dur: 0.20, vol: 0.82 },
      { freq: 1174.66, offset: 1.30, dur: 0.20, vol: 0.86 },
      { freq: 1318.51, offset: 1.50, dur: 0.20, vol: 0.90 },
      { freq: 1479.98, offset: 1.70, dur: 0.40, vol: 0.95 },

      // Phrase 3: Staccato Radar Double-Pulse
      { freq: 1479.98, offset: 2.25, dur: 0.12, vol: 0.92 },
      { freq: 1479.98, offset: 2.45, dur: 0.12, vol: 0.92 },
      { freq: 1760.00, offset: 2.70, dur: 0.15, vol: 0.98 },
      { freq: 1760.00, offset: 2.90, dur: 0.28, vol: 1.00 }
    ];

    pattern.forEach(p => playNote(p.freq, p.offset, p.dur, p.vol));

    // Device Vibration in sync with rhythmic beeps
    if ('vibrate' in navigator) {
      navigator.vibrate([180, 100, 180, 100, 350]);
    }

    // Schedule next repetition every 3.4 seconds indefinitely
    mobileAlarmLoopTimer = setTimeout(scheduleMelodyCycle, 3400);
  }

  scheduleMelodyCycle();
}

function stopMobileAlarmLoop() {
  isMobileAlarmPlaying = false;
  if (mobileAlarmLoopTimer) {
    clearTimeout(mobileAlarmLoopTimer);
    mobileAlarmLoopTimer = null;
  }
  if ('vibrate' in navigator) {
    navigator.vibrate(0);
  }
}

function testAlarmRingtone() {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) {
    showToast('⚠️ Web Audio not supported on this device.');
    return;
  }
  if (isMobileAlarmPlaying) {
    stopMobileAlarmLoop();
    showToast('Alarm sound preview stopped.');
    return;
  }

  showToast('🔊 Playing mobile alarm ringtone preview...');
  playMobileAlarmLoop();
  if (testSoundTimeout) clearTimeout(testSoundTimeout);
  testSoundTimeout = setTimeout(() => {
    if (!state.bedside.isRinging) {
      stopMobileAlarmLoop();
    }
  }, 3400);
}

// ==========================================
// CLOCK & COUNTDOWN ENGINE
// ==========================================
function startBedsideClockCountdown(targetHour, targetMin) {
  const pad = (n) => String(n).padStart(2, '0');

  if (state.bedside.timer) clearInterval(state.bedside.timer);

  const updateClock = () => {
    const now = new Date();
    const currH = now.getHours();
    const currM = now.getMinutes();
    const currS = now.getSeconds();

    const currEl = document.getElementById('bedsideCurrentTime');
    if (currEl) {
      currEl.innerText = `${pad(currH)}:${pad(currM)}:${pad(currS)}`;
    }

    const targetDate = new Date(now);
    targetDate.setHours(targetHour, targetMin, 0, 0);
    if (targetDate.getTime() <= now.getTime()) {
      targetDate.setDate(targetDate.getDate() + 1);
    }

    const diffMs = targetDate.getTime() - now.getTime();
    const totalSec = Math.max(0, Math.floor(diffMs / 1000));
    const h = Math.floor(totalSec / 3600);
    const m = Math.floor((totalSec % 3600) / 60);
    const s = totalSec % 60;

    const countEl = document.getElementById('bedsideCountdown');
    if (countEl) {
      countEl.innerText = `${pad(h)}h ${pad(m)}m ${pad(s)}s`;
    }

    // Trigger Ringing when reached
    if (totalSec <= 0 && !state.bedside.isRinging) {
      triggerBedsideAlarmRinging();
    }
  };

  updateClock();
  state.bedside.timer = setInterval(updateClock, 1000);
}

function triggerBedsideAlarmRinging() {
  state.bedside.isRinging = true;
  const standbyWrap = document.getElementById('bedsideStandbyControls');
  const ringingWrap = document.getElementById('bedsideRingingControls');
  if (standbyWrap) standbyWrap.classList.add('hidden');
  if (ringingWrap) ringingWrap.classList.remove('hidden');

  playMobileAlarmLoop();
}

function stopBedsideAlarmRinging() {
  state.bedside.isRinging = false;
  stopMobileAlarmLoop();

  const standbyWrap = document.getElementById('bedsideStandbyControls');
  const ringingWrap = document.getElementById('bedsideRingingControls');
  if (standbyWrap) standbyWrap.classList.remove('hidden');
  if (ringingWrap) ringingWrap.classList.add('hidden');

  showToast("⏰ Duty alarm dismissed. Have a great shift!");
}

function snoozeBedsideAlarm() {
  stopMobileAlarmLoop();
  state.bedside.isRinging = false;

  // Add 5 minutes to target time
  const now = new Date();
  now.setMinutes(now.getMinutes() + 5);
  state.bedside.targetHour = now.getHours();
  state.bedside.targetMin = now.getMinutes();

  const pad = (n) => String(n).padStart(2, '0');
  const newTargetStr = `${pad(state.bedside.targetHour)}:${pad(state.bedside.targetMin)}`;

  const targetTimeEl = document.getElementById('bedsideTargetTime');
  if (targetTimeEl) targetTimeEl.innerText = newTargetStr;

  const standbyWrap = document.getElementById('bedsideStandbyControls');
  const ringingWrap = document.getElementById('bedsideRingingControls');
  if (standbyWrap) standbyWrap.classList.remove('hidden');
  if (ringingWrap) ringingWrap.classList.add('hidden');

  startBedsideClockCountdown(state.bedside.targetHour, state.bedside.targetMin);
  showToast(`💤 Snoozed for 5 minutes! Alarm will ring at ${newTargetStr}`);
}

function exitBedsideNightstandMode() {
  state.bedside.active = false;
  state.bedside.isRinging = false;
  stopMobileAlarmLoop();

  if (state.bedside.timer) {
    clearInterval(state.bedside.timer);
    state.bedside.timer = null;
  }

  disableScreenAlwaysOn();

  const modal = document.getElementById('bedsideAlarmModal');
  if (modal) modal.classList.add('hidden');
}

// ==========================================
// EVENT LISTENERS & UI LOGIC
// ==========================================
// ==========================================
// TAB NAVIGATION CONTROLLER (Costa App 4-Tab System)
// ==========================================
function switchTab(targetTabId) {
  document.querySelectorAll('.tab-view').forEach(view => {
    if (view.id === targetTabId) {
      view.classList.remove('hidden');
      view.classList.add('active');
    } else {
      view.classList.add('hidden');
      view.classList.remove('active');
    }
  });

  document.querySelectorAll('#bottomNavBar .nav-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === targetTabId);
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('hidden');
}

function setupEventListeners() {
  // Day Selector (Outline Pills)
  document.querySelectorAll('#dayTabs button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#dayTabs button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.currentDay = btn.dataset.day;
      renderSchedule();
    });
  });

  // Meal Shift Selector (Outline Pills)
  document.querySelectorAll('#mealTabs button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#mealTabs button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.currentMeal = btn.dataset.meal;
      renderSchedule();
    });
  });

  // Bottom Navigation Bar Tabs
  document.querySelectorAll('#bottomNavBar .nav-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      switchTab(btn.dataset.tab);
    });
  });

  // Header Avatar Quick Jump to User's Schedule Row
  const quickProfile = document.getElementById('quickProfileBtn');
  if (quickProfile) {
    quickProfile.addEventListener('click', () => {
      if (!hasUserProfile()) {
        openModal('settingsModal');
        return;
      }
      // Switch to Venues tab
      switchTab('tabVenues');
      // Expand all categories so user can see everything
      document.querySelectorAll('.category-card').forEach(card => {
        card.classList.remove('collapsed');
        const body = card.querySelector('.category-body');
        if (body) body.classList.remove('hidden');
      });
      document.querySelectorAll('.venue-group').forEach(grp => {
        grp.classList.remove('sub-collapsed');
      });
      // Scroll to user's highlighted row
      setTimeout(() => {
        const highlightedRow = document.querySelector('.highlight-my-row');
        if (highlightedRow) {
          highlightedRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
          showToast('You are not scheduled in this shift.');
        }
      }, 150);
    });
  }

  // Jump to Venues tab buttons
  const jumpVenuesBtn = document.getElementById('jumpToVenuesTabBtn');
  if (jumpVenuesBtn) {
    jumpVenuesBtn.addEventListener('click', () => switchTab('tabVenues'));
  }
  const spotlightVenuesBtn = document.getElementById('spotlightViewVenuesBtn');
  if (spotlightVenuesBtn) {
    spotlightVenuesBtn.addEventListener('click', () => switchTab('tabVenues'));
  }

  // More Tab Navigation Actions
  const moreItemAlarm = document.getElementById('moreItemAlarm');
  if (moreItemAlarm) {
    moreItemAlarm.addEventListener('click', handleAlarmButtonClick);
  }
  const moreItemGuide = document.getElementById('moreItemGuide');
  if (moreItemGuide) {
    moreItemGuide.addEventListener('click', () => {
      openModal('guideModal');
    });
  }

  // Sample Data Loading Button in Empty State
  const loadSampleBtn = document.getElementById('loadSampleScheduleBtn');
  if (loadSampleBtn) {
    loadSampleBtn.addEventListener('click', () => {
      state.schedules.today[state.currentMeal] = JSON.parse(JSON.stringify(SAMPLE_SCHEDULE));
      saveStoredSchedules();
      renderSchedule();
      showToast("Loaded sample Costa Smeralda roster");
    });
  }

  // Category Accordion Header Click
  document.addEventListener('click', (e) => {
    const catHeader = e.target.closest('[data-toggle-cat]');
    if (catHeader) {
      const catId = catHeader.getAttribute('data-toggle-cat');
      const card = document.getElementById(catId);
      if (card) {
        const body = card.querySelector('.category-body');
        card.classList.toggle('collapsed');
        if (body) body.classList.toggle('hidden');
        updateToggleBtnLabels();
      }
      return;
    }

    // Sub-group Accordion Header Click
    const subHeader = e.target.closest('[data-sub-toggle]');
    if (subHeader) {
      const group = subHeader.closest('.venue-group');
      if (group) {
        group.classList.toggle('sub-collapsed');
      }
      return;
    }
  });

  // 1. Toggle All Button in Schedule Tab (Tab 1)
  const btnToggleAll = document.getElementById('toggleAllAccordionBtn');
  if (btnToggleAll) {
    btnToggleAll.addEventListener('click', () => {
      const allCards = document.querySelectorAll('.category-card');
      const anyCollapsed = Array.from(allCards).some(c => c.classList.contains('collapsed'));
      const shouldExpand = anyCollapsed;

      allCards.forEach(card => setCardExpansion(card, shouldExpand));
      document.querySelectorAll('.venue-group').forEach(grp => {
        if (shouldExpand) grp.classList.remove('sub-collapsed');
        else grp.classList.add('sub-collapsed');
      });

      updateToggleBtnLabels();

      if (shouldExpand) {
        switchTab('tabVenues');
        showToast('Expanded all sections & opened Venues');
      } else {
        showToast('Collapsed all sections');
      }
    });
  }

  // 2. Toggle Button in Venues Tab (Tab 2)
  const btnToggleVenues = document.getElementById('toggleVenuesAccordionBtn');
  if (btnToggleVenues) {
    btnToggleVenues.addEventListener('click', () => {
      const cards = document.querySelectorAll('#tabVenues .category-card');
      const anyCollapsed = Array.from(cards).some(c => c.classList.contains('collapsed'));
      const shouldExpand = anyCollapsed;

      cards.forEach(card => setCardExpansion(card, shouldExpand));
      document.querySelectorAll('#tabVenues .venue-group').forEach(grp => {
        if (shouldExpand) grp.classList.remove('sub-collapsed');
        else grp.classList.add('sub-collapsed');
      });

      updateToggleBtnLabels();
      showToast(shouldExpand ? 'Expanded all restaurant rosters' : 'Collapsed restaurant rosters');
    });
  }

  // 3. Toggle Button in Operations Tab (Tab 3)
  const btnToggleOps = document.getElementById('toggleOperationsAccordionBtn');
  if (btnToggleOps) {
    btnToggleOps.addEventListener('click', () => {
      const cards = document.querySelectorAll('#tabOperations .category-card');
      const anyCollapsed = Array.from(cards).some(c => c.classList.contains('collapsed'));
      const shouldExpand = anyCollapsed;

      cards.forEach(card => setCardExpansion(card, shouldExpand));
      document.querySelectorAll('#tabOperations .venue-group').forEach(grp => {
        if (shouldExpand) grp.classList.remove('sub-collapsed');
        else grp.classList.add('sub-collapsed');
      });

      updateToggleBtnLabels();
      showToast(shouldExpand ? 'Expanded all operations' : 'Collapsed operations');
    });
  }

  // Search Input
  const searchInput = document.getElementById('searchInput');
  const clearBtn = document.getElementById('clearSearchBtn');

  searchInput.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    if (e.target.value) {
      clearBtn.classList.remove('hidden');
    } else {
      clearBtn.classList.add('hidden');
    }
    renderSchedule();
  });

  clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    state.searchQuery = '';
    clearBtn.classList.add('hidden');
    renderSchedule();
  });

  // Alarm Action Button Click
  const alarmBtn = document.getElementById('alarmBtn');
  if (alarmBtn) {
    alarmBtn.addEventListener('click', handleAlarmButtonClick);
  }

  // Modals & Popups
  document.getElementById('openPasteModalBtn').addEventListener('click', () => {
    document.getElementById('pasteModal').classList.remove('hidden');
    document.getElementById('pasteTextarea').focus();
  });

  document.querySelectorAll('[data-close]').forEach(el => {
    el.addEventListener('click', () => {
      const modalId = el.dataset.close;
      const modal = document.getElementById(modalId);
      if (modal) modal.classList.add('hidden');
      const err = document.getElementById('pasteError');
      if (err) err.classList.add('hidden');
      if (modalId === 'bedsideAlarmModal') {
        exitBedsideNightstandMode();
      }
    });
  });

  // Smart Paste from Clipboard
  document.getElementById('autoPasteClipboardBtn').addEventListener('click', async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        document.getElementById('pasteTextarea').value = text;
        processSchedulePaste(text);
      } else {
        showToast('Clipboard is empty. Please paste manually.');
      }
    } catch (err) {
      showToast('Please paste manually into the box below.');
    }
  });

  // Process Paste Button
  document.getElementById('processPasteBtn').addEventListener('click', () => {
    const text = document.getElementById('pasteTextarea').value;
    processSchedulePaste(text);
  });

  // Settings Modal Functions
  let activeAlarmOption = state.alarm.option;

  const openSettingsModal = () => {
    document.getElementById('profileNameInput').value = state.profile.name || '';
    
    const toggleInput = document.getElementById('alarmToggleInput');
    toggleInput.checked = state.alarm.enabled;
    document.getElementById('alarmOptionsWrapper').classList.toggle('hidden', !state.alarm.enabled);

    activeAlarmOption = state.alarm.option;
    document.querySelectorAll('#alarmPillGroup .alarm-pill').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.alarmOption === activeAlarmOption);
    });

    document.getElementById('alarmCustomHours').value = state.alarm.customHours;
    document.getElementById('alarmCustomMinutes').value = state.alarm.customMinutes;
    document.getElementById('customAlarmRow').classList.toggle('hidden', activeAlarmOption !== 'custom');

    document.getElementById('settingsModal').classList.remove('hidden');
  };

  document.getElementById('settingsBtn').addEventListener('click', openSettingsModal);
  document.getElementById('userProfilePill').addEventListener('click', openSettingsModal);

  // Settings Modal: Alarm Toggle Switch
  document.getElementById('alarmToggleInput').addEventListener('change', (e) => {
    document.getElementById('alarmOptionsWrapper').classList.toggle('hidden', !e.target.checked);
  });

  // Settings Modal: Alarm Pill Options
  document.querySelectorAll('#alarmPillGroup .alarm-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('#alarmPillGroup .alarm-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activeAlarmOption = pill.dataset.alarmOption;
      document.getElementById('customAlarmRow').classList.toggle('hidden', activeAlarmOption !== 'custom');
    });
  });


  // Save Settings Button
  document.getElementById('saveSettingsBtn').addEventListener('click', () => {
    state.profile.name = document.getElementById('profileNameInput').value.trim();
    localStorage.setItem('costa_user_name', state.profile.name);
    localStorage.removeItem('costa_user_id');

    state.alarm.enabled = document.getElementById('alarmToggleInput').checked;
    localStorage.setItem('costa_alarm_enabled', state.alarm.enabled);

    state.alarm.option = activeAlarmOption;
    localStorage.setItem('costa_alarm_option', state.alarm.option);

    const customH = parseInt(document.getElementById('alarmCustomHours').value || '0', 10);
    const customM = parseInt(document.getElementById('alarmCustomMinutes').value || '0', 10);
    state.alarm.customHours = isNaN(customH) ? 1 : customH;
    state.alarm.customMinutes = isNaN(customM) ? 0 : customM;
    localStorage.setItem('costa_alarm_custom_h', state.alarm.customHours);
    localStorage.setItem('costa_alarm_custom_m', state.alarm.customMinutes);

    updateAlarmButtonVisibility();
    updateUserProfilePill();
    document.getElementById('settingsModal').classList.add('hidden');
    showToast('✅ Settings saved!');
    renderSchedule();
  });

  // Shift Pill Click: Focus / Filter to User's Assigned Duty
  document.getElementById('displayShift').addEventListener('click', () => {
    if (!hasUserProfile()) {
      openSettingsModal();
      return;
    }

    const schedule = state.schedules[state.currentDay][state.currentMeal];
    if (!schedule) {
      showToast('⚠️ No schedule loaded for this shift.');
      return;
    }

    const userDuty = findUserDuty(schedule);
    if (!userDuty) {
      showToast('⚠️ You are not scheduled in this shift.');
      return;
    }

    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearSearchBtn');
    const userSearchQuery = (state.profile.name || '').trim();

    // Toggle behavior: If already filtered by user query, clear it
    if (state.searchQuery && state.searchQuery.toLowerCase() === userSearchQuery.toLowerCase()) {
      searchInput.value = '';
      state.searchQuery = '';
      clearBtn.classList.add('hidden');
      renderSchedule();
      showToast('📋 Showing full schedule');
    } else {
      searchInput.value = userSearchQuery;
      state.searchQuery = userSearchQuery;
      clearBtn.classList.remove('hidden');
      renderSchedule();
      showToast(`🎯 Focused on your duty: ${userDuty.station || userDuty.venue}`);

      setTimeout(() => {
        const highlightedRow = document.querySelector('.highlight-my-row');
        if (highlightedRow) {
          highlightedRow.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 120);
    }
  });
}

function processSchedulePaste(text) {
  const errorEl = document.getElementById('pasteError');
  errorEl.classList.add('hidden');

  try {
    const schedule = parseWhatsAppPayload(text);
    const mealKey = (schedule.meal || 'LUNCH').toUpperCase();

    state.schedules.today[mealKey] = schedule;
    state.currentDay = 'today';
    state.currentMeal = mealKey;

    document.querySelectorAll('#dayTabs button').forEach(b => {
      b.classList.toggle('active', b.dataset.day === 'today');
    });
    document.querySelectorAll('#mealTabs button').forEach(b => {
      b.classList.toggle('active', b.dataset.meal === mealKey);
    });

    saveStoredSchedules();
    document.getElementById('pasteModal').classList.add('hidden');
    document.getElementById('pasteTextarea').value = '';
    showToast(`Decoded ${schedule.meal} schedule successfully!`);
    renderSchedule();
  } catch (err) {
    errorEl.innerText = '❌ Error: ' + err.message;
    errorEl.classList.remove('hidden');
  }
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.innerText = msg;
  toast.classList.remove('hidden');
  setTimeout(() => {
    toast.classList.add('hidden');
  }, 2800);
}

function escapeHtml(str) {
  if (!str) return '';
  return str.toString()
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
