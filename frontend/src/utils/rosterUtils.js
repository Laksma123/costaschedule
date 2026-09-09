/**
 * Roster Utilities for Costa Schedule Editor
 * Immutable state transformation functions, category extraction,
 * and live Base64 WhatsApp payload generation.
 */

// ── 1. Category Extraction (Real-time, Cache-free) ──
export function extractAllSections(data) {
  if (!data) return []

  const sections = []

  // Venues (Main Dining)
  ;(data.venues || []).forEach((v, vIdx) => {
    sections.push({
      type: 'venue',
      venueIndex: vIdx,
      id: `venue-${vIdx}`,
      name: v.name,
      reportTime: v.reportTime || '',
      stations: (v.assignments || []).map((a, aIdx) => ({
        assignmentIndex: aIdx,
        station: a.station,
        waiterId: a.waiterId,
        waiterName: a.waiterName,
        attendantId: a.attendantId,
        attendantName: a.attendantName,
        tables: a.tables || '',
      })),
      group: 'Main Dining Restaurants',
      badge: 'Venue',
    })
  })

  // Buffet & Specialty Outlets
  ;(data.buffetAndVenues || []).forEach((b, bIdx) => {
    sections.push({
      type: 'buffet',
      buffetIndex: bIdx,
      id: `buffet-${bIdx}`,
      name: b.name,
      timing: b.timing || '',
      lead: b.lead || '',
      crewCount: (b.crew || []).length,
      group: 'Buffet & Specialty Outlets',
      badge: 'Buffet/Outlet',
    })
  })

  // Side Duties & Sub-Teams
  ;(data.sideDuties || []).forEach((s, sIdx) => {
    sections.push({
      type: 'sideDuty',
      sideDutyIndex: sIdx,
      id: `side-${sIdx}`,
      name: s.name,
      timing: s.timing || '',
      crewCount: (s.crew || []).length,
      group: 'Sub-Teams & Side Duties',
      badge: 'Side Duty',
    })
  })

  // Sick Leave / Off Duty
  sections.push({
    type: 'sickLeave',
    id: 'sick-leave',
    name: 'SICK LEAVE / OFF DUTY',
    crewCount: (data.sickLeave || []).length,
    group: 'Sick Leave / Off Duty',
    badge: 'Sick Leave',
  })

  return sections
}

// ── 2. Telemetry Calculation ──
export function calculateTelemetry(data, payloadStr = '', b64Str = '') {
  if (!data) return {}

  const allCrewNames = new Set()

  ;(data.venues || []).forEach(v => {
    ;(v.assignments || []).forEach(a => {
      if (a.waiterName) allCrewNames.add(a.waiterName)
      if (a.attendantName) allCrewNames.add(a.attendantName)
    })
  })

  ;(data.buffetAndVenues || []).forEach(b => {
    ;(b.crew || []).forEach(c => {
      if (c.name) allCrewNames.add(c.name)
    })
  })

  ;(data.sideDuties || []).forEach(s => {
    ;(s.crew || []).forEach(c => {
      if (c.name) allCrewNames.add(c.name)
    })
  })

  ;(data.sickLeave || []).forEach(sk => {
    if (sk.name) allCrewNames.add(sk.name)
  })

  const sectionCount =
    (data.venues || []).length +
    (data.buffetAndVenues || []).length +
    (data.sideDuties || []).length +
    (data.sickLeave?.length ? 1 : 0)

  const stationCount = (data.venues || []).reduce(
    (sum, v) => sum + (v.assignments || []).length,
    0
  )

  return {
    crewCount: allCrewNames.size,
    sectionCount,
    stationCount,
    payloadChars: payloadStr.length,
    b64Bytes: b64Str.length,
  }
}

// ── 3. WhatsApp Encrypted Payload Generator ──
export function generateWhatsAppPayload(scheduleData) {
  if (!scheduleData) return { payload: '', b64: '' }

  try {
    const jsonStr = JSON.stringify(scheduleData)
    // UTF-8 base64 encoding safe for unicode
    const b64 = btoa(unescape(encodeURIComponent(jsonStr)))

    const payload = [
      `${scheduleData.ship || 'COSTA SMERALDA'} — RESTAURANT SCHEDULE`,
      `Date    : ${scheduleData.date || '—'}`,
      `Shift   : ${scheduleData.shift || '—'}`,
      `--------------------------------------------`,
      `[COSTA-DATA-START]`,
      b64,
      `[COSTA-DATA-END]`,
    ].join('\n')

    return { payload, b64 }
  } catch (err) {
    console.error('Failed to generate WhatsApp payload:', err)
    return { payload: '', b64: '' }
  }
}

// ── 4. Move Crew Member ──
export function moveCrew(data, source, target, crew) {
  if (!data || !source || !target || !crew) return data

  const next = JSON.parse(JSON.stringify(data))

  // 1. Remove from source
  if (source.type === 'venue_waiter') {
    const v = next.venues?.[source.venueIndex]
    const a = v?.assignments?.[source.assignmentIndex]
    if (a) {
      a.waiterName = ''
    }
  } else if (source.type === 'venue_attendant') {
    const v = next.venues?.[source.venueIndex]
    const a = v?.assignments?.[source.assignmentIndex]
    if (a) {
      a.attendantName = ''
    }
  } else if (source.type === 'buffet') {
    const b = next.buffetAndVenues?.[source.buffetIndex]
    if (b && b.crew) {
      b.crew = b.crew.filter((c, idx) =>
        source.crewIndex !== undefined ? idx !== source.crewIndex : c.name !== crew.name
      )
    }
  } else if (source.type === 'sideDuty') {
    const s = next.sideDuties?.[source.sideDutyIndex]
    if (s && s.crew) {
      s.crew = s.crew.filter((c, idx) =>
        source.crewIndex !== undefined ? idx !== source.crewIndex : c.name !== crew.name
      )
    }
  } else if (source.type === 'sickLeave') {
    if (next.sickLeave) {
      next.sickLeave = next.sickLeave.filter((sk, idx) =>
        source.sickIndex !== undefined ? idx !== source.sickIndex : sk.name !== crew.name
      )
    }
  } else if (source.type === 'specialEvent') {
    const ev = next.specialEvents?.[source.eventIndex]
    if (ev && ev.participants) {
      ev.participants = ev.participants.filter((p, idx) =>
        source.pIndex !== undefined ? idx !== source.pIndex : p.name !== crew.name
      )
    }
  }

  // 2. Add to target
  if (target.type === 'venue') {
    const v = next.venues?.[target.venueIndex]
    if (v) {
      if (!v.assignments) v.assignments = []

      // If station index specified:
      if (target.assignmentIndex !== undefined && v.assignments[target.assignmentIndex]) {
        const a = v.assignments[target.assignmentIndex]
        if (target.role === 'attendant') {
          a.attendantName = crew.name || ''
        } else {
          a.waiterName = crew.name || ''
        }
      } else {
        // Create new station assignment
        const newStationName = target.stationName || `Station ${v.assignments.length + 1}`
        v.assignments.push({
          station: newStationName,
          waiterName: target.role === 'attendant' ? '' : (crew.name || ''),
          attendantName: target.role === 'attendant' ? (crew.name || '') : '',
          tables: target.tables || '',
        })
      }
    }
  } else if (target.type === 'buffet') {
    const b = next.buffetAndVenues?.[target.buffetIndex]
    if (b) {
      if (!b.crew) b.crew = []
      const newCrewObj = {
        name: crew.name || '',
      }
      if (target.role) newCrewObj.role = target.role
      else if (crew.role) newCrewObj.role = crew.role
      b.crew.push(newCrewObj)
    }
  } else if (target.type === 'sideDuty') {
    const s = next.sideDuties?.[target.sideDutyIndex]
    if (s) {
      if (!s.crew) s.crew = []
      s.crew.push({
        name: crew.name || '',
      })
    }
  } else if (target.type === 'sickLeave') {
    if (!next.sickLeave) next.sickLeave = []
    next.sickLeave.push({
      name: crew.name || '',
    })
  }

  return next
}

// ── 5. Update Timing ──
export function updateTiming(data, target, newTiming) {
  if (!data || !target) return data
  const next = JSON.parse(JSON.stringify(data))

  if (target.type === 'venue') {
    const v = next.venues?.[target.venueIndex]
    if (v) v.reportTime = newTiming
  } else if (target.type === 'buffet') {
    const b = next.buffetAndVenues?.[target.buffetIndex]
    if (b) b.timing = newTiming
  } else if (target.type === 'sideDuty') {
    const s = next.sideDuties?.[target.sideDutyIndex]
    if (s) s.timing = newTiming
  } else if (target.type === 'crew_role') {
    const b = next.buffetAndVenues?.[target.buffetIndex]
    const c = b?.crew?.[target.crewIndex]
    if (c) c.role = newTiming
  }

  return next
}

// ── 6. Update Tables ──
export function updateTables(data, venueIndex, assignmentIndex, newTables) {
  if (!data) return data
  const next = JSON.parse(JSON.stringify(data))
  const v = next.venues?.[venueIndex]
  const a = v?.assignments?.[assignmentIndex]
  if (a) {
    a.tables = newTables
  }
  return next
}

// ── 7. Update Crew Details (Name, Role) ──
export function updateCrewDetails(data, location, updated) {
  if (!data || !location) return data
  const next = JSON.parse(JSON.stringify(data))

  if (location.type === 'venue_waiter') {
    const a = next.venues?.[location.venueIndex]?.assignments?.[location.assignmentIndex]
    if (a) {
      if (updated.name !== undefined) a.waiterName = updated.name
    }
  } else if (location.type === 'venue_attendant') {
    const a = next.venues?.[location.venueIndex]?.assignments?.[location.assignmentIndex]
    if (a) {
      if (updated.name !== undefined) a.attendantName = updated.name
    }
  } else if (location.type === 'buffet') {
    const c = next.buffetAndVenues?.[location.buffetIndex]?.crew?.[location.crewIndex]
    if (c) {
      if (updated.name !== undefined) c.name = updated.name
      if (updated.role !== undefined) c.role = updated.role
    }
  } else if (location.type === 'sideDuty') {
    const c = next.sideDuties?.[location.sideDutyIndex]?.crew?.[location.crewIndex]
    if (c) {
      if (updated.name !== undefined) c.name = updated.name
    }
  } else if (location.type === 'sickLeave') {
    const sk = next.sickLeave?.[location.sickIndex]
    if (sk) {
      if (updated.name !== undefined) sk.name = updated.name
    }
  }

  return next
}

// ── 8. Add Crew to Section ──
export function addCrewToSection(data, targetSection, newCrew) {
  if (!data || !targetSection) return data
  const next = JSON.parse(JSON.stringify(data))

  if (targetSection.type === 'venue') {
    const v = next.venues?.[targetSection.venueIndex]
    if (v) {
      if (!v.assignments) v.assignments = []
      v.assignments.push({
        station: newCrew.station || `Station ${v.assignments.length + 1}`,
        waiterName: newCrew.role === 'attendant' ? '' : (newCrew.name || ''),
        attendantName: newCrew.role === 'attendant' ? (newCrew.name || '') : '',
        tables: newCrew.tables || '',
      })
    }
  } else if (targetSection.type === 'buffet') {
    const b = next.buffetAndVenues?.[targetSection.buffetIndex]
    if (b) {
      if (!b.crew) b.crew = []
      b.crew.push({
        name: newCrew.name || '',
        role: newCrew.role || '',
      })
    }
  } else if (targetSection.type === 'sideDuty') {
    const s = next.sideDuties?.[targetSection.sideDutyIndex]
    if (s) {
      if (!s.crew) s.crew = []
      s.crew.push({
        name: newCrew.name || '',
      })
    }
  } else if (targetSection.type === 'sickLeave') {
    if (!next.sickLeave) next.sickLeave = []
    next.sickLeave.push({
      name: newCrew.name || '',
    })
  }

  return next
}

// ── 9. Delete Crew / Station from Section ──
export function deleteCrewFromSection(data, location) {
  if (!data || !location) return data
  const next = JSON.parse(JSON.stringify(data))

  if (location.type === 'venue_waiter') {
    const a = next.venues?.[location.venueIndex]?.assignments?.[location.assignmentIndex]
    if (a) {
      a.waiterName = ''
    }
  } else if (location.type === 'venue_attendant') {
    const a = next.venues?.[location.venueIndex]?.assignments?.[location.assignmentIndex]
    if (a) {
      a.attendantName = ''
    }
  } else if (location.type === 'venue_station') {
    const v = next.venues?.[location.venueIndex]
    if (v && v.assignments) {
      v.assignments.splice(location.assignmentIndex, 1)
    }
  } else if (location.type === 'buffet') {
    const b = next.buffetAndVenues?.[location.buffetIndex]
    if (b && b.crew) {
      b.crew.splice(location.crewIndex, 1)
    }
  } else if (location.type === 'sideDuty') {
    const s = next.sideDuties?.[location.sideDutyIndex]
    if (s && s.crew) {
      s.crew.splice(location.crewIndex, 1)
    }
  } else if (location.type === 'sickLeave') {
    if (next.sickLeave) {
      next.sickLeave.splice(location.sickIndex, 1)
    }
  }

  return next
}

// ── 10. Duplicate & Typo Detection Engine ──
export function normalizeCrewName(name) {
  if (!name) return ''
  return name
    .toUpperCase()
    .replace(/\s*-[A-Z0-9\s-]+\b/g, '') // strip "-BS", "-TR", "-CT", "-TR -CT"
    .replace(/\(.*?\)/g, '')            // strip "(LEAD)", "(CHEF)"
    .replace(/[^A-Z\s]/g, '')           // keep only letters and spaces
    .replace(/\s+/g, ' ')
    .trim()
}

export function levenshteinDistance(a, b) {
  if (a.length === 0) return b.length
  if (b.length === 0) return a.length

  const matrix = []
  for (let i = 0; i <= b.length; i++) {
    matrix[i] = [i]
  }
  for (let j = 0; j <= a.length; j++) {
    matrix[0][j] = j
  }

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1]
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // substitution
          matrix[i][j - 1] + 1,     // insertion
          matrix[i - 1][j] + 1      // deletion
        )
      }
    }
  }

  return matrix[b.length][a.length]
}

export function detectDuplicates(data) {
  if (!data) {
    return {
      hasDuplicates: false,
      totalIssues: 0,
      nameDuplicates: [],
      fuzzyDuplicates: [],
      flaggedCrewMap: {},
    }
  }

  const entries = []

  // Collect from Venues
  ;(data.venues || []).forEach((v, vIdx) => {
    ;(v.assignments || []).forEach((a, aIdx) => {
      if (a.waiterName) {
        entries.push({
          rawName: (a.waiterName || '').trim(),
          cleanName: normalizeCrewName(a.waiterName),
          location: `${v.name} • Station ${a.station} (Waiter)`,
          locationType: 'venue_waiter',
          venueIndex: vIdx,
          assignmentIndex: aIdx,
        })
      }
      if (a.attendantName) {
        entries.push({
          rawName: (a.attendantName || '').trim(),
          cleanName: normalizeCrewName(a.attendantName),
          location: `${v.name} • Station ${a.station} (Attendant)`,
          locationType: 'venue_attendant',
          venueIndex: vIdx,
          assignmentIndex: aIdx,
        })
      }
    })
  })

  // Collect from Buffet & Outlets
  ;(data.buffetAndVenues || []).forEach((b, bIdx) => {
    ;(b.crew || []).forEach((c, cIdx) => {
      if (c.name) {
        entries.push({
          rawName: (c.name || '').trim(),
          cleanName: normalizeCrewName(c.name),
          location: `${b.name}${c.role ? ` (${c.role})` : ''}`,
          locationType: 'buffet',
          buffetIndex: bIdx,
          crewIndex: cIdx,
        })
      }
    })
  })

  // Collect from Side Duties
  ;(data.sideDuties || []).forEach((s, sIdx) => {
    ;(s.crew || []).forEach((c, cIdx) => {
      if (c.name) {
        entries.push({
          rawName: (c.name || '').trim(),
          cleanName: normalizeCrewName(c.name),
          location: s.name,
          locationType: 'sideDuty',
          sideDutyIndex: sIdx,
          crewIndex: cIdx,
        })
      }
    })
  })

  // Collect from Sick Leave
  ;(data.sickLeave || []).forEach((sk, skIdx) => {
    if (sk.name) {
      entries.push({
        rawName: (sk.name || '').trim(),
        cleanName: normalizeCrewName(sk.name),
        location: 'Sick Leave / Off Duty',
        locationType: 'sickLeave',
        sickIndex: skIdx,
      })
    }
  })

  const flaggedCrewMap = {}
  const nameDuplicates = []
  const fuzzyDuplicates = []

  // 1. Check Name Duplicates (Exact Clean Name)
  const nameGroups = {}
  entries.forEach((e) => {
    if (!e.cleanName || e.cleanName.length < 3) return
    if (!nameGroups[e.cleanName]) nameGroups[e.cleanName] = []
    nameGroups[e.cleanName].push(e)
  })

  Object.entries(nameGroups).forEach(([cleanName, group]) => {
    if (group.length > 1) {
      const issue = {
        type: 'duplicate_name',
        cleanName,
        count: group.length,
        rawNames: [...new Set(group.map((g) => g.rawName))],
        locations: group.map((g) => g.location),
        entries: group,
      }
      nameDuplicates.push(issue)
      group.forEach((g) => {
        const key = g.rawName
        if (!flaggedCrewMap[key]) {
          flaggedCrewMap[key] = {
            type: 'duplicate_name',
            message: `Duplicate Name "${cleanName}" in ${group.length} places (${group.map((x) => x.location).join(' & ')})`,
            otherLocations: group.filter((x) => x !== g).map((x) => x.location),
          }
        }
      })
    }
  })

  // 2. Fuzzy / Typo Name Matching
  const uniqueNames = Object.keys(nameGroups)
  const checkedPairs = new Set()

  for (let i = 0; i < uniqueNames.length; i++) {
    for (let j = i + 1; j < uniqueNames.length; j++) {
      const n1 = uniqueNames[i]
      const n2 = uniqueNames[j]

      if (n1 === n2) continue
      const pairKey = [n1, n2].sort().join('|||')
      if (checkedPairs.has(pairKey)) continue
      checkedPairs.add(pairKey)

      const maxLen = Math.max(n1.length, n2.length)
      if (maxLen < 6) continue

      const dist = levenshteinDistance(n1, n2)
      const isTypoMatch = (dist <= 2 && maxLen >= 7) || (dist === 1 && maxLen >= 5)
      const isSubMatch =
        (n1.includes(n2) || n2.includes(n1)) && Math.abs(n1.length - n2.length) <= 4

      if (isTypoMatch || isSubMatch) {
        const group1 = nameGroups[n1]
        const group2 = nameGroups[n2]
        const combined = [...group1, ...group2]

        const issue = {
          type: 'fuzzy_typo',
          name1: n1,
          name2: n2,
          distance: dist,
          locations: combined.map((c) => `${c.rawName} (${c.location})`),
          entries: combined,
        }
        fuzzyDuplicates.push(issue)

        combined.forEach((g) => {
          const key = g.rawName
          if (!flaggedCrewMap[key]) {
            flaggedCrewMap[key] = {
              type: 'fuzzy_typo',
              message: `Typo/Similarity: "${n1}" vs "${n2}"`,
              otherLocations: combined
                .filter((x) => x !== g)
                .map((x) => `${x.rawName} in ${x.location}`),
            }
          }
        })
      }
    }
  }

  const totalIssues = nameDuplicates.length + fuzzyDuplicates.length

  return {
    hasDuplicates: totalIssues > 0,
    totalIssues,
    idDuplicates: [],
    nameDuplicates,
    fuzzyDuplicates,
    flaggedCrewMap,
  }
}
