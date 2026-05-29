<%*
let cDate = tp.file.creation_date("YYYY-MM-DD");
let title = tp.file.title;

if (!title.startsWith(cDate)) {
  await tp.file.rename(`${cDate}-${title}`);
}

let folderPath = tp.file.folder(true);
let cleanPath = folderPath.replace("_posts/", "").replace("_posts", "");

let categoryPathResult = "[]";
if (cleanPath && cleanPath !== "/") {
  let cats = cleanPath
    .split("/")
    .filter(c => c.length > 0);

  categoryPathResult = "[" + cats.map(c => `"${c}"`).join(", ") + "]";
}

let createdAt = tp.file.creation_date("YYYY-MM-DD HH:mm:ss");
let modifiedAt = tp.file.last_modified_date("YYYY-MM-DD HH:mm:ss");
-%>
---
layout: post
title: "<% tp.file.title.replace(/\d{4}-\d{2}-\d{2}-/, "") %>"
date: <% createdAt %> +0900
last_modified_at: <% modifiedAt %> +0900
category_path: <% categoryPathResult %>
---