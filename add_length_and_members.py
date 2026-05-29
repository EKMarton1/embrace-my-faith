with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

changes = []

# ──────────────────────────────────────────────────────────────────────────────
# 1. HTML — Send Prayer: add length selector before the prayers-remaining div
# ──────────────────────────────────────────────────────────────────────────────
old_send_remaining = (
    '      <div id="sendPrayersRemaining" style="text-align:center;margin-top:16px;font-size:13px;color:rgba(0,0,0,0.65);"></div>\n'
    '      <button class="generate-btn" id="sendGenerateBtn" onclick="generateSendPrayer()" style="margin-top:12px;" disabled>Craft Their Prayer</button>'
)
new_send_remaining = (
    '      <label class="form-label" style="margin-top:12px;">Prayer length</label>\n'
    '      <div class="pp-length-row" id="sendLength">\n'
    "        <button class=\"pp-length-btn\" data-range=\"75-100\" onclick=\"selectPpLength(this,'sendLength')\">Still<span class=\"pp-length-sub\">75–100 words</span></button>\n"
    "        <button class=\"pp-length-btn selected\" data-range=\"125-150\" onclick=\"selectPpLength(this,'sendLength')\">Faithful<span class=\"pp-length-sub\">125–150 words</span></button>\n"
    "        <button class=\"pp-length-btn\" data-range=\"175-200\" onclick=\"selectPpLength(this,'sendLength')\">Abundant<span class=\"pp-length-sub\">175–200 words</span></button>\n"
    '      </div>\n'
    '      <div id="sendPrayersRemaining" style="text-align:center;margin-top:16px;font-size:13px;color:rgba(0,0,0,0.65);"></div>\n'
    '      <button class="generate-btn" id="sendGenerateBtn" onclick="generateSendPrayer()" style="margin-top:12px;" disabled>Craft Their Prayer</button>'
)
assert old_send_remaining in html, 'NOT FOUND 1: sendPrayersRemaining div'
html = html.replace(old_send_remaining, new_send_remaining)
changes.append('1. Send Prayer length selector HTML')

# ──────────────────────────────────────────────────────────────────────────────
# 2. JS — generateSendPrayer(): dynamic word range from sendLength selector
# ──────────────────────────────────────────────────────────────────────────────
old_gen = (
    "  var systemMsg = 'You are a heartfelt Christian prayer minister. Write prayers that are warm, specific, and concise. Hard limit: 120 words maximum.';\n"
    "  var userMsg = [\n"
    "    'Generate a personal prayer of 100-120 words for:',\n"
    "    'PERSON: ' + forWho,\n"
    "    'SITUATION: ' + situation,\n"
    "    'TONE: ' + tone,\n"
    "    'Use ' + forWho + \"'s name naturally at least 3 times. Be specific. No filler phrases.\",\n"
    "    'End with Amen. Respond ONLY with the prayer — no labels, no intro. Start with Heavenly Father or Dear Lord.'\n"
    "  ].join('\\n');\n"
    "\n"
    "  var prayerText = '';\n"
    "  try {\n"
    "    var resp = await fetch('/api/claude', {\n"
    "      method: 'POST',\n"
    "      headers: { 'Content-Type': 'application/json' },\n"
    "      body: JSON.stringify({ system: systemMsg, messages: [{ role: 'user', content: userMsg }], max_tokens: 350 })"
)
new_gen = (
    "  var wordRange = getActivePpLength('sendLength');\n"
    "  var maxWords = parseInt(wordRange.split('-')[1]) || 150;\n"
    "  var maxTokens = maxWords <= 100 ? 280 : (maxWords <= 150 ? 400 : 520);\n"
    "  var systemMsg = 'You are a heartfelt Christian prayer minister. Write prayers that are warm, specific, and concise. Every word must count. Hard limit: ' + maxWords + ' words maximum.';\n"
    "  var userMsg = [\n"
    "    'Generate a personal prayer of ' + wordRange + ' words for:',\n"
    "    'PERSON: ' + forWho,\n"
    "    'SITUATION: ' + situation,\n"
    "    'TONE: ' + tone,\n"
    "    'Use ' + forWho + \"'s name naturally at least 3 times. Be specific. No filler phrases.\",\n"
    "    'End with Amen. Respond ONLY with the prayer — no labels, no intro. Start with Heavenly Father or Dear Lord.'\n"
    "  ].join('\\n');\n"
    "\n"
    "  var prayerText = '';\n"
    "  try {\n"
    "    var resp = await fetch('/api/claude', {\n"
    "      method: 'POST',\n"
    "      headers: { 'Content-Type': 'application/json' },\n"
    "      body: JSON.stringify({ system: systemMsg, messages: [{ role: 'user', content: userMsg }], max_tokens: maxTokens })"
)
assert old_gen in html, 'NOT FOUND 2: generateSendPrayer system/userMsg block'
html = html.replace(old_gen, new_gen)
changes.append('2. generateSendPrayer() dynamic word range')

# ──────────────────────────────────────────────────────────────────────────────
# 3. JS — resetSendPrayer(): reset length selector back to Faithful
# ──────────────────────────────────────────────────────────────────────────────
old_reset = (
    "  var toneEl = document.getElementById('sendPrayerTone');\n"
    "  if (toneEl) toneEl.value = '';\n"
    "  var genBtn = document.getElementById('sendGenerateBtn');\n"
    "  if (genBtn) genBtn.disabled = true;"
)
new_reset = (
    "  var toneEl = document.getElementById('sendPrayerTone');\n"
    "  if (toneEl) toneEl.value = '';\n"
    "  resetPpLength('sendLength');\n"
    "  var genBtn = document.getElementById('sendGenerateBtn');\n"
    "  if (genBtn) genBtn.disabled = true;"
)
assert old_reset in html, 'NOT FOUND 3: resetSendPrayer tone reset block'
html = html.replace(old_reset, new_reset)
changes.append('3. resetSendPrayer() resets sendLength to Faithful')

# ──────────────────────────────────────────────────────────────────────────────
# 4. JS — renderAudienceButtons(): add individual circle member buttons
# ──────────────────────────────────────────────────────────────────────────────
old_render = (
    "function renderAudienceButtons() {\n"
    "  var wrap = document.getElementById('audienceButtonsWrap');\n"
    "  if (!wrap) return;\n"
    "  // Remove old group buttons, keep the static CIRCLE button\n"
    "  wrap.querySelectorAll('.aud-btn:not(#audAll)').forEach(function(b){ b.remove(); });\n"
    "  circleGroups.forEach(function(g){\n"
    "    var b = document.createElement('button');\n"
    "    b.className = 'action-btn aud-btn';\n"
    "    b.textContent = g.name.toUpperCase();\n"
    "    b.dataset.gid = g.id;\n"
    "    b.onclick = function(){ selectAudienceGroup(g.id, b); };\n"
    "    wrap.appendChild(b);\n"
    "  });\n"
    "  // Re-apply the persisted selection (selectedGroupId) after rebuilding buttons.\n"
    "  // undefined = nothing selected yet (default); null = CIRCLE; uuid = group.\n"
    "  wrap.querySelectorAll('.aud-btn').forEach(function(b){ b.classList.remove('selected'); });\n"
    "  if (selectedGroupId === undefined) {\n"
    "    // Nothing selected — leave all buttons unlit (fresh default state)\n"
    "  } else if (selectedGroupId === null) {\n"
    "    var all = document.getElementById('audAll');\n"
    "    if (all) all.classList.add('selected');\n"
    "  } else {\n"
    "    var sel = wrap.querySelector('[data-gid=\"' + selectedGroupId + '\"]');\n"
    "    if (sel) sel.classList.add('selected');\n"
    "  }\n"
    "}"
)
new_render = (
    "function renderAudienceButtons() {\n"
    "  var wrap = document.getElementById('audienceButtonsWrap');\n"
    "  if (!wrap) return;\n"
    "  // Remove old group + member buttons, keep the static CIRCLE button\n"
    "  wrap.querySelectorAll('.aud-btn:not(#audAll)').forEach(function(b){ b.remove(); });\n"
    "  // Group buttons\n"
    "  circleGroups.forEach(function(g){\n"
    "    var b = document.createElement('button');\n"
    "    b.className = 'action-btn aud-btn';\n"
    "    b.textContent = g.name.toUpperCase();\n"
    "    b.dataset.gid = g.id;\n"
    "    b.onclick = function(){ selectAudienceGroup(g.id, b); };\n"
    "    wrap.appendChild(b);\n"
    "  });\n"
    "  // Individual member buttons\n"
    "  if (circleData && circleData.length) {\n"
    "    circleData.forEach(function(m){\n"
    "      var b = document.createElement('button');\n"
    "      b.className = 'action-btn aud-btn';\n"
    "      b.textContent = m.name;\n"
    "      b.dataset.mid = m.userId;\n"
    "      b.onclick = function(){ selectAudienceMember(m.userId, b); };\n"
    "      wrap.appendChild(b);\n"
    "    });\n"
    "  }\n"
    "  // Re-apply the persisted selection after rebuilding buttons.\n"
    "  // selectedMemberId takes priority; else selectedGroupId (undefined/null/uuid).\n"
    "  wrap.querySelectorAll('.aud-btn').forEach(function(b){ b.classList.remove('selected'); });\n"
    "  if (selectedMemberId) {\n"
    "    var sel = wrap.querySelector('[data-mid=\"' + selectedMemberId + '\"]');\n"
    "    if (sel) sel.classList.add('selected');\n"
    "  } else if (selectedGroupId === null) {\n"
    "    var all = document.getElementById('audAll');\n"
    "    if (all) all.classList.add('selected');\n"
    "  } else if (selectedGroupId) {\n"
    "    var sel = wrap.querySelector('[data-gid=\"' + selectedGroupId + '\"]');\n"
    "    if (sel) sel.classList.add('selected');\n"
    "  }\n"
    "}"
)
assert old_render in html, 'NOT FOUND 4: renderAudienceButtons function'
html = html.replace(old_render, new_render)
changes.append('4. renderAudienceButtons() adds individual member buttons')

# ──────────────────────────────────────────────────────────────────────────────
# 5. JS — selectedGroupId variable: add selectedMemberId alongside it
# ──────────────────────────────────────────────────────────────────────────────
old_var = (
    "// ========== PRAYER REQUESTS ==========\n"
    "// undefined = nothing selected yet (default, no button lit)\n"
    "// null      = CIRCLE / send to whole circle\n"
    "// 'uuid'    = specific group\n"
    "var selectedGroupId = undefined;"
)
new_var = (
    "// ========== PRAYER REQUESTS ==========\n"
    "// selectedGroupId: undefined=nothing, null=whole circle, 'uuid'=group\n"
    "// selectedMemberId: undefined=no individual selected, 'uuid'=specific member\n"
    "var selectedGroupId = undefined;\n"
    "var selectedMemberId = undefined;"
)
assert old_var in html, 'NOT FOUND 5: selectedGroupId variable declaration'
html = html.replace(old_var, new_var)
changes.append('5. selectedMemberId variable added')

# ──────────────────────────────────────────────────────────────────────────────
# 6. JS — selectAudienceGroup(): reset selectedMemberId on group/circle selection
# ──────────────────────────────────────────────────────────────────────────────
old_sel_group = (
    "function selectAudienceGroup(groupId, btn) {\n"
    "  selectedGroupId = groupId;\n"
    "  var wrap = document.getElementById('audienceButtonsWrap');\n"
    "  if (wrap) wrap.querySelectorAll('.aud-btn').forEach(function(b){ b.classList.remove('selected'); });\n"
    "  if (btn) btn.classList.add('selected');\n"
    "}"
)
new_sel_group = (
    "function selectAudienceGroup(groupId, btn) {\n"
    "  selectedGroupId = groupId;\n"
    "  selectedMemberId = undefined;\n"
    "  var wrap = document.getElementById('audienceButtonsWrap');\n"
    "  if (wrap) wrap.querySelectorAll('.aud-btn').forEach(function(b){ b.classList.remove('selected'); });\n"
    "  if (btn) btn.classList.add('selected');\n"
    "}\n"
    "\n"
    "function selectAudienceMember(userId, btn) {\n"
    "  selectedMemberId = userId;\n"
    "  selectedGroupId = undefined;\n"
    "  var wrap = document.getElementById('audienceButtonsWrap');\n"
    "  if (wrap) wrap.querySelectorAll('.aud-btn').forEach(function(b){ b.classList.remove('selected'); });\n"
    "  if (btn) btn.classList.add('selected');\n"
    "}"
)
assert old_sel_group in html, 'NOT FOUND 6: selectAudienceGroup function'
html = html.replace(old_sel_group, new_sel_group)
changes.append('6. selectAudienceGroup resets member; selectAudienceMember added')

# ──────────────────────────────────────────────────────────────────────────────
# 7. JS — submitPrayerRequest(): include target_user_id / group_id in payload
#         + require audience selection before submitting
# ──────────────────────────────────────────────────────────────────────────────
old_submit = (
    "async function submitPrayerRequest() {\n"
    "  if (!currentUser) { alert('Please sign in to send prayer requests.'); return; }\n"
    "  var text = document.getElementById('requestPrayerText').value.trim();\n"
    "  if (!text) { alert('Please share what you would like prayer for.'); return; }\n"
    "  var payload = { user_id: currentUser.id, request_text: text };\n"
    "  var result = await supaPost('/rest/v1/prayer_requests', payload);"
)
new_submit = (
    "async function submitPrayerRequest() {\n"
    "  if (!currentUser) { alert('Please sign in to send prayer requests.'); return; }\n"
    "  var text = document.getElementById('requestPrayerText').value.trim();\n"
    "  if (!text) { alert('Please share what you would like prayer for.'); return; }\n"
    "  if (selectedGroupId === undefined && !selectedMemberId) { alert('Please select who to send your request to.'); return; }\n"
    "  var payload = { user_id: currentUser.id, request_text: text };\n"
    "  if (selectedMemberId) { payload.target_user_id = selectedMemberId; }\n"
    "  else if (selectedGroupId) { payload.group_id = selectedGroupId; }\n"
    "  var result = await supaPost('/rest/v1/prayer_requests', payload);"
)
assert old_submit in html, 'NOT FOUND 7: submitPrayerRequest function header'
html = html.replace(old_submit, new_submit)
changes.append('7. submitPrayerRequest includes audience target')

# ──────────────────────────────────────────────────────────────────────────────
# Report
# ──────────────────────────────────────────────────────────────────────────────
print(f'Applied {len(changes)} changes:')
for c in changes:
    print(f'  OK: {c}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('File written.')
