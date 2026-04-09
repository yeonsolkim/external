<%*
  // 1. 파일명 날짜 자동 추가
  let title = tp.file.title;
  let dateNow = tp.date.now("YYYY-MM-DD");
  if (!title.startsWith(dateNow)) {
      await tp.file.rename(`${dateNow}-${title}`);
  }

  // 2. 경로에서 카테고리 추출 및 정제
  let folderPath = tp.file.folder(true);
  let cleanPath = folderPath.replace("_posts/", "").replace("_posts", "");
  
  let categoriesResult = "[]";
  if (cleanPath && cleanPath !== "/") {
      let cats = cleanPath.split("/").filter(c => c.length > 0);
      // ["English", "Grammar"] 형태의 문자열 생성
      categoriesResult = "[" + cats.map(c => `"${c}"`).join(", ") + "]";
  }
-%>
---
layout: post
title: "<% tp.file.title.replace(/\d{4}-\d{2}-\d{2}-/, "") %>"
date: <% tp.date.now("YYYY-MM-DD HH:mm:ss") %> +0900
categories: <% categoriesResult %>
---

<% tp.file.cursor() %>