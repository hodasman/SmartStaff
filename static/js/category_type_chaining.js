/* Цепочка select'ов "категория -> тип устройства".
   Используется в админке (Device) и в фильтре каталога (devices_filter).
   Атрибут data-category-map на select типов содержит JSON вида
   {"<category_id>": ["<type_id>", ...]} — его заполняют DeviceAdminForm
   и DevicesFilter. */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var category = document.getElementById("id_category");
    var type = document.getElementById("id_device_type");
    if (!category || !type) return;

    var map;
    try {
      map = JSON.parse(type.getAttribute("data-category-map") || "{}");
    } catch (e) {
      return;
    }

    // Запоминаем полный список опций (value + текст + текущий выбор)
    var allOptions = Array.prototype.map.call(type.options, function (o) {
      return { value: o.value, text: o.textContent, selected: o.selected };
    });

    function allowedIds(catValue) {
      return (map[catValue] || []).map(String);
    }

    /* На фронте все select'ы оборачивает jquery.nice-select: он рисует
       визуальную копию (<div class="nice-select"> рядом с select) и не
       реагирует на изменение опций нативного select. После пересборки
       перерисовываем копию. В админке глобального jQuery нет — пропустится. */
    function refreshNiceSelect(select) {
      if (!window.jQuery) return;
      var $select = window.jQuery(select);
      var $copy = $select.next("div.nice-select");
      if ($copy.length) {
        $copy.remove();
        $select.niceSelect();
      }
    }

    function rebuild() {
      var cat = category.value;
      // Категория не выбрана — показываем все типы (важно для фильтра)
      var ok = cat ? allowedIds(cat) : null;
      var selected = type.value;
      type.textContent = "";
      allOptions.forEach(function (o) {
        // Пустой вариант, все типы (без категории), типы выбранной категории
        // и текущее выбранное значение (чтобы не терять существующие данные)
        if (o.value === "" || ok === null || ok.indexOf(o.value) !== -1 || o.value === selected) {
          type.add(new Option(o.text, o.value, false, o.value === selected));
        }
      });
      refreshNiceSelect(type);
    }

    function onChange() {
      var ok = allowedIds(category.value);
      if (category.value && type.value && ok.indexOf(type.value) === -1) {
        type.value = ""; // тип не входит в новую категорию — сбрасываем выбор
      }
      rebuild();
    }

    // Важно: jquery.nice-select триггерит "change" через jQuery.trigger(),
    // который НЕ вызывает слушателей, добавленных через addEventListener.
    // Поэтому вешаем оба: нативный слушатель (админка) и jQuery (фронт).
    category.addEventListener("change", onChange);
    if (window.jQuery) {
      window.jQuery(category).on("change.legacy_chain", onChange);
    }

    rebuild();
  });
})();
