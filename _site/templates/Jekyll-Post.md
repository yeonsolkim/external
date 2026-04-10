<%*
  // 1. 파일의 실제 생성 날짜를 가져옴
  let cDate = tp.file.creation_date("YYYY-MM-DD");
  let title = tp.file.title;

  // 2. 파일 이름이 생성 날짜로 시작하지 않으면 강제 변경
  if (!title.startsWith(cDate)) {
      await tp.file.rename(`${cDate}-${title}`);
  }

  // 3. 경로에서 카테고리 추출 및 정제
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
date: <% tp.file.creation_date("YYYY-MM-DD HH:mm:ss") %> +0900
categories: <% categoriesResult %>
---