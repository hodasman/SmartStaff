function setupArticleImageUpload() {
   const maxImageSize = 10 * 1024 * 1024;
   const textArea = document.getElementById("id_text");
   if (!textArea) {
      return;
   }

   const uploadUrl = textArea.dataset.imageUploadUrl;
   const button = document.createElement("button");
   button.type = "button";
   button.className = "button";
   button.textContent = "Загрузить и вставить изображение";
   button.disabled = !uploadUrl;
   button.title = uploadUrl
      ? "Загрузить изображение и вставить его в текущую позицию текста"
      : "Сначала сохраните статью";

   const fileInput = document.createElement("input");
   fileInput.type = "file";
   fileInput.accept = "image/*";
   fileInput.hidden = true;

   textArea.insertAdjacentElement("beforebegin", button);
   button.insertAdjacentElement("afterend", fileInput);

   button.addEventListener("click", function () {
      fileInput.click();
   });

   fileInput.addEventListener("change", async function () {
      const image = fileInput.files[0];
      if (!image) {
         return;
      }
      if (image.size > maxImageSize) {
         window.alert("Размер изображения не должен превышать 10 МиБ.");
         fileInput.value = "";
         return;
      }

      const formData = new FormData();
      formData.append("image", image);
      formData.append("alt", window.prompt("Описание изображения (alt):", "") || "");

      button.disabled = true;
      try {
         const csrfToken = document.querySelector(
            '[name="csrfmiddlewaretoken"]'
         ).value;
         const response = await fetch(uploadUrl, {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken },
            body: formData,
            credentials: "same-origin",
         });
         const result = await response.json();
         if (!response.ok) {
            throw new Error(result.error || "Не удалось загрузить изображение.");
         }

         const token = "[[article-image:" + result.id + "]]";
         const start = textArea.selectionStart;
         const end = textArea.selectionEnd;
         textArea.setRangeText(token, start, end, "end");
         textArea.focus();
      } catch (error) {
         window.alert(error.message);
      } finally {
         fileInput.value = "";
         button.disabled = false;
      }
   });
}

if (document.readyState === "loading") {
   document.addEventListener("DOMContentLoaded", setupArticleImageUpload);
} else {
   setupArticleImageUpload();
}
