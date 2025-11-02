document.addEventListener("DOMContentLoaded", () => {
  const titleInput = document.getElementById("id_title");
  const slugInput = document.getElementById("id_slug");
  if (titleInput && slugInput && !slugInput.value) {
    titleInput.addEventListener("blur", () => {
      if (!slugInput.value) {
        slugInput.value = titleInput.value
          .toString()
          .trim()
          .toLowerCase()
          .replace(/[^a-z0-9\u3040-\u30ff\u4e00-\u9faf\s-]/g, "")
          .replace(/\s+/g, "-")
          .replace(/-+/g, "-");
      }
    });
  }
});
