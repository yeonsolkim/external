<%*
  let cDate = tp.file.creation_date("YYYY-MM-DD");
  let title = tp.file.title;

  if (!title.startsWith(cDate)) {
      await tp.file.rename(`${cDate}-${title}`);
  }

  let folderPath = tp.file.folder(true);
  let cleanPath = folderPath.replace("_posts/", "").replace("_posts", "");
  
  let categoriesResult = "[]";
  if (cleanPath && cleanPath !== "/") {
      let cats = cleanPath.split("/").filter(c => c.length > 0);
      categoriesResult = "[" + cats.map(c => `"${c}"`).join(", ") + "]";
  }
-%>
---
layout: post
title: "<% tp.file.title.replace(/\d{4}-\d{2}-\d{2}-/, "") %>"
date: <% tp.file.creation_date("YYYY-MM-DD HH:mm:ss") %> +0900
categories: <% categoriesResult %>
---