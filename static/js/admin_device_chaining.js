/* Цепочка select'ов в админке: список типов устройства (#id_device_type)
   фильтруется по выбранной категории (#id_category).
   Атрибут data-category-map на select типов содержит JSON вида
   {"<category_id>": ["<type_id>", ...]} — его заполняет DeviceAdminForm. */
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

    function rebuild() {
      var ok = allowedIds(category.value);
      var selected = type.value;
      type.textContent = "";
      allOptions.forEach(function (o) {
        // Оставляем: пустой вариант ("---------"), типы выбранной категории
        // и текущее выбранное значение (чтобы не терять существующие данные)
        if (o.value === "" || ok.indexOf(o.value) !== -1 || o.value === selected) {
          type.add(new Option(o.text, o.value, false, o.value === selected));
        }
      });
    }

    category.addEventListener("change", function () {
      var ok = allowedIds(category.value);
      if (type.value && ok.indexOf(type.value) === -1) {
        type.value = ""; // тип не входит в новую категорию — сбрасываем выбор
      }
      rebuild();
    });

    rebuild();
  });
})();
