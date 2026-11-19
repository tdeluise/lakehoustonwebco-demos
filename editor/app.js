/* Lake Houston Web Co — phone editor for an owner's website.
   Plain JS, no build step. Talks to editor-api/worker.js with the owner's private key. */
(function () {
  "use strict";

  var CONTACT = window.EDITOR_CONTACT || {};
  var LOCAL = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var API = (LOCAL ? location.origin : window.EDITOR_API || "").replace(/\/$/, "");
  var DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  // ---------- words ----------
  var T = {
    en: {
      loading: "Loading your website…",
      nokey_title: "Open your edit link",
      nokey_body: "This page edits your business website. Open it from the private link Lake Houston Web Co texted you.",
      badkey_title: "This link doesn't work",
      contact_us: "Text {name}",
      call_us: "Call {name}",
      view_site: "View my website",
      greeting: "What do you want to change?",
      notice: "Announcement", notice_sub: "Closed today, holiday hours, news",
      hours: "Hours", hours_sub: "When you're open",
      specials: "Specials", specials_sub: "Deals and featured items",
      menu: "Menu & services", menu_sub: "What you offer",
      photos: "Photos", photos_sub: "Add or remove pictures",
      contact: "Phone & tagline", contact_sub: "How customers reach you",
      about: "About", about_sub: "Your story",
      showing_now: "Showing on your site now",
      ends: "until {d}",
      back: "Back",
      save: "Save",
      saving: "Saving…",
      saved: "Saved! Your website updates in about 2 minutes.",
      no_changes: "Nothing changed.",
      unsaved: "You have changes that aren't saved. Leave without saving?",
      conflict_reload: "Reload",
      offline: "No internet connection. Your change wasn't saved.",
      error: "Something went wrong. Your change wasn't saved.",
      site_in_english: "Your website is in English, so write announcements in English (or both languages).",
      notice_label: "Announcement text",
      notice_ph: "Closed today for a family event. See you tomorrow!",
      quick: "Quick picks",
      q_closed: "Closed today", q_closed_txt: "We're closed today. See you tomorrow!",
      q_early: "Closing early", q_early_txt: "Closing early today at 3 PM.",
      q_holiday: "Holiday", q_holiday_txt: "Closed for the holiday. Back to normal hours soon!",
      q_hiring: "Hiring", q_hiring_txt: "We're hiring! Ask at the counter.",
      show_for: "Show it",
      for_today: "Today only",
      for_until: "Until a date",
      for_ever: "Until I remove it",
      until_date: "Last day to show it",
      remove_notice: "Remove announcement",
      removed: "Removed. Your website updates in about 2 minutes.",
      open: "Open",
      closed: "Closed",
      to: "to",
      type_instead: "Type it instead",
      use_times: "Pick times",
      custom_ph: "11 AM – 2 PM, 5 – 9 PM",
      copy_weekdays: "Copy Monday to Tuesday–Friday",
      hours_tip: "Changing hours for one day only? Use an Announcement instead.",
      no_hours: "Your site doesn't list day-by-day hours yet.",
      set_hours: "Set hours for each day",
      phone: "Phone number",
      tagline: "Tagline (one short line under your name)",
      address: "Address",
      address_help: "To change your address, contact {name}. The map link has to be updated too.",
      special_title: "Name", special_price: "Price (optional)", special_text: "Details (optional)",
      special_title_ph: "Taco Tuesday", special_text_ph: "3 tacos and a drink",
      add_special: "+ Add a special",
      remove: "Remove",
      move_up: "Move up",
      no_specials: "No specials yet.",
      menu_heading: "Section heading on your site",
      section_title: "Group name (optional)",
      section_items: "Items, one per line",
      add_section: "+ Add a group",
      add_photo: "+ Add a photo",
      uploading: "Uploading photo…",
      photo_added: "Photo added! It shows on your website in about 2 minutes.",
      photo_alt: "What's in the photo?",
      photo_alt_ph: "Fresh birria tacos",
      no_photos: "No photos yet. Pictures of your food, shop or work help customers choose you.",
      photo_too_big: "That photo couldn't be read. Try a different one.",
      about_label: "About your business. Leave a blank line between paragraphs.",
      install_title: "Put this on your home screen",
      install_ios: "Tap Share, then “Add to Home Screen”. Next time just tap the icon.",
      install_other: "Open your browser menu and tap “Add to Home screen” or “Install”.",
      dismiss: "Got it",
      help: "Need something else changed? {name} can help:",
      lang_switch: "Español",
    },
    es: {
      loading: "Cargando su sitio web…",
      nokey_title: "Abra su enlace de edición",
      nokey_body: "Esta página edita el sitio web de su negocio. Ábrala desde el enlace privado que Lake Houston Web Co le envió por mensaje.",
      badkey_title: "Este enlace no funciona",
      contact_us: "Mensaje a {name}",
      call_us: "Llamar a {name}",
      view_site: "Ver mi sitio web",
      greeting: "¿Qué quiere cambiar?",
      notice: "Aviso", notice_sub: "Cerrado hoy, horario de días festivos, noticias",
      hours: "Horario", hours_sub: "Cuándo está abierto",
      specials: "Especiales", specials_sub: "Ofertas y platillos destacados",
      menu: "Menú y servicios", menu_sub: "Lo que ofrece",
      photos: "Fotos", photos_sub: "Agregar o quitar fotos",
      contact: "Teléfono y lema", contact_sub: "Cómo lo contactan",
      about: "Acerca de", about_sub: "Su historia",
      showing_now: "Se muestra ahora en su sitio",
      ends: "hasta el {d}",
      back: "Atrás",
      save: "Guardar",
      saving: "Guardando…",
      saved: "¡Guardado! Su sitio web se actualiza en unos 2 minutos.",
      no_changes: "No hubo cambios.",
      unsaved: "Tiene cambios sin guardar. ¿Salir sin guardar?",
      conflict_reload: "Recargar",
      offline: "No hay conexión a internet. Su cambio no se guardó.",
      error: "Algo salió mal. Su cambio no se guardó.",
      site_in_english: "Su sitio web está en inglés. Escriba el aviso en inglés (o en los dos idiomas).",
      notice_label: "Texto del aviso",
      notice_ph: "Closed today for a family event. See you tomorrow!",
      quick: "Opciones rápidas",
      q_closed: "Cerrado hoy", q_closed_txt: "We're closed today. See you tomorrow!",
      q_early: "Cerramos temprano", q_early_txt: "Closing early today at 3 PM.",
      q_holiday: "Día festivo", q_holiday_txt: "Closed for the holiday. Back to normal hours soon!",
      q_hiring: "Contratando", q_hiring_txt: "We're hiring! Ask at the counter.",
      show_for: "Mostrarlo",
      for_today: "Solo hoy",
      for_until: "Hasta una fecha",
      for_ever: "Hasta que lo quite",
      until_date: "Último día que se muestra",
      remove_notice: "Quitar aviso",
      removed: "Quitado. Su sitio web se actualiza en unos 2 minutos.",
      open: "Abierto",
      closed: "Cerrado",
      to: "a",
      type_instead: "Escribirlo",
      use_times: "Elegir horas",
      custom_ph: "11 AM – 2 PM, 5 – 9 PM",
      copy_weekdays: "Copiar lunes a martes–viernes",
      hours_tip: "¿Cambia el horario solo un día? Mejor use un Aviso.",
      no_hours: "Su sitio todavía no muestra el horario de cada día.",
      set_hours: "Poner horario para cada día",
      phone: "Número de teléfono",
      tagline: "Lema (una línea corta bajo su nombre)",
      address: "Dirección",
      address_help: "Para cambiar su dirección, contacte a {name}. También hay que actualizar el mapa.",
      special_title: "Nombre", special_price: "Precio (opcional)", special_text: "Detalles (opcional)",
      special_title_ph: "Taco Tuesday", special_text_ph: "3 tacos and a drink",
      add_special: "+ Agregar especial",
      remove: "Quitar",
      move_up: "Subir",
      no_specials: "Todavía no hay especiales.",
      menu_heading: "Título de la sección en su sitio",
      section_title: "Nombre del grupo (opcional)",
      section_items: "Artículos, uno por línea",
      add_section: "+ Agregar grupo",
      add_photo: "+ Agregar foto",
      uploading: "Subiendo foto…",
      photo_added: "¡Foto agregada! Aparece en su sitio web en unos 2 minutos.",
      photo_alt: "¿Qué muestra la foto? (en inglés)",
      photo_alt_ph: "Fresh birria tacos",
      no_photos: "Todavía no hay fotos. Fotos de su comida, local o trabajo ayudan a que lo elijan.",
      photo_too_big: "No se pudo leer esa foto. Pruebe con otra.",
      about_label: "Acerca de su negocio. Deje una línea en blanco entre párrafos.",
      install_title: "Póngalo en su pantalla de inicio",
      install_ios: "Toque Compartir y luego “Agregar a inicio”. La próxima vez solo toque el ícono.",
      install_other: "Abra el menú del navegador y toque “Agregar a la pantalla principal” o “Instalar”.",
      dismiss: "Entendido",
      help: "¿Necesita otro cambio? {name} le puede ayudar:",
      lang_switch: "English",
    },
  };
  var DAY_ES = { Monday: "Lunes", Tuesday: "Martes", Wednesday: "Miércoles", Thursday: "Jueves", Friday: "Viernes", Saturday: "Sábado", Sunday: "Domingo" };

  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  var lang = store.get("lhwc-lang") || (/^es\b/i.test(navigator.language || "") ? "es" : "en");
  function t(k, vars) {
    var s = (T[lang] && T[lang][k]) || T.en[k] || k;
    vars = vars || {};
    if (!vars.name) vars.name = CONTACT.name || "Lake Houston Web Co";
    return s.replace(/\{(\w+)\}/g, function (_, v) { return vars[v] != null ? vars[v] : ""; });
  }
  function dayName(d) { return lang === "es" ? DAY_ES[d] : d; }

  // ---------- key ----------
  // The key stays in the address (#k=...) so "Add to Home Screen" keeps it:
  // iPhone home-screen apps don't share storage with Safari.
  function readKey() {
    var m = location.hash.match(/k=([A-Za-z0-9_-]{20,100})/);
    if (m) { store.set("lhwc-edit-key", m[1]); return m[1]; }
    var k = store.get("lhwc-edit-key");
    if (k) { try { history.replaceState(null, "", "#k=" + k); } catch (e) {} }
    return k;
  }
  var KEY = readKey();

  // ---------- tiny DOM helper ----------
  function h(tag, attrs) {
    var el = document.createElement(tag);
    attrs = attrs || {};
    for (var a in attrs) {
      var v = attrs[a];
      if (v == null || v === false) continue;
      if (a === "class") el.className = v;
      else if (a === "text") el.textContent = v;
      else if (a.slice(0, 2) === "on") el.addEventListener(a.slice(2), v);
      else if (a in el && a !== "list" && a !== "type") el[a] = v;
      else el.setAttribute(a, v === true ? "" : v);
    }
    for (var i = 2; i < arguments.length; i++) add(el, arguments[i]);
    return el;
  }
  function add(el, kid) {
    if (kid == null || kid === false) return;
    if (Array.isArray(kid)) { kid.forEach(function (k) { add(el, k); }); return; }
    el.appendChild(typeof kid === "string" ? document.createTextNode(kid) : kid);
  }
  var uid = 0;
  function field(label, input, help) {
    var id = "f" + ++uid;
    input.id = id;
    return h("div", { class: "field" }, h("label", { for: id, text: label }), input, help ? h("p", { class: "help", text: help }) : null);
  }

  var toastTimer;
  function toast(msg, bad) {
    var el = document.getElementById("toast");
    el.textContent = msg;
    el.className = "show" + (bad ? " bad" : "");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.className = ""; }, bad ? 7000 : 4500);
  }

  // ---------- API ----------
  function api(method, path, body, contentType) {
    var opts = { method: method, headers: { authorization: "Bearer " + KEY } };
    if (body !== undefined) {
      opts.headers["content-type"] = contentType || "application/json";
      opts.body = contentType ? body : JSON.stringify(body);
    }
    return fetch(API + path, opts).then(
      function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) {
          if (!r.ok) { var e = new Error(j.error || t("error")); e.status = r.status; throw e; }
          return j;
        });
      },
      function () { var e = new Error(t("offline")); e.status = 0; throw e; }
    );
  }

  // ---------- state ----------
  var site = null; // last server view
  var screen = "home";
  var panel = null; // { collect, initial }
  var localPhotos = {}; // src -> object URL for photos uploaded this session
  var app = document.getElementById("app");

  function go(next) {
    if (panel && screen !== "home" && next === "home") {
      if (JSON.stringify(panel.collect()) !== panel.initial && !confirm(t("unsaved"))) return;
    }
    screen = next;
    render();
    window.scrollTo(0, 0);
  }

  function render() {
    document.documentElement.lang = lang;
    app.textContent = "";
    if (!KEY) return add(app, noKey(t("nokey_title"), t("nokey_body")));
    if (!site) return add(app, h("p", { class: "loading", text: t("loading") }));
    if (screen === "home") { panel = null; return add(app, home()); }
    add(app, panelScreen(screen));
  }

  function load() {
    if (!KEY) return render();
    render();
    api("GET", "/api/site").then(
      function (j) { site = j; render(); },
      function (e) {
        app.textContent = "";
        add(app, e.status === 401 ? noKey(t("badkey_title"), e.message) : noKey(t("error"), e.message, true));
      }
    );
  }

  // ---------- screens ----------
  function contactButtons() {
    var digits = String(CONTACT.phone || "").replace(/\D/g, "");
    if (!digits) return null;
    return h("div", { class: "row" },
      h("a", { class: "btn sun", href: "sms:+1" + digits, text: t("contact_us") }),
      h("a", { class: "btn plain", href: "tel:+1" + digits, text: t("call_us") }));
  }

  function langButton() {
    return h("button", { class: "lang", type: "button", text: t("lang_switch"), onclick: function () {
      lang = lang === "es" ? "en" : "es";
      store.set("lhwc-lang", lang);
      render();
    } });
  }

  function noKey(title, body, retry) {
    return h("main", { class: "shell narrow" },
      h("div", { class: "top" }, h("span", { class: "brand", text: "Lake Houston Web Co" }), langButton()),
      h("h1", { text: title }),
      h("p", { class: "lede", text: body }),
      retry ? h("button", { class: "btn plain", type: "button", text: t("conflict_reload"), onclick: function () { location.reload(); } }) : null,
      contactButtons());
  }

  var TILES = [
    ["notice", "📣"], ["hours", "🕒"], ["specials", "⭐"], ["menu", "📋"],
    ["photos", "📷"], ["contact", "📞"], ["about", "✍️"],
  ];

  function home() {
    var f = site.fields;
    var n = f.notice;
    var tiles = TILES.map(function (x) {
      var key = x[0];
      var title = key === "menu" && f.items_title && f.items_title !== "Menu" && lang === "en" ? f.items_title : t(key);
      return h("button", { class: "tile", type: "button", onclick: function () { go(key); } },
        h("span", { class: "ico", "aria-hidden": "true", text: x[1] }),
        h("span", { class: "tile-text" }, h("b", { text: title }), h("span", { text: t(key + "_sub") })),
        h("span", { class: "chev", "aria-hidden": "true", text: "›" }));
    });
    return h("main", { class: "shell" },
      h("div", { class: "top" }, h("span", { class: "brand", text: "Lake Houston Web Co" }), langButton()),
      h("header", { class: "biz" },
        h("h1", { text: site.name }),
        h("a", { class: "btn plain small", href: site.live_url, target: "_blank", rel: "noopener", text: t("view_site") + " ↗" })),
      n && n.text ? h("button", { class: "live-notice", type: "button", onclick: function () { go("notice"); } },
        h("span", { class: "eyebrow", text: t("showing_now") + (n.until ? " · " + t("ends", { d: prettyDate(n.until) }) : "") }),
        h("b", { text: n.text })) : null,
      h("h2", { class: "ask", text: t("greeting") }),
      h("div", { class: "tiles" }, tiles),
      installHint(),
      h("footer", { class: "help-foot" }, h("p", { text: t("help") }), contactButtons()));
  }

  function installHint() {
    var standalone = window.navigator.standalone || (window.matchMedia && matchMedia("(display-mode: standalone)").matches);
    if (standalone || store.get("lhwc-install-dismissed")) return null;
    var ios = /iPhone|iPad|iPod/.test(navigator.userAgent);
    var box = h("aside", { class: "install" },
      h("b", { text: t("install_title") }),
      h("p", { text: ios ? t("install_ios") : t("install_other") }),
      h("button", { class: "link", type: "button", text: t("dismiss"), onclick: function () { store.set("lhwc-install-dismissed", "1"); box.remove(); } }));
    return box;
  }

  function panelScreen(name) {
    var builders = { notice: noticePanel, hours: hoursPanel, specials: specialsPanel, menu: menuPanel, photos: photosPanel, contact: contactPanel, about: aboutPanel };
    var p = builders[name]();
    var saveBtn = h("button", { class: "btn sun wide", type: "button", text: t("save") });
    saveBtn.addEventListener("click", function () { save(p.collect(), saveBtn); });
    panel = { collect: p.collect, initial: JSON.stringify(p.collect()) };
    return h("main", { class: "shell narrow panel" },
      h("div", { class: "top" },
        h("button", { class: "back", type: "button", onclick: function () { go("home"); } }, h("span", { "aria-hidden": "true", text: "‹ " }), t("back"))),
      h("h1", { text: name === "menu" && lang === "en" && site.fields.items_title !== "Menu" ? site.fields.items_title : t(name) }),
      p.el,
      p.noSave ? null : h("div", { class: "savebar" }, saveBtn));
  }

  function save(fields, btn, okMsg) {
    if (btn) { btn.disabled = true; btn.textContent = t("saving"); }
    return api("PUT", "/api/site", { version: site.version, fields: fields }).then(
      function (j) {
        site = j;
        toast(j.changed && j.changed.length ? okMsg || t("saved") : t("no_changes"));
        panel = null;
        go("home");
      },
      function (e) {
        if (btn) { btn.disabled = false; btn.textContent = t("save"); }
        toast(e.message, true);
        if (e.status === 409) {
          var b = h("button", { class: "btn plain", type: "button", text: t("conflict_reload"), onclick: function () { location.reload(); } });
          var bar = document.querySelector(".savebar");
          if (bar && !bar.querySelector(".plain")) bar.appendChild(b);
        }
        throw e;
      }
    ).catch(function () {});
  }

  // ---------- panels ----------
  function todayCentral() {
    try { return new Intl.DateTimeFormat("en-CA", { timeZone: "America/Chicago" }).format(new Date()); }
    catch (e) { return new Date().toISOString().slice(0, 10); }
  }
  function prettyDate(iso) {
    var p = iso.split("-");
    try { return new Date(+p[0], +p[1] - 1, +p[2]).toLocaleDateString(lang === "es" ? "es-US" : "en-US", { weekday: "short", month: "short", day: "numeric" }); }
    catch (e) { return iso; }
  }

  function noticePanel() {
    var n = site.fields.notice || {};
    var text = h("textarea", { rows: 3, maxLength: 200, placeholder: t("notice_ph"), value: n.text || "" });
    var today = todayCentral();
    var mode = n.text ? (n.until ? (n.until === today ? "today" : "until") : "ever") : "today";
    var date = h("input", { type: "date", min: today, value: n.until && n.until !== today ? n.until : today });
    var dateField = field(t("until_date"), date);
    var radios = ["today", "until", "ever"].map(function (m) {
      var r = h("input", { type: "radio", name: "dur", value: m, checked: m === mode, onchange: sync });
      return h("label", { class: "choice" }, r, h("span", { text: t("for_" + m) }));
    });
    function current() { var c = document.querySelector('input[name="dur"]:checked'); return c ? c.value : mode; }
    function sync() { dateField.hidden = current() !== "until"; }
    var chips = ["closed", "early", "holiday", "hiring"].map(function (q) {
      return h("button", { class: "chip", type: "button", text: t("q_" + q), onclick: function () {
        text.value = t("q_" + q + "_txt");
        if (q === "closed" || q === "early") { var r = document.querySelector('input[name="dur"][value="today"]'); if (r) { r.checked = true; sync(); } }
        text.focus();
      } });
    });
    dateField.hidden = mode !== "until";
    function collect() {
      var v = text.value.trim();
      if (!v) return { notice: null };
      var m = current();
      return { notice: { text: v, until: m === "today" ? today : m === "until" ? date.value : "" } };
    }
    var el = h("div", null,
      h("p", { class: "help", text: t("site_in_english") }),
      h("div", { class: "field" }, h("span", { class: "label", text: t("quick") }), h("div", { class: "chips" }, chips)),
      field(t("notice_label"), text),
      h("fieldset", { class: "field" }, h("legend", { text: t("show_for") }), radios),
      dateField,
      n.text ? h("button", { class: "btn danger wide", type: "button", text: t("remove_notice"), onclick: function (ev) { save({ notice: null }, ev.target, t("removed")); } }) : null);
    return { el: el, collect: collect };
  }

  // Hours like "8:00 AM – 5:30 PM" get time pickers; anything else is typed.
  var RANGE = /^(\d{1,2})(?::(\d{2}))?\s*([AP])\.?M\.?\s*[–—-]\s*(\d{1,2})(?::(\d{2}))?\s*([AP])\.?M\.?$/i;
  function to24(hh, mm, ap) { hh = +hh % 12 + (/p/i.test(ap) ? 12 : 0); return (hh < 10 ? "0" : "") + hh + ":" + (mm || "00"); }
  function to12(v) {
    var p = v.split(":"), hh = +p[0], ap = hh >= 12 ? "PM" : "AM";
    hh = hh % 12 || 12;
    return hh + ":" + p[1] + " " + ap;
  }

  function dayRow(day, value) {
    value = value || "Closed";
    var closed = /^closed$/i.test(value.trim());
    var m = value.trim().match(RANGE);
    var open = h("input", { type: "time", value: m ? to24(m[1], m[2], m[3]) : "09:00", "aria-label": dayName(day) + " " + t("open") });
    var close = h("input", { type: "time", value: m ? to24(m[4], m[5], m[6]) : "17:00", "aria-label": dayName(day) + " " + t("closed") });
    var custom = h("input", { type: "text", maxLength: 40, value: closed || m ? "" : value, placeholder: t("custom_ph"), "aria-label": dayName(day) });
    var typed = !closed && !m;
    var isOpen = h("input", { type: "checkbox", checked: !closed, onchange: sync });
    var times = h("div", { class: "times" }, open, h("span", { text: t("to") }), close);
    var toggle = h("button", { class: "link", type: "button", onclick: function () { typed = !typed; sync(); } });
    var stateText = h("span");
    function sync() {
      times.hidden = !isOpen.checked || typed;
      custom.hidden = !isOpen.checked || !typed;
      toggle.hidden = !isOpen.checked;
      toggle.textContent = typed ? t("use_times") : t("type_instead");
      stateText.textContent = isOpen.checked ? t("open") : t("closed");
    }
    sync();
    var row = h("div", { class: "day" },
      h("div", { class: "day-head" }, h("b", { text: dayName(day) }), h("label", { class: "switch" }, isOpen, stateText)),
      times, custom, toggle);
    return {
      el: row,
      get: function () {
        if (!isOpen.checked) return "Closed";
        if (typed) return custom.value.trim() || "Closed";
        return to12(open.value || "09:00") + " – " + to12(close.value || "17:00");
      },
      set: function (v) { var copy = dayRow(day, v); row.replaceWith(copy.el); this.el = copy.el; this.get = copy.get; this.set = copy.set; },
    };
  }

  // A site with no day-by-day hours (just a written note, or nothing) keeps that
  // until the owner chooses to set hours, so saving never invents "Closed" days.
  function hoursEditor(hours, note) {
    var rows = DAYS.map(function (d) { return dayRow(d, hours && hours[d]); });
    var copy = h("button", { class: "btn plain small", type: "button", text: t("copy_weekdays"), onclick: function () {
      var mon = rows[0].get();
      for (var i = 1; i <= 4; i++) rows[i].set(mon);
    } });
    var grid = h("div", { class: "hours" }, rows.map(function (r) { return r.el; }), copy);
    var using = !!hours;
    var intro = null;
    if (!using) {
      grid.hidden = true;
      intro = h("div", { class: "card" },
        h("p", { class: "readonly", text: note || t("no_hours") }),
        h("button", { class: "btn plain wide", type: "button", text: t("set_hours"), onclick: function () { using = true; intro.remove(); grid.hidden = false; } }),
        h("div", { class: "row-tools" }));
    }
    return {
      el: h("div", null, intro, grid),
      get: function () {
        if (!using) return null;
        var o = {}; rows.forEach(function (r, i) { o[DAYS[i]] = r.get(); }); return o;
      },
    };
  }

  function hoursPanel() {
    var f = site.fields;
    var tip = h("p", { class: "help", text: t("hours_tip") });
    if (site.has_locations) {
      var eds = f.locations.map(function (L) {
        var ph = h("input", { type: "tel", maxLength: 20, value: L.phone, autocomplete: "tel" });
        var he = hoursEditor(L.hours, L.hours_note);
        return { L: L, ph: ph, he: he, el: h("section", { class: "loc" }, h("h2", { text: L.label || L.address }), h("p", { class: "help", text: L.address }), field(t("phone"), ph), he.el) };
      });
      return {
        el: h("div", null, tip, eds.map(function (e) { return e.el; })),
        collect: function () { return { locations: eds.map(function (e) { return { phone: e.ph.value.trim(), hours: e.he.get() }; }) }; },
      };
    }
    var he = hoursEditor(f.hours, f.hours_note);
    return { el: h("div", null, tip, he.el), collect: function () { return { hours: he.get() }; } };
  }

  function listEditor(items, makeRow, addLabel, emptyText) {
    var wrap = h("div", { class: "list" });
    var rows = [];
    var empty = h("p", { class: "empty", text: emptyText });
    function redraw() {
      wrap.textContent = "";
      rows.forEach(function (r, i) {
        var tools = h("div", { class: "row-tools" },
          i > 0 ? h("button", { class: "link", type: "button", text: "↑ " + t("move_up"), onclick: function () { rows.splice(i - 1, 0, rows.splice(i, 1)[0]); redraw(); } }) : null,
          h("button", { class: "link danger", type: "button", text: t("remove"), onclick: function () { rows.splice(i, 1); redraw(); } }));
        wrap.appendChild(h("div", { class: "card" }, r.el, tools));
      });
      if (!rows.length && emptyText) wrap.appendChild(empty);
    }
    items.forEach(function (x) { rows.push(makeRow(x)); });
    redraw();
    var addBtn = addLabel ? h("button", { class: "btn plain wide", type: "button", text: addLabel, onclick: function () {
      rows.push(makeRow({}));
      redraw();
      var inputs = wrap.querySelectorAll(".card:last-child input, .card:last-child textarea");
      if (inputs[0]) inputs[0].focus();
    } }) : null;
    return {
      el: h("div", null, wrap, addBtn),
      get: function () { return rows.map(function (r) { return r.get(); }); },
      push: function (x) { rows.push(makeRow(x)); redraw(); },
    };
  }

  function specialsPanel() {
    var le = listEditor(site.fields.specials, function (s) {
      var title = h("input", { type: "text", maxLength: 60, value: s.title || "", placeholder: t("special_title_ph") });
      var price = h("input", { type: "text", maxLength: 20, value: s.price || "", placeholder: "$5", inputMode: "decimal" });
      var text = h("textarea", { rows: 2, maxLength: 240, value: s.text || "", placeholder: t("special_text_ph") });
      return {
        el: h("div", null, h("div", { class: "two" }, field(t("special_title"), title), field(t("special_price"), price)), field(t("special_text"), text)),
        get: function () { return { title: title.value.trim(), price: price.value.trim(), text: text.value.trim() }; },
      };
    }, t("add_special"), t("no_specials"));
    return {
      el: h("div", null, h("p", { class: "help", text: t("site_in_english") }), le.el),
      collect: function () { return { specials: le.get().filter(function (s) { return s.title; }) }; },
    };
  }

  function menuPanel() {
    var heading = h("input", { type: "text", maxLength: 30, value: site.fields.items_title || "Menu" });
    var le = listEditor(site.fields.items, function (g) {
      var title = h("input", { type: "text", maxLength: 60, value: g.title || "" });
      var items = h("textarea", { rows: Math.max(4, Math.min(14, (g.list || []).length + 1)), value: (g.list || []).join("\n") });
      return {
        el: h("div", null, field(t("section_title"), title), field(t("section_items"), items)),
        get: function () { return { title: title.value.trim(), list: items.value.split("\n").map(function (s) { return s.trim(); }).filter(Boolean) }; },
      };
    }, t("add_section"), "");
    return {
      el: h("div", null, h("p", { class: "help", text: t("site_in_english") }), field(t("menu_heading"), heading), le.el),
      collect: function () { return { items_title: heading.value.trim() || "Menu", items: le.get().filter(function (g) { return g.list.length; }) }; },
    };
  }

  function photoUrl(src) { return localPhotos[src] || site.live_url + src; }

  function photosPanel() {
    var le = listEditor(site.fields.photos, function (p) {
      var alt = h("input", { type: "text", maxLength: 120, value: p.alt || "", placeholder: t("photo_alt_ph") });
      return {
        el: h("div", { class: "photo-row" }, h("img", { src: photoUrl(p.src), alt: "" }), field(t("photo_alt"), alt)),
        get: function () { return { src: p.src, alt: alt.value.trim() }; },
      };
    }, null, t("no_photos"));
    var input = h("input", { type: "file", accept: "image/*", hidden: true });
    var addBtn = h("button", { class: "btn sun wide", type: "button", text: t("add_photo"), onclick: function () { input.click(); } });
    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      input.value = "";
      if (!file) return;
      addBtn.disabled = true;
      addBtn.textContent = t("uploading");
      shrink(file).then(function (blob) {
        return api("POST", "/api/photo", blob, blob.type).then(function (j) {
          localPhotos[j.src] = URL.createObjectURL(blob);
          var photos = le.get().concat([{ src: j.src, alt: "" }]);
          return save({ photos: photos }, null, t("photo_added")).then(function () { if (site) go("photos"); });
        });
      }).catch(function (e) {
        toast(e && e.message ? e.message : t("photo_too_big"), true);
      }).then(function () {
        addBtn.disabled = false;
        addBtn.textContent = t("add_photo");
      });
    });
    return { el: h("div", null, addBtn, input, le.el), collect: function () { return { photos: le.get() }; } };
  }

  // Phone photos are huge: scale to 1600px on the long side and re-encode as JPEG.
  function shrink(file) {
    var MAX = 1600;
    function draw(img, w, hgt) {
      var s = Math.min(1, MAX / Math.max(w, hgt));
      var c = document.createElement("canvas");
      c.width = Math.round(w * s);
      c.height = Math.round(hgt * s);
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      return new Promise(function (res, rej) { c.toBlob(function (b) { b ? res(b) : rej(new Error(t("photo_too_big"))); }, "image/jpeg", 0.82); });
    }
    if (window.createImageBitmap) {
      return createImageBitmap(file, { imageOrientation: "from-image" }).then(function (bmp) { return draw(bmp, bmp.width, bmp.height); }, function () { return viaImg(); });
    }
    return viaImg();
    function viaImg() {
      return new Promise(function (res, rej) {
        var img = new Image();
        img.onload = function () { res(draw(img, img.naturalWidth, img.naturalHeight)); URL.revokeObjectURL(img.src); };
        img.onerror = function () { rej(new Error(t("photo_too_big"))); };
        img.src = URL.createObjectURL(file);
      });
    }
  }

  function contactPanel() {
    var f = site.fields;
    var tagline = h("textarea", { rows: 2, maxLength: 160, value: f.tagline });
    var phone = site.has_locations ? null : h("input", { type: "tel", maxLength: 20, value: f.phone, autocomplete: "tel" });
    var addr = site.has_locations ? f.locations.map(function (L) { return L.address; }).join(" · ") : f.address;
    return {
      el: h("div", null,
        phone ? field(t("phone"), phone) : null,
        field(t("tagline"), tagline, t("site_in_english")),
        addr ? h("div", { class: "field" }, h("span", { class: "label", text: t("address") }), h("p", { class: "readonly", text: addr }), h("p", { class: "help", text: t("address_help") })) : null),
      collect: function () { var o = { tagline: tagline.value.trim() }; if (phone) o.phone = phone.value.trim(); return o; },
    };
  }

  function aboutPanel() {
    var text = h("textarea", { rows: 12, value: (site.fields.about || []).join("\n\n") });
    return {
      el: h("div", null, field(t("about_label"), text, t("site_in_english"))),
      collect: function () { return { about: text.value.split(/\n\s*\n/).map(function (s) { return s.trim(); }).filter(Boolean) }; },
    };
  }

  window.addEventListener("hashchange", function () { var k = readKey(); if (k && k !== KEY) { KEY = k; site = null; load(); } });
  load();
})();
