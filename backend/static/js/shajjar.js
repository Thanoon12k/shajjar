/* شجّر — front-end behaviour (no build step) */
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.remove("no-js");

  /* ---------- theme ---------- */
  function setTheme(t) {
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("shajjar-theme", t); } catch (e) {}
    document.querySelectorAll("[data-set-theme]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.setTheme === t));
    });
    var meta = document.querySelector('meta[name="theme-color"]');
    var sw = document.querySelector('[data-set-theme="' + t + '"]');
    if (meta && sw) meta.setAttribute("content", sw.dataset.color);
    document.dispatchEvent(new CustomEvent("shajjar:theme", { detail: t }));
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-set-theme]");
    if (b) { setTheme(b.dataset.setTheme); closePop(); }
    var tog = e.target.closest("[data-theme-toggle]");
    if (tog) { document.getElementById("theme-pop").classList.toggle("open"); return; }
    if (!e.target.closest(".theme-menu")) closePop();
  });
  function closePop() { var p = document.getElementById("theme-pop"); if (p) p.classList.remove("open"); }
  setTheme(root.getAttribute("data-theme") || "hadba");

  /* ---------- action sheet ---------- */
  var sheet = document.getElementById("action-sheet"), bd = document.getElementById("sheet-backdrop");
  function sheetToggle(open) { if (!sheet) return; sheet.classList.toggle("open", open); bd.classList.toggle("open", open); }
  document.querySelectorAll("[data-open-sheet]").forEach(function (b) { b.addEventListener("click", function () { sheetToggle(true); }); });
  if (bd) bd.addEventListener("click", function () { sheetToggle(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { sheetToggle(false); closePop(); } });

  /* ---------- auto-hide messages ---------- */
  setTimeout(function () { document.querySelectorAll(".msg").forEach(function (m) { m.style.transition = "opacity .5s"; m.style.opacity = "0"; setTimeout(function () { m.remove(); }, 600); }); }, 6000);

  /* ---------- counters & reveal ---------- */
  var fmt = new Intl.NumberFormat("ar-IQ");
  function countUp(el) {
    var target = parseFloat(el.dataset.count), dec = (el.dataset.count.split(".")[1] || "").length, start = null, dur = 1600;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1), v = target * (1 - Math.pow(1 - p, 3));
      el.textContent = (dec ? new Intl.NumberFormat("ar-IQ", { minimumFractionDigits: dec, maximumFractionDigits: dec }) : fmt).format(dec ? v : Math.round(v)) + (el.dataset.suffix || "");
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        if (en.target.dataset.count !== undefined) countUp(en.target);
        en.target.classList.add("in");
        io.unobserve(en.target);
      });
    }, { threshold: .15 });
    document.querySelectorAll("[data-count], .reveal").forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- falling leaves ---------- */
  document.querySelectorAll(".leaf-fall").forEach(function (box) {
    var leaves = ["🍃", "🌿", "🍂", "🌱"];
    for (var i = 0; i < 12; i++) {
      var l = document.createElement("i");
      l.textContent = leaves[i % leaves.length];
      l.style.left = Math.random() * 100 + "%";
      l.style.animationDuration = 9 + Math.random() * 10 + "s";
      l.style.animationDelay = -Math.random() * 15 + "s";
      l.style.fontSize = 14 + Math.random() * 16 + "px";
      box.appendChild(l);
    }
  });

  /* ---------- before / after ---------- */
  document.querySelectorAll(".ba input[type=range]").forEach(function (r) {
    var ba = r.closest(".ba");
    function upd() { ba.style.setProperty("--pos", r.value + "%"); }
    r.addEventListener("input", upd); upd();
  });

  /* ---------- +/- counters ---------- */
  document.querySelectorAll("[data-counter]").forEach(function (wrap) {
    var input = wrap.querySelector("input");
    wrap.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        var v = parseInt(input.value || "0", 10) + parseInt(b.dataset.step, 10);
        var min = parseInt(input.min || "1", 10), max = parseInt(input.max || "500", 10);
        input.value = Math.max(min, Math.min(max, v));
      });
    });
  });

  /* ---------- image previews ---------- */
  document.querySelectorAll('input[type=file][accept^="image"]').forEach(function (inp) {
    var box = document.createElement("div"); box.className = "previews"; inp.after(box);
    inp.addEventListener("change", function () {
      box.innerHTML = "";
      Array.prototype.slice.call(inp.files, 0, 5).forEach(function (f) {
        var img = document.createElement("img"); img.src = URL.createObjectURL(f); img.alt = ""; box.appendChild(img);
      });
    });
  });

  /* ---------- maps ---------- */
  if (!window.L) return;
  var TILE = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  var ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
  var center = (window.SHAJJAR && SHAJJAR.center) || [36.3456, 43.145];
  var zoom = (window.SHAJJAR && SHAJJAR.zoom) || 12;
  var kindIcon = { forest: "🌲", street: "🛣️", neighborhood: "🏘️", orchard: "🌾", school: "🏫", hospital: "🏥", institution: "🏢", village: "🏡", public: "🌳" };

  function baseMap(el, opts) {
    var m = L.map(el, Object.assign({ scrollWheelZoom: false, attributionControl: true }, opts || {})).setView(center, zoom);
    L.tileLayer(TILE, { maxZoom: 19, attribution: ATTR, referrerPolicy: "strict-origin-when-cross-origin" }).addTo(m);
    m.on("focus click", function () { m.scrollWheelZoom.enable(); });
    return m;
  }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  var nf = new Intl.NumberFormat("ar-IQ");
  var healthLabel = { good: "✅ بحالة جيدة", attention: "🟡 تحتاج متابعة", damaged: "🔴 متضررة", forest: "🌲 غابة / مشروع تشجير" };

  document.querySelectorAll("[data-sites-map]").forEach(function (el) {
    var m = baseMap(el, { scrollWheelZoom: el.dataset.wheel === "1" });
    var layer = L.featureGroup().addTo(m), all = [];
    function draw(filter) {
      layer.clearLayers();
      all.filter(function (f) { return !filter || filter === "all" || f.health === filter || (filter === "trees" && f.type === "tree"); })
        .forEach(function (f) {
          var icon = f.type === "site"
            ? L.divIcon({ className: "", html: '<div class="shj-pin ' + f.health + '"><span>' + (kindIcon[f.kind] || "🌳") + "</span></div>", iconSize: [30, 30], iconAnchor: [15, 30], popupAnchor: [0, -28] })
            : L.divIcon({ className: "", html: '<div class="shj-tree ' + f.health + '"></div>', iconSize: [14, 14], iconAnchor: [7, 7] });
          var html = f.type === "site"
            ? "<h4>" + esc(f.name) + "</h4>" +
              "🌳 " + nf.format(f.trees) + " شجرة<br>" +
              (f.species ? "🌱 النوع: " + esc(f.species) + "<br>" : "") +
              (f.date ? "📅 الزراعة: " + esc(f.date) + "<br>" : "") +
              (f.watering ? "💧 السقي: " + esc(f.watering) + "<br>" : "") +
              (healthLabel[f.health] || "") + (f.rate != null ? " · نسبة النجاح " + nf.format(f.rate) + "%" : "") +
              '<br><a href="' + f.url + '">عرض الموقع ←</a>'
            : "<h4 dir='ltr' style='text-align:right'>" + esc(f.name) + "</h4>🌳 " + esc(f.species) + "<br>📍 " + esc(f.district) + "<br>💚 " + esc(f.status) + '<br><a href="' + f.url + '">ملف الشجرة ←</a>';
          L.marker([f.lat, f.lng], { icon: icon, title: f.name }).bindPopup(html).addTo(layer);
        });
      if (layer.getLayers().length && el.dataset.fit !== "0") m.fitBounds(layer.getBounds().pad(0.15), { maxZoom: 14 });
    }
    fetch(el.dataset.sitesMap).then(function (r) { return r.json(); }).then(function (d) { all = d.features; draw("all"); });
    document.querySelectorAll("[data-map-filter]").forEach(function (b) {
      b.addEventListener("click", function () {
        document.querySelectorAll("[data-map-filter]").forEach(function (x) { x.classList.remove("btn-primary"); x.classList.add("btn-ghost"); });
        b.classList.add("btn-primary"); b.classList.remove("btn-ghost");
        draw(b.dataset.mapFilter);
      });
    });
    var loc = document.querySelector("[data-locate-me]");
    if (loc) loc.addEventListener("click", function () { m.locate({ setView: true, maxZoom: 15 }); });
  });

  document.querySelectorAll("[data-point-map]").forEach(function (el) {
    var lat = parseFloat(el.dataset.lat), lng = parseFloat(el.dataset.lng);
    var m = baseMap(el); m.setView([lat, lng], parseInt(el.dataset.zoom || "15", 10));
    L.marker([lat, lng], { icon: L.divIcon({ className: "", html: '<div class="shj-pin ' + (el.dataset.health || "good") + '"><span>' + (el.dataset.icon || "🌳") + "</span></div>", iconSize: [30, 30], iconAnchor: [15, 30] }) }).addTo(m);
  });

  /* location picker: <div data-picker data-lat="#id_latitude" data-lng="#id_longitude"> */
  document.querySelectorAll("[data-picker]").forEach(function (el) {
    var latI = document.querySelector(el.dataset.lat), lngI = document.querySelector(el.dataset.lng);
    var out = document.querySelector(el.dataset.out);
    var m = baseMap(el, { scrollWheelZoom: true }), marker = null;
    function set(latlng, pan) {
      latI.value = latlng.lat.toFixed(6); lngI.value = latlng.lng.toFixed(6);
      if (!marker) {
        marker = L.marker(latlng, { draggable: true, icon: L.divIcon({ className: "", html: '<div class="shj-pin good"><span>📍</span></div>', iconSize: [30, 30], iconAnchor: [15, 30] }) }).addTo(m);
        marker.on("dragend", function () { set(marker.getLatLng(), false); });
      } else marker.setLatLng(latlng);
      if (pan) m.setView(latlng, Math.max(m.getZoom(), 16));
      if (out) out.textContent = latI.value + ", " + lngI.value;
    }
    if (latI.value && lngI.value) set(L.latLng(parseFloat(latI.value), parseFloat(lngI.value)), true);
    m.on("click", function (e) { set(e.latlng, false); });
    var gps = document.querySelector(el.dataset.gps);
    if (gps) gps.addEventListener("click", function () {
      if (!navigator.geolocation) { alert("المتصفح لا يدعم تحديد الموقع"); return; }
      gps.disabled = true; gps.textContent = "⏳ جاري تحديد موقعك…";
      navigator.geolocation.getCurrentPosition(function (p) {
        set(L.latLng(p.coords.latitude, p.coords.longitude), true); gps.disabled = false; gps.textContent = "📍 تم تحديد موقعك (اسحب الدبوس للتعديل)";
      }, function () { gps.disabled = false; gps.textContent = "📍 تعذر تحديد الموقع — اختر على الخريطة"; }, { enableHighAccuracy: true, timeout: 12000 });
    });
    if (el.dataset.autoGps === "1" && gps && !latI.value) gps.click();
  });
})();
