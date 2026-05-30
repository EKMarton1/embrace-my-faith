with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

changes = []

# ──────────────────────────────────────────────────────────────────────────────
# 1. CSS — member select screen styles
# ──────────────────────────────────────────────────────────────────────────────
css_anchor = '.screen-body{padding:20px 20px 40px;flex:1;}'
assert css_anchor in html, 'CSS ANCHOR NOT FOUND'
html = html.replace(css_anchor, css_anchor +
    '.member-check-row{display:flex;align-items:center;background:rgba(255,255,255,0.5);border-radius:14px;padding:14px 16px;margin-bottom:9px;gap:14px;cursor:pointer;touch-action:manipulation;}'
    '.member-check-row:active{background:rgba(255,255,255,0.78);}'
    '.member-check-box{width:22px;height:22px;border-radius:6px;border:2px solid rgba(61,31,0,0.30);background:rgba(255,255,255,0.55);flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:background 0.12s,border-color 0.12s;}'
    '.member-check-box.checked{background:rgba(30,15,0,0.82);border-color:rgba(30,15,0,0.82);}'
    '.member-check-tick{color:#f5c830;font-size:14px;font-weight:900;line-height:1;display:none;}'
    '.member-check-box.checked .member-check-tick{display:block;}'
    '.member-check-name{font-family:\'Lato\',sans-serif;font-size:15px;font-weight:700;color:rgba(30,10,0,0.88);}'
    '.member-done-bar{position:sticky;bottom:0;padding:10px 0 20px;background:linear-gradient(to bottom,rgba(255,248,210,0) 0%,rgba(255,248,210,1) 36%);}'
)
changes.append('1. member-check CSS added')

# ──────────────────────────────────────────────────────────────────────────────
# 2. HTML — replace individual member buttons in audienceButtonsWrap with a
#    single MEMBERS button (static HTML; JS keeps it in sync)
# ──────────────────────────────────────────────────────────────────────────────
# The wrap currently has only the static CIRCLE button; member buttons are
# added dynamically by renderAudienceButtons(). No HTML change needed here
# (member buttons are removed from renderAudienceButtons() in step 4 below).
changes.append('2. (member buttons removed via JS rewrite in step 4)')

# ──────────────────────────────────────────────────────────────────────────────
# 3. HTML — insert memberSelectScreen before circleSubpageScreen
# ──────────────────────────────────────────────────────────────────────────────
member_screen_html = '''<!-- MEMBER SELECT SUBPAGE -->
<div class="screen" id="memberSelectScreen">
<div class="screen-top">
  <div class="screen-title-row"><button class="back-arrow-btn" onclick="showScreen(\'requestPrayerScreen\')">&lt;</button><div class="screen-title">Select Members</div></div>
</div>
  <div class="screen-body">
    <div id="memberSelectList"></div>
    <div class="member-done-bar">
      <button class="generate-btn" onclick="doneMemberSelect()">Done</button>
    </div>
  </div>
</div>

'''
anchor_html = '<!-- CIRCLE SUBPAGE (My Circle members / group subpage) -->'
assert anchor_html in html, 'HTML ANCHOR NOT FOUND: circle subpage comment'
html = html.replace(anchor_html, member_screen_html + anchor_html)
changes.append('3. memberSelectScreen HTML inserted')

# ──────────────────────────────────────────────────────────────────────────────
# 4. JS — rewrite renderAudienceButtons() to use a single MEMBERS button
#    instead of individual member buttons
# ──────────────────────────────────────────────────────────────────────────────
old_render = (
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
new_render = (
    "function renderAudienceButtons() {\n"
    "  var wrap = document.getElementById('audienceButtonsWrap');\n"
    "  if (!wrap) return;\n"
    "  // Remove all dynamic buttons (groups + MEMBERS), keep static CIRCLE\n"
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
    "  // Single MEMBERS button (only when circle has members)\n"
    "  if (circleData && circleData.length) {\n"
    "    var mb = document.createElement('button');\n"
    "    mb.className = 'action-btn aud-btn';\n"
    "    mb.id = 'audMembers';\n"
    "    var cnt = selectedMemberIds.length;\n"
    "    mb.textContent = cnt > 0 ? 'MEMBERS (' + cnt + ')' : 'MEMBERS';\n"
    "    mb.onclick = function(){ openMemberSelectScreen(); };\n"
    "    wrap.appendChild(mb);\n"
    "  }\n"
    "  // Re-apply selection highlighting\n"
    "  wrap.querySelectorAll('.aud-btn').forEach(function(b){ b.classList.remove('selected'); });\n"
    "  if (selectedMemberIds.length > 0) {\n"
    "    var mb = document.getElementById('audMembers');\n"
    "    if (mb) mb.classList.add('selected');\n"
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
changes.append('4. renderAudienceButtons() uses single MEMBERS button')

# ──────────────────────────────────────────────────────────────────────────────
# 5. JS — replace selectedGroupId/selectedMemberId vars with
#    selectedGroupId + selectedMemberIds (array)
# ──────────────────────────────────────────────────────────────────────────────
old_vars = (
    "// ========== PRAYER REQUESTS ==========\n"
    "// selectedGroupId: undefined=nothing, null=whole circle, 'uuid'=group\n"
    "// selectedMemberId: undefined=no individual selected, 'uuid'=specific member\n"
    "var selectedGroupId = undefined;\n"
    "var selectedMemberId = undefined;"
)
new_vars = (
    "// ========== PRAYER REQUESTS ==========\n"
    "// selectedGroupId: undefined=nothing selected, null=whole circle, 'uuid'=group\n"
    "// selectedMemberIds: array of userId strings for individual member selection\n"
    "var selectedGroupId = undefined;\n"
    "var selectedMemberIds = [];"
)
assert old_vars in html, 'NOT FOUND 5: variable declarations'
html = html.replace(old_vars, new_vars)
changes.append('5. selectedMemberId replaced with selectedMemberIds array')

# ──────────────────────────────────────────────────────────────────────────────
# 6. JS — update selectAudienceGroup() to clear selectedMemberIds
# ──────────────────────────────────────────────────────────────────────────────
old_sel_group = (
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
new_sel_group = (
    "function selectAudienceGroup(groupId, btn) {\n"
    "  selectedGroupId = groupId;\n"
    "  selectedMemberIds = [];\n"
    "  var wrap = document.getElementById('audienceButtonsWrap');\n"
    "  if (wrap) wrap.querySelectorAll('.aud-btn').forEach(function(b){ b.classList.remove('selected'); });\n"
    "  if (btn) btn.classList.add('selected');\n"
    "}\n"
    "\n"
    "// ── MEMBER SELECT SUBPAGE ──────────────────────────────────────────────\n"
    "function openMemberSelectScreen() {\n"
    "  renderMemberSelectList();\n"
    "  showScreen('memberSelectScreen');\n"
    "}\n"
    "\n"
    "function doneMemberSelect() {\n"
    "  // If members are checked, switch to member-mode (clear circle/group choice)\n"
    "  if (selectedMemberIds.length > 0) { selectedGroupId = undefined; }\n"
    "  showScreen('requestPrayerScreen'); // triggers renderAudienceButtons()\n"
    "}\n"
    "\n"
    "function renderMemberSelectList() {\n"
    "  var list = document.getElementById('memberSelectList');\n"
    "  if (!list) return;\n"
    "  if (!circleData || !circleData.length) {\n"
    "    list.innerHTML = '<div style=\"text-align:center;padding:32px 16px;font-family:Lato,sans-serif;font-size:14px;color:rgba(0,0,0,0.45);\">No circle members yet.</div>';\n"
    "    return;\n"
    "  }\n"
    "  list.innerHTML = circleData.map(function(m) {\n"
    "    var checked = selectedMemberIds.indexOf(m.userId) !== -1;\n"
    "    return '<div class=\"member-check-row\" onclick=\"toggleMemberCheck(\\'' + m.userId + '\\')\">' +\n"
    "      '<div class=\"member-check-box' + (checked ? ' checked' : '') + '\" id=\"mbox_' + m.userId + '\"><span class=\"member-check-tick\">&#10003;</span></div>' +\n"
    "      '<div class=\"member-check-name\">' + escHtml(m.name) + '</div>' +\n"
    "      '</div>';\n"
    "  }).join('');\n"
    "}\n"
    "\n"
    "function toggleMemberCheck(userId) {\n"
    "  var idx = selectedMemberIds.indexOf(userId);\n"
    "  var box = document.getElementById('mbox_' + userId);\n"
    "  if (idx === -1) {\n"
    "    selectedMemberIds.push(userId);\n"
    "    if (box) box.classList.add('checked');\n"
    "  } else {\n"
    "    selectedMemberIds.splice(idx, 1);\n"
    "    if (box) box.classList.remove('checked');\n"
    "  }\n"
    "}"
)
assert old_sel_group in html, 'NOT FOUND 6: selectAudienceGroup + selectAudienceMember functions'
html = html.replace(old_sel_group, new_sel_group)
changes.append('6. selectAudienceGroup + member select functions added')

# ──────────────────────────────────────────────────────────────────────────────
# 7. JS — update submitPrayerRequest() to use selectedMemberIds and reset after send
# ──────────────────────────────────────────────────────────────────────────────
old_submit = (
    "  if (selectedGroupId === undefined && !selectedMemberId) { alert('Please select who to send your request to.'); return; }\n"
    "  var payload = { user_id: currentUser.id, request_text: text };\n"
    "  if (selectedMemberId) { payload.target_user_id = selectedMemberId; }\n"
    "  else if (selectedGroupId) { payload.group_id = selectedGroupId; }\n"
    "  var result = await supaPost('/rest/v1/prayer_requests', payload);\n"
    "  if (result && result.code) { alert('Could not send: ' + (result.message||result.code)); return; }\n"
    "  document.getElementById('requestPrayerText').value = '';\n"
    "  var btn = document.querySelector('#requestPrayerScreen .generate-btn');\n"
    "  if (btn) { var t=btn.textContent; btn.textContent='Sent to your circle!'; setTimeout(function(){ btn.textContent=t; }, 2200); }\n"
    "  loadPrayerRequests();"
)
new_submit = (
    "  if (selectedGroupId === undefined && selectedMemberIds.length === 0) { alert('Please select who to send your request to.'); return; }\n"
    "  var payload = { user_id: currentUser.id, request_text: text };\n"
    "  if (selectedMemberIds.length > 0) { payload.target_user_ids = selectedMemberIds; }\n"
    "  else if (selectedGroupId) { payload.group_id = selectedGroupId; }\n"
    "  var result = await supaPost('/rest/v1/prayer_requests', payload);\n"
    "  if (result && result.code) { alert('Could not send: ' + (result.message||result.code)); return; }\n"
    "  document.getElementById('requestPrayerText').value = '';\n"
    "  // Reset member selections after a successful send\n"
    "  selectedMemberIds = [];\n"
    "  selectedGroupId = undefined;\n"
    "  renderAudienceButtons();\n"
    "  var btn = document.querySelector('#requestPrayerScreen .generate-btn');\n"
    "  if (btn) { var t=btn.textContent; btn.textContent='Sent to your circle!'; setTimeout(function(){ btn.textContent=t; }, 2200); }\n"
    "  loadPrayerRequests();"
)
assert old_submit in html, 'NOT FOUND 7: submitPrayerRequest body'
html = html.replace(old_submit, new_submit)
changes.append('7. submitPrayerRequest uses selectedMemberIds, resets on success')

# ──────────────────────────────────────────────────────────────────────────────
# Report + write
# ──────────────────────────────────────────────────────────────────────────────
print(f'Applied {len(changes)} changes:')
for c in changes:
    print(f'  OK: {c}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('File written.')
